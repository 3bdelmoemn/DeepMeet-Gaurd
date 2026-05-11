"use client"

import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from "recharts"

interface PerformanceChartProps {
  metrics: {
    technicalKnowledge: number
    communication: number
    problemSolving: number
    culturalFit: number
    confidence: number
  }
}

const metricLabels = {
  technicalKnowledge: "Technical",
  communication: "Communication",
  problemSolving: "Problem Solving",
  culturalFit: "Cultural Fit",
  confidence: "Confidence"
}

const getColor = (value: number) => {
  if (value >= 80) return "#10b981" // emerald
  if (value >= 60) return "#6366f1" // primary
  return "#f59e0b" // amber
}

export function PerformanceChart({ metrics }: PerformanceChartProps) {
  const data = Object.entries(metrics).map(([key, value]) => ({
    name: metricLabels[key as keyof typeof metricLabels],
    value,
    color: getColor(value)
  }))

  return (
    <div className="glass-card p-8">
      <h3 className="mb-6 text-lg font-semibold text-foreground">
        Performance Breakdown
      </h3>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 0, right: 20 }}>
            <XAxis type="number" domain={[0, 100]} hide />
            <YAxis 
              type="category" 
              dataKey="name" 
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748b', fontSize: 12 }}
              width={100}
            />
            <Bar 
              dataKey="value" 
              radius={[0, 6, 6, 0]}
              background={{ fill: '#f1f5f9', radius: 6 }}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-emerald-500" />
          <span className="text-muted-foreground">Excellent (80+)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-primary" />
          <span className="text-muted-foreground">Good (60-79)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-amber-500" />
          <span className="text-muted-foreground">Needs Work ({"<"}60)</span>
        </div>
      </div>
    </div>
  )
}
