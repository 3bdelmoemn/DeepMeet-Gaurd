"use client"

import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"
import { Shield, ShieldAlert, ShieldCheck, AlertTriangle } from "lucide-react"

interface ThreatSummaryProps {
  overallScore: number
  verdict: "authentic" | "suspicious" | "deepfake"
  confidence: number
}

export function ThreatSummary({ overallScore, verdict, confidence }: ThreatSummaryProps) {
  const [animatedScore, setAnimatedScore] = useState(0)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    setIsVisible(true)
    const duration = 2000
    const steps = 100
    const increment = overallScore / steps
    let current = 0
    const timer = setInterval(() => {
      current += increment
      if (current >= overallScore) {
        setAnimatedScore(overallScore)
        clearInterval(timer)
      } else {
        setAnimatedScore(Math.floor(current))
      }
    }, duration / steps)
    return () => clearInterval(timer)
  }, [overallScore])

  const verdictConfig = {
    authentic: {
      title: "Voice Verified",
      subtitle: "No deepfake detected",
      color: "text-emerald-500",
      bgGradient: "from-emerald-500/20 via-emerald-500/5 to-transparent",
      ringColor: "stroke-emerald-500",
      glowColor: "shadow-emerald-500/30",
      icon: <ShieldCheck className="h-8 w-8" />,
    },
    suspicious: {
      title: "Suspicious Activity",
      subtitle: "Further verification recommended",
      color: "text-amber-500",
      bgGradient: "from-amber-500/20 via-amber-500/5 to-transparent",
      ringColor: "stroke-amber-500",
      glowColor: "shadow-amber-500/30",
      icon: <AlertTriangle className="h-8 w-8" />,
    },
    deepfake: {
      title: "Deepfake Detected",
      subtitle: "AI-generated voice identified",
      color: "text-red-500",
      bgGradient: "from-red-500/20 via-red-500/5 to-transparent",
      ringColor: "stroke-red-500",
      glowColor: "shadow-red-500/30",
      icon: <ShieldAlert className="h-8 w-8" />,
    },
  }

  const config = verdictConfig[verdict]
  const circumference = 2 * Math.PI * 90

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-3xl border border-border/50 bg-card p-8 transition-all duration-700",
        isVisible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
      )}
    >
      {/* Background Gradient */}
      <div className={cn("absolute inset-0 bg-gradient-to-br", config.bgGradient)} />

      <div className="relative flex flex-col items-center gap-8 md:flex-row md:gap-12">
        {/* Score Circle */}
        <div className="relative">
          {/* Glow Effect */}
          <div className={cn(
            "absolute inset-0 rounded-full blur-xl transition-opacity duration-1000",
            config.glowColor,
            "shadow-2xl opacity-50"
          )} />
          
          <svg className="h-48 w-48 -rotate-90" viewBox="0 0 200 200">
            {/* Background Circle */}
            <circle
              cx="100"
              cy="100"
              r="90"
              fill="none"
              stroke="currentColor"
              strokeWidth="8"
              className="text-muted/20"
            />
            {/* Progress Circle */}
            <circle
              cx="100"
              cy="100"
              r="90"
              fill="none"
              strokeWidth="8"
              strokeLinecap="round"
              className={cn(config.ringColor, "transition-all duration-1000")}
              strokeDasharray={circumference}
              strokeDashoffset={circumference - (animatedScore / 100) * circumference}
            />
            {/* Inner Decorative Circle */}
            <circle
              cx="100"
              cy="100"
              r="75"
              fill="none"
              stroke="currentColor"
              strokeWidth="1"
              className="text-border/30"
            />
          </svg>
          
          {/* Center Content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={cn("text-5xl font-bold tabular-nums", config.color)}>
              {animatedScore}
            </span>
            <span className="text-sm text-muted-foreground">Threat Score</span>
          </div>
        </div>

        {/* Verdict Info */}
        <div className="flex-1 text-center md:text-left">
          <div className={cn(
            "mb-4 inline-flex items-center gap-2 rounded-full px-4 py-2",
            verdict === "authentic" ? "bg-emerald-500/10" : verdict === "suspicious" ? "bg-amber-500/10" : "bg-red-500/10"
          )}>
            <span className={config.color}>{config.icon}</span>
            <span className={cn("font-semibold", config.color)}>{config.title}</span>
          </div>
          
          <h2 className="mb-2 text-2xl font-bold text-foreground md:text-3xl">
            {config.subtitle}
          </h2>
          
          <p className="mb-6 text-muted-foreground">
            {verdict === "deepfake" 
              ? "Our multi-layer analysis has detected artificial voice synthesis patterns. This voice sample shows significant indicators of AI generation or voice cloning technology."
              : verdict === "suspicious"
              ? "Some anomalies were detected that may indicate manipulation. We recommend additional verification before proceeding."
              : "All detection layers passed successfully. This voice sample appears to be from a genuine human speaker."
            }
          </p>

          {/* Confidence Bar */}
          <div>
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Detection Confidence</span>
              <span className={cn("font-medium", config.color)}>{confidence}%</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-muted/30">
              <div 
                className={cn(
                  "h-full rounded-full transition-all duration-1000",
                  verdict === "authentic" ? "bg-emerald-500" : verdict === "suspicious" ? "bg-amber-500" : "bg-red-500"
                )}
                style={{ width: `${confidence}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
