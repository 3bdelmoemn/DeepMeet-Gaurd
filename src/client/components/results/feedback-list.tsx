"use client"

import { cn } from "@/lib/utils"
import { CheckCircle, AlertCircle } from "lucide-react"

interface FeedbackListProps {
  strengths: string[]
  improvements: string[]
}

export function FeedbackList({ strengths, improvements }: FeedbackListProps) {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Strengths */}
      <div className="glass-card p-6">
        <div className="mb-4 flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10">
            <CheckCircle className="h-4 w-4 text-emerald-500" />
          </div>
          <h3 className="font-semibold text-foreground">Strengths</h3>
        </div>

        <ul className="space-y-3">
          {strengths.map((strength, index) => (
            <li 
              key={index}
              className="flex items-start gap-3 rounded-lg bg-emerald-500/5 p-3"
            >
              <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
              <span className="text-sm text-foreground">{strength}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Areas for Improvement */}
      <div className="glass-card p-6">
        <div className="mb-4 flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10">
            <AlertCircle className="h-4 w-4 text-amber-500" />
          </div>
          <h3 className="font-semibold text-foreground">Areas for Improvement</h3>
        </div>

        <ul className="space-y-3">
          {improvements.map((improvement, index) => (
            <li 
              key={index}
              className="flex items-start gap-3 rounded-lg bg-amber-500/5 p-3"
            >
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" />
              <span className="text-sm text-foreground">{improvement}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
