/**
 * One participant of a debate, rendered as a self-contained column.
 * Several of these sit side by side so the whole debate is readable without tab-switching:
 * each body scrolls inside a capped height, and can be expanded to full length.
 */
"use client";

import { useState } from "react";
import {
  TrendingUp,
  TrendingDown,
  Zap,
  Shield,
  Scale,
  ChevronDown,
  type LucideIcon,
} from "lucide-react";
import { MarkdownReport } from "@/components/analysis/MarkdownReport";
import { useLanguage } from "@/contexts/LanguageContext";
import { cn } from "@/lib/utils";

export type DebateTone = "bull" | "bear" | "aggressive" | "conservative" | "neutral";

interface DebateCardProps {
  tone: DebateTone;
  title: string;
  content: string;
}

const TONE_THEME: Record<
  DebateTone,
  { icon: LucideIcon; header: string; label: string; ring: string }
> = {
  bull: {
    icon: TrendingUp,
    header: "bg-emerald-50/80 dark:bg-emerald-950/30",
    label: "text-emerald-700 dark:text-emerald-400",
    ring: "border-emerald-200/80 dark:border-emerald-900/60",
  },
  bear: {
    icon: TrendingDown,
    header: "bg-rose-50/80 dark:bg-rose-950/30",
    label: "text-rose-700 dark:text-rose-400",
    ring: "border-rose-200/80 dark:border-rose-900/60",
  },
  aggressive: {
    icon: Zap,
    header: "bg-rose-50/80 dark:bg-rose-950/30",
    label: "text-rose-700 dark:text-rose-400",
    ring: "border-rose-200/80 dark:border-rose-900/60",
  },
  conservative: {
    icon: Shield,
    header: "bg-emerald-50/80 dark:bg-emerald-950/30",
    label: "text-emerald-700 dark:text-emerald-400",
    ring: "border-emerald-200/80 dark:border-emerald-900/60",
  },
  neutral: {
    icon: Scale,
    header: "bg-blue-50/80 dark:bg-blue-950/30",
    label: "text-blue-700 dark:text-blue-400",
    ring: "border-blue-200/80 dark:border-blue-900/60",
  },
};

export function DebateCard({ tone, title, content }: DebateCardProps) {
  const { t } = useLanguage();
  const [expanded, setExpanded] = useState(false);
  const theme = TONE_THEME[tone];
  const Icon = theme.icon;

  return (
    <div
      className={cn(
        "flex h-full flex-col overflow-hidden rounded-xl border bg-card shadow-sm",
        theme.ring,
        // Capped while collapsed so every column stays comparable on screen.
        !expanded && "max-h-[26rem] lg:max-h-[32rem]",
      )}
    >
      <div
        className={cn(
          "flex shrink-0 items-center gap-2 border-b px-4 py-2.5",
          theme.header,
          theme.ring,
        )}
      >
        <Icon className={cn("h-4 w-4 shrink-0", theme.label)} />
        <h3 className={cn("truncate text-sm font-semibold", theme.label)}>{title}</h3>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-4">
        <MarkdownReport compact>{content}</MarkdownReport>
      </div>

      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="flex shrink-0 items-center justify-center gap-1 border-t border-border/60 bg-muted/30 py-2 text-xs text-muted-foreground transition-colors hover:bg-muted/60 hover:text-foreground"
        aria-expanded={expanded}
      >
        {expanded ? t.results.sections.collapse : t.results.sections.expand}
        <ChevronDown
          className={cn("h-3.5 w-3.5 transition-transform", expanded && "rotate-180")}
        />
      </button>
    </div>
  );
}
