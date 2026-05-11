"use client"

import { useState, useCallback, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Download, RefreshCw, Play, Square, Loader2, Activity, Clock, AlertTriangle, History, Shield, TrendingUp } from "lucide-react"
import { cn } from "@/lib/utils"

interface SegmentResult {
  id: number
  timestamp: number
  score: number
  verdict: "authentic" | "suspicious" | "deepfake"
  layer1: number
  layer2: number
  layer3: number
  layer4: number
}

// ─── Start Screen Component ────────────────────────────────────────────────────
function StartScreen({ onStart }: { onStart: () => void }) {
  return (
    <div className="min-h-[70vh] flex items-center justify-center">
      <div className="text-center space-y-8">
        <div className="relative w-32 h-32 mx-auto">
          <div className="absolute inset-0 rounded-full bg-gradient-to-r from-primary to-violet-500 animate-ping opacity-20" />
          <div className="absolute inset-2 rounded-full bg-gradient-to-r from-primary to-violet-500 animate-pulse" />
          <div className="absolute inset-4 rounded-full bg-white dark:bg-slate-900 flex items-center justify-center">
            <Shield className="h-12 w-12 text-primary" />
          </div>
        </div>

        <div className="space-y-3">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-violet-600 bg-clip-text text-transparent">
            Deepfake Voice Detection
          </h1>
          <p className="text-muted-foreground max-w-md">
            Continuous real-time audio analysis — every 10 seconds
          </p>
        </div>

        <Button
          onClick={onStart}
          className="group relative h-14 px-8 text-lg font-semibold bg-gradient-to-r from-primary to-violet-600 hover:from-primary/90 hover:to-violet-700 shadow-xl shadow-primary/25 hover:shadow-2xl hover:shadow-primary/40 transition-all duration-300 transform hover:scale-105"
        >
          <Play className="mr-2 h-5 w-5 group-hover:animate-pulse" />
          Start Continuous Detection
        </Button>

        <p className="text-xs text-muted-foreground">
          Analyzes 10-second audio segments continuously | Redirects to results when done
        </p>
      </div>
    </div>
  )
}

// ─── Analysis Meter Component ──────────────────────────────────────────────────
function AnalysisMeter({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className={cn("font-bold", color === "red" ? "text-red-600" : color === "green" ? "text-green-600" : "text-primary")}>
          {value}%
        </span>
      </div>
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-500",
            color === "red" && "bg-gradient-to-r from-orange-400 to-red-500",
            color === "green" && "bg-gradient-to-r from-emerald-400 to-green-500",
            color === "primary" && "bg-gradient-to-r from-primary to-violet-500"
          )}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  )
}

// ─── Segment History Item ──────────────────────────────────────────────────────
function SegmentHistoryItem({ segment, index }: { segment: SegmentResult; index: number }) {
  return (
    <div className={cn(
      "flex items-center justify-between p-3 rounded-lg border transition-all",
      segment.verdict === "authentic" && "border-green-200 bg-green-50/50",
      segment.verdict === "suspicious" && "border-yellow-200 bg-yellow-50/50",
      segment.verdict === "deepfake" && "border-red-200 bg-red-50/50"
    )}>
      <div className="flex items-center gap-3">
        <span className="text-xs font-mono text-muted-foreground w-12">#{index + 1}</span>
        <span className="text-xs font-mono">{formatSegmentTime(segment.timestamp)}</span>
      </div>
      <div className="flex-1 mx-4">
        <div className="h-1.5 rounded-full bg-muted overflow-hidden">
          <div 
            className={cn(
              "h-full rounded-full transition-all",
              segment.verdict === "authentic" && "bg-green-500",
              segment.verdict === "suspicious" && "bg-yellow-500",
              segment.verdict === "deepfake" && "bg-red-500"
            )}
            style={{ width: `${segment.score}%` }}
          />
        </div>
      </div>
      <div className="flex items-center gap-2">
        <span className={cn(
          "text-xs font-bold",
          segment.verdict === "authentic" && "text-green-600",
          segment.verdict === "suspicious" && "text-yellow-600",
          segment.verdict === "deepfake" && "text-red-600"
        )}>
          {segment.score}%
        </span>
        {segment.verdict === "deepfake" && <AlertTriangle className="h-3 w-3 text-red-500" />}
      </div>
    </div>
  )
}

function formatSegmentTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
}

// ─── Generate random analysis for a segment ───────────────────────────────────
function generateSegmentResult(id: number, elapsedTime: number): SegmentResult {
  const baseScore = 30 + Math.random() * 60
  const score = Math.floor(baseScore)
  
  let verdict: SegmentResult["verdict"]
  if (score >= 70) verdict = "authentic"
  else if (score >= 40) verdict = "suspicious"
  else verdict = "deepfake"
  
  return {
    id,
    timestamp: elapsedTime,
    score,
    verdict,
    layer1: Math.floor(score * (0.7 + Math.random() * 0.3)),
    layer2: Math.floor(score * (0.6 + Math.random() * 0.4)),
    layer3: Math.floor(score * (0.5 + Math.random() * 0.5)),
    layer4: Math.floor(score * (0.8 + Math.random() * 0.2)),
  }
}

// ─── Main Detection Page ───────────────────────────────────────────────────────
export default function DetectionPage() {
  const router = useRouter()
  const [sessionStarted, setSessionStarted] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isAborting, setIsAborting] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [currentSegment, setCurrentSegment] = useState<SegmentResult | null>(null)
  const [history, setHistory] = useState<SegmentResult[]>([])
  
  const segmentIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const segmentCountRef = useRef(0)

  // Timer
  useEffect(() => {
    if (!isAnalyzing || isAborting) return
    timerRef.current = setInterval(() => setElapsed((p) => p + 1), 1000)
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [isAnalyzing, isAborting])

  // Continuous segment analysis - every 10 seconds
  useEffect(() => {
    if (!isAnalyzing || isAborting) return

    const runSegmentAnalysis = () => {
      const segmentId = segmentCountRef.current
      segmentCountRef.current++
      
      setTimeout(() => {
        if (!isAnalyzing || isAborting) return
        
        const result = generateSegmentResult(segmentId, elapsed)
        setCurrentSegment(result)
        setHistory(prev => [result, ...prev.slice(0, 19)])
      }, 100)
    }

    runSegmentAnalysis()
    segmentIntervalRef.current = setInterval(runSegmentAnalysis, 10000)

    return () => {
      if (segmentIntervalRef.current) clearInterval(segmentIntervalRef.current)
    }
  }, [isAnalyzing, isAborting, elapsed])

  const startAnalysis = useCallback(() => {
    setSessionStarted(true)
    setIsAnalyzing(true)
    setIsAborting(false)
    setElapsed(0)
    setCurrentSegment(null)
    setHistory([])
    segmentCountRef.current = 0
  }, [])

  const abortAnalysis = useCallback(() => {
    setIsAborting(true)
    setIsAnalyzing(false)
    if (segmentIntervalRef.current) clearInterval(segmentIntervalRef.current)
    if (timerRef.current) clearInterval(timerRef.current)
    setTimeout(() => {
      // بعد الـ Abort، يروح لصفحة النتائج
      router.push("/results")
    }, 500)
  }, [router])

  const finishAndGoToResults = useCallback(() => {
    setIsAnalyzing(false)
    if (segmentIntervalRef.current) clearInterval(segmentIntervalRef.current)
    if (timerRef.current) clearInterval(timerRef.current)
    router.push("/results")
  }, [router])

  const formatTime = (s: number) =>
    `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`

  const totalSegments = history.length
  const deepfakeCount = history.filter(h => h.verdict === "deepfake").length
  const suspiciousCount = history.filter(h => h.verdict === "suspicious").length
  const authenticCount = history.filter(h => h.verdict === "authentic").length

  if (!sessionStarted) {
    return (
      <div className="min-h-screen pt-28 pb-16">
        <div className="fixed inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-background to-background" />
          <div className="absolute left-1/4 top-1/4 h-96 w-96 rounded-full bg-primary/5 blur-3xl" />
          <div className="absolute right-1/4 bottom-1/4 h-96 w-96 rounded-full bg-violet-500/5 blur-3xl" />
        </div>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <StartScreen onStart={startAnalysis} />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen pt-28 pb-16">
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-background to-background" />
        <div className="absolute left-1/4 top-1/4 h-96 w-96 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute right-1/4 bottom-1/4 h-96 w-96 rounded-full bg-violet-500/5 blur-3xl" />
      </div>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Status Bar */}
        <div className="mb-8 rounded-xl bg-white/80 backdrop-blur-sm border border-border/50 p-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-red-500 animate-pulse" />
                <span className="text-sm font-bold">LIVE DETECTION</span>
              </div>
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Clock className="h-3.5 w-3.5" />
                <span className="font-mono text-sm">{formatTime(elapsed)}</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary/10 border border-primary/20">
                <Activity className="h-3.5 w-3.5 text-primary animate-pulse" />
                <span className="text-xs font-bold text-primary">
                  Segments: {totalSegments}
                </span>
              </div>
              <Button
                variant="destructive"
                size="sm"
                onClick={abortAnalysis}
                disabled={isAborting}
                className="gap-2"
              >
                {isAborting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Square className="h-4 w-4" />
                )}
                {isAborting ? "Aborting..." : "Abort & View Results"}
              </Button>
              <Button
                variant="default"
                size="sm"
                onClick={finishAndGoToResults}
                className="gap-2 bg-green-600 hover:bg-green-700"
              >
                <TrendingUp className="h-4 w-4" />
                Finish & View Results
              </Button>
            </div>
          </div>
        </div>

        {/* Header */}
        <div className="mb-8 text-center">
          <span className="mb-4 inline-block rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary animate-pulse">
            Analyzing 10-Second Segments
          </span>
          <h1 className="mb-3 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Continuous Voice Detection
          </h1>
          <p className="mx-auto max-w-2xl text-muted-foreground">
            New analysis every 10 seconds — click "Finish & View Results" when done
          </p>
        </div>

        {/* Current Segment Result */}
        {currentSegment && (
          <div className={cn(
            "mb-8 rounded-2xl p-6 text-center space-y-3 animate-scale-in border-2",
            currentSegment.verdict === "authentic" && "bg-green-50 border-green-200",
            currentSegment.verdict === "suspicious" && "bg-yellow-50 border-yellow-200",
            currentSegment.verdict === "deepfake" && "bg-red-50 border-red-200"
          )}>
            <div className="flex items-center justify-center gap-3">
              {currentSegment.verdict === "authentic" && <Shield className="h-7 w-7 text-green-600" />}
              {currentSegment.verdict === "suspicious" && <AlertTriangle className="h-7 w-7 text-yellow-600" />}
              {currentSegment.verdict === "deepfake" && <AlertTriangle className="h-7 w-7 text-red-600" />}
              <span className="text-sm font-medium">Latest Segment</span>
              <span className="text-xs font-mono text-muted-foreground">
                at {formatSegmentTime(currentSegment.timestamp)}
              </span>
            </div>
            <div className="text-5xl font-bold">
              {currentSegment.score}%
            </div>
            <p className={cn(
              "font-semibold capitalize",
              currentSegment.verdict === "authentic" && "text-green-600",
              currentSegment.verdict === "suspicious" && "text-yellow-600",
              currentSegment.verdict === "deepfake" && "text-red-600"
            )}>
              {currentSegment.verdict === "authentic" && "✓ Authentic Voice"}
              {currentSegment.verdict === "suspicious" && "⚠ Suspicious Activity"}
              {currentSegment.verdict === "deepfake" && "✗ Deepfake Detected!"}
            </p>
          </div>
        )}

        {/* 4 Layers Grid */}
        {currentSegment && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
            <div className="rounded-xl border border-border/50 bg-white/50 backdrop-blur-sm p-4 space-y-2">
              <span className="text-xs font-bold text-muted-foreground uppercase">Layer 1 · Spectral</span>
              <div className="text-2xl font-bold">{currentSegment.layer1}%</div>
              <AnalysisMeter label="" value={currentSegment.layer1} color="primary" />
              <p className="text-[10px] text-muted-foreground">Frequency pattern analysis</p>
            </div>
            <div className="rounded-xl border border-border/50 bg-white/50 backdrop-blur-sm p-4 space-y-2">
              <span className="text-xs font-bold text-muted-foreground uppercase">Layer 2 · Liveness</span>
              <div className="text-2xl font-bold">{currentSegment.layer2}%</div>
              <AnalysisMeter label="" value={currentSegment.layer2} color="primary" />
              <p className="text-[10px] text-muted-foreground">Human voice detection</p>
            </div>
            <div className="rounded-xl border border-border/50 bg-white/50 backdrop-blur-sm p-4 space-y-2">
              <span className="text-xs font-bold text-muted-foreground uppercase">Layer 3 · Behavioral</span>
              <div className="text-2xl font-bold">{currentSegment.layer3}%</div>
              <AnalysisMeter label="" value={currentSegment.layer3} color="primary" />
              <p className="text-[10px] text-muted-foreground">Speech pattern anomalies</p>
            </div>
            <div className="rounded-xl border border-border/50 bg-white/50 backdrop-blur-sm p-4 space-y-2">
              <span className="text-xs font-bold text-muted-foreground uppercase">Layer 4 · Authenticity</span>
              <div className="text-2xl font-bold">{currentSegment.layer4}%</div>
              <AnalysisMeter label="" value={currentSegment.layer4} color="primary" />
              <p className="text-[10px] text-muted-foreground">Overall authenticity score</p>
            </div>
          </div>
        )}

        {/* Statistics Summary */}
        {history.length > 0 && (
          <div className="grid grid-cols-4 gap-3 mb-8">
            <div className="rounded-xl bg-white/50 backdrop-blur-sm border border-border/50 p-3 text-center">
              <div className="text-2xl font-bold">{totalSegments}</div>
              <div className="text-xs text-muted-foreground">Total Segments</div>
            </div>
            <div className="rounded-xl bg-white/50 backdrop-blur-sm border border-border/50 p-3 text-center">
              <div className="text-2xl font-bold text-green-600">{authenticCount}</div>
              <div className="text-xs text-muted-foreground">Authentic</div>
            </div>
            <div className="rounded-xl bg-white/50 backdrop-blur-sm border border-border/50 p-3 text-center">
              <div className="text-2xl font-bold text-yellow-600">{suspiciousCount}</div>
              <div className="text-xs text-muted-foreground">Suspicious</div>
            </div>
            <div className="rounded-xl bg-white/50 backdrop-blur-sm border border-border/50 p-3 text-center">
              <div className="text-2xl font-bold text-red-600">{deepfakeCount}</div>
              <div className="text-xs text-muted-foreground">Deepfake</div>
            </div>
          </div>
        )}

        {/* History Timeline */}
        {history.length > 0 && (
          <div className="rounded-xl border border-border/50 bg-white/50 backdrop-blur-sm overflow-hidden">
            <div className="flex items-center gap-2 px-5 py-3 border-b border-border/50 bg-muted/20">
              <History className="h-4 w-4 text-muted-foreground" />
              <h3 className="font-semibold text-sm">Detection History</h3>
              <span className="text-xs text-muted-foreground ml-auto">Last {Math.min(history.length, 20)} segments</span>
            </div>
            <div className="p-4 space-y-2 max-h-64 overflow-y-auto">
              {history.map((segment, idx) => (
                <SegmentHistoryItem key={segment.id} segment={segment} index={idx} />
              ))}
            </div>
          </div>
        )}

        {!currentSegment && history.length === 0 && (
          <div className="text-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
            <p className="text-muted-foreground">Analyzing first 10-second segment...</p>
          </div>
        )}
      </div>
    </div>
  )
}