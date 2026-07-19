# -*- coding: utf-8 -*-
"""
TUI 設定畫面所需的所有選項常數與輔助函式。
內容從原本的 cli/utils.py 與 cli/main.py 移植而來。
"""
import os

from tui.models import AnalystType


# ---------------------------------------------------------------------------
# 市場
# ---------------------------------------------------------------------------
# (顯示名稱, 市場代碼)
MARKET_OPTIONS = [
    ("🇺🇸 美股 (US Stocks)", "us"),
    ("🇹🇼 台股 (Taiwan Stocks)", "tw"),
]

# 各市場的預設股票代碼
DEFAULT_TICKERS = {"us": "SPY", "tw": "2330"}


# ---------------------------------------------------------------------------
# 分析師團隊
# ---------------------------------------------------------------------------
# (顯示名稱, AnalystType)
ANALYST_ORDER = [
    ("市場分析師", AnalystType.MARKET),
    ("社群媒體分析師", AnalystType.SOCIAL),
    ("新聞分析師", AnalystType.NEWS),
    ("基本面分析師", AnalystType.FUNDAMENTALS),
]


# ---------------------------------------------------------------------------
# 研究深度
# ---------------------------------------------------------------------------
# (顯示名稱, 深度值)
DEPTH_OPTIONS = [
    ("淺層 - 快速研究，較少的辯論和策略討論", 1),
    ("中等 - 中等程度，適度的辯論和策略討論", 3),
    ("深層 - 全面研究，深入的辯論和策略討論", 5),
]


# ---------------------------------------------------------------------------
# LLM 供應商與 Base URL
# ---------------------------------------------------------------------------
# (顯示名稱, Base URL)
LLM_PROVIDERS = [
    ("OpenAI", "https://api.openai.com/v1"),
    ("Anthropic", "https://api.anthropic.com/v1"),
    ("Google", "https://generativelanguage.googleapis.com/v1beta/openai"),
    ("Grok", "https://api.x.ai/v1"),
    ("DeepSeek", "https://api.deepseek.com/v1"),
    ("Qwen", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
]


# ---------------------------------------------------------------------------
# 各供應商可用的思維模型（快速 / 深度共用同一份清單）
# ---------------------------------------------------------------------------
# {供應商: [(顯示名稱, 模型 ID), ...]}
MODEL_OPTIONS = {
    "OpenAI": [
        ("GPT-5.6 Sol", "gpt-5.6-sol"),
        ("GPT-5.6 Sol-mini", "gpt-5.6-terra"),
        ("GPT-5.6 Sol-nano", "gpt-5.6-luna"),
    ],
    "Anthropic": [
        ("Claude Fable 5", "claude-fable-5"),
        ("Claude Opus 4.8", "claude-opus-4-8"),
        ("Claude Sonnet 5", "claude-sonnet-5"),
        ("Claude Haiku 4.5", "claude-haiku-4-5-20251001"),
    ],
    "Google": [
        ("Gemini 3.5 Flash", "gemini-3.5-flash"),
        ("Gemini 3.1 Flash-Lite", "gemini-3.1-flash-lite"),
    ],
    "Grok": [
        ("Grok 4.5", "grok-4.5"),
        ("Grok 4.3","grok-4.3"),
        ("Grok 4.20", "grok-4.20-0309-reasoning"),
        ("Grok 4.20 (Non-Reasoning)", "grok-4.20-0309-non-reasoning"),
    ],
    "DeepSeek": [
        ("Deepseek V4 Pro", "deepseek-v4-pro"),
        ("Deepseek V4 Flash", "deepseek-v4-flash"),
    ],
    "Qwen": [
        ("Qwen3.7-Max", "qwen3.7-max"),
        ("Qwen3.7-Plus", "qwen3.7-plus"),
        ("Qwen3.5-Flash", "qwen3.5-flash"),
    ],
}


# ---------------------------------------------------------------------------
# 嵌入模型供應商與模型
# ---------------------------------------------------------------------------
# (顯示名稱, Base URL；本地模型為 "local")
EMBEDDING_PROVIDERS = [
    ("🖥️  本地模型 (HuggingFace) - 免費", "local"),
    ("☁️  OpenAI - 收費", "https://api.openai.com/v1"),
]

LOCAL_EMBEDDING_MODELS = [
    ("all-MiniLM-L6-v2 (推薦) - 90MB, 輕量快速", "all-MiniLM-L6-v2"),
    ("all-mpnet-base-v2 - 420MB, 更高質量", "all-mpnet-base-v2"),
]

OPENAI_EMBEDDING_MODELS = [
    ("text-embedding-3-small (推薦) - 高性價比", "text-embedding-3-small"),
    ("text-embedding-3-large - 最高質量", "text-embedding-3-large"),
]


def embedding_models_for(embedding_url: str):
    """根據嵌入供應商的 URL 回傳對應的模型清單。"""
    if embedding_url == "local":
        return LOCAL_EMBEDDING_MODELS
    return OPENAI_EMBEDDING_MODELS


# ---------------------------------------------------------------------------
# API Key 推斷
# ---------------------------------------------------------------------------
# 供應商 → 環境變數名稱
PROVIDER_API_KEY_MAP = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GEMINI_API_KEY",
    "grok": "XAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "qwen": "DASHSCOPE_API_KEY",
}


def infer_provider_from_model(model_name: str) -> str:
    """根據模型名稱推斷供應商。"""
    model_lower = model_name.lower()
    if "gpt" in model_lower or model_lower.startswith("o4"):
        return "openai"
    elif "claude" in model_lower:
        return "anthropic"
    elif "gemini" in model_lower:
        return "google"
    elif "grok" in model_lower:
        return "grok"
    elif "deepseek" in model_lower:
        return "deepseek"
    elif "qwen" in model_lower:
        return "qwen"
    return "openai"  # 預設


def env_api_key_for_provider(provider_name: str) -> str | None:
    """根據供應商名稱從環境變數讀取對應的 API Key（找不到回傳 None）。"""
    env_var_name = PROVIDER_API_KEY_MAP.get(provider_name.lower(), "OPENAI_API_KEY")
    return os.getenv(env_var_name)


def env_api_key_for_model(model_name: str) -> str | None:
    """根據模型名稱推斷供應商並讀取對應的環境變數 API Key。"""
    return env_api_key_for_provider(infer_provider_from_model(model_name))
