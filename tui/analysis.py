# -*- coding: utf-8 -*-
"""
分析流程執行器。

從 cli/main.py 的 run_analysis 移植而來，但與顯示層解耦：
資料寫入傳入的 MessageBuffer，並透過 on_update 回呼通知 UI 重繪。
這個函式會在 Textual 的背景執行緒 (worker) 中執行。
"""
from functools import wraps
from pathlib import Path

from tradingagents.graph.trading_graph import TradingAgentsXGraph
from tradingagents.default_config import DEFAULT_CONFIG

from tui.message_buffer import _content_to_str

# 研究團隊成員（含交易員）
RESEARCH_TEAM = ["Bull Researcher", "Bear Researcher", "Research Manager", "Trader"]


def build_config(selections):
    """依使用者選擇組出 TradingAgentsXGraph 的設定字典。回傳 (config, notes)。"""
    notes = []  # 給 UI 顯示的系統訊息

    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = selections["research_depth"]
    config["max_risk_discuss_rounds"] = selections["research_depth"]
    config["quick_think_llm"] = selections["shallow_thinker"]
    config["deep_think_llm"] = selections["deep_thinker"]
    config["backend_url"] = selections["backend_url"]
    config["llm_provider"] = selections["llm_provider"].lower()

    # API Keys
    config["quick_think_api_key"] = selections["quick_think_api_key"]
    config["deep_think_api_key"] = selections["deep_think_api_key"]
    config["embedding_api_key"] = selections["embedding_api_key"]
    config["embedding_base_url"] = selections["embedding_url"]

    # 根據市場類型設定資料供應商
    market_type = selections.get("market_type", "us")
    if market_type == "tw":
        notes.append("📊 使用 FinMind API 獲取台股資料")
        config["data_vendors"] = {
            "core_stock_apis": "finmind",
            "technical_indicators": "finmind",
            "fundamental_data": "finmind",
            "news_data": "finmind",
        }
    else:
        notes.append("📊 使用 yfinance / Alpha Vantage 獲取美股資料")
        config["data_vendors"] = {
            "core_stock_apis": "yfinance",
            "technical_indicators": "yfinance",
            "fundamental_data": "alpha_vantage",
            "news_data": "openai",
        }

    return config, notes


