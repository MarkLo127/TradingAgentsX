from datetime import datetime
from .alpha_vantage_common import _make_api_request, _filter_csv_by_date_range

def get_stock(
    symbol: str,
    start_date: str,
    end_date: str
) -> str:
    """
    返回原始的每日 OHLCV 值、調整後的收盤價以及歷史上的股票分割/股息事件，
    並過濾到指定的日期範圍。

    Args:
        symbol: 股票的名稱。例如：symbol=IBM
        start_date: 開始日期，格式為 yyyy-mm-dd
        end_date: 結束日期，格式為 yyyy-mm-dd

    Returns:
        包含過濾到指定日期範圍的每日調整後時間序列數據的 CSV 字串。
    """
    # 解析日期以確定範圍
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    today = datetime.now()

    # 根據請求的範圍是否在最近 100 天內選擇 outputsize
    # compact 返回最近 100 個數據點，因此檢查 start_date 是否足夠近
    days_from_today_to_start = (today - start_dt).days
    outputsize = "compact" if days_from_today_to_start < 100 else "full"

    params = {
        "symbol": symbol,
        "outputsize": outputsize,
        "datatype": "csv",
    }

    response = _make_api_request("TIME_SERIES_DAILY_ADJUSTED", params)

    return _filter_csv_by_date_range(response, start_date, end_date) # type: ignore
