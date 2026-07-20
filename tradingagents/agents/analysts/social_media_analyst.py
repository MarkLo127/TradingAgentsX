import time
import json
from tradingagents.agents.utils.agent_utils import get_news, make_cached_system_message
from tradingagents.agents.utils.prompts import get_social_analyst_prompt, get_agent_role_instruction, get_context_message
from tradingagents.dataflows.config import get_config


def create_social_media_analyst(llm, language: str = "zh-TW"):
    """
    建立一個社群媒體分析師節點。

    Args:
        llm: 用於分析的語言模型。
        language: 報告語言 ('en' 或 'zh-TW')

    Returns:
        一個處理社群媒體分析的節點函式。
    """
    def social_media_analyst_node(state):
        """
        分析社群媒體貼文、近期公司新聞和公眾情緒。

        Args:
            state: 當前的代理狀態。

        Returns:
            更新後的代理狀態，包含情緒分析報告和訊息。
        """
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state.get("company_name", ticker)

        tools = [
            get_news,
        ]

        # Get language-specific prompts
        system_message = get_social_analyst_prompt(language)
        role_instruction = get_agent_role_instruction(language)
        context_msg = get_context_message(language, current_date, company_name, ticker)

        tool_names = ", ".join([tool.name for tool in tools])
        # 靜態系統提示合併為單一 cache_control 區塊（僅 Claude 生效）；
        # analyst 的 tool 迴圈會多輪重送此前綴，命中快取後 cache read 只需原價 10%
        system_text = (
            f"{role_instruction} 您可以使用以下工具：{tool_names}。\n"
            f"{system_message} {context_msg}"
        )
        messages = [make_cached_system_message(system_text, llm), *state["messages"]]

        result = llm.bind_tools(tools).invoke(messages)

        # Report logic: only save report when LLM gives final response
        report = state.get("sentiment_report", "")

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return social_media_analyst_node