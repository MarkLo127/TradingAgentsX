/**
 * Header component with mobile-responsive design and i18n support
 */
"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";
import { ThemeToggle } from "@/components/theme/ThemeToggle";
import { ApiSettingsDialog } from "@/components/settings/ApiSettingsDialog";
import { LanguageSwitcher } from "@/components/settings/LanguageSwitcher";
import { LoginButton } from "@/components/auth/login-button";
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/contexts/LanguageContext";
import { usePathname } from "next/navigation";

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { t } = useLanguage();
  const pathname = usePathname();

  if (pathname === "/history/chat") return null;

  // The analysis results page renders already-generated report text, which
  // stays fixed in whichever language it was produced in. Switching the UI
  // locale there would leave the page showing report content and chrome in
  // two different languages, so the switcher is locked while it's open.
  const isReportDetailPage = pathname === "/analysis/results";

  return (
    <header className="sticky top-0 z-50 border-b border-border dark:border-slate-700/40 bg-white/80 dark:bg-[#0A0F1E]/85 backdrop-blur-xl pwa-safe-header shadow-[0_1px_8px_rgba(15,23,42,0.06)] dark:shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
      <div className="container mx-auto px-4 py-4 md:py-5">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 shrink-0">
            <div
              className="text-xl md:text-2xl font-black bg-clip-text text-transparent"
              style={{
                fontFamily: 'Nunito, sans-serif',
                backgroundImage: 'linear-gradient(135deg, #1d4ed8 0%, #0ea5e9 40%, #06b6d4 70%, #2dd4bf 100%)',
              }}
            >
              TradingAgentsX
            </div>
            <div className="hidden lg:block text-xs font-medium text-slate-400 dark:text-slate-500 opacity-80">
              {t.nav.tagline}
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex gap-1 lg:gap-2 items-center">
            <Link
              href="/"
              className="px-4 py-2 rounded-xl font-semibold text-sm text-slate-600 dark:text-slate-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:text-blue-700 dark:hover:text-blue-300 transition-all duration-200"
            >
              {t.nav.home}
            </Link>
            <Link
              href="/analysis"
              className="px-4 py-2 rounded-xl font-semibold text-sm text-slate-600 dark:text-slate-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:text-blue-700 dark:hover:text-blue-300 transition-all duration-200"
            >
              {t.nav.analysis}
            </Link>
            <Link
              href="/history"
              className="px-4 py-2 rounded-xl font-semibold text-sm text-slate-600 dark:text-slate-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:text-blue-700 dark:hover:text-blue-300 transition-all duration-200"
            >
              {t.nav.history}
            </Link>
            <ApiSettingsDialog />
            <LanguageSwitcher disabled={isReportDetailPage} />
            <ThemeToggle />
            <LoginButton />
          </nav>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden items-center gap-2">
            <LanguageSwitcher disabled={isReportDetailPage} />
            <ThemeToggle />
            <Button
              variant="ghost"
              size="icon"
              className="text-slate-600 dark:text-slate-300 hover:bg-blue-50 dark:hover:bg-blue-900/20"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="md:hidden mt-4 pt-4 border-t border-slate-100 dark:border-slate-700/40 space-y-1">
            <Link
              href="/"
              className="block px-4 py-2 rounded-xl font-semibold text-slate-600 dark:text-slate-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:text-blue-700 dark:hover:text-blue-300 transition-all"
              onClick={() => setMobileMenuOpen(false)}
            >
              {t.nav.home}
            </Link>
            <Link
              href="/analysis"
              className="block px-4 py-2 rounded-xl font-semibold text-slate-600 dark:text-slate-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:text-blue-700 dark:hover:text-blue-300 transition-all"
              onClick={() => setMobileMenuOpen(false)}
            >
              {t.nav.analysis}
            </Link>
            <Link
              href="/history"
              className="block px-4 py-2 rounded-xl font-semibold text-slate-600 dark:text-slate-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:text-blue-700 dark:hover:text-blue-300 transition-all"
              onClick={() => setMobileMenuOpen(false)}
            >
              {t.nav.history}
            </Link>
            <div className="flex items-center gap-3 pt-2">
              <ApiSettingsDialog />
              <LoginButton />
            </div>
          </nav>
        )}
      </div>
    </header>
  );
}
