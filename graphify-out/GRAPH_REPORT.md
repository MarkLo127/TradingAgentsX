# Graph Report - .  (2026-07-15)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1363 nodes · 2988 edges · 97 communities (79 shown, 18 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 66 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `77af4953`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- finmind.py
- PDFGenerator
- _make_api_request
- TradingService
- user.py
- HybridTaskManager
- page.tsx
- fix_common_llm_errors
- prompts.py
- YFinanceUtils
- page.tsx
- routes.py
- PendingTaskRecovery.tsx
- main.py
- types.ts
- interface.py
- schemas.py
- redis_client.py
- page.tsx
- agent_utils.py
- verify_access_token
- auth-context.tsx
- storage.ts
- auth.py
- dropdown-menu.tsx
- trading_graph.py
- Reflector
- __init__.py
- page.tsx
- AnalysisForm.tsx
- cn
- y_finance.py
- layout.tsx
- ApiSettingsDialog.tsx
- LanguageContext.tsx
- AgentState
- FinancialSituationMemory
- get_config
- TickerCombobox.tsx
- button.tsx
- TradingAgentsXGraph
- HybridSearchEngine
- .__init__
- DashboardScreen
- ConfigScreen
- constants.py
- sync-retry.ts
- make_cached_system_message
- __init__.py
- run_analysis
- MessageBuffer
- useLanguage
- HybridFinancialMemory
- TradingAgentsXApp
- .setup_graph
- google.py
- config.py
- ScrollReveal.tsx
- tokenize_financial_text
- chat_with_reports
- .search
- retry
- __main__.py
- getBackendUrl
- ImmersivePortalHero.tsx
- report_summarizer.py
- GraphSetup
- run_analysis
- Settings
- HealthResponse
- route.ts
- SoftAurora.jsx
- next.config.ts
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- clean_cache.sh
- eslint.config.mjs
- postcss.config.mjs
- css.d.ts
- DELETE
- GET
- PATCH
- POST
- PUT
- tradingagents

