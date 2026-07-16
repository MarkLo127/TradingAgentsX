"""
重試工具模組，提供統一的重試機制和錯誤處理
"""
import time
import logging
from functools import wraps
from typing import Callable, Type, Tuple

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Callable = None # type: ignore
):
    """
    重試裝飾器，支援指數退避
    
    Args:
        max_attempts: 最大重試次數（包含首次嘗試）
        backoff: 退避基數（每次重試等待時間 = backoff ^ attempt）
        exceptions: 需要重試的例外類型元組
        on_retry: 重試時的回調函數
        
    Returns:
        裝飾後的函數
        
    Example:
        @retry(max_attempts=3, backoff=2.0)
        def fetch_data():
            return api.get_data()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        # 最後一次嘗試失敗
                        logger.error(
                            f"{func.__name__} 在 {max_attempts} 次嘗試後失敗: {e}"
                        )
                        raise
                    
                    # 計算退避時間
                    wait_time = backoff ** (attempt - 1)
                    
                    logger.warning(
                        f"{func.__name__} 第 {attempt} 次嘗試失敗: {e}. "
                        f"將在 {wait_time:.1f} 秒後重試..."
                    )
                    
                    # 執行回調
                    if on_retry:
                        on_retry(attempt, e)
                    
                    # 等待後重試
                    time.sleep(wait_time)
            
            # 理論上不會到這裡，但為了類型安全
            raise last_exception # type: ignore
        
        return wrapper
    return decorator


def log_retry_attempt(attempt: int, exception: Exception) -> None:
    """
    記錄重試嘗試的標準回調函數
    
    Args:
        attempt: 當前嘗試次數
        exception: 遇到的例外
    """
    logger.info(f"重試回調 - 第 {attempt} 次嘗試因以下原因失敗: {type(exception).__name__}")
