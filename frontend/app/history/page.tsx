/**
 * History page - browse saved analysis reports
 */
"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { format } from "date-fns";
import { zhTW } from "date-fns/locale";
import { useAnalysisContext } from "@/context/AnalysisContext";
import { useAuth, getAuthToken } from "@/contexts/auth-context";
import { useLanguage } from "@/contexts/LanguageContext";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Trash2,
  Eye,
  RefreshCw,
  TrendingUp,
  FileText,
  Download,
  MessageCircle,
  X,
} from "lucide-react";
import {
  getReportsByMarketType,
  deleteReport,
  deleteReports,
  getAllReports,
  bulkSaveReports,
  updateReportCloudId,
  type SavedReport,
} from "@/lib/reports-db";
import {
  getCloudReports,
  deleteCloudReport,
  saveCloudReport,
  isCloudSyncEnabled,
} from "@/lib/user-api";
import {
  extractDecisionFromResult,
  getModelDisplayName,
} from "@/lib/report-utils";
// import { LoginPrompt } from "@/components/auth/login-button";
import { PendingTaskRecovery } from "@/components/PendingTaskRecovery";

// Analyst definitions for download
const ANALYSTS = [
  {
    key: "market",
    label: "市場分析師",
    reportKey: "market_report",
    description: "技術分析與市場趨勢評估",
  },
  {
    key: "social",
    label: "社群媒體分析師",
    reportKey: "sentiment_report",
    description: "社群情緒與市場氛圍分析",
  },
  {
    key: "news",
    label: "新聞分析師",
    reportKey: "news_report",
    description: "新聞事件與影響分析",
  },
  {
    key: "fundamentals",
    label: "基本面分析師",
    reportKey: "fundamentals_report",
    description: "財務數據與基本面分析",
  },
  {
    key: "bull",
    label: "看漲研究員",
    reportKey: "investment_debate_state.bull_history",
    description: "看漲觀點與投資論據",
  },
  {
    key: "bear",
    label: "看跌研究員",
    reportKey: "investment_debate_state.bear_history",
    description: "看跌觀點與風險警告",
  },
  {
    key: "research_manager",
    label: "研究經理",
    reportKey: "investment_debate_state.judge_decision",
    description: "研究團隊綜合決策",
  },
  {
    key: "trader",
    label: "交易員",
    reportKey: "trader_investment_plan",
    description: "交易執行計劃與策略",
  },
  {
    key: "risky",
    label: "激進分析師",
    reportKey: "risk_debate_state.risky_history",
    description: "高風險高回報策略分析",
  },
  {
    key: "safe",
    label: "保守分析師",
    reportKey: "risk_debate_state.safe_history",
    description: "穩健保守策略分析",
  },
  {
    key: "neutral",
    label: "中立分析師",
    reportKey: "risk_debate_state.neutral_history",
    description: "中立平衡策略分析",
  },
  {
    key: "risk_manager",
    label: "風險經理",
    reportKey: "risk_debate_state.judge_decision",
    description: "風險管理綜合決策",
  },
];

// Market type labels - dynamic function to support translations
const getMarketLabels = (t: ReturnType<typeof useLanguage>["t"]) => ({
  us: { label: `🇺🇸 ${t.form.usMarket}`, description: t.form.tickerDescUS },
  twse: {
    label: `🇹🇼 ${t.form.twseMarket}`,
    description: t.form.tickerDescTWSE,
  },
  tpex: {
    label: `🇹🇼 ${t.form.tpexMarket}`,
    description: t.form.tickerDescTPEX,
  },
});

// Decision extraction lives in report-utils so the history list and the report
// page always agree on the final call. Kept as a local alias for readability.
const extractDecisionFromReport = (
  report: SavedReport,
): { action: string; color: string } => extractDecisionFromResult(report.result);

/**
 * Detect report language from content (for backward compatibility with old reports)
 * Checks trader_investment_plan for Chinese/English keywords
 */
/**
 * Detect the language of a report by scanning ANY part of its data for CJK characters.
 * Accepts anything — the full result object, a nested reports sub-object, or a plain string.
 * Returns "zh-TW" if ANY Chinese character is found; otherwise "en".
 * This is deliberately broad so old/incomplete reports that lack a `language` field
 * are still classified correctly instead of defaulting to "en".
 */
const detectReportLanguage = (data: any): "en" | "zh-TW" => {
  if (!data) return "en";
  const text = typeof data === "string" ? data : JSON.stringify(data);
  return /[\u4e00-\u9fa5]/.test(text) ? "zh-TW" : "en";
};

/**
 * Parse a date string from the backend as UTC.
 * Backend stores created_at in UTC but may not always include timezone info.
 * This ensures the date is correctly interpreted as UTC so the browser
 * converts it to the user's local timezone for display.
 */
const parseUTCDate = (dateStr: string): Date => {
  // If the string already has timezone info (Z, +, or - offset), parse directly
  if (dateStr.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(dateStr)) {
    return new Date(dateStr);
  }
  // Otherwise, append 'Z' to treat as UTC
  return new Date(dateStr + 'Z');
};