## God Nodes (most connected - your core abstractions)
1. `cn()` - 76 edges
2. `useLanguage()` - 41 edges
3. `_make_api_request()` - 37 edges
4. `PDFGenerator` - 28 edges
5. `normalize_stock_id()` - 26 edges
6. `isCloudSyncEnabled()` - 25 edges
7. `TradingAgentsXGraph` - 24 edges
8. `get_language_closing_instruction()` - 22 edges
9. `HistoryPage()` - 21 edges
10. `format_date()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `HybridSearchEngine` --uses--> `Settings`  [INFERRED]
  tradingagents/agents/utils/hybrid_search.py → backend/app/core/config.py
- `FinancialSituationMemory` --uses--> `Settings`  [INFERRED]
  tradingagents/agents/utils/memory.py → backend/app/core/config.py
- `HybridFinancialMemory` --uses--> `Settings`  [INFERRED]
  tradingagents/agents/utils/memory.py → backend/app/core/config.py
- `TradingService` --uses--> `TradingAgentsXGraph`  [INFERRED]
  backend/app/services/trading_service.py → tradingagents/graph/trading_graph.py
- `run_analysis()` --calls--> `TradingAgentsXGraph`  [EXTRACTED]
  tui/analysis.py → tradingagents/graph/trading_graph.py

## Import Cycles
- 1-file cycle: `tradingagents/dataflows/openai.py -> tradingagents/dataflows/openai.py`

## Communities (97 total, 18 thin omitted)

### Community 0 - "finmind.py"
Cohesion: 0.06
Nodes (86): datetime, Series, _convert_to_serializable(), _filter_by_date_range(), FinMindAuthenticationError, FinMindDataNotFoundError, FinMindError, FinMindRateLimitError (+78 more)

### Community 1 - "PDFGenerator"
Cohesion: 0.07
Nodes (32): DownloadService, Download Service for Analyst Reports Generates combined PDF reports with all ana, Service for handling analyst report downloads, Initialize download service, Create a single combined PDF containing all analyst reports                  Fea, get_model_display_name(), get_pdf_label(), PDFGenerator (+24 more)

### Community 2 - "_make_api_request"
Cohesion: 0.10
Nodes (33): AlphaVantageRateLimitError, _filter_csv_by_date_range(), format_datetime_for_api(), get_api_key(), _make_api_request(), Exception, 從環境變數中檢索 Alpha Vantage 的 API 金鑰。, 將各種日期格式轉換為 Alpha Vantage API 所需的 YYYYMMDDTHHMM 格式。 (+25 more)

### Community 3 - "TradingService"
Cohesion: 0.09
Nodes (21): get_trading_service(), Dependency to get trading service instance, PriceService, Any, DataFrame, Price data service for loading and processing stock price data, Service for loading and processing price data from data_cache, Load price data from data_cache CSV files                  Args:             tic (+13 more)

### Community 4 - "user.py"
Cohesion: 0.12
Nodes (32): cleanup_duplicate_reports(), create_report(), delete_all_reports(), delete_report(), get_current_user_optional(), get_current_user_required(), get_report(), get_report_counts() (+24 more)

### Community 5 - "HybridTaskManager"
Cohesion: 0.10
Nodes (19): is_redis_available(), Check if Redis is available and connected., HybridTaskManager, Any, Get task from in-memory first, then Redis, Create a new task with initial data                  Args:             initial_d, Update task status and optional progress message                  Args:, Update task progress message                  Args:             task_id: Task ID (+11 more)

### Community 6 - "page.tsx"
Cohesion: 0.15
Nodes (24): AnalysisResultsPage(), ANALYST_KEYS, getNestedValue(), AnalystReportProps, extractLastRound(), ReportSection(), calculateHeikinAshi(), HeikinAshiCandlestickShapeProps (+16 more)

### Community 7 - "fix_common_llm_errors"
Cohesion: 0.11
Nodes (28): create_risk_manager(), 建立一個風險管理員（裁判）節點。      Args:         llm: 用於生成決策的語言模型。         memory: 儲存過去情況和反思的, create_bull_researcher(), 建立一個看漲研究員節點。      Args:         llm: 用於生成回應的語言模型。         memory: 儲存過去情況和反思的記憶體物, create_safe_debator(), 建立一個保守的風險辯論員節點。      Args:         llm: 用於生成回應的語言模型。         language: 報告語言 ('en, count_chinese_words(), ensure_min_length() (+20 more)

### Community 8 - "prompts.py"
Cohesion: 0.14
Nodes (25): create_fundamentals_analyst(), 建立一個基本面分析師節點。      Args:         llm: 用於分析的語言模型。         language: 報告語言 ('en' 或, create_market_analyst(), 建立一個市場分析師節點。      Args:         llm: 用於分析的語言模型。         language: 報告語言 ('en' 或 ', create_news_analyst(), 建立一個新聞分析師節點。      Args:         llm: 用於分析的語言模型。         language: 報告語言 ('en' 或 ', create_social_media_analyst(), 建立一個社群媒體分析師節點。      Args:         llm: 用於分析的語言模型。         language: 報告語言 ('en' 或 (+17 more)

### Community 9 - "YFinanceUtils"
Cohesion: 0.09
Nodes (20): decorate_all_methods(), get_current_date(), get_next_weekday(), DataFrame, SavePathType, 將 DataFrame 儲存到 CSV 檔案。      Args:         data (pl.DataFrame): 要儲存的 DataFrame。, 以 YYYY-MM-DD 格式獲取當前日期。      Returns:         str: 當前日期字串。, 一個裝飾器，用於將另一個裝飾器應用於一個類別的所有方法。      Args:         decorator: 要應用的裝飾器。      Returns (+12 more)

### Community 10 - "page.tsx"
Cohesion: 0.12
Nodes (19): ANALYSTS, detectReportLanguage(), extractDecisionFromReport(), getMarketLabels(), getReportSignature(), HistoryPage(), parseUTCDate(), IMPORTANT: Delete from BOTH cloud AND local to prevent re-sync issues (+11 more)

### Community 11 - "routes.py"
Cohesion: 0.10
Nodes (24): cleanup_task(), delete_pdf_temp(), download_reports(), generate_pdf_temp(), get_config(), get_task_status(), get_tickers(), API route definitions for TradingAgentsX Backend (+16 more)

### Community 12 - "PendingTaskRecovery.tsx"
Cohesion: 0.14
Nodes (17): AnalysisPage(), AuthCallbackContent(), AnalysisFormProps, LoginPrompt(), PendingTaskRecovery(), ErrorAlert(), ErrorAlertProps, useAnalysisContext() (+9 more)

### Community 13 - "main.py"
Cohesion: 0.10
Nodes (18): Config, Configuration management for TradingAgentsX Backend API, Configure CORS middleware for the FastAPI application, setup_cors(), global_exception_handler(), Exception, RateLimitMiddleware, FastAPI application entry point for TradingAgentsX Backend (+10 more)

### Community 14 - "types.ts"
Cohesion: 0.13
Nodes (18): ChatMessage, ReportChatProps, TradingDecisionProps, AnalysisContext, AnalysisContextType, api, apiClient, SavedReport (+10 more)

### Community 15 - "interface.py"
Cohesion: 0.14
Nodes (21): get_category_for_method(), get_data_in_range(), get_finnhub_company_insider_sentiment(), get_finnhub_company_insider_transactions(), get_finnhub_news(), get_reddit_company_news(), get_reddit_global_news(), get_simfin_balance_sheet() (+13 more)

### Community 16 - "schemas.py"
Cohesion: 0.13
Nodes (21): chat_with_report(), Chat with the analysis report using the user's LLM.          Sends the analysis, AnalysisRequest, AnalysisResponse, AnalystReport, ChatRequest, ChatResponse, ErrorResponse (+13 more)

### Community 17 - "redis_client.py"
Cohesion: 0.14
Nodes (21): cache_delete(), cache_get(), cache_set(), check_rate_limit(), delete_task_from_redis(), get_redis_client(), get_task_from_redis(), Any (+13 more)

### Community 18 - "page.tsx"
Cohesion: 0.13
Nodes (18): AVAILABLE_MODELS, ChatMessage, HistoryChatContent(), AnalysisForm(), ReportChat(), Select(), SelectContent(), SelectItem() (+10 more)

### Community 19 - "agent_utils.py"
Cohesion: 0.19
Nodes (18): get_stock_data(), 檢索給定股票代碼的股價數據 (OHLCV)。     使用設定的核心股票 API 供應商。     Args:         symbol (str): 公司, get_balance_sheet(), get_cashflow(), get_fundamentals(), get_income_statement(), 檢索給定股票代碼的綜合基本面數據。     使用設定的基本面數據供應商。     Args:         ticker (str): 公司的股票代碼, get_global_news() (+10 more)

### Community 20 - "verify_access_token"
Cohesion: 0.11
Nodes (20): get_current_user_optional(), get_current_user_required(), Any, Shared dependencies for API routes, Get current user from JWT token (optional - returns None if not authenticated), Get current user from JWT token (required - raises 401 if not authenticated), SSE stream for real-time cross-device sync.     Token is passed as a query param, user_events() (+12 more)

### Community 21 - "auth-context.tsx"
Cohesion: 0.21
Nodes (20): ApiSettingsDialog(), AuthContext, AuthContextType, AuthProvider(), getAuthHeaders(), getAuthToken(), User, bulkSaveReports() (+12 more)

### Community 22 - "storage.ts"
Cohesion: 0.21
Nodes (20): clearCryptoData(), decrypt(), decryptObject(), deriveKey(), encrypt(), encryptObject(), generateSalt(), getBrowserFingerprint() (+12 more)

### Community 23 - "auth.py"
Cohesion: 0.17
Nodes (19): exchange_google_token(), get_current_user(), get_frontend_url(), get_google_client_id(), get_google_client_secret(), google_callback(), google_login(), AsyncSession (+11 more)

### Community 24 - "dropdown-menu.tsx"
Cohesion: 0.17
Nodes (11): DropdownMenu(), DropdownMenuCheckboxItem(), DropdownMenuContent(), DropdownMenuItem(), DropdownMenuLabel(), DropdownMenuRadioItem(), DropdownMenuSeparator(), DropdownMenuShortcut() (+3 more)

### Community 25 - "trading_graph.py"
Cohesion: 0.21
Nodes (9): InvestDebateState, RiskDebateState, Propagator, Any, 獲取圖呼叫的參數。         這些參數控制著圖的執行方式，例如串流模式和遞迴限制。          Returns:             Dict[, 處理狀態在圖中的初始化和傳播。     這個類別負責建立圖執行的初始狀態，並提供圖呼叫所需的參數。, 使用設定參數進行初始化。          Args:             max_recur_limit (int): 圖的最大遞迴深度限制，以防止無限循, 為代理圖建立初始狀態。         這個狀態字典包含了執行開始時所需的所有資訊。          Args:             company_na (+1 more)

### Community 26 - "Reflector"
Cohesion: 0.17
Nodes (11): Any, ChatOpenAI, 反思看漲研究員的分析並更新其記憶。          Args:             current_state: 當前的圖狀態。, 反思交易員的決策並更新其記憶。          Args:             current_state: 當前的圖狀態。             re, 使用一個 LLM 初始化反思器。          Args:             quick_thinking_llm (ChatOpenAI): 用於生, 反思風險管理者的決策並更新其記憶。          Args:             current_state: 當前的圖狀態。, 獲取用於反思的系統提示。         這個提示指導 LLM 如何分析交易決策、提出改進建議並總結經驗教訓。, 從狀態中提取當前的市場情況。         這會整合來自不同分析師的報告，為反思提供全面的市場背景。          Args:             c (+3 more)

### Community 27 - "__init__.py"
Cohesion: 0.16
Nodes (16): Base, check_db_connection(), get_db(), init_db(), Database configuration and connection management, Check if database connection is working, Base class for all database models, Dependency for getting database sessions (+8 more)

### Community 28 - "page.tsx"
Cohesion: 0.12
Nodes (3): HomePage(), AgentFlowDiagram(), InteractiveCard()

### Community 29 - "AnalysisForm.tsx"
Cohesion: 0.19
Nodes (14): formSchema, Checkbox(), FormControl(), FormDescription(), FormField(), FormFieldContext, FormFieldContextValue, FormItem() (+6 more)

### Community 30 - "cn"
Cohesion: 0.19
Nodes (14): LoadingSpinner(), LoadingSpinnerProps, Badge(), badgeVariants, Spinner(), Table(), TableBody(), TableCaption() (+6 more)

### Community 31 - "y_finance.py"
Cohesion: 0.16
Nodes (16): get_balance_sheet(), get_cashflow(), get_fundamentals(), get_income_statement(), get_insider_transactions(), _get_stock_stats_bulk(), get_stock_stats_indicators_window(), get_stockstats_indicator() (+8 more)

### Community 32 - "layout.tsx"
Cohesion: 0.15
Nodes (10): inter, metadata, CustomCursor(), Footer(), SoftAurora, SoftAuroraBackground(), SplashCursor, SplashCursorBackground() (+2 more)

### Community 33 - "ApiSettingsDialog.tsx"
Cohesion: 0.17
Nodes (12): formSchema, FormValues, Dialog(), DialogContent(), DialogDescription(), DialogFooter(), DialogHeader(), DialogOverlay() (+4 more)

### Community 34 - "LanguageContext.tsx"
Cohesion: 0.20
Nodes (13): getServerSnapshot(), getStoredLocale(), LanguageContext, LanguageContextType, LanguageProvider(), subscribeToStorage(), useTranslation(), en (+5 more)

### Community 35 - "AgentState"
Cohesion: 0.17
Nodes (10): MessagesState, AgentState, ConditionalLogic, 判斷風險分析是否應該繼續。         如果討論回合數達到上限，則由風險裁判做出最終決定。         否則，在激進、保守和中立分析師之間輪流進行。, 使用設定參數進行初始化。          Args:             max_debate_rounds (int): 投資辯論的最大回合數。, 判斷市場分析是否應該繼續。         如果最後一條訊息包含工具呼叫，則表示代理需要使用工具，         流程應該轉到市場工具節點。否則，分析完成。, 判斷社群媒體分析是否應該繼續。         邏輯與 `should_continue_market` 類似。          Args:, 判斷新聞分析是否應該繼續。         邏輯與 `should_continue_market` 類似。          Args: (+2 more)

### Community 36 - "FinancialSituationMemory"
Cohesion: 0.16
Nodes (9): FinancialSituationMemory, Get embedding using local sentence-transformers model., Get embedding using OpenAI API., Add financial situations and their corresponding advice. Parameter is a list of, Find matching recommendations using embeddings, Initialize the memory with configurable embedding provider.                  Con, Initialize local embedding using sentence-transformers., Initialize OpenAI embedding client. (+1 more)

### Community 37 - "get_config"
Cohesion: 0.18
Nodes (13): get_config(), initialize_config(), get_vendor(), 獲取數據類別或特定工具方法的已設定供應商。     工具級別的設定優先於類別級別。, get_fundamentals_openai(), get_global_news_openai(), get_stock_news_openai(), 使用 OpenAI 模型搜索公司的基本面數據。      Args:         ticker (str): 股票代碼。         curr_date (+5 more)

### Community 38 - "TickerCombobox.tsx"
Cohesion: 0.25
Nodes (14): TickerCombobox(), TickerComboboxProps, displayName(), loadStocks(), loadTw(), loadUs(), lookupStockName(), MarketType (+6 more)

### Community 39 - "button.tsx"
Cohesion: 0.27
Nodes (9): Button(), buttonVariants, Calendar(), CalendarDayButton(), DatePicker(), DatePickerProps, Popover(), PopoverContent() (+1 more)

### Community 40 - "TradingAgentsXGraph"
Cohesion: 0.19
Nodes (6): TradingAgentsX service integration, 在特定日期為某家公司執行交易代理圖。          Args:             company_name (str): 公司名稱或股票代碼。, 根據回報反思決策並更新記憶。         這個方法會觸發對每個相關代理的決策進行反思的過程。, 處理信號以提取核心決策。         將原始的 LLM 輸出轉換為標準化的交易信號（例如，BUY, SELL, HOLD）。, 協調交易代理框架的主要類別。     這個類別整合了所有組件，包括 LLM、記憶體、工具和圖的邏輯，     以執行一個完整的金融分析和交易決策流程。, TradingAgentsXGraph

### Community 41 - "HybridSearchEngine"
Cohesion: 0.21
Nodes (6): HybridSearchEngine, 取得文字的嵌入向量（自動截斷至 4000 字元）。, 從目前語料庫重建 BM25Okapi 索引。, 將文件加入混合搜索索引。          Args:             documents : 文件字串列表             metadatas, 向量語意搜索（ChromaDB）。         回傳 [(文件ID, 相似度分數), ...] 依分數降序排列。, 混合搜索引擎：結合 BM25 關鍵字搜索與向量語意搜索。      工作流程：     1. add_documents() — 同時建立 BM25 倒排索引和

### Community 42 - ".__init__"
Cohesion: 0.14
Nodes (10): set_config(), ChatOpenAI, 使用一個 LLM 進行初始化以進行處理。          Args:             quick_thinking_llm (ChatOpenAI):, 處理完整的交易信號以提取核心決策。          Args:             full_signal (str): 完整的交易信號文本。, 處理交易信號以提取可執行的決策。     這個類別的目的是將來自代理的自然語言格式的完整交易信號，     轉換為標準化的、機器可讀的決策（例如 "BUY",, SignalProcessor, Any, ToolNode (+2 more)

### Community 43 - "DashboardScreen"
Cohesion: 0.24
Nodes (3): DashboardScreen, ComposeResult, Screen

### Community 44 - "ConfigScreen"
Cohesion: 0.23
Nodes (4): Changed, ConfigScreen, Screen, 驗證並收集所有選項，回傳 selections 字典；失敗時回傳 None。

### Community 45 - "constants.py"
Cohesion: 0.21
Nodes (11): Enum, str, embedding_models_for(), env_api_key_for_model(), env_api_key_for_provider(), infer_provider_from_model(), 根據嵌入供應商的 URL 回傳對應的模型清單。, 根據供應商名稱從環境變數讀取對應的 API Key（找不到回傳 None）。 (+3 more)

### Community 46 - "sync-retry.ts"
Cohesion: 0.27
Nodes (10): SyncInitializer(), getAllReports(), getReportKey(), markForRetry(), retryMap, retryPendingSyncs(), RetryRecord, retrySingleReport() (+2 more)

### Community 47 - "make_cached_system_message"
Cohesion: 0.21
Nodes (11): SystemMessage, create_bear_researcher(), 建立一個看跌研究員節點。      Args:         llm: 用於生成回應的語言模型。         memory: 儲存過去情況和反思的記憶體物, create_risky_debator(), 建立一個激進的風險辯論員節點。      Args:         llm: 用於生成回應的語言模型。         language: 報告語言 ('en, make_cached_system_message(), 建立 SystemMessage，若使用 Claude 則自動加上 cache_control 啟用 Prompt Caching。      - Claude, get_aggressive_debator_prompt() (+3 more)

### Community 48 - "__init__.py"
Cohesion: 0.27
Nodes (10): create_research_manager(), 建立一個研究管理員（裁判）節點。      Args:         llm: 用於生成決策和計畫的語言模型。         memory: 儲存過去情況和, create_trader(), 建立一個交易員節點。      Args:         llm: 用於生成決策的語言模型。         memory: 儲存過去情況和反思的記憶體物件。, get_language_closing_instruction(), get_research_manager_prompt(), get_trader_prompt(), Get the language closing instruction placed at the END of agent prompts for maxi (+2 more)

### Community 49 - "run_analysis"
Cohesion: 0.17
Nodes (9): build_config(), 依使用者選擇組出 TradingAgentsXGraph 的設定字典。回傳 (config, notes)。, 執行完整的分析流程。      參數:         selections (dict): 使用者於設定畫面收集到的所有選項。         buffer, run_analysis(), _content_to_str(), 合併工具呼叫與一般訊息，依時間排序後回傳最近 N 筆。, 將訊息內容（可能是 Anthropic 的區塊列表）轉換為純字串。, _decision_badge() (+1 more)

### Community 50 - "MessageBuffer"
Cohesion: 0.20
Nodes (3): MessageBuffer, 回傳 (工具呼叫數, LLM 呼叫數, 已生成報告數)。, 用於儲存和管理應用程式訊息、工具呼叫和報告狀態的緩衝區。

### Community 51 - "useLanguage"
Cohesion: 0.27
Nodes (9): AnalystReport(), AnalystInfo, DownloadReports(), DownloadReportsProps, LoginButton(), Header(), LanguageSwitcher(), ThemeToggle() (+1 more)

### Community 52 - "HybridFinancialMemory"
Cohesion: 0.25
Nodes (5): HybridFinancialMemory, Any, 混合搜索金融記憶體 (Hybrid Financial Memory)      在 FinancialSituationMemory 的向量搜索基礎上，, 新增金融情境與建議，同時建立 BM25 索引和向量索引。         Parameter: list of (situation, recommendati, 混合搜索：BM25 + 向量搜索，透過 RRF 融合後回傳最相關的過去情境。          Args:             current_situat

### Community 53 - "TradingAgentsXApp"
Cohesion: 0.24
Nodes (6): App, main(), _prewarm_multiprocessing(), 在 Textual 接管終端機之前，先啟動 multiprocessing 的 resource_tracker。      背景說明：         分析過, TradingAgentsX 的 Textual 應用程式。, TradingAgentsXApp

### Community 54 - ".setup_graph"
Cohesion: 0.25
Nodes (7): create_neutral_debator(), 建立一個中立的風險辯論員節點。      Args:         llm: 用於生成回應的語言模型。         language: 報告語言 ('en, create_msg_delete(), 建立一個刪除訊息的函式。      Returns:         一個在 langgraph 中用於清除訊息的函式。, get_neutral_debator_prompt(), Get neutral risk debator prompt., 設定並編譯代理工作流程圖。          Args:             selected_analysts (list): 要包含的分析師類型列表。選

### Community 55 - "google.py"
Cohesion: 0.31
Nodes (7): get_google_news(), 使用 Google News 檢索新聞文章。      Args:         query (str): 用於搜索的查詢。         curr_dat, getNewsData(), is_rate_limited(), make_request(), 檢查回應是否表示速率限制 (狀態碼 429), 抓取給定查詢和日期範圍的 Google 新聞搜索結果。     query: str - 搜索查詢     start_date: str - 開始日期，格式為

### Community 56 - "config.py"
Cohesion: 0.36
Nodes (4): Field, ComposeResult, Section, Vertical

### Community 57 - "ScrollReveal.tsx"
Cohesion: 0.46
Nodes (7): apply(), clamp(), easeOut(), items, onScroll(), ScrollReveal(), tick()

### Community 58 - "tokenize_financial_text"
Cohesion: 0.32
Nodes (5): extract_tickers(), 混合搜索引擎 (Hybrid Search Engine)  結合兩種互補的搜索策略： - BM25 關鍵字搜索 (Keyword Search)：精確匹配股票, BM25 關鍵字搜索，含股票代號精確匹配加分。         回傳 [(文件索引, 分數), ...] 依分數降序排列。, 將財務文字分詞，保留股票代號和財務術語的原始大小寫。     其他詞彙統一轉為小寫以提升 BM25 召回率。, tokenize_financial_text()

### Community 59 - "chat_with_reports"
Cohesion: 0.38
Nodes (6): chat_with_reports(), _flatten_reports(), Any, Chat service for answering questions about analysis reports Uses the user's LLM, Send a chat message about analysis reports to the LLM.          Args:         me, Flatten all reports into a single text block for context.

### Community 60 - ".search"
Cohesion: 0.29
Nodes (4): Any, 倒數排名融合 (RRF)：合併 BM25 與向量搜索的排名。          RRF 分數 = Σ weight_i / (k + rank_i), 混合搜索：BM25 關鍵字 + 向量語意，透過 RRF 融合排名。          Args:             query     : 查詢字串（可包, 搜索並回傳格式化字串，供 LLM Agent 直接使用。         每條結果顯示 BM25 分數、向量分數、混合分數及文件摘要。

### Community 61 - "retry"
Cohesion: 0.33
Nodes (6): log_retry_attempt(), Exception, 重試工具模組，提供統一的重試機制和錯誤處理, 重試裝飾器，支援指數退避          Args:         max_attempts: 最大重試次數（包含首次嘗試）         backoff, 記錄重試嘗試的標準回調函數          Args:         attempt: 當前嘗試次數         exception: 遇到的例外, retry()

### Community 62 - "__main__.py"
Cohesion: 0.40
Nodes (5): main(), parse_args(), Backend module entry point Run with: python -m backend Options:   --reload / --r, Parse command line arguments, Start the FastAPI server

### Community 63 - "getBackendUrl"
Cohesion: 0.60
Nodes (3): POST(), proxyRequest(), getBackendUrl()

### Community 64 - "ImmersivePortalHero.tsx"
Cohesion: 0.40
Nodes (4): HeroTradingCanvas(), Node, NODE_COLORS, ImmersivePortalHero()

### Community 65 - "report_summarizer.py"
Cohesion: 0.40
Nodes (5): create_report_summarizer(), Report Summarizer — 將 4 份分析師報告壓縮成 ~600 字的單一結構化摘要。  用途：在 Bull/Bear 研究員和風險辯論員收到報告之, 建立 Report Summarizer 節點。      Args:         llm: quick_thinking_llm（使用者設定的輕量模型）, get_report_summarizer_prompt(), Get the report summarizer system prompt.

### Community 66 - "GraphSetup"
Cohesion: 0.33
Nodes (5): GraphSetup, ChatOpenAI, ToolNode, 處理代理圖的設定和組態。     這個類別負責根據所選的分析師和設定來建立和連接圖中的所有節點。, 使用必要的組件進行初始化。          Args:             quick_thinking_llm (ChatOpenAI): 用於快速任務

### Community 67 - "run_analysis"
Cohesion: 0.40
Nodes (5): AnalysisRequest, Start an async trading analysis task.          This endpoint creates an async ta, run_analysis(), Response when a task is created, TaskCreatedResponse

### Community 68 - "Settings"
Cohesion: 0.40
Nodes (4): Application settings loaded from environment variables, Get CORS origins from environment or use defaults, Settings, BaseSettings

### Community 69 - "HealthResponse"
Cohesion: 0.50
Nodes (4): health_check(), Health check endpoint, HealthResponse, Response model for health check

## Knowledge Gaps
- **53 isolated node(s):** `Config`, `clean_cache.sh script`, `ChatMessage`, `ANALYSTS`, `inter` (+48 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HybridTaskManager` connect `HybridTaskManager` to `redis_client.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `MessageBuffer` connect `MessageBuffer` to `run_analysis`, `DashboardScreen`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **What connects `Config`, `clean_cache.sh script`, `ChatMessage` to the rest of the system?**
  _53 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `finmind.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06358111266947171 - nodes in this community are weakly interconnected._
- **Should `PDFGenerator` be split into smaller, more focused modules?**
  _Cohesion score 0.06557377049180328 - nodes in this community are weakly interconnected._
- **Should `_make_api_request` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `TradingService` be split into smaller, more focused modules?**
  _Cohesion score 0.08712121212121213 - nodes in this community are weakly interconnected._