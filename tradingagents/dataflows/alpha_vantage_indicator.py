from .alpha_vantage_common import _make_api_request

def get_indicator(
    symbol: str,
    indicator: str,
    curr_date: str,
    look_back_days: int,
    interval: str = "daily",
    time_period: int = 14,
    series_type: str = "close"
) -> str:
    """
    返回 Alpha Vantage 在一個時間窗口內的技術指標值。

    Args:
        symbol: 公司的股票代碼
        indicator: 要獲取分析和報告的技術指標
        curr_date: 您正在交易的當前交易日期，格式為 YYYY-mm-dd
        look_back_days: 回溯天數
        interval: 時間間隔 (每日、每週、每月)
        time_period: 用於計算的數據點數量
        series_type: 所需的價格類型 (收盤價、開盤價、最高價、最低價)

    Returns:
        包含指標值和描述的字串
    """
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    supported_indicators = {
        "close_50_sma": ("50 SMA", "close"),
        "close_200_sma": ("200 SMA", "close"),
        "close_10_ema": ("10 EMA", "close"),
        "macd": ("MACD", "close"),
        "macds": ("MACD Signal", "close"),
        "macdh": ("MACD Histogram", "close"),
        "rsi": ("RSI", "close"),
        "boll": ("Bollinger Middle", "close"),
        "boll_ub": ("Bollinger Upper Band", "close"),
        "boll_lb": ("Bollinger Lower Band", "close"),
        "atr": ("ATR", None),
        "vwma": ("VWMA", "close")
    }

    indicator_descriptions = {
        "close_50_sma": "50 SMA：一個中期趨勢指標。用法：識別趨勢方向並作為動態支撐/阻力。提示：它滯後於價格；與更快的指標結合以獲得及時信號。",
        "close_200_sma": "200 SMA：一個長期趨勢基準。用法：確認整體市場趨勢並識別黃金/死亡交叉設置。提示：它反應緩慢；最適合戰略趨勢確認，而非頻繁的交易入場。",
        "close_10_ema": "10 EMA：一個反應靈敏的短期平均線。用法：捕捉動能的快速轉變和潛在的入場點。提示：在震盪市場中容易產生噪音；與較長的平均線一起使用以過濾錯誤信號。",
        "macd": "MACD：通過 EMA 的差異計算動能。用法：尋找交叉和背離作為趨勢變化的信號。提示：在低波動性或橫盤市場中與其他指標確認。",
        "macds": "MACD 信號線：MACD 線的 EMA 平滑。用法：使用與 MACD 線的交叉來觸發交易。提示：應作為更廣泛策略的一部分以避免誤報。",
        "macdh": "MACD 柱狀圖：顯示 MACD 線與其信號線之間的差距。用法：可視化動能強度並及早發現背離。提示：可能不穩定；在快速變動的市場中輔以額外的過濾器。",
        "rsi": "RSI：衡量動能以標記超買/超賣狀況。用法：應用 70/30 閾值並觀察背離以發出反轉信號。提示：在強勁趨勢中，RSI 可能保持極端；務必與趨勢分析交叉檢查。",
        "boll": "布林帶中軌：作為布林帶基礎的 20 SMA。用法：作為價格變動的動態基準。提示：與上下軌結合以有效發現突破或反轉。",
        "boll_ub": "布林帶上軌：通常比中軌高 2 個標準差。用法：發出潛在超買狀況和突破區域的信號。提示：與其他工具確認信號；在強勁趨勢中價格可能會沿著軌道運行。",
        "boll_lb": "布林帶下軌：通常比中軌低 2 個標準差。用法：指示潛在的超賣狀況。提示：使用額外分析以避免錯誤的反轉信號。",
        "atr": "ATR：平均真實波幅，用於衡量波動性。用法：根據當前市場波動性設置止損水平和調整頭寸大小。提示：這是一個反應性指標，因此請將其用作更廣泛風險管理策略的一部分。",
        "vwma": "VWMA：成交量加權移動平均線。用法：通過將價格行為與成交量數據相結合來確認趨勢。提示：注意成交量激增導致的結果偏差；與其他成交量分析結合使用。"
    }

    if indicator not in supported_indicators:
        raise ValueError(
            f"不支持指標 {indicator}。請從以下選項中選擇：{list(supported_indicators.keys())}"
        )

    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date_dt - relativedelta(days=look_back_days)

    # 獲取整個期間的完整數據，而不是單獨調用
    _, required_series_type = supported_indicators[indicator]

    # 使用提供的 series_type 或回退到必需的類型
    if required_series_type:
        series_type = required_series_type

    try:
        # 獲取期間的指標數據
        if indicator == "close_50_sma":
            data = _make_api_request("SMA", {
                "symbol": symbol,
                "interval": interval,
                "time_period": "50",
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator == "close_200_sma":
            data = _make_api_request("SMA", {
                "symbol": symbol,
                "interval": interval,
                "time_period": "200",
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator == "close_10_ema":
            data = _make_api_request("EMA", {
                "symbol": symbol,
                "interval": interval,
                "time_period": "10",
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator == "macd":
            data = _make_api_request("MACD", {
                "symbol": symbol,
                "interval": interval,
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator == "macds":
            data = _make_api_request("MACD", {
                "symbol": symbol,
                "interval": interval,
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator == "macdh":
            data = _make_api_request("MACD", {
                "symbol": symbol,
                "interval": interval,
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator == "rsi":
            data = _make_api_request("RSI", {
                "symbol": symbol,
                "interval": interval,
                "time_period": str(time_period),
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator in ["boll", "boll_ub", "boll_lb"]:
            data = _make_api_request("BBANDS", {
                "symbol": symbol,
                "interval": interval,
                "time_period": "20",
                "series_type": series_type,
                "datatype": "csv"
            })
        elif indicator == "atr":
            data = _make_api_request("ATR", {
                "symbol": symbol,
                "interval": interval,
                "time_period": str(time_period),
                "datatype": "csv"
            })
        elif indicator == "vwma":
            # Alpha Vantage 沒有直接的 VWMA，因此我們將返回一條資訊性訊息
            # 在實際實現中，這需要從 OHLCV 數據中計算
            return f"## {symbol} 的 VWMA (成交量加權移動平均線)：\n\nVWMA 計算需要 OHLCV 數據，無法直接從 Alpha Vantage API 獲得。\n此指標需要使用成交量加權價格平均從原始股票數據中計算。\n\n{indicator_descriptions.get('vwma', '無可用描述。')}"
        else:
            return f"錯誤：指標 {indicator} 尚未實現。"

        # 解析 CSV 數據並提取日期範圍內的值
        lines = data.strip().split('\n') # type: ignore
        if len(lines) < 2:
            return f"錯誤：{indicator} 沒有返回數據"

        # 解析標頭和數據
        header = [col.strip() for col in lines[0].split(',')]
        try:
            date_col_idx = header.index('time')
        except ValueError:
            return f"錯誤：在 {indicator} 的數據中找不到 'time' 欄位。可用欄位：{header}"

        # 將內部指標名稱映射到 Alpha Vantage 預期的 CSV 欄位名稱
        col_name_map = {
            "macd": "MACD", "macds": "MACD_Signal", "macdh": "MACD_Hist",
            "boll": "Real Middle Band", "boll_ub": "Real Upper Band", "boll_lb": "Real Lower Band",
            "rsi": "RSI", "atr": "ATR", "close_10_ema": "EMA",
            "close_50_sma": "SMA", "close_200_sma": "SMA"
        }

        target_col_name = col_name_map.get(indicator)

        if not target_col_name:
            # 如果沒有特定的映射，則預設為第二欄
            value_col_idx = 1
        else:
            try:
                value_col_idx = header.index(target_col_name)
            except ValueError:
                return f"錯誤：指標 '{indicator}' 找不到欄位 '{target_col_name}'。可用欄位：{header}"

        result_data = []
        for line in lines[1:]:
            if not line.strip():
                continue
            values = line.split(',')
            if len(values) > value_col_idx:
                try:
                    date_str = values[date_col_idx].strip()
                    # 解析日期
                    date_dt = datetime.strptime(date_str, "%Y-%m-%d")

                    # 檢查日期是否在我們的範圍內
                    if before <= date_dt <= curr_date_dt:
                        value = values[value_col_idx].strip()
                        result_data.append((date_dt, value))
                except (ValueError, IndexError):
                    continue

        # 按日期排序並格式化輸出
        result_data.sort(key=lambda x: x[0])

        ind_string = ""
        for date_dt, value in result_data:
            ind_string += f"{date_dt.strftime('%Y-%m-%d')}: {value}\n"

        if not ind_string:
            ind_string = "指定日期範圍內無可用數據。\n"

        result_str = (
            f"## 從 {before.strftime('%Y-%m-%d')} 到 {curr_date} 的 {indicator.upper()} 值：\n\n"
            + ind_string
            + "\n\n"
            + indicator_descriptions.get(indicator, "無可用描述。")
        )

        return result_str

    except Exception as e:
        print(f"獲取 {indicator} 的 Alpha Vantage 指標數據時出錯：{e}")
        return f"檢索 {indicator} 數據時出錯：{str(e)}"