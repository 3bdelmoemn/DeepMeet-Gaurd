"use client"

import { cn } from "@/lib/utils"
import { Activity, Waves, Brain } from "lucide-react"

interface DetectionBreakdownProps {
  result: {
    audioCharacteristics: number
    voicePatterns: number
    aiConfidence: number
  } | null
}

const layers = [
  {
    key: "audioCharacteristics" as const,
    icon: Activity,
    title: "Audio Characteristics",
    description: "Analyzes frequency patterns, noise levels, and audio artifacts",
    color: "from-primary to-violet-500"
  },
  {
    key: "voicePatterns" as const,
    icon: Waves,
    title: "Voice Pattern Analysis",
    description: "Examines speech patterns, breathing, and natural variations",
    color: "from-teal-400 to-cyan-400"
  },
  {
    key: "aiConfidence" as const,
    icon: Brain,
    title: "AI Model Confidence",
    description: "Deep learning model evaluation of authenticity markers",
    color: "from-rose-400 to-orange-400"
  }
]

export function DetectionBreakdown({ result }: DetectionBreakdownProps) {
  if (!result) return null

  return (
    <div className="glass-card p-8">
      <h3 className="mb-6 text-lg font-semibold text-foreground">
        Detection Breakdown
      </h3>

      <div className="space-y-6">
        {layers.map((layer) => {
          const score = result[layer.key]
          const Icon = layer.icon
          
          return (
            <div key={layer.key}>
              <div className="mb-3 flex items-start gap-3">
                <div className={cn(
                  "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br shadow-lg",
                  layer.color
                )}>
                  <Icon className="h-5 w-5 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-foreground">{layer.title}</h4>
                    <span className={cn(
                      "text-lg font-bold",
                      score >= 70 ? "text-emerald-500" : 
                      score >= 40 ? "text-amber-500" : "text-rose-500"
                    )}>
                      {score}%
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">{layer.description}</p>
                </div>
              </div>
              
              {/* Progress bar */}
              <div className="ml-13 h-2 overflow-hidden rounded-full bg-muted">
                <div 
                  className={cn("h-full rounded-full bg-gradient-to-r", layer.color)}
                  style={{ 
                    width: `${score}%`,
                    transition: "width 1s ease-out"
                  }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
