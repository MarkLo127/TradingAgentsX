# -*- coding: utf-8 -*-
# TradingAgentsX/graph/signal_processing.py

from langchain_openai import ChatOpenAI


class SignalProcessor:
    """
    處理交易信號以提取可執行的決策。
    這個類別的目的是將來自代理的自然語言格式的完整交易信號，
    轉換為標準化的、機器可讀的決策（例如 "BUY", "SELL", "HOLD"）。
    """

    def __init__(self, quick_thinking_llm: ChatOpenAI):
        """
        使用一個 LLM 進行初始化以進行處理。

        Args:
            quick_thinking_llm (ChatOpenAI): 用於提取決策的語言模型。
        """
        self.quick_thinking_llm = quick_thinking_llm

    def process_signal(self, full_signal: str) -> str:
        """
        處理完整的交易信號以提取核心決策。

        Args:
            full_signal (str): 完整的交易信號文本。

        Returns:
            str: 提取出的決策（BUY, SELL, 或 HOLD）。
        """
        # 建立傳送給 LLM 的訊息列表
        messages = [
            (
                "system",
                # 系統提示，指導 LLM 的行為
                "您是一位高效的助理，旨在分析一組分析師提供的段落或財務報告。您的任務是提取投資決策：SELL (賣出)、BUY (買入) 或 HOLD (持有)。請僅提供提取的決策（SELL、BUY 或 HOLD）作為您的輸出，不要添加任何額外的文本或資訊。",
            ),
            ("human", full_signal),  # 人類訊息，包含要處理的完整信號
        ]

        # 呼叫 LLM 並返回其內容，即提取出的決策
        return self.quick_thinking_llm.invoke(messages).content # type: ignore