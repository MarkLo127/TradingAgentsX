"use client";

import Link from "next/link";
import Image from "next/image";
import {
  Bot,
  Globe,
  Wrench,
  BarChart3,
  RefreshCw,
  Brain,
  Palette,
  Container,
  Download,
  TrendingUp,
  TrendingDown,
  Users,
  Shield,
  Zap,
  Database,
  Lock,
  CheckCircle2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { AgentFlowDiagram } from "@/components/AgentFlowDiagram";
import { ImmersivePortalHero } from "@/components/home/ImmersivePortalHero";
import { InteractiveCard } from "@/components/home/InteractiveCard";
import { ScrollReveal } from "@/components/home/ScrollReveal";
import { useLanguage } from "@/contexts/LanguageContext";

export default function HomePage() {
  const { t } = useLanguage();

  return (
    <div>
      {/* Immersive scroll-driven portal hero */}
      <ImmersivePortalHero />

      {/* Content flows straight on from the dive — same background, no seam */}
      <div className="relative z-10 overflow-x-clip">
        <div className="container mx-auto px-4 pt-12 pb-12">

        {/* Core Features Section */}
        <ScrollReveal from="left" className="mb-32 md:mb-40">
          <SectionHeading eyebrow={t.home.subtitle} title={t.home.coreFeatures} />
          <p className="text-center text-blue-500/80 dark:text-blue-400/80 mb-8 max-w-3xl mx-auto font-medium">
            {t.home.coreFeaturesDesc}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard title={t.home.features.multiAgent} description={t.home.features.multiAgentDesc} icon={<Bot className="w-6 h-6 text-blue-500" />} />
            <FeatureCard title={t.home.features.multiModel} description={t.home.features.multiModelDesc} icon={<Globe className="w-6 h-6 text-pink-500" />} />
            <FeatureCard title={t.home.features.customEndpoint} description={t.home.features.customEndpointDesc} icon={<Wrench className="w-6 h-6 text-blue-500" />} />
            <FeatureCard title={t.home.features.fullAnalysis} description={t.home.features.fullAnalysisDesc} icon={<BarChart3 className="w-6 h-6 text-pink-500" />} />
            <FeatureCard title={t.home.features.structuredDecision} description={t.home.features.structuredDecisionDesc} icon={<RefreshCw className="w-6 h-6 text-blue-500" />} />
            <FeatureCard title={t.home.features.longTermMemory} description={t.home.features.longTermMemoryDesc} icon={<Brain className="w-6 h-6 text-pink-500" />} />
            <FeatureCard title={t.home.features.modernUI} description={t.home.features.modernUIDesc} icon={<Palette className="w-6 h-6 text-blue-500" />} />
            <FeatureCard title={t.home.features.oneClickDeploy} description={t.home.features.oneClickDeployDesc} icon={<Container className="w-6 h-6 text-pink-500" />} />
            <FeatureCard title={t.home.features.reportDownload} description={t.home.features.reportDownloadDesc} icon={<Download className="w-6 h-6 text-blue-500" />} />
          </div>
        </ScrollReveal>

        {/* 12 Professional Agents Section */}
        <ScrollReveal from="right" className="mb-32 md:mb-40">
          <SectionHeading eyebrow={t.home.subtitle} title={t.home.professionalAgents} />
          <p className="text-center text-blue-500/80 dark:text-blue-400/80 mb-8 max-w-3xl mx-auto font-medium">
            {t.home.professionalAgentsDesc}
          </p>

          {/* Analyst Team */}
          <div className="mb-8">
            <h3 className="text-xl font-bold mb-4 text-blue-700 dark:text-blue-300 flex items-center gap-2" style={{ fontFamily: 'Nunito, sans-serif' }}>
              <BarChart3 className="w-5 h-5" />
              {t.home.analystsTeamTitle}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <AgentCard name={t.agents.market_analyst} role={t.agents.market_analyst_role} description={t.agents.market_analyst_desc} />
              <AgentCard name={t.agents.social_analyst} role={t.agents.social_analyst_role} description={t.agents.social_analyst_desc} />
              <AgentCard name={t.agents.news_analyst} role={t.agents.news_analyst_role} description={t.agents.news_analyst_desc} />
              <AgentCard name={t.agents.fundamentals_analyst} role={t.agents.fundamentals_analyst_role} description={t.agents.fundamentals_analyst_desc} />
            </div>
          </div>

          {/* Research Team */}
          <div className="mb-8">
            <h3 className="text-xl font-bold mb-4 text-blue-700 dark:text-blue-300 flex items-center gap-2" style={{ fontFamily: 'Nunito, sans-serif' }}>
              <Brain className="w-5 h-5" />
              {t.home.researchTeamTitle}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <AgentCard name={t.agents.bull_researcher} role={t.agents.bull_researcher_role} description={t.agents.bull_researcher_desc} accent="bull" />
              <AgentCard name={t.agents.bear_researcher} role={t.agents.bear_researcher_role} description={t.agents.bear_researcher_desc} accent="bear" />
              <AgentCard name={t.agents.research_manager} role={t.agents.research_manager_role} description={t.agents.research_manager_desc} />
            </div>
          </div>

          {/* Trading Team */}
          <div className="mb-8">
            <h3 className="text-xl font-bold mb-4 text-blue-700 dark:text-blue-300 flex items-center gap-2" style={{ fontFamily: 'Nunito, sans-serif' }}>
              <TrendingUp className="w-5 h-5" />
              {t.home.tradingTeamTitle}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-1 gap-4 max-w-md">
              <AgentCard name={t.agents.trader} role={t.agents.trader_role} description={t.agents.trader_desc} />
            </div>
          </div>

          {/* Risk Management Team */}
          <div className="mb-8">
            <h3 className="text-xl font-bold mb-4 text-blue-700 dark:text-blue-300 flex items-center gap-2" style={{ fontFamily: 'Nunito, sans-serif' }}>
              <Shield className="w-5 h-5" />
              {t.home.riskTeamTitle}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <AgentCard name={t.agents.aggressive_debator} role={t.agents.aggressive_debator_role} description={t.agents.aggressive_debator_desc} />
              <AgentCard name={t.agents.conservative_debator} role={t.agents.conservative_debator_role} description={t.agents.conservative_debator_desc} />
              <AgentCard name={t.agents.neutral_debator} role={t.agents.neutral_debator_role} description={t.agents.neutral_debator_desc} />
              <AgentCard name={t.agents.risk_manager} role={t.agents.risk_manager_role} description={t.agents.risk_manager_desc} />
            </div>
          </div>
        </ScrollReveal>

        {/* Agent Flow Diagram Section */}
        <ScrollReveal from="left" className="mb-32 md:mb-40">
          <SectionHeading title={t.home.workflowTitle} />
          <p className="text-center text-blue-500/80 dark:text-blue-400/80 mb-8 max-w-3xl mx-auto font-medium">
            {t.home.workflowDescription}
          </p>
          <AgentFlowDiagram />
        </ScrollReveal>

        {/* LLM Support Section */}
        <ScrollReveal from="right" className="mb-32 md:mb-40">
          <SectionHeading title={t.home.llmSupport} />
          <p className="text-center text-blue-500/80 dark:text-blue-400/80 mb-8 max-w-3xl mx-auto font-medium">
            {t.home.llmSupportDesc}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <LLMProviderCard name="OpenAI" models={["GPT-5.6 Sol", "GPT-5.6 Terra", "GPT-5.6 Luna"]} />
            <LLMProviderCard name="Anthropic" models={["Claude Fable 5","Claude Opus 4.8","Claude Sonnet 5","Claude Haiku 4.5"]} />
            <LLMProviderCard name="Google Gemini" models={["Gemini 3.5 Flash","Gemini 3.1 Flash-Lite"]} />
            <LLMProviderCard name="Grok (xAI)" models={["Grok 4.5","Grok 4.3","Grok 4.20","Grok 4.20 (Non-Reasoning)"]} />
            <LLMProviderCard name="DeepSeek" models={["Deepseek V4 Pro", "Deepseek V4 Flash"]} />
            <LLMProviderCard name="Qwen (Alibaba)" models={["Qwen3.7-Max","Qwen3.7-Plus","Qwen3.5-Flash"]} />
          </div>
          <div className="mt-6 text-center">
            <p className="text-sm text-blue-500/70 dark:text-blue-400/70 font-medium">
              {t.home.llmFeatures}
            </p>
          </div>
        </ScrollReveal>

        {/* Workflow Section */}
        <ScrollReveal from="left" className="mb-32 md:mb-40">
          <SectionHeading title={t.home.workflowTitle} />
          <Card className="shadow-none">
            <CardContent className="pt-6">
              <div className="space-y-4">
                <WorkflowStep number={1} title={t.home.processSteps.dataCollection.title} description={t.home.processSteps.dataCollection.description} />
                <WorkflowStep number={2} title={t.home.processSteps.analysts.title} description={t.home.processSteps.analysts.description} />
                <WorkflowStep number={3} title={t.home.processSteps.researchers.title} description={t.home.processSteps.researchers.description} />
                <WorkflowStep number={4} title={t.home.processSteps.trader.title} description={t.home.processSteps.trader.description} />
                <WorkflowStep number={5} title={t.home.processSteps.risk.title} description={t.home.processSteps.risk.description} />
                <WorkflowStep number={6} title={t.home.processSteps.finalDecision.title} description={t.home.processSteps.finalDecision.description} />
              </div>
            </CardContent>
          </Card>
        </ScrollReveal>

        {/* Technical Highlights */}
        <ScrollReveal from="right" className="mb-32 md:mb-40">
          <SectionHeading title={t.home.techHighlights} />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <TechnicalCard title={t.home.dynamicResearch} features={t.home.dynamicResearchFeatures} icon={<Zap className="w-5 h-5 text-blue-500" />} />
            <TechnicalCard title={t.home.memorySystem} features={t.home.memorySystemFeatures} icon={<Database className="w-5 h-5 text-pink-500" />} />
            <TechnicalCard title={t.home.realTimeData} features={t.home.realTimeDataFeatures} icon={<TrendingUp className="w-5 h-5 text-blue-500" />} />
            <TechnicalCard title={t.home.fullApiSupport} features={t.home.fullApiSupportFeatures} icon={<Lock className="w-5 h-5 text-pink-500" />} />
          </div>
        </ScrollReveal>

        {/* Call to Action Section */}
        <ScrollReveal className="relative overflow-hidden rounded-[2.5rem] bg-gradient-to-br from-blue-600 via-cyan-500 to-teal-400 text-center py-20 px-6 mt-8 shadow-[0_20px_60px_-20px_rgba(6,182,212,0.5)]">
          <div className="absolute inset-0 gradient-shimmer bg-[linear-gradient(110deg,transparent_30%,rgba(255,255,255,0.18)_50%,transparent_70%)]" />
          <div className="relative">
            <h2
              className="text-3xl sm:text-4xl font-black mb-4 text-white drop-shadow-[0_2px_8px_rgba(0,0,0,0.2)]"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              {t.home.readyToStart}
            </h2>
            <p className="text-lg text-white/90 mb-10 max-w-2xl mx-auto font-medium drop-shadow-[0_1px_4px_rgba(0,0,0,0.15)]">
              {t.home.ctaDescription}
            </p>
            <Link href="/analysis">
              <Button size="lg" variant="outline" className="text-lg px-10 py-4 animate-clay-bounce">
                {t.home.startAnalysis} →
              </Button>
            </Link>
          </div>
        </ScrollReveal>
        </div>
      </div>
    </div>
  );
}

/* ── Shared sub-components ── */

function SectionHeading({ title, eyebrow }: { title: string; eyebrow?: string }) {
  return (
    <div className="text-center mb-4">
      {eyebrow && (
        <span className="inline-block mb-3 text-xs font-bold tracking-[0.2em] uppercase text-cyan-600/80 dark:text-cyan-400/80">
          {eyebrow}
        </span>
      )}
      <h2
        className="text-2xl sm:text-3xl md:text-4xl font-black gradient-text-primary"
        style={{ fontFamily: 'Nunito, sans-serif' }}
      >
        {title}
      </h2>
      <div className="mx-auto mt-4 h-1 w-14 rounded-full bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-300" />
    </div>
  );
}

function FeatureCard({ title, description, icon }: { title: string; description: string; icon: React.ReactNode }) {
  return (
    <InteractiveCard>
    <Card className="animate-slide-up h-full">
      <CardHeader>
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-100 to-blue-100 dark:from-blue-900/40 dark:to-blue-900/40 flex items-center justify-center mb-2 shadow-[0_2px_0_rgba(147,197,253,0.5),0_4px_12px_rgba(37,99,235,0.1)]">
          {icon}
        </div>
        <CardTitle className="text-base text-blue-800 dark:text-blue-200">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-blue-500/80 dark:text-blue-400/70">{description}</p>
      </CardContent>
    </Card>
    </InteractiveCard>
  );
}

function AgentCard({ name, role, description, accent }: { name: string; role: string; description: string; accent?: "bull" | "bear" }) {
  const accentClass =
    accent === "bull"
      ? "border-emerald-300 dark:border-emerald-600/40"
      : accent === "bear"
      ? "border-rose-300 dark:border-rose-600/40"
      : "";

  return (
    <InteractiveCard>
    <Card className={`animate-scale-up h-full ${accentClass}`}>
      <CardHeader>
        <div className="flex items-center gap-2">
          {accent === "bull" && <TrendingUp className="w-4 h-4 text-emerald-500" />}
          {accent === "bear" && <TrendingDown className="w-4 h-4 text-rose-500" />}
          {!accent && <Users className="w-4 h-4 text-blue-400" />}
          <CardTitle className="text-sm text-blue-800 dark:text-blue-200">{name}</CardTitle>
        </div>
        <CardDescription className="text-xs text-blue-400 dark:text-blue-400">{role}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-xs text-blue-500/80 dark:text-blue-400/70">{description}</p>
      </CardContent>
    </Card>
    </InteractiveCard>
  );
}

function LLMProviderCard({ name, models }: { name: string; models: string[] }) {
  const logoMap: Record<string, string> = {
    OpenAI: "/logos/openai.svg",
    Anthropic: "/logos/claude-color.svg",
    "Google Gemini": "/logos/gemini-color.svg",
    "Grok (xAI)": "/logos/grok.svg",
    DeepSeek: "/logos/deepseek-color.svg",
    "Qwen (Alibaba)": "/logos/qwen-color.svg",
  };
  const logoSrc = logoMap[name];

  return (
    <InteractiveCard>
    <Card className="animate-slide-up animate-delay-100 h-full">
      <CardHeader>
        <div className="flex items-center gap-3">
          {logoSrc ? (
            <div className="w-10 h-10 rounded-2xl bg-white dark:bg-blue-900/30 flex items-center justify-center shadow-[0_2px_0_rgba(147,197,253,0.4),0_4px_10px_rgba(37,99,235,0.08)] flex-shrink-0">
              <Image src={logoSrc} alt={`${name} logo`} width={28} height={28} className="object-contain" />
            </div>
          ) : (
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-100 to-blue-100 dark:from-blue-900/40 dark:to-blue-900/40 flex items-center justify-center shadow-[0_2px_0_rgba(147,197,253,0.4)] flex-shrink-0">
              <Globe className="w-5 h-5 text-blue-500" />
            </div>
          )}
          <CardTitle className="text-base text-blue-800 dark:text-blue-200">{name}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <ul className="space-y-1.5">
          {models.map((model, i) => (
            <li key={i} className="flex items-center gap-2 text-xs text-blue-500/80 dark:text-blue-400/70">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" />
              {model}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
    </InteractiveCard>
  );
}

function TechnicalCard({ title, features, icon }: { title: string; features: string[]; icon: React.ReactNode }) {
  return (
    <InteractiveCard>
    <Card className="animate-slide-up animate-delay-300 h-full">
      <CardHeader>
        <div className="flex items-center gap-2">
          {icon}
          <CardTitle className="text-base text-blue-800 dark:text-blue-200">{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {features.map((feature, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-blue-500/80 dark:text-blue-400/70">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
              {feature}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
    </InteractiveCard>
  );
}

function WorkflowStep({ number, title, description }: { number: number; title: string; description: string }) {
  return (
    <div className="flex gap-4 items-start">
      <div className="flex-shrink-0 w-9 h-9 rounded-2xl bg-gradient-to-br from-blue-400 to-blue-600 text-white flex items-center justify-center font-black text-sm shadow-[0_3px_0_rgba(30,64,175,0.4),0_6px_16px_rgba(37,99,235,0.3)]" style={{ fontFamily: 'Nunito, sans-serif' }}>
        {number}
      </div>
      <div>
        <h4 className="font-bold mb-1 text-blue-800 dark:text-blue-200" style={{ fontFamily: 'Nunito, sans-serif' }}>{title}</h4>
        <p className="text-sm text-blue-500/80 dark:text-blue-400/70">{description}</p>
      </div>
    </div>
  );
}
