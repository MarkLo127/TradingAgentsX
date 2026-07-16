import tradingagents.default_config as default_config
from typing import Dict, Optional

# 使用預設設定，但允許被覆寫
_config: Optional[Dict] = None
DATA_DIR: Optional[str] = None


def initialize_config():
    """使用預設值初始化設定。"""
    global _config, DATA_DIR
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()
        DATA_DIR = _config["data_dir"]


def set_config(config: Dict):
    """使用自訂值更新設定。"""
    global _config, DATA_DIR
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()
    _config.update(config)
    DATA_DIR = _config["data_dir"]


def get_config() -> Dict:
    """獲取當前設定。"""
    if _config is None:
        initialize_config()
    return _config.copy() # type: ignore


# 使用預設設定進行初始化
initialize_config()