import os
from openai import OpenAI
from .config import get_config


def get_stock_news_openai(query, start_date, end_date):
    """
    使用 OpenAI 模型搜索社交媒體上的股票新聞。

    Args:
        query (str): 搜索查詢。
        start_date (str): 開始日期。
        end_date (str): 結束日期。

    Returns:
        str: 模型的文字回應。
    """
    config = get_config()
    # Get the OpenAI API key from environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(base_url=config["backend_url"], api_key=openai_api_key)

    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"您能從 {start_date} 到 {end_date} 在社交媒體上搜索關於 {query} 的資訊嗎？請確保您只獲取在該期間內發布的數據。",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=0.5,  # Reduced to 0.5 for maximum accuracy and consistency
        max_output_tokens=8192,  # Increased from 4096 to prevent truncation
        top_p=1,
        store=True,
    )

    return response.output[1].content[0].text # type: ignore


def get_global_news_openai(curr_date, look_back_days=7, limit=5):
    """
    使用 OpenAI 模型搜索全球宏觀經濟新聞。

    Args:
        curr_date (str): 當前日期。
        look_back_days (int): 回溯天數。
        limit (int): 結果數量限制。

    Returns:
        str: 模型的文字回應。
    """
    config = get_config()
    # Get the OpenAI API key from environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(base_url=config["backend_url"], api_key=openai_api_key)

    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"您能從 {curr_date} 前回溯 {look_back_days} 天到 {curr_date} 期間，搜索對交易有參考價值的全球或宏觀經濟新聞嗎？請確保您只獲取在該期間內發布的數據。將結果限制在 {limit} 篇文章。",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=0.5,  # Reduced to 0.5 for maximum accuracy and consistency
        max_output_tokens=8192,  # Increased from 4096 to prevent truncation
        top_p=1,
        store=True,
    )

    return response.output[1].content[0].text # type: ignore


def get_fundamentals_openai(ticker, curr_date):
    """
    使用 OpenAI 模型搜索公司的基本面數據。

    Args:
        ticker (str): 股票代碼。
        curr_date (str): 當前日期。

    Returns:
        str: 模型的文字回應。
    """
    config = get_config()
    # Get the OpenAI API key from environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(base_url=config["backend_url"], api_key=openai_api_key)

    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"您能搜索關於 {ticker} 在 {curr_date} 前一個月到 {curr_date} 當月的討論中的基本面數據嗎？請確保您只獲取在該期間內發布的數據。以表格形式列出，包含本益比/市銷率/現金流等資訊。",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=0.5,  # Reduced to 0.5 for maximum accuracy and consistency
        max_output_tokens=8192,  # Increased from 4096 to prevent truncation
        top_p=1,
        store=True,
    )

    return response.output[1].content[0].text # type: ignore
