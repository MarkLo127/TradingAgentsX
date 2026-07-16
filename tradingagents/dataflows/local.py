from typing import Annotated
import polars as pl
import os
from .config import DATA_DIR
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
from .reddit_utils import fetch_top_from_category
from tqdm import tqdm

def get_YFin_data_window(
    symbol: Annotated[str, "公司的股票代碼"],
    curr_date: Annotated[str, "開始日期，格式為 yyyy-mm-dd"],
    look_back_days: Annotated[int, "回溯天數"],
) -> str:
    """
    獲取給定股票代碼在特定時間窗口內的 Yahoo Finance 數據。

    Args:
        symbol (str): 公司的股票代碼。
        curr_date (str): 當前日期，格式為 yyyy-mm-dd。
        look_back_days (int): 回溯天數。

    Returns:
        str: 包含原始市場數據的格式化字串。
    """
    # 計算過去的日期
    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    start_date = before.strftime("%Y-%m-%d")

    # 讀取數據
    data = pl.read_csv(
        os.path.join(
            DATA_DIR, # type: ignore
            f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
        ) # type: ignore
    )

    # 節取日期部分
    data = data.with_columns(
        pl.col("Date").str.slice(0, 10).alias("DateOnly")
    )

    # 過濾指定日期範圍內的數據 (包含起訖日期)
    filtered_data = data.filter(
        (pl.col("DateOnly") >= start_date) & (pl.col("DateOnly") <= curr_date)
    )

    # 刪除我們創建的臨時欄位
    filtered_data = filtered_data.drop("DateOnly")

    # polars 的字串輸出
    df_string = str(filtered_data)

    return (
        f"## {symbol} 從 {start_date} 到 {curr_date} 的原始市場數據：\n\n"
        + df_string
    )

def get_YFin_data(
    symbol: Annotated[str, "公司的股票代碼"],
    start_date: Annotated[str, "開始日期，格式為 yyyy-mm-dd"],
    end_date: Annotated[str, "結束日期，格式為 yyyy-mm-dd"],
) -> str:
    """
    獲取給定股票代碼在特定日期範圍內的 Yahoo Finance 數據。

    Args:
        symbol (str): 公司的股票代碼。
        start_date (str): 開始日期，格式為 yyyy-mm-dd。
        end_date (str): 結束日期，格式為 yyyy-mm-dd。

    Returns:
        pd.DataFrame: 包含過濾後數據的 DataFrame。
    """
    # 讀取數據
    data = pl.read_csv(
        os.path.join(
            DATA_DIR, # type: ignore
            f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
        ) # type: ignore
    )

    if end_date > "2025-03-25":
        raise Exception(
            f"Get_YFin_Data：{end_date} 超出 2015-01-01 到 2025-03-25 的數據範圍"
        )

    # 節取日期部分
    data = data.with_columns(
        pl.col("Date").str.slice(0, 10).alias("DateOnly")
    )

    # 過濾指定日期範圏內的數據 (包含起訖日期)
    filtered_data = data.filter(
        (pl.col("DateOnly") >= start_date) & (pl.col("DateOnly") <= end_date)
    )

    # 刪除我們創建的臨時欄位
    filtered_data = filtered_data.drop("DateOnly")

    # 重置索引 (在 polars 中不需要，但保持一致性)
    # filtered_data = filtered_data.with_row_count(name="index", offset=0)

    return filtered_data # type: ignore

def get_finnhub_news(
    query: Annotated[str, "搜索查詢或股票代碼"],
    start_date: Annotated[str, "開始日期，格式為 yyyy-mm-dd"],
    end_date: Annotated[str, "結束日期，格式為 yyyy-mm-dd"],
):
    """
    在一個時間範圍內檢索關於一家公司的新聞。

    Args:
        query (str): 搜索查詢或股票代碼。
        start_date (str): 開始日期，格式為 yyyy-mm-dd。
        end_date (str): 結束日期，格式為 yyyy-mm-dd。
    Returns:
        str: 包含該公司在該時間範圍內新聞的數據框。

    """

    result = get_data_in_range(query, start_date, end_date, "news_data", DATA_DIR)

    if len(result) == 0:
        return ""

    combined_result = ""
    total_articles = 0
    max_articles = 15  # 限制總文章數量
    
    for day, data in result.items():
        if len(data) == 0:
            continue
        for entry in data:
            if total_articles >= max_articles:
                break
                
            headline = entry.get("headline", "")
            summary = entry.get("summary", "")
            
            # 限制摘要長度
            if summary and len(summary) > 300:
                summary = summary[:300] + "..."
            
            current_news = (
                "### " + headline + f" ({day})" + "\n" + summary
            )
            combined_result += current_news + "\n\n"
            total_articles += 1
        
        if total_articles >= max_articles:
            break

    return f"## {query} 新聞，從 {start_date} 到 {end_date}：\n" + str(combined_result)


