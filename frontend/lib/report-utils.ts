/**
 * Shared utilities for report deduplication, language detection, and date parsing.
 * Single source of truth — imported by history/page.tsx, analysis/page.tsx, results/page.tsx, etc.
 */

/**
 * Normalize report language. All null/undefined values become "zh-TW"
 * to match backend behavior (COALESCE(language, 'zh-TW')).
 */
export function normalizeLanguage(
  language?: string | null
): "en" | "zh-TW" {
  if (language === "en") return "en";
  return "zh-TW";
}

/**
 * Detect report language from content (for backward compatibility with old reports
 * that don't have a language field stored).
 * Checks trader_investment_plan for Chinese/English keywords.
 */
export function detectReportLanguage(reports: any): "en" | "zh-TW" {
  const traderPlan = reports?.trader_investment_plan;
  if (!traderPlan || typeof traderPlan !== "string") {
    // If no trader plan, check other reports for Chinese characters
    const allText = JSON.stringify(reports || {});
    const chineseRegex = /[\u4e00-\u9fa5]/;
    return chineseRegex.test(allText) ? "zh-TW" : "en";
  }

  // Check for Chinese decision keywords
  const chineseKeywords = ["買入", "賣出", "持有", "最終交易提案"];
  for (const keyword of chineseKeywords) {
    if (traderPlan.includes(keyword)) {
      return "zh-TW";
    }
  }

  // Check for English decision keywords
  const englishKeywords = ["buy", "sell", "hold", "final trading proposal"];
  const lowerPlan = traderPlan.toLowerCase();
  for (const keyword of englishKeywords) {
    if (lowerPlan.includes(keyword)) {
      return "en";
    }
  }

  // Fallback: check for Chinese characters in the content
  const chineseRegex = /[\u4e00-\u9fa5]/;
  return chineseRegex.test(traderPlan) ? "zh-TW" : "en";
}

/**
 * Generate a unique signature for report deduplication.
 * Uses stable key fields: ticker + date + market_type + language.
 * Language is normalized to "zh-TW" when null/undefined to match backend behavior.
 */
export function getReportSignature(report: {
  ticker: string;
  analysis_date: string;
  market_type?: string;
  language?: string | null;
  result?: { deep_think_llm?: string; quick_think_llm?: string } | null;
}): string {
  const lang = normalizeLanguage(report.language);
  const deep = report.result?.deep_think_llm || "";
  const quick = report.result?.quick_think_llm || "";
  const modelSuffix = (deep || quick) ? `_${deep}_${quick}` : "";
  return `${report.ticker}_${report.analysis_date}_${report.market_type || "us"}_${lang}${modelSuffix}`;
}

// Model ID → human-readable display name mapping (mirrors pdf_generator.py)
const MODEL_DISPLAY_NAMES: Record<string, string> = {
  // Anthropic Claude
  "claude-fable-5": "Claude Fable 5",
  "claude-opus-5": "Claude Opus 5",
  "claude-sonnet-5": "Claude Sonnet 5",
  "claude-haiku-4-5-20251001": "Claude Haiku 4.5",

  // Google Gemini
  "gemini-3.6-flash": "Gemini 3.6 Flash",
  "gemini-3.5-flash": "Gemini 3.5 Flash",
  "gemini-3.5-flash-lite": "Gemini 3.5 Flash-Lite",
  
  // OpenAI
  "gpt-5.6-sol": "GPT-5.6 Sol",
  "gpt-5.6-terra": "GPT-5.6 Terra",
  "gpt-5.6-luna": "GPT-5.6 Luna",

  // Grok
  "grok-4.5": "Grok 4.5",
  "grok-4.3": "Grok 4.3",
  "grok-4.20-0309-reasoning": "Grok 4.20",
  "grok-4.20-0309-non-reasoning": "Grok 4.20 (Non-Reasoning)",
  
  // DeepSeek
  "deepseek-v4-pro": "Deepseek V4 Pro",
  "deepseek-v4-flash": "Deepseek V4 Flash",
  
  // Qwen
  "qwen3.7-max": "Qwen3.7-Max",
  "qwen3.7-plus": "Qwen3.7-Plus",
  "qwen3.5-flash": "Qwen3.5-Flash",
};

