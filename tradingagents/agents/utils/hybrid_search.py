"""
混合搜索引擎 (Hybrid Search Engine)

結合兩種互補的搜索策略：
- BM25 關鍵字搜索 (Keyword Search)：精確匹配股票代號與財務術語
- 向量搜索 (Vector Search)：ChromaDB + 嵌入模型，理解語意與概念
- 倒數排名融合 (Reciprocal Rank Fusion, RRF)：加權合併兩種搜索結果

專為金融文件設計，特別處理：
- 股票代號 (e.g., AAPL, TSLA, 2330, 2330.TW)
- 財務術語 (P/E、EPS、EBITDA、ROE 等)
- 語意金融概念 (看漲情緒、獲利成長、技術突破等)
"""

import os
import re
import logging
from typing import List, Dict, Tuple, Optional, Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 文字處理工具
# ---------------------------------------------------------------------------

# 常見財務術語縮寫，保留大寫
_FINANCIAL_ABBREVIATIONS = {
    "PE", "PB", "PS", "EPS", "ROE", "ROA", "ROCE", "EBITDA", "EBIT",
    "FCF", "DCF", "LBO", "IPO", "M&A", "YOY", "QOQ", "TTM", "NTM",
    "CAGR", "IRR", "NPV", "WACC", "NAV", "AUM", "ETF", "REITs",
    "GDP", "CPI", "PPI", "PMI", "FOMC", "FED", "ECB", "BOJ",
    "USD", "EUR", "JPY", "CNY", "TWD", "HKD",
}

# 股票代號正則：1-5 大寫字母（可選 .XX 後綴），或 4-6 位數字代號（台股）
_TICKER_PATTERN = re.compile(
    r'\b([A-Z]{1,5}(?:\.[A-Z]{1,2})?|\d{4,6}(?:\.[A-Z]{1,2})?)\b'
)


def tokenize_financial_text(text: str) -> List[str]:
    """
    將財務文字分詞，保留股票代號和財務術語的原始大小寫。
    其他詞彙統一轉為小寫以提升 BM25 召回率。
    """
    tokens = []
    for word in re.findall(r'\b[\w.]+\b', text):
        # 股票代號模式（全大寫 + 數字代號）
        if re.match(r'^[A-Z]{1,5}(?:\.[A-Z]{1,2})?$', word):
            tokens.append(word)
        # 財務術語縮寫
        elif word.upper() in _FINANCIAL_ABBREVIATIONS:
            tokens.append(word.upper())
        # 數字型股票代號（台股，如 2330）
        elif re.match(r'^\d{4,6}(?:\.[A-Z]{1,2})?$', word):
            tokens.append(word)
        else:
            tokens.append(word.lower())
    return tokens


def extract_tickers(text: str) -> List[str]:
    """從查詢或文件中提取潛在的股票代號。"""
    return _TICKER_PATTERN.findall(text)


# ---------------------------------------------------------------------------
# 主要類別
# ---------------------------------------------------------------------------