def get_finnhub_company_insider_sentiment(
    ticker: Annotated[str, "公司的股票代碼"],
    curr_date: Annotated[str, "您正在交易的當前日期，格式為 yyyy-mm-dd"],
):
    """
    檢索過去 15 天內關於一家公司的內部人士情緒 (從公開的 SEC 資訊中檢索)。
    Args:
        ticker (str): 公司的股票代碼。
        curr_date (str): 您正在交易的當前日期，格式為 yyyy-mm-dd。
    Returns:
        str: 從 curr_date 開始的過去 15 天內的情緒報告。
    """

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=15)  # 預設回溯 15 天
    before = before.strftime("%Y-%m-%d")

    data = get_data_in_range(ticker, before, curr_date, "insider_senti", DATA_DIR)

    if len(data) == 0:
        return ""

    result_str = ""
    seen_dicts = []
    for date, senti_list in data.items():
        for entry in senti_list:
            if entry not in seen_dicts:
                result_str += f"### {entry['year']}-{entry['month']}:\n變動: {entry['change']}\n月度購股比例: {entry['mspr']}\n\n"
                seen_dicts.append(entry)

    return (
        f"## {ticker} 從 {before} 到 {curr_date} 的內部人士情緒數據：\n"
        + result_str
        + "change 欄位指的是所有內部人士交易的淨買入/賣出。mspr 欄位指的是月度購股比例。"
    )


def get_finnhub_company_insider_transactions(
    ticker: Annotated[str, "股票代碼"],
    curr_date: Annotated[str, "您正在交易的當前日期，格式為 yyyy-mm-dd"],
):
    """
    檢索過去 15 天內關於一家公司的內部人士交易資訊 (從公開的 SEC 資訊中檢索)。
    Args:
        ticker (str): 公司的股票代碼。
        curr_date (str): 您正在交易的當前日期，格式為 yyyy-mm-dd。
    Returns:
        str: 過去 15 天內公司內部人士交易/買賣資訊的報告。
    """

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=15)  # 預設回溯 15 天
    before = before.strftime("%Y-%m-%d")

    data = get_data_in_range(ticker, before, curr_date, "insider_trans", DATA_DIR)

    if len(data) == 0:
        return ""

    result_str = ""

    seen_dicts = []
    for date, senti_list in data.items():
        for entry in senti_list:
            if entry not in seen_dicts:
                result_str += f"### 申報日期: {entry['filingDate']}, {entry['name']}:\n變動:{entry['change']}\n股份: {entry['share']}\n交易價格: {entry['transactionPrice']}\n交易代碼: {entry['transactionCode']}\n\n"
                seen_dicts.append(entry)

    return (
        f"## {ticker} 從 {before} 到 {curr_date} 的內部人士交易：\n"
        + result_str
        + "change 欄位反映了股份數量的變化——此處負數表示持股減少——而 share 指定了涉及的總股數。transactionPrice 表示執行交易的每股價格，transactionDate 標記了交易發生的時間。name 欄位標識了進行交易的內部人士，transactionCode (例如，S 代表賣出) 闡明了交易的性質。FilingDate 記錄了交易正式報告的時間，唯一的 id 連結到特定的 SEC 文件，如來源所示。此外，symbol 將交易與特定公司聯繫起來，isDerivative 標記交易是否涉及衍生證券，currency 註明交易的貨幣背景。"
    )

