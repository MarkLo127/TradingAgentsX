import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
)


def is_rate_limited(response):
    """檢查回應是否表示速率限制 (狀態碼 429)"""
    return response.status_code == 429


@retry(
    retry=(retry_if_result(is_rate_limited)),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
)
def make_request(url, headers):
    """使用重試邏輯發出請求以處理速率限制"""
    # 在每個請求前隨機延遲以避免被偵測
    time.sleep(random.uniform(2, 6))
    response = requests.get(url, headers=headers)
    return response


def getNewsData(query, start_date, end_date):
    """
    抓取給定查詢和日期範圍的 Google 新聞搜索結果。
    query: str - 搜索查詢
    start_date: str - 開始日期，格式為 yyyy-mm-dd 或 mm/dd/yyyy
    end_date: str - 結束日期，格式為 yyyy-mm-dd 或 mm/dd/yyyy
    """
    if "-" in start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = start_date.strftime("%m/%d/%Y")
    if "-" in end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date = end_date.strftime("%m/%d/%Y")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/101.0.4951.54 Safari/537.36"
        )
    }

    news_results = []
    page = 0
    while True:
        offset = page * 10
        url = (
            f"https://www.google.com/search?q={query}"
            f"&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}"
            f"&tbm=nws&start={offset}"
        )

        try:
            response = make_request(url, headers)
            soup = BeautifulSoup(response.content, "html.parser")
            results_on_page = soup.select("div.SoaBEf")

            if not results_on_page:
                break  # 找不到更多結果

            for el in results_on_page:
                try:
                    link = el.find("a")["href"] # type: ignore
                    title = el.select_one("div.MBeuO").get_text() # type: ignore
                    snippet = el.select_one(".GI74Re").get_text() # type: ignore
                    date = el.select_one(".LfVVr").get_text() # type: ignore
                    source = el.select_one(".NUnG9d span").get_text() # type: ignore
                    news_results.append(
                        {
                            "link": link,
                            "title": title,
                            "snippet": snippet,
                            "date": date,
                            "source": source,
                        }
                    )
                except Exception as e:
                    print(f"處理結果時出錯：{e}")
                    # 如果找不到其中一個欄位，則跳過此結果
                    continue

            # 使用當前抓取的結果數量更新進度條

            # 檢查「下一頁」連結 (分頁)
            next_link = soup.find("a", id="pnnext")
            if not next_link:
                break

            page += 1

        except Exception as e:
            print(f"多次重試後失敗：{e}")
            break

    return news_results