class HybridSearchEngine:
    """
    混合搜索引擎：結合 BM25 關鍵字搜索與向量語意搜索。

    工作流程：
    1. add_documents() — 同時建立 BM25 倒排索引和 ChromaDB 向量索引
    2. search() — 分別執行兩種搜索，透過 RRF 融合排名後回傳結果
    3. 股票代號精確匹配時獲得額外加分 (ticker_boost)

    設定項 (config)：
        embedding_provider   : "local"（預設）或 "openai"
        embedding_model      : 嵌入模型名稱
        hybrid_search_k      : RRF 常數 k，預設 60
        vector_weight        : 向量搜索權重（0~1），預設 0.5
        keyword_weight       : BM25 權重（0~1），預設 0.5
        ticker_boost         : 股票代號精確匹配加分倍數，預設 2.0
    """

    # 跨實例共用嵌入模型快取，避免重複載入佔用記憶體
    _model_cache: Dict[str, Any] = {}

    def __init__(self, collection_name: str, config: dict):
        self.collection_name = collection_name
        self.config = config
        self.rrf_k = config.get("hybrid_search_k", 60)
        self.vector_weight = config.get("vector_weight", 0.5)
        self.keyword_weight = config.get("keyword_weight", 0.5)
        self.ticker_boost = config.get("ticker_boost", 2.0)

        # 內部文件儲存
        self._documents: List[str] = []
        self._metadatas: List[Dict] = []
        self._ids: List[str] = []
        self._tokenized_corpus: List[List[str]] = []
        self._bm25 = None

        self._init_vector_store()
        self._init_embeddings(config)

    # ------------------------------------------------------------------
    # 初始化
    # ------------------------------------------------------------------

    def _init_vector_store(self):
        """初始化 ChromaDB 向量資料庫。"""
        import chromadb
        from chromadb.config import Settings

        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name
        )

    def _init_embeddings(self, config: dict):
        """初始化嵌入模型（優先使用快取）。"""
        provider = config.get("embedding_provider", "local").lower()
        self.provider = provider

        if provider == "local":
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                raise ImportError(
                    "sentence-transformers 為本地嵌入所必需。"
                    "請執行：pip install sentence-transformers"
                )
            model_name = config.get("embedding_model", "all-MiniLM-L6-v2")
            if model_name not in HybridSearchEngine._model_cache:
                logger.info(f"載入嵌入模型：{model_name}")
                HybridSearchEngine._model_cache[model_name] = SentenceTransformer(model_name)
            self.model = HybridSearchEngine._model_cache[model_name]

        elif provider == "openai":
            from openai import OpenAI

            self.embedding_model = config.get("embedding_model", "text-embedding-3-small")
            api_key = (
                config.get("embedding_api_key")
                or os.getenv("OPENAI_API_KEY")
                or config.get("quick_think_api_key")
                or config.get("deep_think_api_key")
            )
            if not api_key:
                raise ValueError("OpenAI 嵌入需要提供 API 金鑰。")
            base_url = config.get("embedding_base_url", "https://api.openai.com/v1")
            self.openai_client = OpenAI(base_url=base_url, api_key=api_key)

        else:
            raise ValueError(f"不支援的嵌入提供者：{provider}。請使用 'local' 或 'openai'。")

    # ------------------------------------------------------------------
    # 嵌入
    # ------------------------------------------------------------------

    def _get_embedding(self, text: str) -> List[float]:
        """取得文字的嵌入向量（自動截斷至 4000 字元）。"""
        text = text[:4000]
        if self.provider == "local":
            return self.model.encode(text, normalize_embeddings=True).tolist()
        else:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model, input=text
            )
            return response.data[0].embedding

    # ------------------------------------------------------------------
    # BM25 索引管理
    # ------------------------------------------------------------------

    def _rebuild_bm25(self):
        """從目前語料庫重建 BM25Okapi 索引。"""
        if not self._tokenized_corpus:
            self._bm25 = None
            return
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            raise ImportError(
                "rank-bm25 為關鍵字搜索所必需。"
                "請執行：pip install rank-bm25"
            )
        self._bm25 = BM25Okapi(self._tokenized_corpus)

    # ------------------------------------------------------------------
    # 文件管理
    # ------------------------------------------------------------------

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
    ):
        """
        將文件加入混合搜索索引。

        Args:
            documents : 文件字串列表
            metadatas : 每份文件的中繼資料（可選）
            ids       : 文件識別碼（可選，預設為流水號）
        """
        if not documents:
            return

        offset = len(self._documents)
        if ids is None:
            ids = [str(offset + i) for i in range(len(documents))]
        if metadatas is None:
            metadatas = [{} for _ in documents]

        # 更新 BM25 語料庫
        new_tokenized = [tokenize_financial_text(doc) for doc in documents]
        self._tokenized_corpus.extend(new_tokenized)
        self._documents.extend(documents)
        self._metadatas.extend(metadatas)
        self._ids.extend(ids)
        self._rebuild_bm25()

        # 更新向量索引
        embeddings = [self._get_embedding(doc) for doc in documents]
        self.collection.add(
            documents=documents,
            metadatas=metadatas, # type: ignore
            embeddings=embeddings, # type: ignore
            ids=ids,
        )
        logger.debug(
            f"已新增 {len(documents)} 份文件至混合索引 '{self.collection_name}'（"
            f"共 {len(self._documents)} 份）"
        )

    # ------------------------------------------------------------------
    # 搜索
    # ------------------------------------------------------------------

    def _bm25_search(self, query: str, n: int) -> List[Tuple[int, float]]:
        """
        BM25 關鍵字搜索，含股票代號精確匹配加分。
        回傳 [(文件索引, 分數), ...] 依分數降序排列。
        """
        if self._bm25 is None or not self._documents:
            return []

        query_tokens = tokenize_financial_text(query)
        scores = self._bm25.get_scores(query_tokens)

        # 股票代號加分：查詢中出現代號且文件精確匹配時提升分數
        query_tickers = extract_tickers(query)
        if query_tickers and self.ticker_boost > 1.0:
            for i, doc in enumerate(self._documents):
                for ticker in query_tickers:
                    if re.search(r'\b' + re.escape(ticker) + r'\b', doc):
                        scores[i] *= self.ticker_boost

        indexed = [(i, float(scores[i])) for i in range(len(scores))]
        indexed.sort(key=lambda x: x[1], reverse=True)
        return indexed[:n]

    def _vector_search(self, query: str, n: int) -> List[Tuple[str, float]]:
        """
        向量語意搜索（ChromaDB）。
        回傳 [(文件ID, 相似度分數), ...] 依分數降序排列。
        """
        total = self.collection.count()
        if total == 0:
            return []

        n = min(n, total)
        query_embedding = self._get_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n,
            include=["distances"],
        )

        # ChromaDB 回傳餘弦距離，轉換為相似度
        return [
            (results["ids"][0][i], 1.0 - results["distances"][0][i]) # type: ignore
            for i in range(len(results["ids"][0]))
        ]

    def _reciprocal_rank_fusion(
        self,
        bm25_results: List[Tuple[int, float]],
        vector_results: List[Tuple[str, float]],
    ) -> List[Tuple[int, float]]:
        """
        倒數排名融合 (RRF)：合併 BM25 與向量搜索的排名。

        RRF 分數 = Σ weight_i / (k + rank_i)
        """
        rrf_scores: Dict[int, float] = {}

        # BM25 貢獻
        for rank, (doc_idx, _) in enumerate(bm25_results):
            rrf_scores[doc_idx] = rrf_scores.get(doc_idx, 0.0) + (
                self.keyword_weight / (self.rrf_k + rank + 1)
            )

        # 向量搜索貢獻（doc_id → doc_index 轉換）
        id_to_idx = {doc_id: i for i, doc_id in enumerate(self._ids)}
        for rank, (doc_id, _) in enumerate(vector_results):
            if doc_id in id_to_idx:
                doc_idx = id_to_idx[doc_id]
                rrf_scores[doc_idx] = rrf_scores.get(doc_idx, 0.0) + (
                    self.vector_weight / (self.rrf_k + rank + 1)
                )

        return sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        混合搜索：BM25 關鍵字 + 向量語意，透過 RRF 融合排名。

        Args:
            query     : 查詢字串（可包含股票代號、財務術語或語意概念）
            n_results : 回傳結果數量

        Returns:
            結果列表，每項包含：
                document     - 文件內容
                metadata     - 中繼資料
                id           - 文件識別碼
                bm25_score   - BM25 原始分數
                vector_score - 向量相似度分數
                hybrid_score - RRF 混合分數
        """
        if not self._documents:
            return []

        # 候選數量：至少取 n_results*3 份，最多取全部
        n_candidates = min(max(n_results * 3, 20), len(self._documents))

        bm25_results = self._bm25_search(query, n_candidates)
        vector_results = self._vector_search(query, n_candidates)

        # 建立分數查找表
        bm25_score_map = {idx: score for idx, score in bm25_results}
        id_to_idx = {doc_id: i for i, doc_id in enumerate(self._ids)}
        vector_score_map = {
            id_to_idx[doc_id]: score
            for doc_id, score in vector_results
            if doc_id in id_to_idx
        }

        fused = self._reciprocal_rank_fusion(bm25_results, vector_results)

        results = []
        for doc_idx, hybrid_score in fused[:n_results]:
            if doc_idx < len(self._documents):
                results.append({
                    "document": self._documents[doc_idx],
                    "metadata": self._metadatas[doc_idx],
                    "id": self._ids[doc_idx],
                    "bm25_score": bm25_score_map.get(doc_idx, 0.0),
                    "vector_score": vector_score_map.get(doc_idx, 0.0),
                    "hybrid_score": hybrid_score,
                })

        return results

    def search_formatted(self, query: str, n_results: int = 5) -> str:
        """
        搜索並回傳格式化字串，供 LLM Agent 直接使用。
        每條結果顯示 BM25 分數、向量分數、混合分數及文件摘要。
        """
        results = self.search(query, n_results)
        if not results:
            return f"未找到與查詢相關的文件：{query}"

        lines = [f"## 混合搜索結果：{query}\n"]
        for i, r in enumerate(results, 1):
            meta_parts = [f"{k}: {v}" for k, v in r["metadata"].items() if v]
            meta_str = f" [{', '.join(meta_parts)}]" if meta_parts else ""
            snippet = r["document"][:500] + ("..." if len(r["document"]) > 500 else "")
            lines.append(
                f"**結果 {i}**{meta_str}  "
                f"(BM25: {r['bm25_score']:.3f} | 向量: {r['vector_score']:.3f} | "
                f"混合: {r['hybrid_score']:.4f})\n{snippet}\n"
            )

        return "\n".join(lines)

    @property
    def count(self) -> int:
        """目前索引中的文件數量。"""
        return len(self._documents)
