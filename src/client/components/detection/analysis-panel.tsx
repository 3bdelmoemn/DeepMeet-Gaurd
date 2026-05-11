"use client"

import { cn } from "@/lib/utils"
import { Shield, AlertTriangle, XCircle, Loader2 } from "lucide-react"

interface AnalysisPanelProps {
  isAnalyzing: boolean
  result: {
    score: number
    verdict: "authentic" | "suspicious" | "deepfake"
    confidence: number
  } | null
}

const verdictConfig = {
  authentic: {
    icon: Shield,
    label: "AUTHENTIC",
    color: "text-emerald-500",
    bgColor: "bg-emerald-500/10",
    borderColor: "border-emerald-500/20",
    ringColor: "stroke-emerald-500",
    description: "This audio appears to be genuine human speech."
  },
  suspicious: {
    icon: AlertTriangle,
    label: "SUSPICIOUS",
    color: "text-amber-500",
    bgColor: "bg-amber-500/10",
    borderColor: "border-amber-500/20",
    ringColor: "stroke-amber-500",
    description: "Some anomalies detected. Further verification recommended."
  },
  deepfake: {
    icon: XCircle,
    label: "DEEPFAKE DETECTED",
    color: "text-rose-500",
    bgColor: "bg-rose-500/10",
    borderColor: "border-rose-500/20",
    ringColor: "stroke-rose-500",
    description: "High probability of AI-generated or manipulated audio."
  }
}

export function AnalysisPanel({ isAnalyzing, result }: AnalysisPanelProps) {
  if (isAnalyzing) {
    return (
      <div className="glass-card flex flex-col items-center justify-center p-12">
        <div className="relative mb-8">
          {/* Animated rings */}
          <div className="absolute inset-0 animate-ping rounded-full bg-primary/20" />
          <div className="relative flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-primary to-violet-500 shadow-xl shadow-primary/30">
            <Loader2 className="h-12 w-12 animate-spin text-white" />
          </div>
        </div>
        <h3 className="mb-2 text-xl font-semibold text-foreground">Analyzing Audio</h3>
        <p className="text-muted-foreground">Running 4-layer detection analysis...</p>

        {/* Progress indicators */}
        <div className="mt-8 w-full max-w-xs space-y-3">
          {["Audio Characteristics", "Voice Patterns", "AI Model"].map((step, i) => (
            <div key={step} className="flex items-center gap-3">
              <div className={cn(
                "h-2 w-2 rounded-full",
                i === 0 ? "bg-primary animate-pulse" : "bg-muted"
              )} />
              <span className={cn(
                "text-sm",
                i === 0 ? "text-foreground" : "text-muted-foreground"
              )}>
                {step}
              </span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="glass-card flex flex-col items-center justify-center p-12 text-center">
        <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-muted/50">
          <Shield className="h-10 w-10 text-muted-foreground" />
        </div>
        <h3 className="mb-2 text-xl font-semibold text-foreground">Ready to Analyze</h3>
        <p className="max-w-sm text-muted-foreground">
          Upload an audio file to begin the deepfake detection analysis
        </p>
      </div>
    )
  }

  const config = verdictConfig[result.verdict]
  const VerdictIcon = config.icon
  const circumference = 2 * Math.PI * 45
  const strokeDashoffset = circumference - (result.score / 100) * circumference

  return (
    <div className="glass-card p-8">
      {/* Score circle */}
      <div className="mb-8 flex justify-center">
        <div className="relative">
          <svg className="h-40 w-40 -rotate-90" viewBox="0 0 100 100">
            {/* Background circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="currentColor"
              strokeWidth="6"
              className="text-muted"
            />
            {/* Progress circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              strokeWidth="6"
              strokeLinecap="round"
              className={config.ringColor}
              style={{
                strokeDasharray: circumference,
                strokeDashoffset,
                transition: "stroke-dashoffset 1s ease-out"
              }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={cn("text-4xl font-bold", config.color)}>
              {result.score}
            </span>
            <span className="text-sm text-muted-foreground">/ 100</span>
          </div>
        </div>
      </div>

      {/* Verdict badge */}
      <div className="mb-6 flex justify-center">
        <div className={cn(
          "inline-flex items-center gap-2 rounded-full border px-4 py-2",
          config.bgColor,
          config.borderColor
        )}>
          <VerdictIcon className={cn("h-5 w-5", config.color)} />
          <span className={cn("font-semibold", config.color)}>{config.label}</span>
        </div>
      </div>

      {/* Description */}
      <p className="mb-6 text-center text-muted-foreground">
        {config.description}
      </p>

      {/* Confidence */}
      <div className="rounded-xl bg-muted/50 p-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Confidence Level</span>
          <span className="font-semibold text-foreground">{result.confidence}%</span>
        </div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-muted">
          <div 
            className="h-full rounded-full bg-gradient-to-r from-primary to-violet-500"
            style={{ width: `${result.confidence}%` }}
          />
        </div>
      </div>
    </div>
  )
}
