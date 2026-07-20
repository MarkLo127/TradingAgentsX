import time
import json
from tradingagents.agents.utils.agent_utils import get_stock_data, get_indicators, make_cached_system_message
from tradingagents.agents.utils.prompts import get_language_instruction, get_language_closing_instruction, get_agent_role_instruction, get_context_message
from tradingagents.dataflows.config import get_config


def create_market_analyst(llm, language: str = "zh-TW"):
    """
    建立一個市場分析師節點。

    Args:
        llm: 用於分析的語言模型。
        language: 報告語言 ('en' 或 'zh-TW')

    Returns:
        一個處理市場分析的節點函式。
    """

    def market_analyst_node(state):
        """
        分析市場數據和技術指標。

        Args:
            state: 當前的代理狀態。

        Returns:
            更新後的代理狀態，包含市場分析報告和訊息。
        """
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state.get("company_name", ticker)

        tools = [
            get_stock_data,
            get_indicators,
        ]

        # Get language-specific instructions
        lang_instruction = get_language_instruction(language)
        lang_closing = get_language_closing_instruction(language)
        role_instruction = get_agent_role_instruction(language)
        context_msg = get_context_message(language, current_date, company_name, ticker)

        if language == "en":
            system_message = f"""{lang_instruction}

【Professional Identity】
You are a senior technical analyst responsible for providing precise market technical assessments.

【Analysis Focus】
1. **Trend Analysis**: Based on price movements and volume, clearly determine the current market phase (uptrend/downtrend/consolidation)
2. **Technical Indicators**: Focus on 3-4 core indicators (recommended: 50-day/200-day MA, MACD, RSI), interpret their signal meanings
3. **Support & Resistance**: Mark key price zones, explain technical turning points
4. **Trading Recommendations**: Provide entry/exit positions, risk control parameters

【Technical Operations】
• Use get_stock_data to obtain historical price data
• Use get_indicators to calculate technical indicators (set look_back_days to 50 or 200 for moving averages)
• Integrate data to provide professional insights

【Report Structure】
**Content Structure**:
1. Market Overview (120-150 words): Trend direction and momentum strength
2. Technical Analysis (400-600 words): Indicator interpretation and cross-validation
3. Key Price Levels (80-120 words): Support/resistance levels and their technical significance
4. Trading Strategy (150-200 words): Entry points, stop-loss settings, target prices
5. Data Summary Table (required, not counted in word count)

**Writing Principles**:
- Professional yet clear, avoid overly technical expressions
- Clear conclusions, provide actionable trading recommendations
- Must include core data summary table
- Control length, ensure analysis is completed within 1500 words

**Closing Note**:
Please add the following at the end of your report:
\"---
※ This report is technical analysis only. Recommend combining with fundamental and sentiment analysis. Technical indicators are lagging, investment involves risk, please evaluate carefully.\"

Please provide a professional, precise, and actionable technical analysis report. Be sure to include a Markdown table at the end summarizing key points.

{lang_closing}"""
        else:
            system_message = f"""{lang_instruction}

【專業身份】
您是資深技術分析師，負責提供精準的市場技術面評估。

【分析重點】
1. **趨勢研判**：基於價格走勢與成交量，明確判斷當前市場階段（上升趨勢/下降趨勢/區間整理）
2. **技術指標**：聚焦3-4個核心指標（建議：50日/200日均線、MACD、RSI），解讀其訊號意義
3. **支撐壓力**：標示關鍵價格區間，說明技術面轉折點
4. **操作建議**：提供進出場位置、風險控制參數

【技術操作】
• 使用 get_stock_data 取得歷史價格資料
• 使用 get_indicators 計算技術指標（均線請設定 look_back_days 為 50 或 200）
• 整合數據後提出專業見解

【報告架構】

**內容結構**：
1. 市場概況：趨勢方向與動能強弱
2. 技術分析：指標解讀與相互驗證
3. 關鍵價位：支撐/壓力位及其技術意義
4. 操作策略：進場點位、停損設定、目標價位
5. 數據摘要表格（必須）

**撰寫原則**：
- 專業但清晰，避免過度技術化的表述
- 結論明確，提供可執行的交易建議
- 必須包含核心數據整理表格
- 控制篇幅，確保在1500字以內完成分析

**結尾提示**：
請在報告最後加上以下結尾：
「---
※ 本報告為技術面分析，建議搭配基本面及市場情緒綜合研判。技術指標具滯後性，投資有風險，請謹慎評估。」

請提供專業、精準且具操作性的技術分析報告。請務必在報告結尾附加一個 Markdown 表格，以整理報告中的要點。

{lang_closing}"""

        tool_names = ", ".join([tool.name for tool in tools])
        # 靜態系統提示合併為單一 cache_control 區塊（僅 Claude 生效）；
        # analyst 的 tool 迴圈會多輪重送此前綴，命中快取後 cache read 只需原價 10%
        system_text = (
            f"{role_instruction} 您可以使用以下工具：{tool_names}。\n"
            f"{system_message}{context_msg}"
        )
        messages = [make_cached_system_message(system_text, llm), *state["messages"]]

        result = llm.bind_tools(tools).invoke(messages)

        # Report logic: only save report when LLM gives final response
        report = state.get("market_report", "")
        
        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node