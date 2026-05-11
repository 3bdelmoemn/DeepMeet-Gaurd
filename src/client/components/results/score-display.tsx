"use client"

import { useEffect, useState } from "react"
import { cn } from "@/lib/utils"
import { Trophy, Star, TrendingUp } from "lucide-react"

interface ScoreDisplayProps {
  score: number
}

const tiers = {
  excellent: {
    label: "Excellent",
    icon: Trophy,
    color: "text-emerald-500",
    bgColor: "bg-emerald-500/10",
    borderColor: "border-emerald-500/20",
    ringColor: "stroke-emerald-500"
  },
  good: {
    label: "Good",
    icon: Star,
    color: "text-primary",
    bgColor: "bg-primary/10",
    borderColor: "border-primary/20",
    ringColor: "stroke-primary"
  },
  needsWork: {
    label: "Needs Work",
    icon: TrendingUp,
    color: "text-amber-500",
    bgColor: "bg-amber-500/10",
    borderColor: "border-amber-500/20",
    ringColor: "stroke-amber-500"
  }
}

export function ScoreDisplay({ score }: ScoreDisplayProps) {
  const [animatedScore, setAnimatedScore] = useState(0)
  const tier = score >= 80 ? "excellent" : score >= 60 ? "good" : "needsWork"
  const config = tiers[tier]
  const TierIcon = config.icon

  useEffect(() => {
    const duration = 1500
    const steps = 60
    const increment = score / steps
    let current = 0
    
    const interval = setInterval(() => {
      current += increment
      if (current >= score) {
        setAnimatedScore(score)
        clearInterval(interval)
      } else {
        setAnimatedScore(Math.floor(current))
      }
    }, duration / steps)

    return () => clearInterval(interval)
  }, [score])

  const circumference = 2 * Math.PI * 80
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference

  return (
    <div className="glass-card p-8">
      <div className="flex flex-col items-center">
        {/* Score circle */}
        <div className="relative mb-6">
          <svg className="h-48 w-48 -rotate-90" viewBox="0 0 180 180">
            {/* Background circle */}
            <circle
              cx="90"
              cy="90"
              r="80"
              fill="none"
              stroke="currentColor"
              strokeWidth="12"
              className="text-muted"
            />
            {/* Progress circle */}
            <circle
              cx="90"
              cy="90"
              r="80"
              fill="none"
              strokeWidth="12"
              strokeLinecap="round"
              className={config.ringColor}
              style={{
                strokeDasharray: circumference,
                strokeDashoffset,
                transition: "stroke-dashoffset 1.5s ease-out"
              }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={cn("text-5xl font-bold", config.color)}>
              {animatedScore}
            </span>
            <span className="text-lg text-muted-foreground">/ 100</span>
          </div>
        </div>

        {/* Tier badge */}
        <div className={cn(
          "inline-flex items-center gap-2 rounded-full border px-5 py-2.5",
          config.bgColor,
          config.borderColor
        )}>
          <TierIcon className={cn("h-5 w-5", config.color)} />
          <span className={cn("font-semibold", config.color)}>{config.label}</span>
        </div>

        {/* Message */}
        <p className="mt-4 text-center text-muted-foreground">
          {tier === "excellent" && "Outstanding performance! You're well-prepared for your interview."}
          {tier === "good" && "Great job! A few more practice sessions will make you shine."}
          {tier === "needsWork" && "Keep practicing! Focus on the improvement areas below."}
        </p>
      </div>
    </div>
  )
}
