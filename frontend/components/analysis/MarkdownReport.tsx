/**
 * Shared markdown renderer for agent report bodies.
 * Centralises the prose/table styling that every report surface needs.
 */
"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";

interface MarkdownReportProps {
  children: string;
  className?: string;
  /** Slightly tighter type for the narrow debate columns. */
  compact?: boolean;
}

export function MarkdownReport({ children, className, compact = false }: MarkdownReportProps) {
  return (
    <div
      className={cn(
        "prose max-w-none dark:prose-invert",
        compact ? "prose-sm" : "prose-sm xl:prose-base",
        // Tables can't wrap, so make each one its own horizontal scroller.
        // `block` is what allows the overflow; the page itself never scrolls sideways.
        "prose-table:block prose-table:overflow-x-auto prose-table:max-w-full",
        "prose-table:border-collapse",
        "prose-td:border prose-td:border-gray-300 dark:prose-td:border-gray-600 prose-td:p-2",
        "prose-th:border prose-th:border-gray-300 dark:prose-th:border-gray-600 prose-th:p-2",
        "prose-th:bg-gray-100 dark:prose-th:bg-gray-800",
        "prose-pre:overflow-x-auto break-words",
        className,
      )}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children}</ReactMarkdown>
    </div>
  );
}
