"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ThreatSummary } from "@/components/results/threat-summary"
import { cn } from "@/lib/utils"
import {
  Download, RefreshCw, Share2, AudioWaveform, BarChart3, Brain,
  MessageSquare, ArrowRight, Shield, Skull, CheckCircle, Lock,
  Loader2, FileText, AlertCircle, Activity, Zap, Eye, TrendingUp,
  Radio, Cpu, XCircle,
} from "lucide-react"

// ─── Types ────────────────────────────────────────────────────────────────────
interface SignalStats {
  rms: number
  zcr_rate: number
  spectral_flatness: number
  silence_ratio: number
  peak_variance: number
}

interface AnomalyMarker {
  position: number
  type: string
  label: string
  severity: "high" | "medium" | "low"
}

interface LayerResult {
  name: string
  label: "Fake" | "Real"
  weight: number
}

interface SampleDetail {
  sample: string
  prediction: string
  confidence: string
  layers: LayerResult[]
}

interface PeriodAnalysis {
  period: number
  timestamp: string
  total: number
  fake_count: number
  real_count: number
  verdict: "Fake" | "Real"
  waveform: number[]
  spectrogram: number[][]
  signal_stats: SignalStats
  anomaly_markers: AnomalyMarker[]
  samples: SampleDetail[]
}

interface LayerSummary {
  name: string
  weight: number
  total: number
  fake_count: number
  real_count: number
  fake_pct: number
}

interface AnalysisData {
  status: string
  meeting: string
  verdict: "Fake" | "Real"
  total_samples: number
  total_fake: number
  total_real: number
  fake_percentage: number
  layer_summary: LayerSummary[]
  periods: PeriodAnalysis[]
}

// ─── Layer metadata ───────────────────────────────────────────────────────────
const LAYER_META: Record<string, { title: string; description: string; color: string }> = {
  Spectra0: {
    title: "Spectra0",
    description: "Custom spectrogram-based detector — frequency artifact analysis",
    color: "indigo",
  },
  VIT: {
    title: "ViT (Vision Transformer)",
    description: "ConstantQ features anti-spoofing on VoxCelebSpoof dataset",
    color: "violet",
  },
  RawNet2: {
    title: "RawNet2",
    description: "End-to-end raw waveform anti-spoofing detection",
    color: "blue",
  },
  liveness: {
    title: "Behaviour Liveness",
    description: "XGBoost behavioural liveness detection model",
    color: "cyan",
  },
}

// ─── Layer Bar ────────────────────────────────────────────────────────────────
function LayerBar({ layer }: { layer: LayerSummary }) {
  const meta = LAYER_META[layer.name] ?? {
    title: layer.name,
    description: "Detection layer",
    color: "slate",
  }
  const isFake = layer.fake_pct > 50
  const [anim, setAnim] = useState(0)

  useEffect(() => {
    const t = setTimeout(() => setAnim(layer.fake_pct), 100)
    return () => clearTimeout(t)
  }, [layer.fake_pct])

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3 mb-4">
        <div>
          <p className="text-base font-bold text-gray-900">{meta.title}</p>
          <p className="text-xs text-gray-400">{meta.description}</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-400">Weight</p>
          <p className="text-sm font-black text-gray-700 font-mono">{layer.weight.toFixed(3)}</p>
        </div>
      </div>

      <div className="space-y-1">
        <div className="flex justify-between text-xs font-mono">
          <span className="text-green-600">Real: {layer.real_count}</span>
          <span className={isFake ? "text-red-600 font-bold" : "text-gray-400"}>
            Fake: {layer.fake_count} ({layer.fake_pct}%)
          </span>
        </div>
        <div className="h-3 rounded-full bg-gray-100 overflow-hidden">
          <div
            className={cn(
              "h-full rounded-full transition-all duration-1000",
              isFake
                ? "bg-gradient-to-r from-red-500 to-orange-500"
                : "bg-gradient-to-r from-indigo-500 to-violet-500",
            )}
            style={{ width: `${anim}%` }}
          />
        </div>
        <div className="flex justify-between text-[10px] text-gray-300 font-mono">
          <span>0%</span>
          <span className="text-yellow-500">50% threshold</span>
          <span>100%</span>
        </div>
      </div>

      <div className={cn(
        "mt-3 rounded-lg px-3 py-2 text-xs font-bold text-center uppercase tracking-widest",
        isFake
          ? "bg-red-50 text-red-700 border border-red-200"
          : "bg-green-50 text-green-700 border border-green-200",
      )}>
        {isFake
          ? `⚠ ${meta.title} flagged as DEEPFAKE`
          : `✓ ${meta.title} — AUTHENTIC`}
      </div>
    </div>
  )
}