/**
 * Convert a model ID to a human-readable display name.
 * Falls back to the raw model ID if not found in the mapping.
 */
export function getModelDisplayName(modelId: string | undefined | null): string | null {
  if (!modelId) return null;
  return MODEL_DISPLAY_NAMES[modelId] ?? modelId;
}

/**
 * Parse a date string from the backend as UTC.
 * Backend stores created_at in UTC but may not always include timezone info.
 * This ensures the date is correctly interpreted as UTC so the browser
 * converts it to the user's local timezone for display.
 */
export function parseUTCDate(dateStr: string): Date {
  // If the string already has timezone info (Z, +, or - offset), parse directly
  if (dateStr.endsWith("Z") || /[+-]\d{2}:\d{2}$/.test(dateStr)) {
    return new Date(dateStr);
  }
  // Otherwise, append 'Z' to treat as UTC
  return new Date(dateStr + "Z");
}

/** Normalized trading signal, independent of the language the report was written in. */
export type DecisionSignal = "buy" | "sell" | "hold" | "unknown";

export interface ExtractedDecision {
  /** Label as it appeared in the report (e.g. "賣出" or "SELL"). */
  action: string;
  signal: DecisionSignal;
  /** Tailwind text colour, kept for callers that render the label inline. */
  color: string;
}

/**
 * Minimal shape the decision/confidence extractors need. Deliberately structural
 * so both `AnalysisResponse` and stored report payloads satisfy it.
 */
export interface DecisionSource {
  decision?: { action?: string; confidence?: number } | null;
  reports?: {
    trader_investment_plan?: string;
    final_trade_decision?: string;
    market_report?: string;
    sentiment_report?: string;
    news_report?: string;
    fundamentals_report?: string;
    risk_debate_state?: { judge_decision?: string } | null;
  } | null;
}

const SIGNAL_COLORS: Record<DecisionSignal, string> = {
  buy: "text-green-600",
  sell: "text-red-600",
  hold: "text-yellow-600",
  unknown: "text-gray-500",
};

function decision(action: string, signal: DecisionSignal): ExtractedDecision {
  return { action, signal, color: SIGNAL_COLORS[signal] };
}

/**
 * Match an explicit "最終交易提案：X" / "Final Trading Proposal: X" statement.
 * Reports repeat the phrase, so the LAST match is the binding one.
 */
function findFinalProposal(text: unknown): ExtractedDecision | null {
  if (!text || typeof text !== "string") return null;

  const zhMatches = [
    ...text.matchAll(/\*{0,2}最終交易提案[：:]\s*\*{0,2}(買入|賣出|持有)\*{0,2}/g),
  ];
  if (zhMatches.length > 0) {
    const found = zhMatches[zhMatches.length - 1][1];
    if (found === "買入") return decision("買入", "buy");
    if (found === "賣出") return decision("賣出", "sell");
    if (found === "持有") return decision("持有", "hold");
  }

  const enMatches = [
    ...text.matchAll(
      /\*{0,2}Final Trading Proposal\*{0,2}[：:]\s*\*{0,2}(BUY|SELL|HOLD)\*{0,2}/gi,
    ),
  ];
  if (enMatches.length > 0) {
    const found = enMatches[enMatches.length - 1][1].toUpperCase();
    if (found === "BUY") return decision("BUY", "buy");
    if (found === "SELL") return decision("SELL", "sell");
    if (found === "HOLD") return decision("HOLD", "hold");
  }

  return null;
}