/**
 * Helper to generate a unique signature for deduplication.
 * Uses only stable key fields: ticker + date + market_type + language.
 * Language is normalized to "zh-TW" when null/undefined to match backend behavior.
 */
const getReportSignature = (report: any): string => {
  const lang = report.language || "zh-TW";
  const deep = report.result?.deep_think_llm || "";
  const quick = report.result?.quick_think_llm || "";
  const modelSuffix = (deep || quick) ? `_${deep}_${quick}` : "";
  return `${report.ticker}_${report.analysis_date}_${report.market_type || 'us'}_${lang}${modelSuffix}`;
};

export default function HistoryPage() {
  const router = useRouter();
  const { setAnalysisResult, setTaskId, setMarketType } = useAnalysisContext();
  const { isAuthenticated } = useAuth();
  const { t, locale } = useLanguage();

  // Dynamic market labels based on language
  const MARKET_LABELS = getMarketLabels(t);

  const [activeTab, setActiveTab] = useState<"us" | "twse" | "tpex">("us");
  const [reports, setReports] = useState<SavedReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [counts, setCounts] = useState({ us: 0, twse: 0, tpex: 0 });
  const [isCloudData, setIsCloudData] = useState(false);

  // Delete confirmation dialog
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [reportToDelete, setReportToDelete] = useState<SavedReport | null>(
    null,
  );
  const [deleting, setDeleting] = useState(false);

  // Sync state
  const [syncing, setSyncing] = useState(false);

  // Auto-sync tracking ref
  const hasAutoSyncedRef = useRef(false);
  const cloudReportsPromiseRef = useRef<Promise<any[] | null> | null>(null);
  // Version counter — incremented on every loadReports call; stale async paths
  // that complete after a newer invocation started are silently discarded.
  const loadVersionRef = useRef(0);

  const fetchCloudReportsCached = async (forceRefresh = false) => {
    if (forceRefresh || !cloudReportsPromiseRef.current) {
      cloudReportsPromiseRef.current = getCloudReports().catch(() => {
        cloudReportsPromiseRef.current = null;
        return null;
      });
    }
    return cloudReportsPromiseRef.current;
  };

  // Load reports when tab changes, auth state changes, or language changes
  useEffect(() => {
    loadReports();
  }, [activeTab, isAuthenticated, locale]);

  // Load counts on mount, auth change, or language change
  useEffect(() => {
    loadCounts();
  }, [isAuthenticated, locale]);

  // Bidirectional sync: upload local to cloud AND download cloud to local
  const performBidirectionalSync = async (isInitialSync = false) => {
    if (!isAuthenticated || !isCloudSyncEnabled()) {
      return;
    }

    // For initial sync, only run once per session
    if (isInitialSync && hasAutoSyncedRef.current) {
      return;
    }

    if (isInitialSync) {
      hasAutoSyncedRef.current = true;
    }

    try {
      // Auto-clean local duplicates that might exist from older flawed versions
      try {
        const allLocal = await getAllReports();
        const seenSignatures = new Set<string>();
        const idsToDelete: number[] = [];

        for (const report of allLocal) {
          const signature = getReportSignature(report as any);
          if (seenSignatures.has(signature)) {
            if (report.id) idsToDelete.push(report.id);
          } else {
            seenSignatures.add(signature);
          }
        }

        if (idsToDelete.length > 0) {
          console.log(`🧹 Found ${idsToDelete.length} duplicate local reports, cleaning...`);
          await deleteReports(idsToDelete);
        }
      } catch (err) {
        console.error("Failed to cleanup local duplicates:", err);
      }

      // Get all local reports (re-fetch after cleanup)
      const [usLocal, twseLocal, tpexLocal] = await Promise.all([
        getReportsByMarketType("us"),
        getReportsByMarketType("twse"),
        getReportsByMarketType("tpex"),
      ]);
      const allLocal = [...usLocal, ...twseLocal, ...tpexLocal];

      // Get cloud reports
      const cloudReports = await fetchCloudReportsCached(true); // Force refresh
      if (!cloudReports) {
        console.warn("☁️ Sync: Failed to fetch cloud reports. Aborting sync to prevent data loss.");
        return; // Abort sync if fetching fails
      }
      const cloudKeys = new Set(cloudReports.map((r) => getReportSignature(r)));
      const localKeys = new Set(allLocal.map((r) => getReportSignature(r)));

      // === UPLOAD: Local -> Cloud ===
      // Only upload reports that have never been synced (no cloud_id).
      // Reports with a cloud_id were previously synced; if they're absent from cloud
      // now, they were deleted on another device — do NOT re-upload them.
      const toUpload = allLocal.filter(
        (r) => !cloudKeys.has(getReportSignature(r)) && !r.cloud_id,
      );

      // Track signatures that failed to upload so we don't purge them below
      const uploadFailedSigs = new Set<string>();
      if (toUpload.length > 0) {
        console.log(`☁️ Sync: Uploading ${toUpload.length} local reports to cloud...`);
        let uploadSuccess = 0;
        for (const report of toUpload) {
          const sig = getReportSignature(report as any);
          try {
            const cloudId = await saveCloudReport({
              ticker: report.ticker,
              market_type: report.market_type,
              analysis_date: report.analysis_date,
              result: report.result,
              language: report.language || detectReportLanguage(report.result?.reports),
            });
            if (cloudId) {
              uploadSuccess++;
              // Store cloud_id locally so future syncs know this report was synced.
              // Without this, a remote deletion would be mistaken as "never uploaded"
              // and the report would be re-uploaded instead of purged locally.
              if (report.id !== undefined) {
                await updateReportCloudId(report.id, cloudId);
              }
            } else {
              uploadFailedSigs.add(sig);
            }
          } catch (e) {
            uploadFailedSigs.add(sig); // preserve on network error
          }
        }
        if (uploadSuccess > 0) {
          console.log(`☁️ Sync: Uploaded ${uploadSuccess} reports to cloud`);
        }
      }

      // Re-fetch cloud after uploads so the authoritative list includes just-uploaded reports.
      // Without this, successfully uploaded reports would appear absent from cloudKeys
      // and incorrectly be purged in the next step.
      const authoritativeCloud = toUpload.length > 0
        ? (await fetchCloudReportsCached(true) || cloudReports)
        : cloudReports;
      const authoritativeKeys = new Set(authoritativeCloud.map((r) => getReportSignature(r)));

      // === PURGE: Remove local reports deleted on another device ===
      // A report can only be "deleted on another device" if it was previously synced
      // to cloud (has a cloud_id). Without cloud_id, absence from cloud means it was
      // never uploaded — not deleted remotely.
      // Exception: skip reports whose upload just failed (preserve local data on error).
      const toPurgeLocally = allLocal.filter((r) => {
        const sig = getReportSignature(r as any);
        return r.cloud_id && !authoritativeKeys.has(sig) && !uploadFailedSigs.has(sig);
      });

      if (toPurgeLocally.length > 0) {
        const idsToRemove = toPurgeLocally
          .filter((r) => r.id !== undefined)
          .map((r) => r.id!);
        if (idsToRemove.length > 0) {
          await deleteReports(idsToRemove);
          console.log(`☁️ Sync: Removed ${idsToRemove.length} report(s) deleted on another device`);
        }
      }

      // === DOWNLOAD: Cloud -> Local ===
      const toDownload = authoritativeCloud.filter(
        (r) => !localKeys.has(getReportSignature(r)),
      );

      if (toDownload.length > 0) {
        console.log(`☁️ Sync: Downloading ${toDownload.length} cloud reports to local...`);
        const reportsToSave = toDownload.map((r) => ({
          ticker: r.ticker,
          market_type: r.market_type as "us" | "twse" | "tpex",
          analysis_date: r.analysis_date,
          saved_at: parseUTCDate(r.created_at),
          result: r.result,
          language: (r.language || detectReportLanguage(r.result?.reports)) as "en" | "zh-TW" | undefined,
          cloud_id: r.id, // Mark as synced so future deletions can be tracked
        }));

        const savedCount = await bulkSaveReports(reportsToSave);
        if (savedCount > 0) {
          console.log(`☁️ Sync: Downloaded ${savedCount} reports to local`);
        }
      }

      // Reload UI if any changes
      if (toUpload.length > 0 || toDownload.length > 0 || toPurgeLocally.length > 0) {
        await loadReports();
        await loadCounts();
      } else {
        console.log("☁️ Sync: Already in sync");
      }
    } catch (error) {
      console.error("☁️ Sync failed:", error);
    }
  };

  // Initial sync when page loads (if authenticated)
  useEffect(() => {
    performBidirectionalSync(true);
  }, [isAuthenticated]);

  // Re-sync when page becomes visible (handles cross-device changes)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible" && isAuthenticated && isCloudSyncEnabled()) {
        console.log("☁️ Page visible, checking for updates...");
        performBidirectionalSync(false);
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [isAuthenticated]);

  // SSE: real-time cross-device sync via Server-Sent Events
  // Falls back to 30s polling if SSE is unavailable (e.g. proxy strips streaming)
  useEffect(() => {
    if (!isAuthenticated || !isCloudSyncEnabled()) return;

    const token = getAuthToken();
    if (!token) return;

    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";
    let es: EventSource | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let reconnectDelay = 2000;
    let sseWorking = false;

    // Fallback poll — used only when SSE is not working
    const fallbackInterval = setInterval(() => {
      if (!sseWorking && document.visibilityState === "visible") {
        console.log("☁️ SSE fallback poll...");
        performBidirectionalSync(false);
      }
    }, 30000);

    const connect = () => {
      es = new EventSource(
        `${API_BASE}/api/user/events?token=${encodeURIComponent(token)}`
      );

      es.addEventListener("connected", () => {
        console.log("☁️ SSE connected — real-time sync active");
        sseWorking = true;
        reconnectDelay = 2000; // reset backoff on success
      });

      es.addEventListener("report_changed", () => {
        console.log("☁️ SSE: report_changed — syncing...");
        performBidirectionalSync(false);
      });

      es.onerror = () => {
        sseWorking = false;
        es?.close();
        es = null;
        // Exponential backoff, cap at 60s
        reconnectTimer = setTimeout(() => {
          reconnectDelay = Math.min(reconnectDelay * 2, 60000);
          connect();
        }, reconnectDelay);
      };
    };

    connect();

    return () => {
      es?.close();
      clearInterval(fallbackInterval);
      if (reconnectTimer) clearTimeout(reconnectTimer);
    };
  }, [isAuthenticated]);

  const loadReports = async () => {
    // Bump version so any older in-flight invocations can self-abort
    const myVersion = ++loadVersionRef.current;

    // Helper to filter reports by current UI language (captured at call time)
    const currentLocale = locale;
    const filterByLang = (reports: SavedReport[]) =>
      reports.filter((report) => {
        // Use explicit language field when available; otherwise scan the FULL
        // result object so even old reports without a language field are
        // detected correctly (report.result?.reports may be undefined for
        // some report shapes — scanning the whole object is more robust).
        const reportLang =
          report.language || detectReportLanguage(report.result);
        return reportLang === currentLocale;
      });

    // ── PHASE 1: Show local IndexedDB data INSTANTLY (no loading spinner) ──
    try {
      const localData = await getReportsByMarketType(activeTab);
      if (loadVersionRef.current !== myVersion) return; // stale — newer call took over
      setReports(filterByLang(localData));
      setIsCloudData(false);
    } catch (error) {
      console.error("Failed to load local reports:", error);
    } finally {
      if (loadVersionRef.current === myVersion) setLoading(false);
    }

    // ── PHASE 2: Silently fetch cloud data and merge in background ──
    if (!isAuthenticated || !isCloudSyncEnabled()) return;

    try {
      const cloudReports = await fetchCloudReportsCached();
      if (loadVersionRef.current !== myVersion) return; // stale
      if (!cloudReports) return;

      // Re-fetch local to ensure we have the latest after potential sync
      const localData = await getReportsByMarketType(activeTab);
      if (loadVersionRef.current !== myVersion) return; // stale

      const cloudFiltered = cloudReports
        .filter((r) => r.market_type === activeTab)
        .map((r) => ({
          id: parseInt(r.id.replace(/-/g, "").slice(0, 8), 16),
          cloudId: r.id,
          ticker: r.ticker,
          market_type: r.market_type as "us" | "twse" | "tpex",
          analysis_date: r.analysis_date,
          saved_at: parseUTCDate(r.created_at),
          result: r.result,
          language: r.language,
        })) as (SavedReport & { cloudId?: string })[];

      if (cloudFiltered.length > 0) {
        const localSignatures = new Set(localData.map((r) => getReportSignature(r)));
        const cloudOnly = cloudFiltered.filter(
          (r) => !localSignatures.has(getReportSignature(r)),
        );
        const merged = [...localData, ...cloudOnly];
        merged.sort(
          (a, b) => new Date(b.saved_at).getTime() - new Date(a.saved_at).getTime(),
        );
        setReports(filterByLang(merged));
        setIsCloudData(true);
      }
    } catch (error) {
      console.error("Failed to load cloud reports:", error);
    }
  };

  const loadCounts = async () => {
    try {
      // Helper to filter reports by language (matches current UI locale)
      const filterByLanguage = (reports: SavedReport[]) =>
        reports.filter((report) => {
          const reportLang =
            report.language || detectReportLanguage(report.result);
          return reportLang === locale;
        });
      
      if (isAuthenticated && isCloudSyncEnabled()) {
        const cloudReports = await fetchCloudReportsCached();
        
        if (cloudReports && cloudReports.length > 0) {
          // Get local reports to check for duplicates
          const [usLocal, twseLocal, tpexLocal] = await Promise.all([
            getReportsByMarketType("us"),
            getReportsByMarketType("twse"),
            getReportsByMarketType("tpex"),
          ]);
          
          // Cloud report keys for deduplication
          const cloudKeys = new Set(
            cloudReports.map(r => getReportSignature(r))
          );
          
          // Convert cloud reports to SavedReport format for language filtering
          const cloudAsSaved = cloudReports.map(r => ({
            id: 0,
            ticker: r.ticker,
            market_type: r.market_type as "us" | "twse" | "tpex",
            analysis_date: r.analysis_date,
            saved_at: parseUTCDate(r.created_at),
            result: r.result,
            language: r.language,
          })) as SavedReport[];
          
          // Filter cloud reports by language
          const cloudFiltered = filterByLanguage(cloudAsSaved);
          
          // Count local-only reports (not in cloud) and filter by language
          const usLocalOnly = filterByLanguage(usLocal.filter(
            r => !cloudKeys.has(getReportSignature(r))
          )).length;
          const twseLocalOnly = filterByLanguage(twseLocal.filter(
            r => !cloudKeys.has(getReportSignature(r))
          )).length;
          const tpexLocalOnly = filterByLanguage(tpexLocal.filter(
            r => !cloudKeys.has(getReportSignature(r))
          )).length;
          
          // Cloud counts (already filtered by language)
          const usCloud = cloudFiltered.filter(r => r.market_type === "us").length;
          const twseCloud = cloudFiltered.filter(r => r.market_type === "twse").length;
          const tpexCloud = cloudFiltered.filter(r => r.market_type === "tpex").length;
          
          // Merged counts: cloud + local-only (both filtered by language)
          setCounts({
            us: usCloud + usLocalOnly,
            twse: twseCloud + twseLocalOnly,
            tpex: tpexCloud + tpexLocalOnly,
          });
          return;
        }
      }
      
      // If no cloud data or not authenticated, use local only with language filter
      const [usLocal, twseLocal, tpexLocal] = await Promise.all([
        getReportsByMarketType("us"),
        getReportsByMarketType("twse"),
        getReportsByMarketType("tpex"),
      ]);
      
      setCounts({
        us: filterByLanguage(usLocal).length,
        twse: filterByLanguage(twseLocal).length,
        tpex: filterByLanguage(tpexLocal).length,
      });
    } catch (error) {
      console.error("Failed to load counts:", error);
    }
  };

  // Handle refresh button - performs full sync if authenticated
  const handleRefresh = async () => {
    if (isAuthenticated && isCloudSyncEnabled()) {
      setSyncing(true);
      try {
        await performBidirectionalSync(false);
      } finally {
        setSyncing(false);
      }
    } else {
      await loadReports();
    }
  };

  const handleViewReport = (report: SavedReport) => {
    // Set the context with the saved report data
    setAnalysisResult(report.result);
    setTaskId(report.task_id || null);
    setMarketType(report.market_type);
    // Navigate to results page
    router.push("/analysis/results");
  };

  const handleDeleteClick = (report: SavedReport) => {
    setReportToDelete(report);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!reportToDelete) return;

    setDeleting(true);
    try {
      const cloudId = (reportToDelete as any).cloudId;
      const targetLang = reportToDelete.language || detectReportLanguage(reportToDelete.result?.reports);

      // IMPORTANT: Delete from BOTH cloud AND local to prevent re-sync issues
      // 1. Delete from cloud: delete the specific report AND any other duplicates with the same key
      const deleteDeep = reportToDelete.result?.deep_think_llm || "";
      const deleteQuick = reportToDelete.result?.quick_think_llm || "";
      try {
        const allCloudReports = await fetchCloudReportsCached(true);
        if (allCloudReports) {
          const matchingCloudIds = allCloudReports
            .filter((r) => {
              const lang = r.language || "zh-TW";
              if (
                r.ticker !== reportToDelete.ticker ||
                r.analysis_date !== reportToDelete.analysis_date ||
                r.market_type !== reportToDelete.market_type ||
                lang !== (targetLang || "zh-TW")
              ) return false;
              // Also match by model so only the correct model's report is deleted
              const cloudDeep = r.result?.deep_think_llm || "";
              const cloudQuick = r.result?.quick_think_llm || "";
              if ((deleteDeep || deleteQuick) && (cloudDeep || cloudQuick)) {
                if (deleteDeep !== cloudDeep || deleteQuick !== cloudQuick) return false;
              }
              return true;
            })
            .map((r) => r.id);

          if (matchingCloudIds.length > 0) {
            console.log(`🗑️ Deleting ${matchingCloudIds.length} cloud report(s):`, matchingCloudIds);
            await Promise.all(matchingCloudIds.map((id) => deleteCloudReport(id)));
          } else if (cloudId) {
            // Fallback: delete by cloudId if no match found by key
            console.log("🗑️ Deleting from cloud by ID:", cloudId);
            await deleteCloudReport(cloudId);
          }
        } else if (cloudId) {
          console.log("🗑️ Deleting from cloud by original ID because fetch failed:", cloudId);
          await deleteCloudReport(cloudId);
        }
      } catch (cloudErr) {
        console.warn("Could not delete cloud copy:", cloudErr);
        // Fallback to original cloudId delete
        if (cloudId) {
          await deleteCloudReport(cloudId);
        }
      }

      // 2. Always try to delete from local IndexedDB as well
      // Use strict matching: ticker + date + market_type + language
      try {
        const localReports = await getReportsByMarketType(
          reportToDelete.market_type,
        );
        // Get language of report to delete (use stored or detect)
        const targetLang = reportToDelete.language || detectReportLanguage(reportToDelete.result?.reports);

        // Find matching report with same ticker, date, market, language AND model
        const matchingLocal = localReports.find((r) => {
          if (r.ticker !== reportToDelete.ticker) return false;
          if (r.analysis_date !== reportToDelete.analysis_date) return false;
          if (r.market_type !== reportToDelete.market_type) return false;
          // Match language (detect if not stored)
          const localLang = r.language || detectReportLanguage(r.result?.reports);
          if (localLang !== targetLang) return false;
          // Also match by model names to avoid deleting the wrong report
          const localDeep = r.result?.deep_think_llm || "";
          const localQuick = r.result?.quick_think_llm || "";
          if ((deleteDeep || deleteQuick) && (localDeep || localQuick)) {
            if (deleteDeep !== localDeep || deleteQuick !== localQuick) return false;
          }
          return true;
        });

        if (matchingLocal && matchingLocal.id) {
          console.log("🗑️ Deleting from local IndexedDB:", matchingLocal.id, "language:", targetLang);
          await deleteReport(matchingLocal.id);
        }
      } catch (localError) {
        console.warn("Could not delete local copy:", localError);
      }

      // Refresh reports and counts
      await fetchCloudReportsCached(true);
      await loadReports();
      await loadCounts();
      setDeleteDialogOpen(false);
      setReportToDelete(null);
    } catch (error) {
      console.error("Failed to delete report:", error);
    } finally {
      setDeleting(false);
    }
  };

  // PDF Preview Modal state
  const [pdfPreviewOpen, setPdfPreviewOpen] = useState(false);
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState<string | null>(null);
  const [pdfTempId, setPdfTempId] = useState<string | null>(null);
  const [pdfPreviewFilename, setPdfPreviewFilename] = useState<string>("");
  const [pdfGenerating, setPdfGenerating] = useState(false);
  const [pdfPreviewReport, setPdfPreviewReport] = useState<SavedReport | null>(null);
  const [pdfError, setPdfError] = useState<string | null>(null);
  const [pdfIframeLoaded, setPdfIframeLoaded] = useState(false);

  // Safari's <embed> may not fire onLoad — clear the loading overlay after 3s max
  useEffect(() => {
    if (!pdfPreviewUrl || pdfIframeLoaded) return;
    const timer = setTimeout(() => setPdfIframeLoaded(true), 3000);
    return () => clearTimeout(timer);
  }, [pdfPreviewUrl, pdfIframeLoaded]);

  const handleClosePdfPreview = () => {
    setPdfPreviewOpen(false);
    // Ask backend to clean up the temp PDF (fire-and-forget)
    if (pdfTempId) {
      fetch(`/api/pdf/temp/${pdfTempId}`, { method: "DELETE" }).catch(() => {});
      setPdfTempId(null);
    }
    setPdfPreviewUrl(null);
    setPdfPreviewFilename("");
    setPdfPreviewReport(null);
    setPdfError(null);
    setPdfIframeLoaded(false);
  };

  const handleDownloadFromPreview = () => {
    if (!pdfTempId || !pdfPreviewFilename) return;
    // Download via ?download=true — backend serves with Content-Disposition: attachment
    const link = document.createElement("a");
    link.href = `/api/pdf/serve/${pdfTempId}?download=true`;
    link.download = pdfPreviewFilename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    // Note: backend no longer auto-deletes on download, cleanup happens on modal close
  };

  // Helper: build PDF request body for a report
  const buildPdfRequestBody = (report: SavedReport) => {
    const getNestedValue = (obj: any, path: string) =>
      path.split(".").reduce((current, key) => current?.[key], obj);

    const availableAnalystKeys = ANALYSTS.filter((analyst) => {
      const content = getNestedValue(report.result.reports, analyst.reportKey);
      return content && content.trim().length > 0;
    }).map((a) => a.key);

    if (availableAnalystKeys.length === 0) return null;

    // Detect report language from content
    const detectLang = (reports: any): "zh-TW" | "en" => {
      const traderPlan = reports?.trader_investment_plan;
      if (!traderPlan || typeof traderPlan !== "string") return "zh-TW";
      const chineseKeywords = ["買入", "賣出", "持有", "最終交易提案"];
      for (const kw of chineseKeywords) {
        if (traderPlan.includes(kw)) return "zh-TW";
      }
      const englishKeywords = ["buy", "sell", "hold", "final trading proposal"];
      const lower = traderPlan.toLowerCase();
      for (const kw of englishKeywords) {
        if (lower.includes(kw)) return "en";
      }
      return /[\u4e00-\u9fa5]/.test(traderPlan) ? "zh-TW" : "en";
    };

    return {
      analysts: availableAnalystKeys,
      ticker: report.ticker,
      analysis_date: report.analysis_date,
      reports: report.result.reports,
      price_data: report.result.price_data,
      price_stats: report.result.price_stats,
      language: detectLang(report.result.reports),
      deep_think_llm: report.result.deep_think_llm,
      quick_think_llm: report.result.quick_think_llm,
    };
  };

  const handleDownloadPdf = async (report: SavedReport) => {
    const requestBody = buildPdfRequestBody(report);
    if (!requestBody) {
      alert("此報告沒有可下載的分析師報告");
      return;
    }

    // Open preview modal immediately with loading state
    setPdfPreviewReport(report);
    setPdfTempId(null);
    setPdfPreviewUrl(null);
    setPdfPreviewFilename(`${report.ticker}_Report_${report.analysis_date}.pdf`);
    setPdfGenerating(true);
    setPdfError(null);
    setPdfIframeLoaded(false);
    setPdfPreviewOpen(true);

    try {
      // POST to generate endpoint — backend generates PDF, caches it, returns temp_id
      const response = await fetch("/api/pdf/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `PDF 產生失敗 (${response.status})`);
      }

      const { temp_id, filename } = await response.json();

      setPdfTempId(temp_id);
      setPdfPreviewUrl(`/api/pdf/serve/${temp_id}`);
      setPdfPreviewFilename(filename);
    } catch (error: any) {
      console.error("PDF generation error:", error);
      setPdfError(error.message || "PDF 產生失敗，請稍後再試");
    } finally {
      setPdfGenerating(false);
    }
  };

  return (
    <div>
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <div className="text-center relative animate-fade-in">
            <div className="absolute inset-0 gradient-bg-radial opacity-40 -z-10" />
            <h1 className="text-4xl font-bold mb-2 gradient-text-primary">
              {t.history.title}
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              {t.history.noHistory.replace(
                "尚無分析紀錄",
                "瀏覽已儲存的分析報告",
              )}
            </p>
          </div>

          {/* Pending Task Recovery Notice */}
          <PendingTaskRecovery />

          {/* Market Type Tabs */}
          <Tabs
            value={activeTab}
            onValueChange={(v: string) => setActiveTab(v as typeof activeTab)}
            className="w-full animate-slide-up animate-delay-200"
          >
            <TabsList className="grid w-full grid-cols-1 sm:grid-cols-3 h-auto gap-2">
              {(
                Object.keys(MARKET_LABELS) as Array<keyof typeof MARKET_LABELS>
              ).map((key) => (
                <TabsTrigger
                  key={key}
                  value={key}
                  className="py-2 sm:py-3 text-sm sm:text-base transition-all duration-300 hover:scale-105"
                >
                  <span className="mr-1 sm:mr-2">{MARKET_LABELS[key].label}</span>
                  <span className="px-1.5 sm:px-2 py-0.5 rounded-full bg-white/20 text-xs">
                    {counts[key]}
                  </span>
                </TabsTrigger>
              ))}
            </TabsList>

            {(
              Object.keys(MARKET_LABELS) as Array<keyof typeof MARKET_LABELS>
            ).map((marketType) => (
              <TabsContent key={marketType} value={marketType} className="mt-6">
                <div className="space-y-4">
                  {/* Refresh/Sync button */}
                  <div className="flex justify-end">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleRefresh}
                      disabled={loading || syncing}
                      className="gap-2"
                    >
                      <RefreshCw
                        className={`h-4 w-4 ${loading || syncing ? "animate-spin" : ""}`}
                      />
                      {syncing ? t.history.syncing : t.history.refresh}
                    </Button>
                  </div>

                  {/* Report List */}
                  {loading ? (
                    <div className="text-center py-12">
                      <RefreshCw className="h-8 w-8 animate-spin mx-auto text-gray-400" />
                      <p className="text-gray-500 mt-4">{t.history.loading}</p>
                    </div>
                  ) : reports.length === 0 ? (
                    <Card className="animate-fade-in">
                      <CardContent className="py-12 text-center">
                        <TrendingUp className="h-12 w-12 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
                        <p className="text-gray-500 dark:text-gray-400">
                          {t.history.noReportsFor}{" "}
                          {MARKET_LABELS[marketType].label}
                        </p>
                        <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
                          {t.history.afterAnalysisSave}
                        </p>
                        <Button
                          variant="outline"
                          className="mt-4"
                          onClick={() => router.push("/analysis")}
                        >
                          {t.home.startAnalysis}
                        </Button>
                      </CardContent>
                    </Card>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {reports.map((report) => (
                        <Card
                          key={report.id}
                          className="hover-lift animate-scale-up transition-all duration-300"
                        >
                          <CardHeader>
                            <CardTitle className="flex items-center justify-between">
                              <span className="text-xl font-bold gradient-text-primary">
                                {report.ticker}
                              </span>
                              <span className="text-xs px-3 py-1 rounded-2xl bg-gradient-to-r from-blue-100 to-blue-100 dark:from-blue-900/40 dark:to-blue-900/40 border-2 border-blue-200 dark:border-slate-600/30 text-blue-600 dark:text-blue-300 font-semibold shadow-[0_2px_0_rgba(147,197,253,0.5)]">
                                {MARKET_LABELS[report.market_type].label}
                              </span>
                            </CardTitle>
                            <CardDescription>
                              {t.history.analysisDate}：{report.analysis_date}
                            </CardDescription>
                          </CardHeader>
                          <CardContent>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              {t.history.savedAt}：
                              {format(
                                new Date(report.saved_at),
                                "yyyy/MM/dd HH:mm",
                                { locale: zhTW },
                              )}
                            </p>
                            {(() => {
                              const decision =
                                extractDecisionFromReport(report);
                              return (
                                <p className="text-sm mt-2">
                                  <span className="font-medium">
                                    {t.history.decision}：
                                  </span>
                                  <span
                                    className={`ml-1 font-semibold ${decision.color}`}
                                  >
                                    {decision.action}
                                  </span>
                                </p>
                              );
                            })()}
                            {(() => {
                              const deepName = getModelDisplayName(report.result?.deep_think_llm);
                              const quickName = getModelDisplayName(report.result?.quick_think_llm);
                              if (!deepName && !quickName) return null;
                              return (
                                <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                                  {deepName === quickName && deepName
                                    ? deepName
                                    : [deepName, quickName].filter(Boolean).join(" / ")}
                                </p>
                              );
                            })()}
                          </CardContent>
                          <CardFooter className="grid grid-cols-2 gap-2">
                            <Button
                              variant="default"
                              size="sm"
                              className="w-full gap-1"
                              onClick={() => handleViewReport(report)}
                            >
                              <Eye className="h-4 w-4" />
                              {t.history.view}
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              className="w-full gap-1"
                              onClick={() => handleDownloadPdf(report)}
                              disabled={pdfGenerating && pdfPreviewReport?.id === report.id}
                            >
                              {pdfGenerating && pdfPreviewReport?.id === report.id ? (
                                <>
                                  <Download className="h-4 w-4 animate-bounce" />
                                  {t.history.downloading}
                                </>
                              ) : (
                                <>
                                  <FileText className="h-4 w-4" />
                                  PDF
                                </>
                              )}
                            </Button>
                            
                            <Button
                              variant="outline"
                              size="sm"
                              className="col-span-2 w-full gap-2 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-800 hover:bg-blue-50 dark:hover:bg-blue-950/50"
                              onClick={() => router.push(`/history/chat?ticker=${report.ticker}&date=${report.analysis_date}&market=${report.market_type}`)}
                            >
                              <MessageCircle className="h-4 w-4" />
                              {t.chat?.title || "Report Chat"} — {t.chat?.allReports || "All Reports"}
                            </Button>
                            
                            <Button
                              variant="destructive"
                              size="sm"
                              className="col-span-2 w-full gap-1"
                              onClick={() => handleDeleteClick(report)}
                            >
                              <Trash2 className="h-4 w-4" />
                              {t.history.delete}
                            </Button>
                          </CardFooter>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t.history.confirmDeleteTitle}</DialogTitle>
            <DialogDescription>
              {t.history.confirmDeleteDesc}{" "}
              <strong>{reportToDelete?.ticker}</strong> {t.history.on}{" "}
              <strong>{reportToDelete?.analysis_date}</strong>?
              <br />
              <span className="text-red-500">{t.history.cannotUndo}</span>
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
              disabled={deleting}
            >
              {t.history.cancel}
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={deleting}
            >
              {deleting ? t.history.deleting : t.history.confirmDeleteBtn}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* PDF Preview Modal */}
      {pdfPreviewOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="relative bg-white dark:bg-gray-900 rounded-2xl shadow-2xl flex flex-col w-full max-w-5xl h-[90vh]">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200 dark:border-gray-700 shrink-0">
              <div className="flex items-center gap-2 min-w-0">
                <FileText className="h-5 w-5 text-blue-500 shrink-0" />
                <span className="text-sm font-semibold text-gray-700 dark:text-gray-200 truncate">
                  {pdfPreviewFilename}
                </span>
              </div>
              <button
                onClick={handleClosePdfPreview}
                className="ml-3 p-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors shrink-0"
                aria-label="Close preview"
              >
                <X className="h-5 w-5 text-gray-500" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 relative overflow-hidden bg-gray-100 dark:bg-gray-800">
              {/* Generating spinner */}
              {pdfGenerating && (
                <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-4 bg-white dark:bg-gray-900">
                  <div className="h-16 w-16 rounded-full border-4 border-blue-200 border-t-blue-600 animate-spin" />
                  <p className="text-gray-600 dark:text-gray-300 font-medium">
                    {locale === "zh-TW" ? "正在產生 PDF 報告…" : "Generating PDF report…"}
                  </p>
                  <p className="text-sm text-gray-400 dark:text-gray-500">
                    {locale === "zh-TW" ? "請稍候，通常需要 10–30 秒" : "This usually takes 10–30 seconds"}
                  </p>
                </div>
              )}

              {/* Error state */}
              {!pdfGenerating && pdfError && (
                <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-4 bg-white dark:bg-gray-900 p-8 text-center">
                  <p className="text-red-500 font-medium">
                    {locale === "zh-TW" ? "PDF 產生失敗" : "Failed to generate PDF"}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{pdfError}</p>
                  <Button
                    variant="outline"
                    onClick={() => pdfPreviewReport && handleDownloadPdf(pdfPreviewReport)}
                  >
                    {locale === "zh-TW" ? "重試" : "Retry"}
                  </Button>
                </div>
              )}

              {/* iframe loading overlay — shown until iframe fires onLoad */}
              {pdfPreviewUrl && !pdfIframeLoaded && !pdfGenerating && !pdfError && (
                <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-3 bg-white dark:bg-gray-900">
                  <div className="h-10 w-10 rounded-full border-4 border-blue-200 border-t-blue-600 animate-spin" />
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {locale === "zh-TW" ? "載入中…" : "Loading…"}
                  </p>
                </div>
              )}

              {/* Inline PDF embed — <embed> works in Safari; <iframe> does not */}
              {pdfPreviewUrl && (
                <embed
                  key={pdfPreviewUrl}
                  src={pdfPreviewUrl}
                  type="application/pdf"
                  className="w-full h-full"
                  onLoad={() => setPdfIframeLoaded(true)}
                />
              )}
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-end gap-3 px-5 py-4 border-t border-gray-200 dark:border-gray-700 shrink-0">
              <Button
                onClick={handleDownloadFromPreview}
                disabled={!pdfTempId || pdfGenerating || !!pdfError}
                className="gap-2 bg-blue-600 hover:bg-blue-700 text-white"
              >
                <Download className="h-4 w-4" />
                {locale === "zh-TW" ? "下載 PDF" : "Download PDF"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
