"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useAnalysisContext } from "@/context/AnalysisContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { PriceChart } from "@/components/analysis/PriceChart";
import { VerdictBanner } from "@/components/analysis/VerdictBanner";
import { DebateCard, type DebateTone } from "@/components/analysis/DebateCard";
import { FullReport, type FullReportSection } from "@/components/analysis/FullReport";
import { Button } from "@/components/ui/button";
import { ChevronLeft } from "lucide-react";
import { lookupStockName, type MarketType } from "@/lib/stock-search";
import {
  extractConfidence,
  extractDecisionFromResult,
  extractLastDebateRound,
  getModelDisplayName,
} from "@/lib/report-utils";

/** Read a dot-separated path out of the reports object. */
const getNestedValue = (obj: unknown, path: string): unknown =>
  path
    .split(".")
    .reduce<unknown>(
      (current, key) =>
        current && typeof current === "object"
          ? (current as Record<string, unknown>)[key]
          : undefined,
      obj,
    );

/** Non-empty string, or null. Reports occasionally arrive as blank strings. */
const asContent = (value: unknown): string | null =>
  typeof value === "string" && value.trim().length > 0 ? value : null;

/** The four analyst reports, used for the "N analysts" count in the banner. */
const ANALYST_REPORT_KEYS = [
  "market_report",
  "sentiment_report",
  "news_report",
  "fundamentals_report",
] as const;