/** Looser fallback for reports that phrase the call as 最終決策/最終建議/recommendation. */
function findOtherDecision(text: unknown): ExtractedDecision | null {
  if (!text || typeof text !== "string") return null;

  const zhMatch = text.match(/最終(?:決策|建議)[：:]\s*(買入|賣出|持有)/);
  if (zhMatch) {
    if (zhMatch[1] === "買入") return decision("買入", "buy");
    if (zhMatch[1] === "賣出") return decision("賣出", "sell");
    if (zhMatch[1] === "持有") return decision("持有", "hold");
  }

  if (/(?:final|recommendation|decision)[:\s]*(buy|long)/i.test(text))
    return decision("買入", "buy");
  if (/(?:final|recommendation|decision)[:\s]*(sell|short)/i.test(text))
    return decision("賣出", "sell");
  if (/(?:final|recommendation|decision)[:\s]*(hold)/i.test(text))
    return decision("持有", "hold");

  return null;
}

/**
 * Resolve the final BUY/SELL/HOLD call for an analysis result.
 * Priority: trader plan → final_trade_decision → risk manager → decision.action → analyst reports.
 */
export function extractDecisionFromResult(
  result: DecisionSource | null | undefined,
): ExtractedDecision {
  const reports = result?.reports;

  const fromTrader = findFinalProposal(reports?.trader_investment_plan);
  if (fromTrader) return fromTrader;

  const finalTrade = reports?.final_trade_decision;
  if (finalTrade) {
    const found = findFinalProposal(finalTrade) || findOtherDecision(finalTrade);
    if (found) return found;
  }

  const riskJudge = reports?.risk_debate_state?.judge_decision;
  if (riskJudge) {
    const found = findOtherDecision(riskJudge);
    if (found) return found;
  }

  const action = result?.decision?.action;
  if (typeof action === "string" && action) {
    const lower = action.toLowerCase();
    const signal: DecisionSignal = lower.includes("buy")
      ? "buy"
      : lower.includes("sell")
        ? "sell"
        : "hold";
    return decision(action, signal);
  }

  for (const text of [
    reports?.market_report,
    reports?.sentiment_report,
    reports?.news_report,
    reports?.fundamentals_report,
  ]) {
    const found = findFinalProposal(text);
    if (found) return found;
  }

  return decision("N/A", "unknown");
}

/**
 * Resolve a 0–1 confidence score, either from the structured decision field
 * or from a "信心度：85%" / "confidence: 85%" statement in the trader plan.
 * Returns null when the report contains no parsable value.
 */
export function extractConfidence(
  result: DecisionSource | null | undefined,
): number | null {
  const raw = result?.decision?.confidence;
  if (typeof raw === "number" && Number.isFinite(raw)) {
    // Backend has used both 0–1 and 0–100 at different times.
    return raw > 1 ? Math.min(raw / 100, 1) : Math.max(raw, 0);
  }

  const sources = [
    result?.reports?.trader_investment_plan,
    result?.reports?.final_trade_decision,
    result?.reports?.risk_debate_state?.judge_decision,
  ];
  for (const text of sources) {
    if (!text || typeof text !== "string") continue;
    const match = text.match(
      /(?:信心度|信心水準|把握度|confidence)\D{0,12}?(\d{1,3}(?:\.\d+)?)\s*%/i,
    );
    if (match) {
      const pct = parseFloat(match[1]);
      if (Number.isFinite(pct)) return Math.min(Math.max(pct / 100, 0), 1);
    }
  }

  return null;
}

/** Debate-round prefixes emitted by the agents, in both supported languages. */
const DEBATE_ROUND_PREFIXES = [
  "看漲分析師：",
  "看跌分析師：",
  "激進分析師：",
  "保守分析師：",
  "中立分析師：",
  "Bull Analyst: ",
  "Bear Analyst: ",
  "Aggressive Analyst: ",
  "Conservative Analyst: ",
  "Neutral Analyst: ",
];

/**
 * Keep only the final round of a multi-round debate history.
 * Earlier rounds restate the same arguments and make the cards unreadable.
 */
export function extractLastDebateRound(history: string): string {
  if (!history) return history;

  let lastIndex = -1;
  for (const prefix of DEBATE_ROUND_PREFIXES) {
    const idx = history.lastIndexOf("\n" + prefix);
    if (idx > lastIndex) lastIndex = idx;
  }

  if (lastIndex === -1) return history.trimStart();
  return history.slice(lastIndex + 1); // skip the leading \n
}
