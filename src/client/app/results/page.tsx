"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ThreatSummary } from "@/components/results/threat-summary"
import { DefenseLayerCard } from "@/components/results/defense-layer-card"
import { SpectrogramDisplay } from "@/components/results/spectrogram-display"
import {
  Download,
  RefreshCw,
  Share2,
  AudioWaveform,
  BarChart3,
  Brain,
  MessageSquare,
  ArrowRight,
  Shield,
  Skull,
  CheckCircle,
  Lock,
} from "lucide-react"

const DETECTION_RESULTS = {
  overallScore: 94,
  verdict: "deepfake" as const,
  confidence: 97,
  layers: [
    {
      layer: 1,
      title: "Spectrogram Image Analysis",
      description: "Visual pattern recognition of audio frequency distribution over time",
      score: 96,
      status: "deepfake" as const,
      iconName: "wave" as const,
      details: [
        "Detected unnatural frequency harmonics at 2.4 kHz – 4.8 kHz range",
        "Spectral smearing indicates synthetic voice generation via neural vocoder",
        "Missing natural micro-variations in formant transitions",
        "Identified characteristic GAN artifact patterns in high-frequency bands",
        "Abnormal energy distribution in voiced consonants (B, D, G)",
      ],
    },
    {
      layer: 2,
      title: "Spectral Analysis",
      description: "Deep frequency-domain examination of audio characteristics",
      score: 92,
      status: "deepfake" as const,
      iconName: "chart" as const,
      details: [
        "Mel-frequency cepstral coefficients (MFCCs) show synthetic voice signatures",
        "Pitch contour analysis reveals machine-like precision — 0.3% jitter vs 3–5% human norm",
        "Fundamental frequency (F0) lacks natural shimmer and micro-perturbation",
        "Spectral flux patterns inconsistent with biological speech production",
        "Phase discontinuities typical of transformer-based TTS with speaker embedding",
      ],
    },
    {
      layer: 3,
      title: "Behavior & Liveness Detection",
      description: "Real-time behavioral patterns and liveness verification",
      score: 89,
      status: "deepfake" as const,
      iconName: "brain" as const,
      details: [
        "Response timing shows artificial consistency (±12 ms variance — humans average ±120 ms)",
        "Breathing patterns absent between speech segments",
        "No natural hesitations, filled pauses, or disfluencies detected",
        "Background noise floor is suspiciously clean — consistent with studio synthesis",
        "Lip-sync mismatch detected in video stream (audio-visual desynchronisation)",
      ],
    },
    {
      layer: 4,
      title: "Contextual Analysis",
      description: "Semantic and conversational coherence examination",
      score: 78,
      status: "suspicious" as const,
      iconName: "message" as const,
      details: [
        "Social engineering pattern detected: urgency + authority + exception request",
        'Classic pretexting: fabricated time-pressure ("CFO is waiting")',
        "Claimed approval from unavailable authority — unverifiable by design",
        "Response coherence score: 82% — language model-like consistency",
        "Vocabulary and phrasing shift detected mid-call (adaptation artefact)",
      ],
    },
  ],
}

// Map icon names to components (avoids Server→Client ReactNode serialisation issues)
const ICON_MAP = {
  wave: <AudioWaveform className="h-5 w-5" />,
  chart: <BarChart3 className="h-5 w-5" />,
  brain: <Brain className="h-5 w-5" />,
  message: <MessageSquare className="h-5 w-5" />,
} as const

