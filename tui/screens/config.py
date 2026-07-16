# -*- coding: utf-8 -*-
"""
設定畫面：以 Textual 原生元件收集執行分析所需的所有選項，
取代原本 CLI 用 questionary 逐步詢問的流程。
"""
import datetime

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Input,
    Label,
    Select,
    Static,
)

from tui import constants


class Section(Vertical):
    """帶標題邊框的區塊卡片。"""

    def __init__(self, title: str, **kwargs):
        super().__init__(**kwargs)
        self.border_title = title
        self.add_class("section")


class Field(Vertical):
    """一組「標籤 + 輸入元件」的欄位包裝。"""

    def __init__(self, label: str, widget, **kwargs):
        super().__init__(**kwargs)
        self.add_class("field")
        self._label = label
        self._widget = widget

    def compose(self) -> ComposeResult:
        yield Label(self._label, classes="field-label")
        yield self._widget


class ConfigScreen(Screen):
    """收集使用者分析設定的表單畫面。"""

    BINDINGS = [
        ("ctrl+r", "start", "開始分析"),
        ("q", "quit", "離開"),
    ]

    def compose(self) -> ComposeResult:
        # 歡迎橫幅（ASCII 藝術）
        with Vertical(id="banner"):
            yield Static(self.app.welcome_ascii, id="welcome-art") # type: ignore
            yield Static(
                "多代理 LLM 金融交易框架   ·   "
                "分析師團隊 → 研究團隊 → 交易員 → 風險管理 → 投資組合管理",
                id="welcome-sub",
            )

        default_models = [
            (disp, val) for disp, val in constants.MODEL_OPTIONS["OpenAI"]
        ]
        default_emb_models = [
            (disp, val) for disp, val in constants.LOCAL_EMBEDDING_MODELS
        ]

        with VerticalScroll(id="config-form"):
            # ── 標的與市場 ──────────────────────────────────
            with Section("標的與市場"):
                with Grid(classes="grid2"):
                    yield Field(
                        "市場",
                        Select(
                            list(constants.MARKET_OPTIONS),
                            value="us",
                            allow_blank=False,
                            id="market",
                        ),
                    )
                    yield Field(
                        "股票代碼",
                        Input(
                            value="SPY",
                            placeholder="SPY / AAPL / 2330",
                            id="ticker",
                        ),
                    )
                yield Field(
                    "分析日期 (YYYY-MM-DD)",
                    Input(
                        value=datetime.datetime.now().strftime("%Y-%m-%d"),
                        placeholder="YYYY-MM-DD",
                        id="date",
                    ),
                )

            # ── 分析範圍 ────────────────────────────────────
            with Section("分析範圍"):
                yield Label("分析師團隊（可複選，至少一位）", classes="field-label")
                with Horizontal(id="analysts-row"):
                    for disp, analyst in constants.ANALYST_ORDER:
                        yield Checkbox(disp, value=True, id=f"analyst-{analyst.value}")
                yield Field(
                    "研究深度",
                    Select(
                        list(constants.DEPTH_OPTIONS),
                        value=1,
                        allow_blank=False,
                        id="depth",
                    ),
                )

            # ── LLM 模型 ────────────────────────────────────
            with Section("LLM 模型"):
                yield Field(
                    "供應商",
                    Select(
                        [(disp, disp) for disp, _ in constants.LLM_PROVIDERS],
                        value="OpenAI",
                        allow_blank=False,
                        id="provider",
                    ),
                )
                with Grid(classes="grid2"):
                    yield Field(
                        "快速思維模型",
                        Select(
                            default_models,
                            value=default_models[0][1],
                            allow_blank=False,
                            id="shallow-model",
                        ),
                    )
                    yield Field(
                        "深度思維模型",
                        Select(
                            default_models,
                            value=default_models[0][1],
                            allow_blank=False,
                            id="deep-model",
                        ),
                    )

            # ── 嵌入模型 ────────────────────────────────────
            with Section("嵌入模型"):
                with Grid(classes="grid2"):
                    yield Field(
                        "供應商",
                        Select(
                            list(constants.EMBEDDING_PROVIDERS),
                            value="local",
                            allow_blank=False,
                            id="embedding-provider",
                        ),
                    )
                    yield Field(
                        "模型",
                        Select(
                            default_emb_models,
                            value=default_emb_models[0][1],
                            allow_blank=False,
                            id="embedding-model",
                        ),
                    )

            # ── API 金鑰 ────────────────────────────────────
            with Section("API 金鑰"):
                yield Static("留空則使用 .env 中的設定", classes="section-hint")
                with Grid(classes="grid2"):
                    yield Field(
                        "快速思維",
                        Input(placeholder="可留空", password=True, id="quick-key"),
                    )
                    yield Field(
                        "深度思維",
                        Input(placeholder="可留空", password=True, id="deep-key"),
                    )
                with Grid(classes="grid2"):
                    yield Field(
                        "嵌入模型",
                        Input(
                            placeholder="本地模型免填",
                            password=True,
                            id="embedding-key",
                        ),
                    )
                    yield Field(
                        "Alpha Vantage",
                        Input(placeholder="可留空", password=True, id="alpha-key"),
                    )

        yield Static("", id="error-msg")
        with Horizontal(id="button-row"):
            yield Button("▶  開始分析", id="start")
            yield Button("離開", id="quit", classes="ghost")

    # ------------------------------------------------------------------
    # 動態更新
    # ------------------------------------------------------------------
    def _refresh_model_options(self, provider: str) -> None:
        options = [(disp, val) for disp, val in constants.MODEL_OPTIONS[provider]]
        for widget_id in ("shallow-model", "deep-model"):
            select = self.query_one(f"#{widget_id}", Select)
            select.set_options(options)
            select.value = options[0][1]

    def _refresh_embedding_models(self, embedding_url: str) -> None:
        options = [
            (disp, val) for disp, val in constants.embedding_models_for(embedding_url)
        ]
        select = self.query_one("#embedding-model", Select)
        select.set_options(options)
        select.value = options[0][1]

    @on(Select.Changed, "#provider")
    def _on_provider_changed(self, event: Select.Changed) -> None:
        if event.value is not Select.BLANK:
            self._refresh_model_options(event.value) # type: ignore

    @on(Select.Changed, "#market")
    def _on_market_changed(self, event: Select.Changed) -> None:
        # 切換市場時更新預設股票代碼（僅在使用者尚未改動時）
        if event.value is Select.BLANK:
            return
        ticker = self.query_one("#ticker", Input)
        if ticker.value in constants.DEFAULT_TICKERS.values() or not ticker.value:
            ticker.value = constants.DEFAULT_TICKERS.get(event.value, "SPY") # type: ignore

    @on(Select.Changed, "#embedding-provider")
    def _on_embedding_provider_changed(self, event: Select.Changed) -> None:
        if event.value is not Select.BLANK:
            self._refresh_embedding_models(event.value) # type: ignore

    # ------------------------------------------------------------------
    # 送出
    # ------------------------------------------------------------------
    @on(Button.Pressed, "#quit")
    def action_quit(self) -> None:
        self.app.exit()

    @on(Button.Pressed, "#start")
    def action_start(self) -> None:
        selections = self._collect()
        if selections is not None:
            self.app.start_analysis(selections) # type: ignore

    def _error(self, message: str) -> None:
        self.query_one("#error-msg", Static).update(
            f"[b #F26D6D]✗  {message}[/b #F26D6D]"
        )

    def _collect(self):
        """驗證並收集所有選項，回傳 selections 字典；失敗時回傳 None。"""
        import os

        # 市場
        market_type = self.query_one("#market", Select).value

        # 股票代碼
        ticker = self.query_one("#ticker", Input).value.strip().upper()
        if not ticker:
            self._error("請輸入股票代碼")
            return None

        # 日期
        date_str = self.query_one("#date", Input).value.strip()
        try:
            analysis_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            if analysis_date.date() > datetime.datetime.now().date():
                self._error("分析日期不能是未來日期")
                return None
        except ValueError:
            self._error("日期格式無效，請使用 YYYY-MM-DD")
            return None

        # 分析師
        analysts = []
        for disp, analyst in constants.ANALYST_ORDER:
            if self.query_one(f"#analyst-{analyst.value}", Checkbox).value:
                analysts.append(analyst)
        if not analysts:
            self._error("至少需選擇一位分析師")
            return None

        # 研究深度
        research_depth = self.query_one("#depth", Select).value

        # LLM 供應商 → backend_url
        provider_name = self.query_one("#provider", Select).value
        backend_url = dict(constants.LLM_PROVIDERS)[provider_name] # type: ignore

        # 思維模型
        shallow_thinker = self.query_one("#shallow-model", Select).value
        deep_thinker = self.query_one("#deep-model", Select).value

        # 嵌入
        embedding_url = self.query_one("#embedding-provider", Select).value
        embedding_model = self.query_one("#embedding-model", Select).value
        is_local_embedding = embedding_url == "local"

        # API Keys（留空則回退到 .env）
        quick_key = self.query_one("#quick-key", Input).value.strip()
        deep_key = self.query_one("#deep-key", Input).value.strip()
        embedding_key_input = self.query_one("#embedding-key", Input).value.strip()
        alpha_key_input = self.query_one("#alpha-key", Input).value.strip()

        quick_think_api_key = quick_key or constants.env_api_key_for_model(shallow_thinker) # type: ignore
        deep_think_api_key = deep_key or constants.env_api_key_for_model(deep_thinker) # type: ignore

        if not quick_think_api_key:
            self._error("缺少快速思維模型的 API Key（輸入框或 .env 皆為空）")
            return None
        if not deep_think_api_key:
            self._error("缺少深度思維模型的 API Key（輸入框或 .env 皆為空）")
            return None

        if is_local_embedding:
            embedding_api_key = None
        else:
            embedding_api_key = embedding_key_input or constants.env_api_key_for_provider(
                "openai"
            )
            if not embedding_api_key:
                self._error("缺少嵌入模型的 API Key（輸入框或 .env 皆為空）")
                return None

        alpha_vantage_api_key = alpha_key_input or os.getenv("ALPHA_VANTAGE_API_KEY")
        if not alpha_vantage_api_key:
            self._error("缺少 Alpha Vantage API Key（輸入框或 .env 皆為空）")
            return None

        return {
            "ticker": ticker,
            "analysis_date": date_str,
            "analysts": analysts,
            "research_depth": research_depth,
            "llm_provider": provider_name.lower(), # type: ignore
            "backend_url": backend_url,
            "shallow_thinker": shallow_thinker,
            "deep_thinker": deep_thinker,
            "market_type": market_type,
            "embedding_provider": embedding_url,
            "embedding_url": embedding_url,
            "embedding_model": embedding_model,
            "quick_think_api_key": quick_think_api_key,
            "deep_think_api_key": deep_think_api_key,
            "embedding_api_key": embedding_api_key,
            "alpha_vantage_api_key": alpha_vantage_api_key,
        }
