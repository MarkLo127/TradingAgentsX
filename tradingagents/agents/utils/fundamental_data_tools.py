from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_fundamentals(
    ticker: Annotated[str, "股票代碼"],
    curr_date: Annotated[str, "您正在交易的當前日期，格式為 yyyy-mm-dd"],
) -> str:
    """
    檢索給定股票代碼的綜合基本面數據。
    使用設定的基本面數據供應商。
    Args:
        ticker (str): 公司的股票代碼
        curr_date (str): 您正在交易的當前日期，格式為 yyyy-mm-dd
    Returns:
        str: 一份包含綜合基本面數據的格式化報告
    """
    return route_to_vendor("get_fundamentals", ticker, curr_date)


@tool
def get_balance_sheet(
    ticker: Annotated[str, "股票代碼"],
    freq: Annotated[str, "報告頻率：年度/季度"] = "quarterly",
    curr_date: Annotated[str, "您正在交易的當前日期，格式為 yyyy-mm-dd"] = None, # type: ignore
) -> str:
    """
    檢索給定股票代碼的資產負債表數據。
    使用設定的基本面數據供應商。
    Args:
        ticker (str): 公司的股票代碼
        freq (str): 報告頻率：年度/季度 (預設為季度)
        curr_date (str): 您正在交易的當前日期，格式為 yyyy-mm-dd
    Returns:
        str: 一份包含資產負債表數據的格式化報告
    """
    return route_to_vendor("get_balance_sheet", ticker, freq, curr_date)


@tool
def get_cashflow(
    ticker: Annotated[str, "股票代碼"],
    freq: Annotated[str, "報告頻率：年度/季度"] = "quarterly",
    curr_date: Annotated[str, "您正在交易的當前日期，格式為 yyyy-mm-dd"] = None, # type: ignore
) -> str:
    """
    檢索給定股票代碼的現金流量表數據。
    使用設定的基本面數據供應商。
    Args:
        ticker (str): 公司的股票代碼
        freq (str): 報告頻率：年度/季度 (預設為季度)
        curr_date (str): 您正在交易的當前日期，格式為 yyyy-mm-dd
    Returns:
        str: 一份包含現金流量表數據的格式化報告
    """
    return route_to_vendor("get_cashflow", ticker, freq, curr_date)


@tool
def get_income_statement(
    ticker: Annotated[str, "股票代碼"],
    freq: Annotated[str, "報告頻率：年度/季度"] = "quarterly",
    curr_date: Annotated[str, "您正在交易的當前日期，格式為 yyyy-mm-dd"] = None, # type: ignore
) -> str:
    """
    檢索給定股票代碼的損益表數據。
    使用設定的基本面數據供應商。
    Args:
        ticker (str): 公司的股票代碼
        freq (str): 報告頻率：年度/季度 (預設為季度)
        curr_date (str): 您正在交易的當前日期，格式為 yyyy-mm-dd
    Returns:
        str: 一份包含損益表數據的格式化報告
    """
    return route_to_vendor("get_income_statement", ticker, freq, curr_date)
