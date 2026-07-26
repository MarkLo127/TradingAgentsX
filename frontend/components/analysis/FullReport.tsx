/**
 * The long-form reports, all stacked on a single page.
 *
 * The pill row is navigation, not a tab bar: every section stays mounted and
 * visible, and clicking a pill scrolls to it. That keeps the compact overview of
 * the reference layout without forcing the reader to switch views to compare
 * two reports.
 */
"use client";

import { useEffect, useRef, useState } from "react";
import { FileText } from "lucide-react";
import { MarkdownReport } from "@/components/analysis/MarkdownReport";
import { useLanguage } from "@/contexts/LanguageContext";
import { cn } from "@/lib/utils";

export interface FullReportSection {
  id: string;
  label: string;
  content: string;
}

interface FullReportProps {
  sections: FullReportSection[];
}

export function FullReport({ sections }: FullReportProps) {
  const { t } = useLanguage();
  const [activeId, setActiveId] = useState(sections[0]?.id ?? "");
  const sectionRefs = useRef<Record<string, HTMLElement | null>>({});
  const pillRefs = useRef<Record<string, HTMLButtonElement | null>>({});
  const navRef = useRef<HTMLElement | null>(null);

  // Highlight the section the reader is currently in: the last one whose heading has
  // passed under the sticky headers. Measured on scroll rather than with an
  // IntersectionObserver, which only reports sections whose visibility *changed* and
  // so drifts out of sync when several are on screen at once.
  useEffect(() => {
    if (sections.length === 0) return;

    let frame = 0;
    const update = () => {
      frame = 0;
      const line = 180; // px below the viewport top, clear of both sticky bars
      const atBottom =
        window.innerHeight + window.scrollY >= document.body.scrollHeight - 2;

      let current = sections[0].id;
      if (atBottom) {
        current = sections[sections.length - 1].id;
      } else {
        for (const section of sections) {
          const el = sectionRefs.current[section.id];
          if (el && el.getBoundingClientRect().top <= line) current = section.id;
        }
      }
      setActiveId(current);
    };

    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(update);
    };

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      if (frame) cancelAnimationFrame(frame);
    };
  }, [sections]);

  // Keep the active pill in view on narrow screens. This scrolls the pill row only —
  // `scrollIntoView` would also scroll the page, yanking the reader away on mount.
  useEffect(() => {
    const nav = navRef.current;
    const pill = pillRefs.current[activeId];
    if (!nav || !pill) return;
    const target = pill.offsetLeft - (nav.clientWidth - pill.clientWidth) / 2;
    nav.scrollTo({ left: Math.max(0, target), behavior: "smooth" });
  }, [activeId]);

  if (sections.length === 0) return null;

  return (
    // No `overflow-hidden` here: an overflow ancestor would break the sticky nav below.
    <section className="rounded-2xl border border-border bg-card shadow-sm">
      {/* Sticky section nav — offsets clear the sticky site header. */}
      <div className="sticky top-15 z-20 rounded-t-2xl border-b border-border/70 bg-card/95 backdrop-blur-md md:top-18">
        <div className="flex flex-col gap-2 px-4 py-3 sm:px-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex shrink-0 items-center gap-2">
            <FileText className="h-4 w-4 text-muted-foreground" />
            <h2 className="text-sm font-semibold">{t.results.sections.fullReport}</h2>
          </div>

          <nav
            ref={navRef}
            aria-label={t.results.sections.fullReport}
            className="-mx-1 flex gap-1 overflow-x-auto px-1 pb-0.5 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
          >
            {sections.map((section) => (
              <button
                key={section.id}
                type="button"
                ref={(el) => {
                  pillRefs.current[section.id] = el;
                }}
                aria-current={activeId === section.id ? "true" : undefined}
                onClick={() => {
                  sectionRefs.current[section.id]?.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                  });
                }}
                className={cn(
                  "shrink-0 whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-medium transition-colors sm:text-sm",
                  activeId === section.id
                    ? "bg-foreground text-background"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                )}
              >
                {section.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      <div className="divide-y divide-border/60">
        {sections.map((section) => (
          <article
            key={section.id}
            id={section.id}
            ref={(el) => {
              sectionRefs.current[section.id] = el;
            }}
            className="scroll-mt-32 px-4 py-6 sm:px-6 md:scroll-mt-36"
          >
            <h3 className="mb-3 text-base font-semibold">{section.label}</h3>
            <MarkdownReport>{section.content}</MarkdownReport>
          </article>
        ))}
      </div>
    </section>
  );
}