export default function ResultsPage() {
  return (
    <div className="min-h-screen pt-28 pb-16">
      {/* Subtle background tint */}
      <div className="fixed inset-0 -z-10 bg-gradient-to-b from-red-500/5 via-background to-background pointer-events-none" />

      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">

        {/* ── Header ─────────────────────────────────────────────── */}
        <div className="mb-10 text-center space-y-3">
          <span className="inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-bold bg-red-100 text-red-700 border border-red-200">
            <Shield className="h-4 w-4" />
            Red Team vs Blue Team — Detection Report
          </span>
          <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-foreground text-balance">
            Voice Authentication Analysis
          </h1>
          <p className="mx-auto max-w-2xl text-muted-foreground leading-relaxed">
            The Blue Team (interviewer) successfully identified a Red Team voice-cloning attack using DeepMeet Guard&apos;s 4-layer defense system.
          </p>

          {/* Team outcome strip */}
          <div className="flex items-stretch justify-center gap-0 max-w-md mx-auto rounded-2xl overflow-hidden border border-border/60 shadow-sm mt-4">
            <div className="flex-1 flex items-center gap-2 px-4 py-3 bg-indigo-50">
              <Shield className="h-5 w-5 text-indigo-600 flex-shrink-0" />
              <div className="text-left">
                <p className="text-xs font-black text-indigo-700 uppercase tracking-widest">Blue Team</p>
                <p className="text-xs text-indigo-500">Defender — Human Interviewer</p>
              </div>
              <CheckCircle className="h-5 w-5 text-emerald-500 ml-auto flex-shrink-0" />
            </div>
            <div className="w-px bg-border" />
            <div className="flex-1 flex items-center gap-2 px-4 py-3 bg-red-50">
              <Skull className="h-5 w-5 text-red-600 flex-shrink-0" />
              <div className="text-left">
                <p className="text-xs font-black text-red-700 uppercase tracking-widest">Red Team</p>
                <p className="text-xs text-red-500">Attacker — Cloned Voice</p>
              </div>
              <span className="ml-auto text-xs font-bold text-red-600 bg-red-100 border border-red-200 px-2 py-0.5 rounded-full flex-shrink-0">BLOCKED</span>
            </div>
          </div>
        </div>

        {/* ── Threat Summary ──────────────────────────────────────── */}
        <div className="mb-8">
          <ThreatSummary
            overallScore={DETECTION_RESULTS.overallScore}
            verdict={DETECTION_RESULTS.verdict}
            confidence={DETECTION_RESULTS.confidence}
          />
        </div>

        {/* ── Spectrogram Comparison ──────────────────────────────── */}
        <div className="mb-8 space-y-3">
          <h2 className="flex items-center gap-2 text-xl font-bold text-foreground">
            <AudioWaveform className="h-5 w-5 text-primary" />
            Spectrogram Comparison
          </h2>
          <div className="grid gap-4 md:grid-cols-2">
            <SpectrogramDisplay isDeepfake={false} label="Reference — Authentic Human Voice" />
            <SpectrogramDisplay isDeepfake={true} label="Red Team Sample — AI-Synthesized Voice" />
          </div>
          <p className="text-center text-sm text-muted-foreground">
            Authentic voices show organic frequency variation. Deepfakes exhibit unnatural regularity and GAN banding artefacts.
          </p>
        </div>

        {/* ── 4 Defense Layers ────────────────────────────────────── */}
        <div className="mb-8 space-y-3">
          <h2 className="flex items-center gap-2 text-xl font-bold text-foreground">
            <Lock className="h-5 w-5 text-primary" />
            4-Layer Defense Analysis
          </h2>
          <p className="text-sm text-muted-foreground">Click each layer to expand detailed findings.</p>
          <div className="space-y-3">
            {DETECTION_RESULTS.layers.map((layer) => (
              <DefenseLayerCard
                key={layer.layer}
                layer={layer.layer}
                title={layer.title}
                description={layer.description}
                score={layer.score}
                status={layer.status}
                details={layer.details}
                icon={ICON_MAP[layer.iconName]}
                delay={layer.layer * 150}
              />
            ))}
          </div>
        </div>

        {/* ── Technical Summary ───────────────────────────────────── */}
        <div className="mb-8 glass-card p-6 space-y-4">
          <h3 className="font-bold text-foreground flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-primary" />
            Technical Summary
          </h3>
          <div className="grid gap-4 sm:grid-cols-3">
            {[
              { label: "Detection Method", value: "Multi-Modal Neural Analysis" },
              { label: "Processing Time", value: "2.34 seconds" },
              { label: "Model Version", value: "DeepGuard v3.2.1" },
            ].map((item) => (
              <div key={item.label}>
                <p className="text-xs text-muted-foreground mb-1">{item.label}</p>
                <p className="text-sm font-semibold text-foreground">{item.value}</p>
              </div>
            ))}
          </div>
          <div className="border-t border-border/50 pt-4">
            <p className="text-xs text-muted-foreground mb-1">Suspected Generation Method</p>
            <p className="text-sm font-semibold text-red-600">
              Real-Time Voice Cloning — Transformer-based TTS with speaker embedding extraction (likely ElevenLabs / XTTS architecture)
            </p>
          </div>
          <div className="border-t border-border/50 pt-4">
            <p className="text-xs text-muted-foreground mb-1">Attack Technique</p>
            <p className="text-sm font-semibold text-foreground">
              Vishing + Deepfake Voice — Social engineering with fabricated urgency, impersonating a verified employee to gain unauthorised system access.
            </p>
          </div>
        </div>

        {/* ── Actions ─────────────────────────────────────────────── */}
        <div className="glass-card p-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h3 className="font-bold text-foreground">What&apos;s Next?</h3>
              <p className="text-sm text-muted-foreground">Download the report or run a new detection session.</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button variant="outline" className="gap-2">
                <Download className="h-4 w-4" />
                Download Report
              </Button>
              <Button variant="outline" className="gap-2">
                <Share2 className="h-4 w-4" />
                Share
              </Button>
              <Button asChild className="gap-2 bg-gradient-to-r from-primary to-violet-500 shadow-lg shadow-primary/25">
                <Link href="/simulation/meeting">
                  <RefreshCw className="h-4 w-4" />
                  New Session
                </Link>
              </Button>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center">
          <Link href="/about" className="inline-flex items-center gap-2 text-sm text-primary hover:underline">
            Learn how our 4-layer detection system works
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </div>
  )
}
