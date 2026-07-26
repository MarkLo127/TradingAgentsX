/**
 * Headline verdict panel shown at the top of a report:
 * the final BUY/SELL/HOLD call plus the numbers needed to judge it at a glance.
 */
"use client";

import { useLanguage } from "@/contexts/LanguageContext";
import { cn } from "@/lib/utils";
import type { DecisionSignal } from "@/lib/report-utils";

interface VerdictBannerProps {
  action: string;
  signal: DecisionSignal;
  /** 0–1, or null when the report contains no parsable value. */
  confidence: number | null;
  analystCount: number;
  /** Percent change over the analysed window, e.g. -3.86. */
  periodChange?: number | null;
  marketLabel?: string | null;
  /** Source filename or task id, shown small and monospaced on the right. */
  sourceLabel?: string | null;
}

const SIGNAL_THEME: Record<
  DecisionSignal,
  { panel: string; text: string; bar: string }
> = {
  buy: {
    panel:
      "border-emerald-200/80 bg-emerald-50/70 dark:border-emerald-900/60 dark:bg-emerald-950/30",
    text: "text-emerald-700 dark:text-emerald-400",
    bar: "bg-emerald-600 dark:bg-emerald-500",
  },
  sell: {
    panel:
      "border-rose-200/80 bg-rose-50/70 dark:border-rose-900/60 dark:bg-rose-950/30",
    text: "text-rose-700 dark:text-rose-400",
    bar: "bg-rose-600 dark:bg-rose-500",
  },
  hold: {
    panel:
      "border-amber-200/80 bg-amber-50/70 dark:border-amber-900/60 dark:bg-amber-950/30",
    text: "text-amber-700 dark:text-amber-400",
    bar: "bg-amber-500",
  },
  unknown: {
    panel: "border-border bg-muted/40",
    text: "text-muted-foreground",
    bar: "bg-muted-foreground",
  },
};

export function VerdictBanner({
  action,
  signal,
  confidence,
  analystCount,
  periodChange,
  marketLabel,
  sourceLabel,
}: VerdictBannerProps) {
  const { t } = useLanguage();
  const theme = SIGNAL_THEME[signal];
  const v = t.results.verdict;

  const changeTone =
    periodChange == null
      ? "text-muted-foreground"
      : periodChange >= 0
        ? "text-emerald-600 dark:text-emerald-400"
        : "text-rose-600 dark:text-rose-400";

  return (
    <section
      className={cn(
        "rounded-2xl border px-5 py-5 sm:px-7 sm:py-6 animate-scale-up",
        theme.panel,
      )}
    >
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        {/* Verdict + supporting numbers */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:gap-7 min-w-0">
          <div className="shrink-0">
            <div
              className={cn(
                "font-serif leading-none tracking-tight text-5xl sm:text-6xl",
                theme.text,
              )}
            >
              {signal === "unknown" ? v.undecided : action}
            </div>
            <div className="mt-1.5 text-xs text-muted-foreground">{v.label}</div>
          </div>

          <div className="min-w-0 space-y-2.5 text-sm">
            {confidence == null ? (
              <p className="text-muted-foreground">{v.noConfidence}</p>
            ) : (
              <div className="flex items-center gap-3">
                <span className="text-muted-foreground shrink-0">{v.confidence}</span>
                <div className="h-1.5 w-24 sm:w-32 overflow-hidden rounded-full bg-foreground/10">
                  <div
                    className={cn("h-full rounded-full", theme.bar)}
                    style={{ width: `${Math.round(confidence * 100)}%` }}
                  />
                </div>
                <span className="font-medium tabular-nums">
                  {Math.round(confidence * 100)}%
                </span>
              </div>
            )}

            <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
              <span className="text-muted-foreground">
                {v.analystCount}{" "}
                <span className="font-medium tabular-nums text-foreground">
                  {analystCount}
                </span>
                {v.analystCountUnit ? ` ${v.analystCountUnit}` : ""}
              </span>
              {periodChange != null && (
                <span className="text-muted-foreground">
                  {v.periodChange}{" "}
                  <span className={cn("font-medium tabular-nums", changeTone)}>
                    {periodChange >= 0 ? "+" : ""}
                    {periodChange.toFixed(2)}%
                  </span>
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Provenance */}
        <div className="flex shrink-0 flex-row items-center gap-3 lg:flex-col lg:items-end lg:gap-2">
          {marketLabel && (
            <span className="rounded-full border border-border/70 bg-background/60 px-2.5 py-0.5 text-xs text-muted-foreground">
              {marketLabel}
            </span>
          )}
          {sourceLabel && (
            <span className="truncate font-mono text-[11px] text-muted-foreground/70">
              {sourceLabel}
            </span>
          )}
        </div>
      </div>
    </section>
  );
}