export default function AnalysisResultsPage() {
  const router = useRouter();
  const { analysisResult, marketType } = useAnalysisContext();
  const { t, locale } = useLanguage();
  const [companyName, setCompanyName] = useState<string | null>(null);

  // Resolve the full company name for the analyzed ticker (localized).
  useEffect(() => {
    const ticker = analysisResult?.ticker;
    if (!ticker) {
      setCompanyName(null);
      return;
    }
    const market = (analysisResult?.market_type ?? marketType) as MarketType;
    let cancelled = false;
    lookupStockName(ticker, market, locale)
      .then((name) => {
        if (!cancelled) setCompanyName(name);
      })
      .catch(() => {
        if (!cancelled) setCompanyName(null);
      });
    return () => {
      cancelled = true;
    };
  }, [analysisResult?.ticker, analysisResult?.market_type, marketType, locale]);

  // Redirect back to the form when there is nothing to show.
  useEffect(() => {
    if (!analysisResult) {
      router.push("/analysis");
    }
  }, [analysisResult, router]);

  const reports = analysisResult?.reports;

  const decision = useMemo(
    () => extractDecisionFromResult(analysisResult),
    [analysisResult],
  );
  const confidence = useMemo(
    () => extractConfidence(analysisResult),
    [analysisResult],
  );
  const analystCount = useMemo(
    () => ANALYST_REPORT_KEYS.filter((key) => asContent(reports?.[key])).length,
    [reports],
  );

  // Bull/bear and risk debates: every participant shown at once, side by side.
  const researchDebate = useMemo(() => {
    const entries: { tone: DebateTone; title: string; content: string }[] = [];
    const add = (tone: DebateTone, title: string, path: string) => {
      const content = asContent(getNestedValue(reports, path));
      // Debate histories accumulate every round; only the last one is worth showing.
      if (content) entries.push({ tone, title, content: extractLastDebateRound(content) });
    };
    add("bull", t.results.roles.bull, "investment_debate_state.bull_history");
    add("bear", t.results.roles.bear, "investment_debate_state.bear_history");
    return entries;
  }, [reports, t]);

  const riskDebate = useMemo(() => {
    const entries: { tone: DebateTone; title: string; content: string }[] = [];
    const add = (tone: DebateTone, title: string, path: string) => {
      const content = asContent(getNestedValue(reports, path));
      if (content) entries.push({ tone, title, content: extractLastDebateRound(content) });
    };
    add("aggressive", t.results.roles.aggressive, "risk_debate_state.risky_history");
    add("conservative", t.results.roles.conservative, "risk_debate_state.safe_history");
    add("neutral", t.results.roles.neutral, "risk_debate_state.neutral_history");
    return entries;
  }, [reports, t]);

  // Long-form reports, stacked in one scrollable column with a jump-nav.
  const fullReportSections = useMemo<FullReportSection[]>(() => {
    const labels = t.results.reportSections;
    const candidates: { id: string; label: string; path: string }[] = [
      { id: "report-trader", label: labels.trader, path: "trader_investment_plan" },
      {
        id: "report-risk-decision",
        label: labels.riskDecision,
        path: "risk_debate_state.judge_decision",
      },
      {
        id: "report-investment-plan",
        label: labels.investmentPlan,
        path: "investment_debate_state.judge_decision",
      },
      { id: "report-technical", label: labels.technical, path: "market_report" },
      { id: "report-fundamental", label: labels.fundamental, path: "fundamentals_report" },
      { id: "report-news", label: labels.news, path: "news_report" },
      { id: "report-social", label: labels.social, path: "sentiment_report" },
    ];

    return candidates.flatMap(({ id, label, path }) => {
      const content = asContent(getNestedValue(reports, path));
      return content ? [{ id, label, content }] : [];
    });
  }, [reports, t]);

  if (!analysisResult) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">{t.results.noResults}</h1>
          <p className="text-gray-600 mb-4">{t.results.runAnalysisFirst}</p>
          <Button onClick={() => router.push("/analysis")}>
            {t.results.backToAnalysis}
          </Button>
        </div>
      </div>
    );
  }

  const marketLabels: Record<string, string> = {
    us: `🇺🇸 ${t.form.usMarket}`,
    twse: `🇹🇼 ${t.form.twseMarket}`,
    tpex: `🇹🇼 ${t.form.tpexMarket}`,
  };
  const marketLabel =
    marketLabels[(analysisResult.market_type ?? marketType ?? "us") as string] ?? null;

  const models = [
    getModelDisplayName(analysisResult.deep_think_llm),
    getModelDisplayName(analysisResult.quick_think_llm),
  ].filter(Boolean) as string[];

  const hasDebates = researchDebate.length > 0 || riskDebate.length > 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/30 via-slate-50/20 to-blue-50/30 dark:from-gray-950 dark:via-blue-950/40 dark:to-gray-950">
      <div className="container mx-auto px-4 py-8 md:py-12">
        <div className="mx-auto max-w-7xl space-y-6 md:space-y-8">
          {/* Header */}
          <div className="relative flex flex-col gap-4 animate-fade-in md:flex-row md:items-center md:justify-between">
            <div className="absolute inset-0 gradient-bg-radial opacity-30 -z-10 rounded-lg" />
            <div className="min-w-0">
              <h1 className="mb-2 text-3xl font-bold gradient-text-primary sm:text-4xl">
                {companyName ?? analysisResult.ticker} {t.results.detailedResults}
              </h1>
              <p className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-gray-600 dark:text-gray-400">
                <span className="font-mono font-medium text-foreground/70">
                  {analysisResult.ticker}
                </span>
                <span>·</span>
                <span>
                  {t.results.analysisDate}：{analysisResult.analysis_date}
                </span>
                {models.length > 0 && (
                  <>
                    <span>·</span>
                    <span className="truncate">{models.join(" + ")}</span>
                  </>
                )}
              </p>
            </div>
            <div className="flex shrink-0 flex-wrap items-center gap-2">
              <Button
                variant="outline"
                onClick={() => router.push("/analysis")}
                className="gap-2 hover-lift"
              >
                <ChevronLeft className="h-4 w-4" />
                {t.results.backButton}
              </Button>
            </div>
          </div>

          {/* Final call */}
          <VerdictBanner
            action={decision.action}
            signal={decision.signal}
            confidence={confidence}
            analystCount={analystCount}
            periodChange={analysisResult.price_stats?.growth_rate ?? null}
            marketLabel={marketLabel}
          />

          {/* Price chart — shown once, instead of repeated per analyst */}
          {analysisResult.price_data && analysisResult.price_stats && (
            <PriceChart
              priceData={analysisResult.price_data}
              priceStats={analysisResult.price_stats}
              ticker={analysisResult.ticker}
            />
          )}

          {/* Debates: all participants visible at the same time */}
          {researchDebate.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-sm font-medium text-muted-foreground">
                {t.results.sections.bullBearDebate}
              </h2>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {researchDebate.map((entry) => (
                  <DebateCard key={entry.tone} {...entry} />
                ))}
              </div>
            </section>
          )}

          {riskDebate.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-sm font-medium text-muted-foreground">
                {t.results.sections.riskDebate}
              </h2>
              <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
                {riskDebate.map((entry) => (
                  <DebateCard key={entry.tone} {...entry} />
                ))}
              </div>
            </section>
          )}

          {/* Long-form reports, stacked on the same page */}
          <FullReport sections={fullReportSections} />

          {!hasDebates && fullReportSections.length === 0 && (
            <div className="rounded-2xl border border-border bg-card py-12 text-center">
              <p className="text-gray-500 dark:text-gray-400">
                {t.results.noReportGenerated}
              </p>
              <p className="mt-2 text-sm text-gray-400 dark:text-gray-500">
                {t.results.notSelectedOrNoReport}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
