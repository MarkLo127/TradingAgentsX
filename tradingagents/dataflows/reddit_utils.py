import requests
import time
import json
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Annotated
import os
import re

ticker_to_company = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google",
    "AMZN": "Amazon",
    "TSLA": "Tesla",
    "NVDA": "Nvidia",
    "TSM": "Taiwan Semiconductor Manufacturing Company OR TSMC",
    "JPM": "JPMorgan Chase OR JP Morgan",
    "JNJ": "Johnson & Johnson OR JNJ",
    "V": "Visa",
    "WMT": "Walmart",
    "META": "Meta OR Facebook",
    "AMD": "AMD",
    "INTC": "Intel",
    "QCOM": "Qualcomm",
    "BABA": "Alibaba",
    "ADBE": "Adobe",
    "NFLX": "Netflix",
    "CRM": "Salesforce",
    "PYPL": "PayPal",
    "PLTR": "Palantir",
    "MU": "Micron",
    "SQ": "Block OR Square",
    "ZM": "Zoom",
    "CSCO": "Cisco",
    "SHOP": "Shopify",
    "ORCL": "Oracle",
    "X": "Twitter OR X",
    "SPOT": "Spotify",
    "AVGO": "Broadcom",
    "ASML": "ASML ",
    "TWLO": "Twilio",
    "SNAP": "Snap Inc.",
    "TEAM": "Atlassian",
    "SQSP": "Squarespace",
    "UBER": "Uber",
    "ROKU": "Roku",
    "PINS": "Pinterest",
}


def fetch_top_from_category(
    category: Annotated[
        str, "要從中獲取熱門貼文的類別。子版塊的集合。"
    ],
    date: Annotated[str, "要從中獲取熱門貼文的日期。"],
    max_limit: Annotated[int, "要獲取的最大貼文數。"],
    query: Annotated[str, "在子版塊中搜索的可選查詢。"] = None, # type: ignore
    data_path: Annotated[
        str,
        "數據資料夾的路徑。預設為 'reddit_data'。",
    ] = "reddit_data",
):
    """
    從指定類別中獲取熱門貼文。

    Args:
        category (str): 要從中獲取熱門貼文的類別。子版塊的集合。
        date (str): 要從中獲取熱門貼文的日期。
        max_limit (int): 要獲取的最大貼文數。
        query (str, optional): 在子版塊中搜索的可選查詢。預設為 None。
        data_path (str, optional): 數據資料夾的路徑。預設為 'reddit_data'。

    Returns:
        list: 包含熱門貼文的列表。
    """
    base_path = data_path

    all_content = []

    if max_limit < len(os.listdir(os.path.join(base_path, category))):
        raise ValueError(
            "REDDIT 抓取錯誤：最大限制小於類別中的檔案數。將無法獲取任何貼文"
        )

    limit_per_subreddit = max_limit // len(
        os.listdir(os.path.join(base_path, category))
    )

    for data_file in os.listdir(os.path.join(base_path, category)):
        # 檢查 data_file 是否為 .jsonl 檔案
        if not data_file.endswith(".jsonl"):
            continue

        all_content_curr_subreddit = []

        with open(os.path.join(base_path, category, data_file), "rb") as f:
            for i, line in enumerate(f):
                # 跳過空行
                if not line.strip():
                    continue

                parsed_line = json.loads(line)

                # 只選擇來自該日期的行
                post_date = datetime.utcfromtimestamp(
                    parsed_line["created_utc"]
                ).strftime("%Y-%m-%d")
                if post_date != date:
                    continue

                # 如果是 company_news，檢查標題或內容是否提及公司名稱 (查詢)
                if "company" in category and query:
                    search_terms = []
                    if "OR" in ticker_to_company[query]:
                        search_terms = ticker_to_company[query].split(" OR ")
                    else:
                        search_terms = [ticker_to_company[query]]

                    search_terms.append(query)

                    found = False
                    for term in search_terms:
                        if re.search(
                            term, parsed_line["title"], re.IGNORECASE
                        ) or re.search(term, parsed_line["selftext"], re.IGNORECASE):
                            found = True
                            break

                    if not found:
                        continue

                post = {
                    "title": parsed_line["title"],
                    "content": parsed_line["selftext"],
                    "url": parsed_line["url"],
                    "upvotes": parsed_line["ups"],
                    "posted_date": post_date,
                }

                all_content_curr_subreddit.append(post)

        # 按讚數降序排序 all_content_curr_subreddit
        all_content_curr_subreddit.sort(key=lambda x: x["upvotes"], reverse=True)

        all_content.extend(all_content_curr_subreddit[:limit_per_subreddit])

    return all_content