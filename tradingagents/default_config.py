import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results")),
    "data_dir": os.path.join(os.path.expanduser("~"), "Documents/Code/ScAI/FR1-data"),
    "data_cache_dir": os.getenv("TRADINGAGENTS_DATA_CACHE_DIR", os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    )),
    # LLM 設定
    "llm_provider": "anthropic",
    "deep_think_llm": "claude-sonnet-5",
    "quick_think_llm": "claude-haiku-4-5-20251001",
    "backend_url": "https://api.anthropic.com/v1",
    # 辯論與討論設定
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 200,
    # 資料供應商設定
    # 類別層級設定 (該類別所有工具的預設值)
    # 可用供應商:
    #   - yfinance: Yahoo Finance (美股為主)
    #   - alpha_vantage: Alpha Vantage API (美股為主)
    #   - finmind: FinMind API (台股專用)
    #   - openai: OpenAI 網路搜尋
    #   - google: Google News
    #   - local: 本地資料
    "data_vendors": {
        "core_stock_apis": "yfinance",       # 選項: yfinance, alpha_vantage, finmind, local
        "technical_indicators": "yfinance",  # 選項: yfinance, alpha_vantage, finmind, local
        "fundamental_data": "alpha_vantage", # 選項: openai, alpha_vantage, yfinance, finmind
        "news_data": "alpha_vantage",        # 選項: openai, alpha_vantage, google, finmind, local
    },
    # 工具層級設定 (優先於類別層級設定)
    "tool_vendors": {
        # 範例: "get_stock_data": "alpha_vantage",  # 覆寫類別預設值
        # 範例: "get_news": "openai",               # 覆寫類別預設值
        # 範例: "get_stock_data": "finmind",        # 使用 FinMind 獲取台股資料
        "get_global_news": "openai",  # get_global_news 不支持 alpha_vantage，使用 openai 作為主要供應商
    },
    # 混合搜索設定 (Hybrid Search)
    # 結合向量搜索（語意理解）與 BM25 關鍵字搜索（精確匹配股票代號/財務術語）
    "hybrid_search": {
        # 嵌入提供者：
        #   "local"  — 使用本地 sentence-transformers（不需 API 金鑰，預設）
        #   "openai" — 使用 OpenAI text-embedding 模型（需 API 金鑰）
        "embedding_provider": "local",
        "embedding_model": "all-mpnet-base-v2",
        # RRF 常數 k（越大越平滑，預設 60）
        "hybrid_search_k": 60,
        # 向量搜索與 BM25 的融合權重（總和建議為 1.0）
        "vector_weight": 0.6,   # 語意理解比重較高
        "keyword_weight": 0.4,  # 精確關鍵字比重
        # 股票代號精確匹配加分倍數（設為 1.0 可停用）
        "ticker_boost": 2.0,
    },
}