def run_analysis(selections, buffer, on_update):
    """
    執行完整的分析流程。

    參數:
        selections (dict): 使用者於設定畫面收集到的所有選項。
        buffer (MessageBuffer): 儲存訊息 / 狀態 / 報告的緩衝區。
        on_update (callable): 每次狀態變動時呼叫，通知 UI 重繪。

    回傳:
        (final_state, decision)
    """
    import os

    config, notes = build_config(selections)
    for note in notes:
        buffer.add_message("系統", note)

    market_type = selections.get("market_type", "us")

    # 設置環境變數（某些工具可能需要）
    os.environ["OPENAI_API_KEY"] = selections["quick_think_api_key"] or ""
    os.environ["ALPHA_VANTAGE_API_KEY"] = selections["alpha_vantage_api_key"] or ""

    if market_type == "tw":
        finmind_key = os.getenv("FINMIND_API_KEY", "")
        if finmind_key:
            os.environ["FINMIND_API_KEY"] = finmind_key
            buffer.add_message("系統", "✓ 已載入 FinMind API Key")
        else:
            buffer.add_message("系統", "⚠ 未找到 FINMIND_API_KEY，部分功能可能受限")

    on_update()

    # 初始化圖
    graph = TradingAgentsXGraph(
        [analyst.value for analyst in selections["analysts"]],
        config=config,
        debug=True,
    )

    # 建立結果目錄
    results_dir = (
        Path(config["results_dir"]) / selections["ticker"] / selections["analysis_date"]
    )
    results_dir.mkdir(parents=True, exist_ok=True)
    report_dir = results_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    log_file = results_dir / "message_tool.log"
    log_file.touch(exist_ok=True)

    # 裝飾器：儲存訊息 / 工具呼叫 / 報告區塊到檔案
    def save_message_decorator(obj, func_name):
        func = getattr(obj, func_name)

        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, message_type, content = obj.messages[-1]
            content = _content_to_str(content).replace("\n", " ")
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [{message_type}] {content}\n")

        return wrapper

    def save_tool_call_decorator(obj, func_name):
        func = getattr(obj, func_name)

        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, tool_name, targs = obj.tool_calls[-1]
            if isinstance(targs, dict):
                args_str = ", ".join(f"{k}={v}" for k, v in targs.items())
            else:
                args_str = str(targs)
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [工具呼叫] {tool_name}({args_str})\n")

        return wrapper

    def save_report_section_decorator(obj, func_name):
        func = getattr(obj, func_name)

        @wraps(func)
        def wrapper(section_name, content):
            func(section_name, content)
            if (
                section_name in obj.report_sections
                and obj.report_sections[section_name] is not None
            ):
                content = obj.report_sections[section_name]
                if content:
                    file_name = f"{section_name}.md"
                    with open(report_dir / file_name, "w") as f:
                        f.write(content)

        return wrapper

    buffer.add_message = save_message_decorator(buffer, "add_message")
    buffer.add_tool_call = save_tool_call_decorator(buffer, "add_tool_call")
    buffer.update_report_section = save_report_section_decorator(
        buffer, "update_report_section"
    )

    def update_research_team_status(status):
        for agent in RESEARCH_TEAM:
            buffer.update_agent_status(agent, status)

    # 初始訊息
    buffer.add_message("系統", f"選擇的股票代碼: {selections['ticker']}")
    buffer.add_message("系統", f"分析日期: {selections['analysis_date']}")
    buffer.add_message(
        "系統",
        f"選擇的分析師: {', '.join(a.value for a in selections['analysts'])}",
    )

    # 重設代理與報告狀態
    for agent in buffer.agent_status:
        buffer.update_agent_status(agent, "pending")
    for section in buffer.report_sections:
        buffer.report_sections[section] = None
    buffer.current_report = None
    buffer.final_report = None

    # 第一個分析師設為進行中
    first_analyst = f"{selections['analysts'][0].value.capitalize()} Analyst"
    buffer.update_agent_status(first_analyst, "in_progress")
    buffer.add_message(
        "系統",
        f"正在分析 {selections['ticker']} 於 {selections['analysis_date']}...",
    )
    on_update()

    # 初始化狀態並取得圖參數
    init_agent_state = graph.propagator.create_initial_state(
        selections["ticker"], selections["analysis_date"]
    )
    args = graph.propagator.get_graph_args()

    # 串流分析
    trace = []
    for chunk in graph.graph.stream(init_agent_state, **args): # type: ignore
        if len(chunk["messages"]) > 0:
            last_message = chunk["messages"][-1]

            if hasattr(last_message, "content"):
                content = _content_to_str(last_message.content)
                msg_type = "推理"
            else:
                content = str(last_message)
                msg_type = "系統"

            buffer.add_message(msg_type, content)

            # 工具呼叫
            if hasattr(last_message, "tool_calls"):
                for tool_call in last_message.tool_calls:
                    if isinstance(tool_call, dict):
                        buffer.add_tool_call(tool_call["name"], tool_call["args"])
                    else:
                        buffer.add_tool_call(tool_call.name, tool_call.args)

            # 分析師團隊報告
            if "market_report" in chunk and chunk["market_report"]:
                buffer.update_report_section("market_report", chunk["market_report"])
                buffer.update_agent_status("Market Analyst", "completed")
                if "social" in selections["analysts"]:
                    buffer.update_agent_status("Social Analyst", "in_progress")

            if "sentiment_report" in chunk and chunk["sentiment_report"]:
                buffer.update_report_section(
                    "sentiment_report", chunk["sentiment_report"]
                )
                buffer.update_agent_status("Social Analyst", "completed")
                if "news" in selections["analysts"]:
                    buffer.update_agent_status("News Analyst", "in_progress")

            if "news_report" in chunk and chunk["news_report"]:
                buffer.update_report_section("news_report", chunk["news_report"])
                buffer.update_agent_status("News Analyst", "completed")
                if "fundamentals" in selections["analysts"]:
                    buffer.update_agent_status("Fundamentals Analyst", "in_progress")

            if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
                buffer.update_report_section(
                    "fundamentals_report", chunk["fundamentals_report"]
                )
                buffer.update_agent_status("Fundamentals Analyst", "completed")
                update_research_team_status("in_progress")

            # 研究團隊 - 投資辯論狀態
            if "investment_debate_state" in chunk and chunk["investment_debate_state"]:
                debate_state = chunk["investment_debate_state"]

                if debate_state.get("bull_history"):
                    update_research_team_status("in_progress")
                    bull_responses = debate_state["bull_history"].split("\n")
                    latest_bull = bull_responses[-1] if bull_responses else ""
                    if latest_bull:
                        buffer.add_message("推理", latest_bull)
                        buffer.update_report_section(
                            "investment_plan",
                            f"### 看漲研究員分析\n{latest_bull}",
                        )

                if debate_state.get("bear_history"):
                    update_research_team_status("in_progress")
                    bear_responses = debate_state["bear_history"].split("\n")
                    latest_bear = bear_responses[-1] if bear_responses else ""
                    if latest_bear:
                        buffer.add_message("推理", latest_bear)
                        buffer.update_report_section(
                            "investment_plan",
                            f"{buffer.report_sections['investment_plan']}\n\n### 看跌研究員分析\n{latest_bear}",
                        )

                if debate_state.get("judge_decision"):
                    update_research_team_status("in_progress")
                    buffer.add_message(
                        "推理", f"研究經理: {debate_state['judge_decision']}"
                    )
                    buffer.update_report_section(
                        "investment_plan",
                        f"{buffer.report_sections['investment_plan']}\n\n### 研究經理決策\n{debate_state['judge_decision']}",
                    )
                    update_research_team_status("completed")
                    buffer.update_agent_status("Risky Analyst", "in_progress")

            # 交易團隊
            if "trader_investment_plan" in chunk and chunk["trader_investment_plan"]:
                buffer.update_report_section(
                    "trader_investment_plan", chunk["trader_investment_plan"]
                )
                buffer.update_agent_status("Risky Analyst", "in_progress")

            # 風險管理團隊 - 風險辯論狀態
            if "risk_debate_state" in chunk and chunk["risk_debate_state"]:
                risk_state = chunk["risk_debate_state"]

                if risk_state.get("current_risky_response"):
                    buffer.update_agent_status("Risky Analyst", "in_progress")
                    buffer.add_message(
                        "推理",
                        f"風險分析師: {risk_state['current_risky_response']}",
                    )
                    buffer.update_report_section(
                        "final_trade_decision",
                        f"### 風險分析師分析\n{risk_state['current_risky_response']}",
                    )

                if risk_state.get("current_safe_response"):
                    buffer.update_agent_status("Safe Analyst", "in_progress")
                    buffer.add_message(
                        "推理",
                        f"安全分析師: {risk_state['current_safe_response']}",
                    )
                    buffer.update_report_section(
                        "final_trade_decision",
                        f"### 安全分析師分析\n{risk_state['current_safe_response']}",
                    )

                if risk_state.get("current_neutral_response"):
                    buffer.update_agent_status("Neutral Analyst", "in_progress")
                    buffer.add_message(
                        "推理",
                        f"中立分析師: {risk_state['current_neutral_response']}",
                    )
                    buffer.update_report_section(
                        "final_trade_decision",
                        f"### 中立分析師分析\n{risk_state['current_neutral_response']}",
                    )

                if risk_state.get("judge_decision"):
                    buffer.update_agent_status("Portfolio Manager", "in_progress")
                    buffer.add_message(
                        "推理",
                        f"投資組合經理: {risk_state['judge_decision']}",
                    )
                    buffer.update_report_section(
                        "final_trade_decision",
                        f"### 投資組合經理決策\n{risk_state['judge_decision']}",
                    )
                    buffer.update_agent_status("Risky Analyst", "completed")
                    buffer.update_agent_status("Safe Analyst", "completed")
                    buffer.update_agent_status("Neutral Analyst", "completed")
                    buffer.update_agent_status("Portfolio Manager", "completed")

            on_update()

        trace.append(chunk)

    # 最終狀態與決策
    final_state = trace[-1]
    decision = graph.process_signal(final_state["final_trade_decision"])

    for agent in buffer.agent_status:
        buffer.update_agent_status(agent, "completed")

    buffer.add_message("分析", f"已完成 {selections['analysis_date']} 的分析")

    for section in buffer.report_sections.keys():
        if section in final_state:
            buffer.update_report_section(section, final_state[section])

    on_update()
    return final_state, decision