def get_data_in_range(ticker, start_date, end_date, data_type, data_dir, period=None):
    """
    獲取保存在磁碟上並已處理的 finnhub 數據。
    Args:
        start_date (str): 開始日期，格式為 YYYY-MM-DD。
        end_date (str): 結束日期，格式為 YYYY-MM-DD。
        data_type (str): 要從 finnhub 獲取的數據類型。可以是 insider_trans、SEC_filings、news_data、insider_senti 或 fin_as_reported。
        data_dir (str): 數據保存的目錄。
        period (str): 預設為 none，如果指定了期間，應為 annual 或 quarterly。
    """

    if period:
        data_path = os.path.join(
            data_dir,
            "finnhub_data",
            data_type,
            f"{ticker}_{period}_data_formatted.json",
        )
    else:
        data_path = os.path.join(
            data_dir, "finnhub_data", data_type, f"{ticker}_data_formatted.json"
        )

    data = open(data_path, "r")
    data = json.load(data)

    # filter keys (date, str in format YYYY-MM-DD) by the date range (str, str in format YYYY-MM-DD)
    filtered_data = {}
    for key, value in data.items():
        if start_date <= key <= end_date and len(value) > 0:
            filtered_data[key] = value
    return filtered_data

def get_simfin_balance_sheet(
    ticker: Annotated[str, "股票代碼"],
    freq: Annotated[
        str,
        "公司的財務歷史報告頻率：年度/季度",
    ],
    curr_date: Annotated[str, "您正在交易的當前日期，格式為 yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR, # type: ignore
        "fundamental_data",
        "simfin_data_all",
        "balance_sheet",
        "companies",
        "us",
        f"us-balance-{freq}.csv",
    ) # type: ignore
    df = pl.read_csv(data_path, separator=";")

    # 將日期字串轉換為日期時間物件並移除任何時間部分
    df = df.with_columns(
        pl.col("Report Date").str.to_datetime().dt.date().alias("Report Date"),
        pl.col("Publish Date").str.to_datetime().dt.date().alias("Publish Date")
    )

    # 將當前日期轉換為日期時間並標準化
    from datetime import datetime as dt
    curr_date_dt = dt.strptime(curr_date, "%Y-%m-%d").date()

    # 過濾 DataFrame，篩選出給定股票代碼且報告發布日期在當前日期或之前的報告
    filtered_df = df.filter(
        (pl.col("Ticker") == ticker) & (pl.col("Publish Date") <= curr_date_dt)
    )

    # 檢查是否有可用的報告；如果沒有，則返回通知
    if filtered_df.is_empty():
        print("在給定的當前日期之前沒有可用的資產負債表。")
        return ""

    # 通過選擇具有最新發布日期的行來獲取最新的資產負債表
    max_date_idx = filtered_df.select(pl.col("Publish Date")).arg_max() # type: ignore
    latest_balance_sheet = filtered_df.row(max_date_idx, named=True)

    # 刪除 SimFinID 欄位
    # latest_balance_sheet = latest_balance_sheet.drop("SimFinId")

    return (
        f"## {ticker} 於 {str(latest_balance_sheet['Publish Date'])[0:10]} 發布的 {freq} 資產負債表：\n"
        + str(latest_balance_sheet)
        + "\n\n這包括報告日期和貨幣等元數據、股份詳細資訊，以及資產、負債和權益的明細。資產分為流動資產 (如現金和應收帳款等流動項目) 和非流動資產 (長期投資和財產)。負債分為短期義務和長期債務，而權益反映股東資金，如實收資本和保留盈餘。總之，這些組成部分確保總資產等於負債和權益的總和。"
    )


def get_simfin_cashflow(
    ticker: Annotated[str, "股票代碼"],
    freq: Annotated[
        str,
        "公司的財務歷史報告頻率：年度/季度",
    ],
    curr_date: Annotated[str, "您正在交易的當前日期，格式為 yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR, # type: ignore
        "fundamental_data",
        "simfin_data_all",
        "cash_flow",
        "companies",
        "us",
        f"us-cashflow-{freq}.csv",
    ) # type: ignore
    df = pl.read_csv(data_path, separator=";")

    # 將日期字串轉換為日期時間物件並移除任何時間部分
    df = df.with_columns(
        pl.col("Report Date").str.to_datetime().dt.date().alias("Report Date"),
        pl.col("Publish Date").str.to_datetime().dt.date().alias("Publish Date")
    )

    # 將當前日期轉換為日期時間並標準化
    from datetime import datetime as dt
    curr_date_dt = dt.strptime(curr_date, "%Y-%m-%d").date()

    # 過濾 DataFrame，篩選出給定股票代碼且報告發布日期在當前日期或之前的報告
    filtered_df = df.filter(
        (pl.col("Ticker") == ticker) & (pl.col("Publish Date") <= curr_date_dt)
    )

    # 檢查是否有可用的報告；如果沒有，則返回通知
    if filtered_df.is_empty():
        print("在給定的當前日期之前沒有可用的現金流量表。")
        return ""

    # 通過選擇具有最新發布日期的行來獲取最新的現金流量表
    max_date_idx = filtered_df.select(pl.col("Publish Date")).arg_max() # type: ignore
    latest_cash_flow = filtered_df.row(max_date_idx, named=True)

    # 刪除 SimFinID 欄位
    latest_cash_flow = latest_cash_flow.drop("SimFinId") # type: ignore

    return (
        f"## {ticker} 於 {str(latest_cash_flow['Publish Date'])[0:10]} 發布的 {freq} 現金流量表：\n"
        + str(latest_cash_flow)
        + "\n\n這包括報告日期和貨幣等元數據、股份詳細資訊，以及現金流動的明細。營運活動顯示核心業務營運產生的現金，包括非現金項目的淨利潤調整和營運資金變動。投資活動涵蓋資產購置/處置和投資。融資活動包括債務交易、股權發行/回購和股息支付。現金淨變動代表公司在報告期內現金部位的整體增加或減少。"
    )


def get_simfin_income_statements(
    ticker: Annotated[str, "股票代碼"],
    freq: Annotated[
        str,
        "公司的財務歷史報告頻率：年度/季度",
    ],
    curr_date: Annotated[str, "您正在交易的當前日期，格式為 yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR, # type: ignore
        "fundamental_data",
        "simfin_data_all",
        "income_statements",
        "companies",
        "us",
        f"us-income-{freq}.csv",
    ) # type: ignore
    df = pl.read_csv(data_path, separator=";")

    # 將日期字串轉換為日期時間物件並移除任何時間部分
    df = df.with_columns(
        pl.col("Report Date").str.to_datetime().dt.date().alias("Report Date"),
        pl.col("Publish Date").str.to_datetime().dt.date().alias("Publish Date")
    )

    # 將當前日期轉換為日期時間並標準化
    from datetime import datetime as dt
    curr_date_dt = dt.strptime(curr_date, "%Y-%m-%d").date()

    # 過濾 DataFrame，篩選出給定股票代碼且報告發布日期在當前日期或之前的報告
    filtered_df = df.filter(
        (pl.col("Ticker") == ticker) & (pl.col("Publish Date") <= curr_date_dt)
    )

    # 檢查是否有可用的報告；如果沒有，則返回通知
    if filtered_df.is_empty():
        print("在給定的當前日期之前沒有可用的損益表。")
        return ""

    # 通過選擇具有最新發布日期的行來獲取最新的損益表
    max_date_idx = filtered_df.select(pl.col("Publish Date")).arg_max() # type: ignore
    latest_income = filtered_df.row(max_date_idx, named=True)

    # 刪除 SimFinID 欄位
    latest_income = latest_income.drop("SimFinId") # type: ignore

    return (
        f"## {ticker} 於 {str(latest_income['Publish Date'])[0:10]} 發布的 {freq} 損益表：\n"
        + str(latest_income)
        + "\n\n這包括報告日期和貨幣等元數據、股份詳細資訊，以及公司財務績效的全面明細。從收入開始，顯示銷貨成本和由此產生的毛利。詳細列出營運費用，包括銷售、一般和管理費用、研發費用和折舊。然後，報表顯示營運收入，接著是非營運項目和利息費用，得出稅前收入。在考慮所得稅和任何非常規項目後，最終以淨利潤作結，代表公司在該期間的最終獲利或虧損。"
    )


def get_reddit_global_news(
    curr_date: Annotated[str, "當前日期，格式為 yyyy-mm-dd"],
    look_back_days: Annotated[int, "回溯天數"] = 7,
    limit: Annotated[int, "返回的最大文章數"] = 5,
) -> str:
    """
    檢索最新的 Reddit 熱門新聞。
    Args:
        curr_date: 當前日期，格式為 yyyy-mm-dd。
        look_back_days: 回溯天數 (預設 7)。
        limit: 返回的最大文章數 (預設 5)。
    Returns:
        str: 包含 Reddit 上最新新聞文章貼文的格式化字串。
    """
    
    # 檢查數據目錄是否存在
    reddit_data_path = os.path.join(DATA_DIR, "reddit_data") # type: ignore
    global_news_path = os.path.join(reddit_data_path, "global_news")
    
    if not os.path.exists(reddit_data_path):
        print(f"警告：Reddit 數據目錄不存在: {reddit_data_path}。請確保數據目錄已正確設置。")
        return ""
    
    if not os.path.exists(global_news_path):
        print(f"警告：全球新聞數據目錄不存在: {global_news_path}。請確保已下載 Reddit 全球新聞數據。")
        return ""

    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date_dt - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    posts = []
    # 從 before 到 curr_date 迭代
    curr_iter_date = datetime.strptime(before, "%Y-%m-%d")

    total_iterations = (curr_date_dt - curr_iter_date).days + 1
    pbar = tqdm(desc=f"正在獲取 {curr_date} 的全球新聞", total=total_iterations)

    while curr_iter_date <= curr_date_dt:
        curr_date_str = curr_iter_date.strftime("%Y-%m-%d")
        try:
            fetch_result = fetch_top_from_category(
                "global_news",
                curr_date_str,
                limit,
                data_path=reddit_data_path,
            )
            posts.extend(fetch_result)
        except (FileNotFoundError, ValueError) as e:
            # 如果特定日期的數據不存在，繼續下一天
            print(f"警告：無法獲取 {curr_date_str} 的數據: {e}")
        curr_iter_date += relativedelta(days=1)
        pbar.update(1)

    pbar.close()

    if len(posts) == 0:
        return ""

    news_str = ""
    for post in posts:
        if post["content"] == "":
            news_str += f"### {post['title']}\n\n"
        else:
            news_str += f"### {post['title']}\n\n{post['content']}\n\n"

    return f"## 全球新聞 Reddit，從 {before} 到 {curr_date}：\n{news_str}"


def get_reddit_company_news(
    query: Annotated[str, "搜索查詢或股票代碼"],
    start_date: Annotated[str, "開始日期，格式為 yyyy-mm-dd"],
    end_date: Annotated[str, "結束日期，格式為 yyyy-mm-dd"],
) -> str:
    """
    檢索最新的 Reddit 熱門新聞。
    Args:
        query: 搜索查詢或股票代碼。
        start_date: 開始日期，格式為 yyyy-mm-dd。
        end_date: 結束日期，格式為 yyyy-mm-dd。
    Returns:
        str: 包含 Reddit 上新聞文章貼文的格式化字串。
    """
    
    # 檢查數據目錄是否存在
    reddit_data_path = os.path.join(DATA_DIR, "reddit_data") # type: ignore
    company_news_path = os.path.join(reddit_data_path, "company_news")
    
    if not os.path.exists(reddit_data_path):
        print(f"警告：Reddit 數據目錄不存在: {reddit_data_path}。請確保數據目錄已正確設置。")
        return ""
    
    if not os.path.exists(company_news_path):
        print(f"警告：公司新聞數據目錄不存在: {company_news_path}。請確保已下載 Reddit 公司新聞數據。")
        return ""

    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")

    posts = []
    # 從 start_date 到 end_date 迭代
    curr_date = start_date_dt

    total_iterations = (end_date_dt - curr_date).days + 1
    pbar = tqdm(
        desc=f"正在獲取 {query} 從 {start_date} 到 {end_date} 的公司新聞",
        total=total_iterations,
    )

    # 限制每天的文章數量以避免 token 過多
    max_per_day = 5  # 從 10 降低到 5

    while curr_date <= end_date_dt:
        curr_date_str = curr_date.strftime("%Y-%m-%d")
        try:
            fetch_result = fetch_top_from_category(
                "company_news",
                curr_date_str,
                max_per_day,
                query,
                data_path=reddit_data_path,
            )
            posts.extend(fetch_result)
        except (FileNotFoundError, ValueError) as e:
            # 如果特定日期的數據不存在，繼續下一天
            print(f"警告：無法獲取 {curr_date_str} 的數據: {e}")
        curr_date += relativedelta(days=1)

        pbar.update(1)

    pbar.close()

    if len(posts) == 0:
        return ""

    # 限制總文章數量和內容長度
    max_total_posts = 20  # 最多 20 篇文章
    posts = posts[:max_total_posts]
    
    news_str = ""
    for post in posts:
        title = post['title']
        content = post['content']
        
        # 限制每篇文章的內容長度
        if content and len(content) > 300:
            content = content[:300] + "..."
        
        if content == "":
            news_str += f"### {title}\n\n"
        else:
            news_str += f"### {title}\n\n{content}\n\n"

    return f"##{query} 新聞 Reddit，從 {start_date} 到 {end_date}：\n\n{news_str}"