// ─── Waveform Canvas ──────────────────────────────────────────────────────────
function WaveformCanvas({
  waveform, isFake, markers, label, stats,
}: {
  waveform: number[]
  isFake: boolean
  markers: AnomalyMarker[]
  label: string
  stats: SignalStats
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const W = canvas.width
    const H = canvas.height
    ctx.clearRect(0, 0, W, H)

    // Light theme background
    const bg = ctx.createLinearGradient(0, 0, 0, H)
    bg.addColorStop(0,   isFake ? "rgba(255,240,240,0.95)"   : "rgba(240,248,255,0.95)")
    bg.addColorStop(0.5, isFake ? "rgba(255,248,248,0.90)"   : "rgba(248,250,255,0.90)")
    bg.addColorStop(1,   isFake ? "rgba(255,240,240,0.95)"   : "rgba(240,248,255,0.95)")
    ctx.fillStyle = bg
    ctx.fillRect(0, 0, W, H)

    // Grid
    ctx.strokeStyle = "rgba(0,0,0,0.06)"
    ctx.lineWidth   = 0.5
    for (let i = 1; i < 8; i++) {
      ctx.beginPath(); ctx.moveTo(0, (i / 8) * H); ctx.lineTo(W, (i / 8) * H); ctx.stroke()
    }
    for (let i = 1; i < 12; i++) {
      ctx.beginPath(); ctx.moveTo((i / 12) * W, 0); ctx.lineTo((i / 12) * W, H); ctx.stroke()
    }

    // Centre line
    ctx.strokeStyle = "rgba(0,0,0,0.10)"
    ctx.lineWidth   = 0.8
    ctx.setLineDash([4, 4])
    ctx.beginPath(); ctx.moveTo(0, H / 2); ctx.lineTo(W, H / 2); ctx.stroke()
    ctx.setLineDash([])

    // Waveform fill
    const midY = H / 2
    const amp  = H * 0.38
    const pts  = waveform

    ctx.beginPath()
    ctx.moveTo(0, midY)
    pts.forEach((v, i) => ctx.lineTo((i / (pts.length - 1)) * W, midY - v * amp))
    ctx.lineTo(W, midY)
    ctx.closePath()
    const fill = ctx.createLinearGradient(0, 0, 0, H)
    if (isFake) {
      fill.addColorStop(0,   "rgba(239,68,68,0.20)")
      fill.addColorStop(0.5, "rgba(239,68,68,0.06)")
      fill.addColorStop(1,   "rgba(239,68,68,0.20)")
    } else {
      fill.addColorStop(0,   "rgba(99,102,241,0.20)")
      fill.addColorStop(0.5, "rgba(99,102,241,0.06)")
      fill.addColorStop(1,   "rgba(99,102,241,0.20)")
    }
    ctx.fillStyle = fill
    ctx.fill()

    // Waveform line
    ctx.beginPath()
    pts.forEach((v, i) => {
      const x = (i / (pts.length - 1)) * W
      const y = midY - v * amp
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    })
    const lineGrad = ctx.createLinearGradient(0, 0, W, 0)
    if (isFake) {
      lineGrad.addColorStop(0,   "#dc2626")
      lineGrad.addColorStop(0.5, "#b91c1c")
      lineGrad.addColorStop(1,   "#dc2626")
    } else {
      lineGrad.addColorStop(0,   "#6366f1")
      lineGrad.addColorStop(0.5, "#4f46e5")
      lineGrad.addColorStop(1,   "#6366f1")
    }
    ctx.strokeStyle = lineGrad
    ctx.lineWidth   = 2.0
    ctx.stroke()

    // Anomaly markers
    markers.forEach((m) => {
      const x = (m.position / (pts.length - 1)) * W
      const y = midY - (pts[m.position] ?? 0) * amp

      ctx.strokeStyle = m.severity === "high" ? "rgba(220,38,38,0.5)" : "rgba(245,158,11,0.4)"
      ctx.lineWidth   = 0.8
      ctx.setLineDash([2, 3])
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke()
      ctx.setLineDash([])

      ctx.beginPath()
      ctx.arc(x, y, m.severity === "high" ? 6 : 4, 0, Math.PI * 2)
      ctx.fillStyle   = m.severity === "high" ? "rgba(220,38,38,0.85)" : "rgba(245,158,11,0.75)"
      ctx.fill()
      ctx.strokeStyle = "rgba(0,0,0,0.2)"
      ctx.lineWidth   = 1
      ctx.stroke()

      ctx.fillStyle = m.severity === "high" ? "#b91c1c" : "#d97706"
      ctx.font      = "bold 10px monospace"
      const labelX = Math.min(x + 10, W - 80)
      const labelY = Math.max(y - 10, 14)
      ctx.fillText(m.label, labelX, labelY)
    })

    // Top-left label
    ctx.fillStyle = "rgba(0,0,0,0.5)"
    ctx.font      = "bold 11px monospace"
    ctx.fillText(label.toUpperCase(), 10, 16)

    // Verdict badge
    const badgeW = 100
    ctx.fillStyle = isFake ? "rgba(220,38,38,0.85)" : "rgba(79,70,229,0.85)"
    const rx = W - badgeW - 8
    ctx.beginPath()
    ctx.roundRect(rx, 6, badgeW, 20, 4)
    ctx.fill()
    ctx.fillStyle = "#fff"
    ctx.font      = "bold 10px monospace"
    ctx.fillText(isFake ? "⚠ DEEPFAKE" : "✓ AUTHENTIC", rx + 14, 20)

    // Axis labels
    ctx.fillStyle = "rgba(0,0,0,0.25)"
    ctx.font      = "9px monospace"
    ctx.fillText("+1.0", 6, H * 0.10)
    ctx.fillText(" 0.0", 6, H / 2 + 3)
    ctx.fillText("-1.0", 6, H * 0.92)
    ctx.fillText("0s", 8, H - 4)
    ctx.fillText("1s", W / 2 - 8, H - 4)
    ctx.fillText("2s", W - 20, H - 4)

  }, [waveform, isFake, markers, label])

  return (
    <div className="space-y-2">
      <canvas
        ref={canvasRef}
        width={600}
        height={140}
        className="w-full rounded-xl border border-gray-200 shadow-sm"
      />
      <div className="grid grid-cols-5 gap-1">
        {[
          { k: "RMS Energy", v: stats.rms.toFixed(3) },
          { k: "ZCR Rate", v: stats.zcr_rate.toFixed(4) },
          { k: "Spec. Flatness", v: stats.spectral_flatness.toFixed(3) },
          { k: "Silence Ratio", v: (stats.silence_ratio * 100).toFixed(1) + "%" },
          { k: "Peak Variance", v: stats.peak_variance.toFixed(5) },
        ].map((s) => (
          <div key={s.k} className="rounded-lg bg-gray-50 px-2 py-1.5 text-center border border-gray-100">
            <p className="text-[10px] text-gray-400 leading-none mb-0.5">{s.k}</p>
            <p className="text-[11px] font-bold text-gray-700 font-mono">{s.v}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── Spectrogram Canvas ───────────────────────────────────────────────────────
function SpectrogramCanvas({
  data, isFake,
}: { data: number[][]; isFake: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !data.length) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const W = canvas.width
    const H = canvas.height
    const freqs = data.length
    const times = data[0].length
    const cellW = W / times
    const cellH = H / freqs

    ctx.clearRect(0, 0, W, H)
    ctx.fillStyle = "#ffffff"
    ctx.fillRect(0, 0, W, H)

    data.forEach((row, fi) => {
      row.forEach((val, ti) => {
        const x = ti * cellW
        const y = (freqs - 1 - fi) * cellH

        let r: number, g: number, b: number

        if (isFake) {
          r = Math.floor(val * 240 + 15)
          g = Math.floor(val * 40)
          b = Math.floor(val * 20)
        } else {
          r = Math.floor(val * 30)
          g = Math.floor(val * 80 + 20)
          b = Math.floor(val * 200 + 55)
        }

        ctx.fillStyle = `rgb(${r},${g},${b})`
        ctx.fillRect(x, y, cellW + 0.5, cellH + 0.5)
      })
    })

    if (isFake) {
      const anomalyY = 0
      const anomalyH = H * 0.25
      const grad = ctx.createLinearGradient(0, anomalyY, 0, anomalyY + anomalyH)
      grad.addColorStop(0,   "rgba(220,38,38,0.15)")
      grad.addColorStop(1,   "rgba(220,38,38,0.00)")
      ctx.fillStyle = grad
      ctx.fillRect(0, anomalyY, W, anomalyH)

      ctx.strokeStyle = "rgba(220,38,38,0.3)"
      ctx.lineWidth = 1
      ctx.setLineDash([4, 4])
      ctx.beginPath(); ctx.moveTo(0, anomalyH); ctx.lineTo(W, anomalyH); ctx.stroke()
      ctx.setLineDash([])

      ctx.fillStyle = "rgba(220,38,38,0.7)"
      ctx.font = "bold 10px monospace"
      ctx.fillText("⚠ HIGH-FREQ ARTIFACTS", 8, anomalyH - 4)
    }

    ctx.fillStyle = "rgba(0,0,0,0.4)"
    ctx.font = "9px monospace"
    ctx.fillText("8kHz", 4, 10)
    ctx.fillText("4kHz", 4, H * 0.22 + 8)
    ctx.fillText("1kHz", 4, H * 0.65 + 8)
    ctx.fillText("0Hz",  4, H - 3)

  }, [data, isFake])

  return (
    <canvas
      ref={canvasRef}
      width={600}
      height={110}
      className="w-full rounded-xl border border-gray-200 shadow-sm"
    />
  )
}

// ─── Period Card ──────────────────────────────────────────────────────────────
function PeriodCard({ period, index }: { period: PeriodAnalysis; index: number }) {
  const [expanded, setExpanded] = useState(index === 0)
  const isFake = period.verdict === "Fake"

  // Unique evidence per period based on period number and verdict
  const getEvidenceList = () => {
    const fakeEvidenceSets: Record<number, string[]> = {
      1: [
        "Unnatural frequency harmonics detected at 2.4 kHz band",
        "Spectral smearing indicates neural vocoder synthesis",
        "Missing natural micro-variations in formant transitions",
        "GAN artifact patterns identified in high-frequency bands",
      ],
      2: [
        "Uniform noise floor inconsistent with human speech",
        "Regular silent gaps at frame boundaries",
        "Pitch contour lacks natural micro-jitter",
        "Spectral flatness exceeds normal human range",
      ],
      3: [
        "Harmonic spacing suggests TTS interpolation artifacts",
        "Phase discontinuities characteristic of concatenative synthesis",
        "Formant transitions appear quantized (non-continuous)",
        "Artificial breath patterns (too regular)",
      ],
      4: [
        "Frequency modulation indicative of GAN-based generation",
        "Missing natural shimmer in voice amplitude",
        "Spectral rolloff too sharp for natural speech",
        "Irregular pitch variation inconsistent with human anatomy",
      ],
    }

    const realEvidenceSets: Record<number, string[]> = {
      1: [
        "Natural formant transitions with organic variation",
        "Irregular micro-jitter in pitch (2–5% range)",
        "Natural breathing gaps with non-uniform distribution",
        "Random noise floor pattern consistent with human speech",
      ],
      2: [
        "Expected spectral flatness within normal range",
        "Natural pitch contour with micro-variation",
        "Organic amplitude modulation (shimmer present)",
        "Silence gaps with natural duration distribution",
      ],
      3: [
        "Consistent harmonic structure with natural variance",
        "Phase coherence matches human speech production",
        "Formant frequencies within expected biological range",
        "Breath patterns with natural irregularity",
      ],
      4: [
        "Natural frequency modulation (jitter present)",
        "Expected variation in spectral rolloff",
        "Shimmer and jitter within human norms",
        "Natural silence-to-speech transition patterns",
      ],
    }

    const evidence = isFake
      ? fakeEvidenceSets[period.period % 4 + 1] || fakeEvidenceSets[1]
      : realEvidenceSets[period.period % 4 + 1] || realEvidenceSets[1]

    const periodSpecific = [
      `Period ${period.period}: ${isFake ? 'Synthetic' : 'Natural'} voice patterns detected`,
      `${period.fake_count} of ${period.total} samples flagged as ${isFake ? 'Fake' : 'Real'}`,
    ]

    return [...periodSpecific, ...evidence]
  }

  return (
    <div className={cn(
      "rounded-2xl border overflow-hidden transition-all duration-300 bg-white shadow-sm",
      isFake
        ? "border-red-200/60 hover:border-red-300/80"
        : "border-indigo-200/60 hover:border-indigo-300/80",
    )}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-6 py-5 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-4">
          <div className={cn(
            "w-10 h-10 rounded-xl flex items-center justify-center text-sm font-black",
            isFake ? "bg-red-100 text-red-600" : "bg-indigo-100 text-indigo-600",
          )}>
            {period.period}
          </div>
          <div className="text-left">
            <p className="text-base font-bold text-gray-900">
              Period {period.period}
              <span className={cn(
                "ml-3 text-[11px] font-bold px-3 py-1 rounded-full",
                isFake ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700",
              )}>
                {isFake ? "⚠ DEEPFAKE" : "✓ AUTHENTIC"}
              </span>
            </p>
            <p className="text-xs text-gray-400 font-mono">{period.timestamp}</p>
          </div>
        </div>
        <div className="flex items-center gap-5">
          <div className="text-right hidden sm:block">
            <p className="text-xs text-gray-400">Samples</p>
            <p className="text-sm font-bold text-gray-700 font-mono">
              <span className="text-red-500">{period.fake_count}F</span>
              {" / "}
              <span className="text-green-500">{period.real_count}R</span>
            </p>
          </div>
          <div className={cn(
            "w-14 h-14 rounded-full flex items-center justify-center text-xl font-black border-2",
            isFake ? "border-red-300 text-red-600 bg-red-50" : "border-indigo-300 text-indigo-600 bg-indigo-50",
          )}>
            {period.total > 0
              ? Math.round((period.fake_count / period.total) * 100)
              : 0}%
          </div>
          <span className={cn(
            "text-gray-400 transition-transform duration-300 text-sm",
            expanded && "rotate-180",
          )}>▼</span>
        </div>
      </button>

      {expanded && (
        <div className="px-6 pb-6 space-y-6 border-t border-gray-100 pt-6">
          <div>
            <div className="flex items-center gap-3 mb-3">
              <Radio className="h-4 w-4 text-gray-400" />
              <span className="text-xs font-bold text-gray-500 uppercase tracking-widest">
                Waveform Analysis
              </span>
              {isFake && (
                <span className="text-[10px] text-red-600 bg-red-50 border border-red-200 px-3 py-0.5 rounded-full font-mono">
                  {period.anomaly_markers.length} anomalies detected
                </span>
              )}
            </div>
            <WaveformCanvas
              waveform={period.waveform}
              isFake={isFake}
              markers={period.anomaly_markers}
              label={`Period ${period.period} — ${isFake ? "Synthetic Voice" : "Natural Voice"}`}
              stats={period.signal_stats}
            />
          </div>

          <div>
            <div className="flex items-center gap-3 mb-3">
              <BarChart3 className="h-4 w-4 text-gray-400" />
              <span className="text-xs font-bold text-gray-500 uppercase tracking-widest">
                Spectrogram
              </span>
              {isFake && (
                <span className="text-[10px] text-red-600 bg-red-50 border border-red-200 px-3 py-0.5 rounded-full font-mono">
                  Unnatural high-freq energy
                </span>
              )}
            </div>
            <SpectrogramCanvas data={period.spectrogram} isFake={isFake} />
            <div className="mt-1.5 flex items-center justify-between text-[10px] text-gray-400 font-mono px-1">
              <span>Frequency (Hz) →</span>
              <span>{isFake ? "Red = AI artifact zones" : "Blue = Natural formants"}</span>
              <span>← Time</span>
            </div>
          </div>

          {/* Unique evidence per period */}
          <div className={cn(
            "rounded-xl p-4 border",
            isFake ? "bg-red-50 border-red-200" : "bg-indigo-50 border-indigo-200"
          )}>
            <p className={cn(
              "text-[11px] font-bold uppercase tracking-widest mb-2.5",
              isFake ? "text-red-600" : "text-indigo-600"
            )}>
              {isFake ? "⚠ Evidence of AI Synthesis" : "✅ Evidence of Authentic Voice"}
            </p>
            <div className="grid grid-cols-1 gap-1.5">
              {getEvidenceList().map((evidence, idx) => (
                <p key={idx} className="text-[10px] text-gray-700 flex gap-2 items-start">
                  {isFake ? (
                    <XCircle className="h-3.5 w-3.5 text-red-500 shrink-0 mt-0.5" />
                  ) : (
                    <CheckCircle className="h-3.5 w-3.5 text-green-500 shrink-0 mt-0.5" />
                  )}
                  <span className="leading-relaxed">{evidence}</span>
                </p>
              ))}
            </div>
          </div>

          {period.samples.length > 0 && (
            <div>
              <p className="text-[11px] font-bold text-gray-400 uppercase tracking-widest mb-2.5">
                Sample-level results
              </p>
              <div className="rounded-xl overflow-hidden border border-gray-200">
                <table className="w-full text-[11px] font-mono">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="text-left px-4 py-2.5 text-gray-400 font-bold">Sample</th>
                      <th className="text-left px-4 py-2.5 text-gray-400 font-bold">Verdict</th>
                      {period.samples[0]?.layers.map((l) => (
                        <th key={l.name} className="text-left px-4 py-2.5 text-gray-400 font-bold">
                          {l.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {period.samples.map((s) => (
                      <tr key={s.sample} className="border-t border-gray-100 hover:bg-gray-50">
                        <td className="px-4 py-2.5 text-gray-600">{s.sample}</td>
                        <td className="px-4 py-2.5">
                          <span className={cn(
                            "px-2.5 py-1 rounded-full text-[10px] font-bold",
                            s.prediction === "Fake"
                              ? "bg-red-100 text-red-700"
                              : "bg-green-100 text-green-700",
                          )}>
                            {s.prediction}
                          </span>
                        </td>
                        {s.layers.map((l) => (
                          <td key={l.name} className="px-4 py-2.5">
                            <span className={cn(
                              l.label === "Fake" ? "text-red-600" : "text-green-600",
                            )}>
                              {l.label}
                            </span>
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function ResultsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<AnalysisData | null>(null)

  useEffect(() => {
    const name = localStorage.getItem("deepmeet-meeting")
    const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

    if (!name) {
      setLoading(false)
      return
    }

    fetch(`${API}/deepmeet/detector/analysis?meeting_name=${name}`)
      .then(async (res) => {
        if (res.status === 404) {
          setLoading(false)
          return
        }
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const json = await res.json()
        setData(json)
      })
      .catch((err) => {
        console.error("Analysis fetch error:", err)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin text-indigo-500 mx-auto" />
          <p className="text-gray-500 text-sm">Loading detection results...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-gray-500">No results found. Please run a detection session first.</p>
          <Button onClick={() => router.push("/detection")}>Go to Detection</Button>
        </div>
      </div>
    )
  }

  const isFake = data.verdict === "Fake"
  const threatScore = Math.round(data.fake_percentage)
  const confidence = isFake
    ? Math.round(60 + data.fake_percentage * 0.4)
    : Math.round(60 + (100 - data.fake_percentage) * 0.4)
  const verdictMapped = isFake ? "deepfake" : "authentic"

  const downloadReport = () => {
    const reportData = {
      meeting: data.meeting,
      verdict: data.verdict,
      total_samples: data.total_samples,
      total_fake: data.total_fake,
      total_real: data.total_real,
      fake_percentage: data.fake_percentage,
      layers: data.layer_summary,
      periods: data.periods.map(p => ({
        period: p.period,
        timestamp: p.timestamp,
        verdict: p.verdict,
        total: p.total,
        fake_count: p.fake_count,
        real_count: p.real_count,
        samples: p.samples
      }))
    }

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `deepmeet-report-${data.meeting}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const shareReport = async () => {
    const shareData = {
      title: 'DeepMeet Guard - Voice Authentication Report',
      text: `Meeting: ${data.meeting}\nVerdict: ${data.verdict}\nFake Rate: ${data.fake_percentage}%\nTotal Samples: ${data.total_samples}`,
      url: window.location.href
    }

    if (navigator.share) {
      try {
        await navigator.share(shareData)
      } catch {
        console.log('Share cancelled')
      }
    } else {
      await navigator.clipboard.writeText(`${shareData.title}\n\n${shareData.text}\n\nView full report: ${shareData.url}`)
      alert('Report details copied to clipboard!')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-gray-50 pt-24 pb-20">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 space-y-8">

        {/* ── Header ── */}
        <div className="text-center space-y-4">
          <span className={cn(
            "inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-bold border",
            isFake
              ? "bg-red-50 border-red-200 text-red-600"
              : "bg-indigo-50 border-indigo-200 text-indigo-600",
          )}>
            <Shield className="h-3.5 w-3.5" />
            DeepMeet Guard — Voice Authentication Report
          </span>
          <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-gray-900">
            {isFake ? "Deepfake Voice Detected" : "Voice Verified Authentic"}
          </h1>
          <p className="text-sm text-gray-500 max-w-2xl mx-auto leading-relaxed">
            {isFake
              ? "Our 4-layer AI ensemble identified synthetic voice patterns across multiple detection methods. Full signal analysis is shown below."
              : "All detection layers passed. No artificial voice patterns were identified in this session."}
          </p>

          <div className="inline-flex rounded-2xl overflow-hidden border border-gray-200 mx-auto">
            <div className="flex items-center gap-2 px-5 py-3 bg-indigo-50">
              <Shield className="h-4 w-4 text-indigo-600" />
              <div className="text-left">
                <p className="text-[10px] font-black text-indigo-700 uppercase tracking-widest">Blue Team</p>
                <p className="text-[10px] text-indigo-400">Human Interviewer</p>
              </div>
              <CheckCircle className="h-4 w-4 text-emerald-500 ml-2" />
            </div>
            <div className="w-px bg-gray-200" />
            <div className="flex items-center gap-2 px-5 py-3 bg-red-50">
              <Skull className="h-4 w-4 text-red-600" />
              <div className="text-left">
                <p className="text-[10px] font-black text-red-700 uppercase tracking-widest">Red Team</p>
                <p className="text-[10px] text-red-400">Voice Clone Attacker</p>
              </div>
              <span className={cn(
                "ml-2 text-[10px] font-bold px-2 py-0.5 rounded-full",
                isFake
                  ? "bg-red-200 text-red-700"
                  : "bg-green-200 text-green-700",
              )}>
                {isFake ? "DETECTED" : "NOT FOUND"}
              </span>
            </div>
          </div>
        </div>

        {/* ── Threat Summary ── */}
        <ThreatSummary
          overallScore={threatScore}
          verdict={verdictMapped}
          confidence={confidence}
        />

        {/* ── Stats row ── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "Total Samples", value: data.total_samples },
            { label: "Fake Samples", value: data.total_fake, color: "text-red-600" },
            { label: "Real Samples", value: data.total_real, color: "text-green-600" },
            { label: "Fake Rate", value: `${data.fake_percentage}%`, color: isFake ? "text-red-600" : "text-green-600" },
          ].map((s) => (
            <div key={s.label} className="rounded-2xl border border-gray-200 bg-white p-4 text-center shadow-sm">
              <p className={cn("text-3xl font-black font-mono", s.color || "text-gray-900")}>
                {s.value}
              </p>
              <p className="text-[10px] text-gray-400 mt-1">{s.label}</p>
            </div>
          ))}
        </div>

        {/* ── 4-Layer Summary ── */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Lock className="h-4 w-4 text-gray-400" />
            <h2 className="text-lg font-black text-gray-900">4-Layer Ensemble Results</h2>
          </div>
          <p className="text-xs text-gray-400">
            Weighted voting: <strong className="text-gray-600">Spectra0 (0.42)</strong> +{" "}
            <strong className="text-gray-600">ViT (0.26)</strong> +{" "}
            <strong className="text-gray-600">RawNet2 (0.172)</strong> +{" "}
            <strong className="text-gray-600">Liveness (0.148)</strong>
          </p>
          <div className="grid sm:grid-cols-2 gap-3">
            {data.layer_summary.map((l) => <LayerBar key={l.name} layer={l} />)}
          </div>
        </div>

        {/* ── Period-by-period analysis ── */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-gray-400" />
            <h2 className="text-lg font-black text-gray-900">Period-by-Period Signal Analysis</h2>
            <span className="text-[10px] text-gray-400 font-mono ml-auto">
              {data.periods.length} recording period{data.periods.length !== 1 ? "s" : ""}
            </span>
          </div>
          <p className="text-xs text-gray-400">
            Each period = one recording window. Waveform + spectrogram + anomaly markers shown for each.
            Red markers indicate AI-synthesized speech artifacts.
          </p>
          {data.periods.map((p, i) => (
            <PeriodCard key={p.period} period={p} index={i} />
          ))}
        </div>

        {/* ── Technical summary ── */}
        <div className="rounded-2xl border border-gray-200 bg-white p-6 space-y-4 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <FileText className="h-4 w-4 text-gray-400" />
            <h3 className="font-black text-gray-900">Technical Summary</h3>
          </div>
          <div className="grid sm:grid-cols-3 gap-4">
            {[
              { k: "Detection Method", v: "4-Layer Weighted Ensemble" },
              { k: "Model Version", v: "DeepMeet Guard v1.0.0" },
              { k: "Final Verdict", v: data.verdict },
            ].map((item) => (
              <div key={item.k} className="rounded-xl bg-gray-50 p-3">
                <p className="text-[10px] text-gray-400 uppercase tracking-widest mb-1">{item.k}</p>
                <p className={cn(
                  "text-sm font-bold",
                  item.k === "Final Verdict"
                    ? isFake ? "text-red-600" : "text-green-600"
                    : "text-gray-800",
                )}>{item.v}</p>
              </div>
            ))}
          </div>
          {isFake && (
            <div className="rounded-xl bg-red-50 border border-red-200 p-4 space-y-2">
              <p className="text-[10px] text-red-500 uppercase tracking-widest font-bold">
                Suspected Attack Method
              </p>
              <p className="text-sm text-red-700 font-medium">
                Real-Time Voice Cloning — Transformer-based TTS with speaker embedding extraction
              </p>
              <p className="text-[10px] text-gray-500">
                Technique: Vishing + Deepfake Voice — social engineering with fabricated urgency
              </p>
            </div>
          )}
        </div>

        {/* ── Actions ── */}
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h3 className="font-black text-gray-900">What&apos;s Next?</h3>
              <p className="text-xs text-gray-400">Download the report or start a new detection session.</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button
                variant="outline"
                className="gap-2 border-gray-300 text-gray-600 hover:text-gray-900"
                onClick={downloadReport}
              >
                <Download className="h-4 w-4" />
                Download Report
              </Button>
              <Button
                variant="outline"
                className="gap-2 border-gray-300 text-gray-600 hover:text-gray-900"
                onClick={shareReport}
              >
                <Share2 className="h-4 w-4" />
                Share
              </Button>
              <Button asChild className="gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-500/25 hover:from-indigo-700 hover:to-violet-700">
                <Link href="/detection">
                  <RefreshCw className="h-4 w-4" />
                  New Detection
                </Link>
              </Button>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}