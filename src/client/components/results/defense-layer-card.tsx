"use client"

import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"
import { CheckCircle2, XCircle, AlertTriangle, ChevronDown } from "lucide-react"

interface DefenseLayerCardProps {
  layer: number
  title: string
  description: string
  score: number
  status: "authentic" | "suspicious" | "deepfake"
  details: string[]
  icon: React.ReactNode
  delay?: number
}

export function DefenseLayerCard({
  layer,
  title,
  description,
  score,
  status,
  details,
  icon,
  delay = 0,
}: DefenseLayerCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isVisible, setIsVisible] = useState(false)
  const [animatedScore, setAnimatedScore] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true)
    }, delay)
    return () => clearTimeout(timer)
  }, [delay])

  useEffect(() => {
    if (isVisible) {
      const duration = 1500
      const steps = 60
      const increment = score / steps
      let current = 0
      const timer = setInterval(() => {
        current += increment
        if (current >= score) {
          setAnimatedScore(score)
          clearInterval(timer)
        } else {
          setAnimatedScore(Math.floor(current))
        }
      }, duration / steps)
      return () => clearInterval(timer)
    }
  }, [isVisible, score])

  const statusConfig = {
    authentic: {
      color: "text-emerald-500",
      bgColor: "bg-emerald-500/10",
      borderColor: "border-emerald-500/30",
      icon: <CheckCircle2 className="h-5 w-5 text-emerald-500" />,
      label: "Authentic",
    },
    suspicious: {
      color: "text-amber-500",
      bgColor: "bg-amber-500/10",
      borderColor: "border-amber-500/30",
      icon: <AlertTriangle className="h-5 w-5 text-amber-500" />,
      label: "Suspicious",
    },
    deepfake: {
      color: "text-red-500",
      bgColor: "bg-red-500/10",
      borderColor: "border-red-500/30",
      icon: <XCircle className="h-5 w-5 text-red-500" />,
      label: "Deepfake Detected",
    },
  }

  const config = statusConfig[status]

  return (
    <div
      className={cn(
        "glass-card overflow-hidden transition-all duration-700",
        isVisible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
      )}
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-start gap-4 p-6 text-left transition-colors hover:bg-muted/30"
      >
        {/* Layer Number */}
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-violet-500 text-lg font-bold text-white shadow-lg shadow-primary/25">
          {layer}
        </div>

        {/* Content */}
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex items-center gap-2">
            <span className="text-muted-foreground">{icon}</span>
            <h3 className="font-semibold text-foreground">{title}</h3>
          </div>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>

        {/* Score & Status */}
        <div className="flex shrink-0 items-center gap-4">
          {/* Score Ring */}
          <div className="relative h-14 w-14">
            <svg className="h-14 w-14 -rotate-90" viewBox="0 0 56 56">
              <circle
                cx="28"
                cy="28"
                r="24"
                fill="none"
                stroke="currentColor"
                strokeWidth="4"
                className="text-muted/30"
              />
              <circle
                cx="28"
                cy="28"
                r="24"
                fill="none"
                stroke="url(#scoreGradient)"
                strokeWidth="4"
                strokeLinecap="round"
                strokeDasharray={`${(animatedScore / 100) * 150.8} 150.8`}
                className="transition-all duration-1000"
              />
              <defs>
                <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor={status === "deepfake" ? "#ef4444" : status === "suspicious" ? "#f59e0b" : "#10b981"} />
                  <stop offset="100%" stopColor={status === "deepfake" ? "#dc2626" : status === "suspicious" ? "#d97706" : "#059669"} />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className={cn("text-sm font-bold", config.color)}>
                {animatedScore}%
              </span>
            </div>
          </div>

          {/* Status Badge */}
          <div className={cn(
            "flex items-center gap-1.5 rounded-full px-3 py-1.5",
            config.bgColor
          )}>
            {config.icon}
            <span className={cn("text-xs font-medium", config.color)}>
              {config.label}
            </span>
          </div>

          {/* Expand Arrow */}
          <ChevronDown 
            className={cn(
              "h-5 w-5 text-muted-foreground transition-transform duration-300",
              isExpanded && "rotate-180"
            )} 
          />
        </div>
      </button>

      {/* Expanded Details */}
      <div className={cn(
        "grid transition-all duration-300",
        isExpanded ? "grid-rows-[1fr]" : "grid-rows-[0fr]"
      )}>
        <div className="overflow-hidden">
          <div className={cn("border-t border-border/50 p-6", config.bgColor)}>
            <h4 className="mb-3 text-sm font-medium text-foreground">Analysis Details</h4>
            <ul className="space-y-2">
              {details.map((detail, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <span className={cn("mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full", config.color.replace("text-", "bg-"))} />
                  {detail}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
