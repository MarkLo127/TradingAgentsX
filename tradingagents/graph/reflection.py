# -*- coding: utf-8 -*-
# TradingAgentsX/graph/reflection.py

from typing import Dict, Any
from langchain_openai import ChatOpenAI


class Reflector:
    """
    處理對決策的反思並更新記憶。
    這個類別的目的是評估過去的交易決策，從中學習，並將學到的知識儲存起來以供未來使用。
    """

    def __init__(self, quick_thinking_llm: ChatOpenAI):
        """
        使用一個 LLM 初始化反思器。

        Args:
            quick_thinking_llm (ChatOpenAI): 用於生成反思內容的語言模型。
        """
        self.quick_thinking_llm = quick_thinking_llm
        self.reflection_system_prompt = self._get_reflection_prompt()

    def _get_reflection_prompt(self) -> str:
        """
        獲取用於反思的系統提示。
        這個提示指導 LLM 如何分析交易決策、提出改進建議並總結經驗教訓。
        """
        return """
您是一位專家級金融分析師，負責審查交易決策/分析並提供全面、逐步的分析。
您的目標是提供對投資決策的詳細見解，並強調改進的機會，嚴格遵守以下準則：

1. 推理：
   - 對於每個交易決策，判斷其正確與否。正確的決策會導致回報增加，而錯誤的決策則相反。
   - 分析導致每次成功或失誤的因素。考慮以下方面：
     - 市場情報。
     - 技術指標。
     - 技術信號。
     - 價格變動分析。
     - 整體市場數據分析。
     - 新聞分析。
     - 社群媒體和情緒分析。
     - 基本面數據分析。
   - 在決策過程中權衡每個因素的重要性。

2. 改進：
   - 對於任何不正確的決策，提出修正建議以最大化回報。
   - 提供詳細的糾正措施或改進清單，包括具體建議（例如，將某個日期的決策從「持有」改為「購買」）。

3. 總結：
   - 總結從成功和失誤中學到的經驗教訓。
   - 強調這些教訓如何應用於未來的交易場景，並在相似情況之間建立聯繫以應用所學知識。

4. 查詢：
   - 將總結中的關鍵見解提取成一個不超過 1000 個 token 的簡潔句子。
   - 確保濃縮後的句子能捕捉到經驗教訓和推理的精髓，以便於參考。

請嚴格遵守這些說明，並確保您的輸出詳細、準確且具有可操作性。您還將獲得關於市場價格變動、技術指標、新聞和情緒的客觀描述，以便為您的分析提供更多背景資訊。
"""

    def _extract_current_situation(self, current_state: Dict[str, Any]) -> str:
        """
        從狀態中提取當前的市場情況。
        這會整合來自不同分析師的報告，為反思提供全面的市場背景。

        Args:
            current_state (Dict[str, Any]): 當前的圖狀態。

        Returns:
            str: 描述當前市場情況的字串。
        """
        curr_market_report = current_state["market_report"]
        curr_sentiment_report = current_state["sentiment_report"]
        curr_news_report = current_state["news_report"]
        curr_fundamentals_report = current_state["fundamentals_report"]

        return f"{curr_market_report}\n\n{curr_sentiment_report}\n\n{curr_news_report}\n\n{curr_fundamentals_report}"

    def _reflect_on_component(
        self, component_type: str, report: str, situation: str, returns_losses
    ) -> str:
        """
        為一個組件生成反思。
        這個通用函式會呼叫 LLM 來評估特定組件（例如，看漲研究員）的報告或決策。

        Args:
            component_type (str): 組件的類型（例如，"BULL"、"TRADER"）。
            report (str): 該組件生成的報告或決策。
            situation (str): 當前的市場情況。
            returns_losses: 相關期間的收益或損失。

        Returns:
            str: LLM 生成的反思結果。
        """
        messages = [
            ("system", self.reflection_system_prompt),
            (
                "human",
                f"回報: {returns_losses}\n\n分析/決策: {report}\n\n供參考的客觀市場報告: {situation}",
            ),
        ]

        result = self.quick_thinking_llm.invoke(messages).content
        return result # type: ignore

    def reflect_bull_researcher(self, current_state, returns_losses, bull_memory):
        """
        反思看漲研究員的分析並更新其記憶。

        Args:
            current_state: 當前的圖狀態。
            returns_losses: 相關的收益/損失。
            bull_memory: 看漲研究員的記憶體物件。
        """
        situation = self._extract_current_situation(current_state)
        bull_debate_history = current_state["investment_debate_state"]["bull_history"]

        result = self._reflect_on_component(
            "BULL", bull_debate_history, situation, returns_losses
        )
        bull_memory.add_situations([(situation, result)])

    def reflect_bear_researcher(self, current_state, returns_losses, bear_memory):
        """
        反思看跌研究員的分析並更新其記憶。

        Args:
            current_state: 當前的圖狀態。
            returns_losses: 相關的收益/損失。
            bear_memory: 看跌研究員的記憶體物件。
        """
        situation = self._extract_current_situation(current_state)
        bear_debate_history = current_state["investment_debate_state"]["bear_history"]

        result = self._reflect_on_component(
            "BEAR", bear_debate_history, situation, returns_losses
        )
        bear_memory.add_situations([(situation, result)])

    def reflect_trader(self, current_state, returns_losses, trader_memory):
        """
        反思交易員的決策並更新其記憶。

        Args:
            current_state: 當前的圖狀態。
            returns_losses: 相關的收益/損失。
            trader_memory: 交易員的記憶體物件。
        """
        situation = self._extract_current_situation(current_state)
        trader_decision = current_state["trader_investment_plan"]

        result = self._reflect_on_component(
            "TRADER", trader_decision, situation, returns_losses
        )
        trader_memory.add_situations([(situation, result)])

    def reflect_invest_judge(self, current_state, returns_losses, invest_judge_memory):
        """
        反思投資裁判的決策並更新其記憶。

        Args:
            current_state: 當前的圖狀態。
            returns_losses: 相關的收益/損失。
            invest_judge_memory: 投資裁判的記憶體物件。
        """
        situation = self._extract_current_situation(current_state)
        judge_decision = current_state["investment_debate_state"]["judge_decision"]

        result = self._reflect_on_component(
            "INVEST JUDGE", judge_decision, situation, returns_losses
        )
        invest_judge_memory.add_situations([(situation, result)])

    def reflect_risk_manager(self, current_state, returns_losses, risk_manager_memory):
        """
        反思風險管理者的決策並更新其記憶。

        Args:
            current_state: 當前的圖狀態。
            returns_losses: 相關的收益/損失。
            risk_manager_memory: 風險管理者的記憶體物件。
        """
        situation = self._extract_current_situation(current_state)
        judge_decision = current_state["risk_debate_state"]["judge_decision"]

        result = self._reflect_on_component(
            "RISK JUDGE", judge_decision, situation, returns_losses
        )
        risk_manager_memory.add_situations([(situation, result)])