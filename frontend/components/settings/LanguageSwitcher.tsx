"use client";

import { Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useLanguage } from "@/contexts/LanguageContext";
import { Locale, localeNames } from "@/lib/i18n";

interface LanguageSwitcherProps {
  /**
   * When true, the switcher is rendered as a disabled, inert button instead
   * of a dropdown trigger. Use this on pages that show already-generated
   * report text (e.g. the analysis results page) — that text is fixed in
   * whatever language it was produced in, so letting the UI locale change
   * mid-view would leave the page showing two languages at once.
   */
  disabled?: boolean;
}

export function LanguageSwitcher({ disabled = false }: LanguageSwitcherProps) {
  const { locale, setLocale, t } = useLanguage();

  const locales: Locale[] = ['en', 'zh-TW'];

  if (disabled) {
    return (
      <Button
        variant="ghost"
        size="icon"
        disabled
        className="text-slate-400 dark:text-slate-600 opacity-50 cursor-not-allowed"
        aria-label="Switch language (disabled)"
        title={t.nav.languageLockedOnReport}
      >
        <Globe className="h-5 w-5" />
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="text-slate-600 dark:text-slate-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:text-blue-700 dark:hover:text-blue-300"
          aria-label="Switch language"
        >
          <Globe className="h-5 w-5" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {locales.map((loc) => (
          <DropdownMenuItem
            key={loc}
            onClick={() => setLocale(loc)}
            className={locale === loc ? "bg-accent" : ""}
          >
            {localeNames[loc]}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
