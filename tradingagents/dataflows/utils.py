import os
import json
import polars as pl
from datetime import date, timedelta, datetime
from typing import Annotated

SavePathType = Annotated[str, "儲存資料的檔案路徑。如果為 None，則不儲存資料。"]

def save_output(data: pl.DataFrame, tag: str, save_path: SavePathType = None) -> None: # type: ignore
    """
    將 DataFrame 儲存到 CSV 檔案。

    Args:
        data (pl.DataFrame): 要儲存的 DataFrame。
        tag (str): 用於在控制台中打印的標籤。
        save_path (SavePathType, optional): 儲存檔案的路徑。預設為 None。
    """
    if save_path:
        data.write_csv(save_path)
        print(f"{tag} 已儲存至 {save_path}")


def get_current_date():
    """
    以 YYYY-MM-DD 格式獲取當前日期。

    Returns:
        str: 當前日期字串。
    """
    return date.today().strftime("%Y-%m-%d")


def decorate_all_methods(decorator):
    """
    一個裝飾器，用於將另一個裝飾器應用於一個類別的所有方法。

    Args:
        decorator: 要應用的裝飾器。

    Returns:
        function: 類別裝飾器。
    """
    def class_decorator(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value):
                setattr(cls, attr_name, decorator(attr_value))
        return cls

    return class_decorator


def get_next_weekday(date):
    """
    獲取給定日期之後的下一個工作日。

    Args:
        date (str or datetime): 日期。

    Returns:
        datetime: 下一個工作日。
    """

    if not isinstance(date, datetime):
        date = datetime.strptime(date, "%Y-%m-%d")

    if date.weekday() >= 5:
        days_to_add = 7 - date.weekday()
        next_weekday = date + timedelta(days=days_to_add)
        return next_weekday
    else:
        return date