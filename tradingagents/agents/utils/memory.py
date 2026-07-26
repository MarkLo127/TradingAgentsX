import os
import re
import logging
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class FinancialSituationMemory:
    # Class-level cache: share a single SentenceTransformer instance across all memory objects
    _model_cache: dict = {}

    def __init__(self, name, config):
        """
        Initialize the memory with configurable embedding provider.
        
        Config options:
            embedding_provider: "local" (default) or "openai"
            embedding_model: Model name for the embedding provider
                - For local: "all-mpnet-base-v2" (default), etc.
                - For OpenAI: "text-embedding-3-small" (default), "text-embedding-3-large", etc.
            embedding_base_url: Base URL for OpenAI-compatible API (only used when provider is "openai")
            embedding_api_key: API key for OpenAI (only used when provider is "openai")
        """
        self.provider = config.get("embedding_provider", "local").lower()
        
        if self.provider == "local":
            self._init_local_embedding(config)
        elif self.provider == "openai":
            self._init_openai_embedding(config)
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}. Use 'local' or 'openai'.")
        
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        self.situation_collection = self.chroma_client.get_or_create_collection(name=name)

    def _init_local_embedding(self, config):
        """Initialize local embedding without any API key.

        優先用 sentence-transformers（品質較好，但需要 torch）。若環境沒有 torch
        （例如精簡打包的桌面版），自動退回 ChromaDB 內建的 ONNX MiniLM 嵌入 ——
        不需 torch、不需 API 金鑰，首次使用會下載約 80MB 的 onnx 模型後即可離線運作。
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            self._init_onnx_local_embedding()
            return

        # Default to all-mpnet-base-v2 - higher-quality general-purpose embeddings
        model_name = config.get("embedding_model", "all-mpnet-base-v2")

        import logging

        # Reuse cached model if already loaded (avoids loading 5 copies and OOM)
        if model_name not in FinancialSituationMemory._model_cache:
            logging.info(f"Loading local embedding model: {model_name}")
            FinancialSituationMemory._model_cache[model_name] = SentenceTransformer(model_name)
            logging.info(f"Local embedding model loaded successfully.")
        else:
            logging.info(f"Reusing cached embedding model: {model_name}")

        self.local_backend = "sentence-transformers"
        self.model = FinancialSituationMemory._model_cache[model_name]
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    def _init_onnx_local_embedding(self):
        """torch-free 本地嵌入：使用 ChromaDB 內建的 ONNX all-MiniLM-L6-v2。"""
        import logging
        from chromadb.utils import embedding_functions

        cache_key = "__chroma_onnx_default__"
        if cache_key not in FinancialSituationMemory._model_cache:
            logging.info(
                "sentence-transformers 不可用，改用 ChromaDB 內建 ONNX 嵌入（無需 torch / API 金鑰）"
            )
            FinancialSituationMemory._model_cache[cache_key] = (
                embedding_functions.DefaultEmbeddingFunction()
            )
        self.local_backend = "onnx"
        self._onnx_ef = FinancialSituationMemory._model_cache[cache_key]
        self.embedding_dim = 384  # all-MiniLM-L6-v2

    def _init_openai_embedding(self, config):
        """Initialize OpenAI embedding client."""
        from openai import OpenAI
        
        self.embedding_model = config.get("embedding_model", "text-embedding-3-small")
        
        # Get embedding configuration from config, with fallbacks
        embedding_base_url = config.get("embedding_base_url", "https://api.openai.com/v1")
        embedding_api_key = config.get("embedding_api_key")
        
        # Fallback chain for API key
        if not embedding_api_key:
            # Try environment variable first
            embedding_api_key = os.getenv("OPENAI_API_KEY")
            if not embedding_api_key:
                # Fall back to LLM keys as last resort
                embedding_api_key = config.get("quick_think_api_key") or config.get("deep_think_api_key")
                if embedding_api_key:
                    import logging
                    logging.warning("Using LLM API key for embeddings. Consider setting embedding_api_key or OPENAI_API_KEY.")
        
        if not embedding_api_key:
            raise ValueError(
                "OpenAI API key is required for OpenAI embeddings. "
                "Set 'embedding_api_key' in config or OPENAI_API_KEY environment variable, "
                "or use 'embedding_provider': 'local' for local embeddings without API key."
            )
        
        # Use configured endpoint for embeddings
        self.client = OpenAI(base_url=embedding_base_url, api_key=embedding_api_key)

    def get_embedding(self, text):
        """Get embedding for a text using the configured provider."""
        # Truncate text to avoid exceeding embedding model's token limit
        max_chars = 4000
        if len(text) > max_chars:
            text = text[:max_chars]
        
        if self.provider == "local":
            return self._get_local_embedding(text)
        else:
            return self._get_openai_embedding(text)

    def _get_local_embedding(self, text):
        """Get embedding using the local backend (sentence-transformers 或 ONNX)."""
        if getattr(self, "local_backend", "sentence-transformers") == "onnx":
            # ChromaDB embedding function 接受字串列表，回傳對應的向量列表
            result = self._onnx_ef([text])
            vec = result[0]
            return vec.tolist() if hasattr(vec, "tolist") else list(vec)
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def _get_openai_embedding(self, text):
        """Get embedding using OpenAI API."""
        response = self.client.embeddings.create(
            model=self.embedding_model, input=text
        )
        return response.data[0].embedding

    def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice. Parameter is a list of tuples (situation, rec)"""

        situations = []
        advice = []
        ids = []
        embeddings = []

        offset = self.situation_collection.count()

        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))
            embeddings.append(self.get_embedding(situation))

        self.situation_collection.add(
            documents=situations,
            metadatas=[{"recommendation": rec} for rec in advice],
            embeddings=embeddings,
            ids=ids,
        )

    def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using embeddings"""
        # Guard: return empty list if collection has no documents yet.
        # ChromaDB raises ValueError when querying an empty collection.
        collection_size = self.situation_collection.count()
        if collection_size == 0:
            return []

        # Clamp n_matches to avoid requesting more results than available documents.
        n_matches = min(n_matches, collection_size)

        query_embedding = self.get_embedding(current_situation)

        results = self.situation_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_matches,
            include=["metadatas", "documents", "distances"],
        )

        matched_results = []
        for i in range(len(results["documents"][0])): # type: ignore
            matched_results.append(
                {
                    "matched_situation": results["documents"][0][i], # type: ignore
                    "recommendation": results["metadatas"][0][i]["recommendation"], # type: ignore
                    "similarity_score": 1 - results["distances"][0][i], # type: ignore
                }
            )

        return matched_results


class HybridFinancialMemory(FinancialSituationMemory):
    """
    混合搜索金融記憶體 (Hybrid Financial Memory)

    在 FinancialSituationMemory 的向量搜索基礎上，
    加入 BM25 關鍵字搜索，並透過 RRF 融合兩種搜索結果。

    優點：
    - 向量搜索：理解語意，找到概念相似的過去情境
    - BM25 關鍵字搜索：精確匹配股票代號與財務術語
    - 股票代號自動加分：查詢包含代號時優先匹配相關記錄

    設定項 (config)：
        hybrid_search_k  : RRF 常數 k，預設 60
        vector_weight    : 向量搜索權重（0~1），預設 0.6
        keyword_weight   : BM25 權重（0~1），預設 0.4
        ticker_boost     : 股票代號精確匹配加分倍數，預設 2.0
    """

    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        self._situations: List[str] = []
        self._recommendations: List[str] = []
        self._tokenized_corpus: List[List[str]] = []
        self._bm25 = None

        self.rrf_k = config.get("hybrid_search_k", 60)
        self.vector_weight = config.get("vector_weight", 0.6)
        self.keyword_weight = config.get("keyword_weight", 0.4)
        self.ticker_boost = config.get("ticker_boost", 2.0)

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """分詞並保留股票代號與財務術語大小寫。"""
        from .hybrid_search import tokenize_financial_text
        return tokenize_financial_text(text)

    @staticmethod
    def _extract_tickers(text: str) -> List[str]:
        """提取股票代號。"""
        from .hybrid_search import extract_tickers
        return extract_tickers(text)

    def _rebuild_bm25(self):
        """重建 BM25Okapi 索引。"""
        if not self._tokenized_corpus:
            self._bm25 = None
            return
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            raise ImportError(
                "rank-bm25 為關鍵字搜索所必需。請執行：pip install rank-bm25"
            )
        self._bm25 = BM25Okapi(self._tokenized_corpus)

    # ------------------------------------------------------------------
    # 覆寫父類別方法
    # ------------------------------------------------------------------

    def add_situations(self, situations_and_advice):
        """
        新增金融情境與建議，同時建立 BM25 索引和向量索引。
        Parameter: list of (situation, recommendation) tuples
        """
        super().add_situations(situations_and_advice)
        for situation, recommendation in situations_and_advice:
            self._situations.append(situation)
            self._recommendations.append(recommendation)
            self._tokenized_corpus.append(self._tokenize(situation))
        self._rebuild_bm25()

    def get_memories(self, current_situation: str, n_matches: int = 1) -> List[Dict[str, Any]]:
        """
        混合搜索：BM25 + 向量搜索，透過 RRF 融合後回傳最相關的過去情境。

        Args:
            current_situation : 當前市場情境描述
            n_matches         : 回傳結果數量

        Returns:
            列表，每項包含：
                matched_situation - 匹配的歷史情境
                recommendation    - 對應建議
                similarity_score  - RRF 混合分數
                search_type       - "hybrid"
        """
        if not self._situations:
            return []

        n_matches = min(n_matches, len(self._situations))
        n_candidates = min(max(n_matches * 3, 10), len(self._situations))

        # --- 向量搜索 ---
        query_embedding = self.get_embedding(current_situation)
        vector_raw = self.situation_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_candidates,
            include=["distances"],
        )
        # id (字串) → (index, similarity)
        vector_ranking: List[tuple] = []
        for doc_id, dist in zip(
            vector_raw.get("ids", [[]])[0],
            vector_raw.get("distances", [[]])[0], # type: ignore
        ):
            try:
                vector_ranking.append((int(doc_id), 1.0 - dist))
            except (ValueError, TypeError):
                pass

        # --- BM25 關鍵字搜索 ---
        bm25_ranking: List[tuple] = []
        if self._bm25 is not None:
            query_tokens = self._tokenize(current_situation)
            scores = self._bm25.get_scores(query_tokens)

            # 股票代號精確匹配加分
            query_tickers = self._extract_tickers(current_situation)
            if query_tickers and self.ticker_boost > 1.0:
                for i, situation in enumerate(self._situations):
                    for ticker in query_tickers:
                        if re.search(r'\b' + re.escape(ticker) + r'\b', situation):
                            scores[i] *= self.ticker_boost

            indexed = [(i, float(scores[i])) for i in range(len(scores))]
            indexed.sort(key=lambda x: x[1], reverse=True)
            bm25_ranking = indexed[:n_candidates]

        # --- RRF 融合 ---
        rrf_scores: Dict[int, float] = {}
        for rank, (idx, _) in enumerate(bm25_ranking):
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (
                self.keyword_weight / (self.rrf_k + rank + 1)
            )
        for rank, (idx, _) in enumerate(vector_ranking):
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (
                self.vector_weight / (self.rrf_k + rank + 1)
            )

        top = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:n_matches]

        return [
            {
                "matched_situation": self._situations[idx],
                "recommendation": self._recommendations[idx],
                "similarity_score": score,
                "search_type": "hybrid",
            }
            for idx, score in top
            if idx < len(self._situations)
        ]


if __name__ == "__main__":
    # Example usage with local embedding (no API key required!)
    config = {
        "embedding_provider": "local",  # Use local model, no API key needed
        "embedding_model": "all-mpnet-base-v2",  # Higher-quality general-purpose embeddings
    }
    
    matcher = FinancialSituationMemory("test_memory", config)

    # Example data
    example_data = [
        (
            "High inflation rate with rising interest rates and declining consumer spending",
            "Consider defensive sectors like consumer staples and utilities. Review fixed-income portfolio duration.",
        ),
        (
            "Tech sector showing high volatility with increasing institutional selling pressure",
            "Reduce exposure to high-growth tech stocks. Look for value opportunities in established tech companies with strong cash flows.",
        ),
        (
            "Strong dollar affecting emerging markets with increasing forex volatility",
            "Hedge currency exposure in international positions. Consider reducing allocation to emerging market debt.",
        ),
        (
            "Market showing signs of sector rotation with rising yields",
            "Rebalance portfolio to maintain target allocations. Consider increasing exposure to sectors benefiting from higher rates.",
        ),
    ]

    # Add the example situations and recommendations
    print("Adding example situations...")
    matcher.add_situations(example_data)
    print("Done!")

    # Example query
    current_situation = """
    Market showing increased volatility in tech sector, with institutional investors 
    reducing positions and rising interest rates affecting growth stock valuations
    """

    try:
        print("\nSearching for recommendations...")
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            print(f"\nMatch {i}:")
            print(f"Similarity Score: {rec['similarity_score']:.2f}")
            print(f"Matched Situation: {rec['matched_situation']}")
            print(f"Recommendation: {rec['recommendation']}")

    except Exception as e:
        print(f"Error during recommendation: {str(e)}")
