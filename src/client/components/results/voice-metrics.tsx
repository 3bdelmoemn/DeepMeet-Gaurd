"use client"

import { cn } from "@/lib/utils"
import { Mic, Timer, Volume2 } from "lucide-react"

interface VoiceMetricsProps {
  metrics: {
    clarity: number
    pace: number
    tone: number
  }
}

const metricConfig = [
  {
    key: "clarity" as const,
    label: "Clarity Score",
    description: "How clear and articulate your speech is",
    icon: Mic,
    color: "from-primary to-violet-500"
  },
  {
    key: "pace" as const,
    label: "Pace Consistency",
    description: "Steadiness and rhythm of your speaking",
    icon: Timer,
    color: "from-teal-400 to-cyan-400"
  },
  {
    key: "tone" as const,
    label: "Tone Confidence",
    description: "Assertiveness and energy in your voice",
    icon: Volume2,
    color: "from-rose-400 to-orange-400"
  }
]

export function VoiceMetrics({ metrics }: VoiceMetricsProps) {
  return (
    <div className="glass-card p-8">
      <h3 className="mb-6 text-lg font-semibold text-foreground">
        Voice Analysis
      </h3>

      <div className="grid gap-6 sm:grid-cols-3">
        {metricConfig.map(({ key, label, description, icon: Icon, color }) => {
          const value = metrics[key]
          const circumference = 2 * Math.PI * 35
          const strokeDashoffset = circumference - (value / 100) * circumference

          return (
            <div key={key} className="text-center">
              <div className="mx-auto mb-4 relative h-24 w-24">
                <svg className="h-24 w-24 -rotate-90" viewBox="0 0 80 80">
                  <circle
                    cx="40"
                    cy="40"
                    r="35"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="6"
                    className="text-muted"
                  />
                  <circle
                    cx="40"
                    cy="40"
                    r="35"
                    fill="none"
                    strokeWidth="6"
                    strokeLinecap="round"
                    className={cn("stroke-current", 
                      key === "clarity" ? "text-primary" :
                      key === "pace" ? "text-teal-400" : "text-rose-400"
                    )}
                    style={{
                      strokeDasharray: circumference,
                      strokeDashoffset,
                      transition: "stroke-dashoffset 1s ease-out"
                    }}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-xl font-bold text-foreground">{value}%</span>
                </div>
              </div>

              <div className={cn(
                "mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br",
                color
              )}>
                <Icon className="h-5 w-5 text-white" />
              </div>

              <h4 className="font-medium text-foreground">{label}</h4>
              <p className="mt-1 text-xs text-muted-foreground">{description}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}
