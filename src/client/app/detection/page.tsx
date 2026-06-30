// ============================================================
// FILE: src/client/app/detection/page.tsx
// ============================================================

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
  layer1: number      // Spectra0
  layer2: number      // ViT
  layer3: number      // RawNet2
  layer4: number      // Behaviour Liveness
  layer1_label?: string
  layer2_label?: string
  layer3_label?: string
  layer4_label?: string
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

// ─── Process Report from Backend ──────────────────────────────────────────────
function processReport(reportData: any, history: SegmentResult[], setHistory: React.Dispatch<React.SetStateAction<SegmentResult[]>>, setCurrentSegment: React.Dispatch<React.SetStateAction<SegmentResult | null>>) {
  try {
    console.log("📥 Processing report:", reportData)
    
    let segments: any[] = []
    
    // ✅ Handle periods with samples and layers
    if (reportData.periods && Array.isArray(reportData.periods)) {
      segments = reportData.periods.map((period: any, idx: number) => {
        // Extract layer data from samples
        let layer1 = 0, layer2 = 0, layer3 = 0, layer4 = 0
        let layer1_label = "Unknown", layer2_label = "Unknown", layer3_label = "Unknown", layer4_label = "Unknown"
        
        // Get layers from first sample in period
        if (period.samples && period.samples.length > 0) {
          const firstSample = period.samples[0]
          if (firstSample.result && firstSample.result.layers) {
            const layers = firstSample.result.layers
            layers.forEach((l: any) => {
              const layerName = l.layer || ""
              if (layerName === "Spectra0" || layerName === "layer1") {
                layer1 = l.label === 1 ? 100 : 0
                layer1_label = l.label === 1 ? "Spoof" : "Bonafide"
              } else if (layerName === "VIT" || layerName === "ViT" || layerName === "layer2") {
                layer2 = l.label === 1 ? 100 : 0
                layer2_label = l.label === 1 ? "Spoof" : "Bonafide"
              } else if (layerName === "RawNet2" || layerName === "layer3") {
                layer3 = l.label === 1 ? 100 : 0
                layer3_label = l.label === 1 ? "Spoof" : "Bonafide"
              } else if (layerName === "liveness" || layerName === "Behaviour Liveness" || layerName === "layer4") {
                layer4 = l.label === 1 ? 100 : 0
                layer4_label = l.label === 1 ? "AI" : "Human"
              }
            })
          }
        }
        
        // Also check if period has direct layers field
        if (period.layers) {
          const layers = period.layers
          if (layers.spectra0 !== undefined) {
            layer1 = layers.spectra0
          }
          if (layers.vit !== undefined) {
            layer2 = layers.vit
          }
          if (layers.rawnet2 !== undefined) {
            layer3 = layers.rawnet2
          }
          if (layers.liveness !== undefined) {
            layer4 = layers.liveness
          }
        }
        
        const score = period.total > 0 ? (period.real_count / period.total) * 100 : 50
        const isDeepfake = period.fake_count > 0 && period.fake_count >= period.real_count
        
        return {
          id: period.period || idx,
          timestamp: new Date(period.timestamp).getTime() / 1000 || Math.floor(Date.now() / 1000) - (idx * 10),
          score: Math.round(score),
          verdict: isDeepfake ? "deepfake" : (period.total > 0 ? "authentic" : "suspicious") as SegmentResult['verdict'],
          layer1: layer1,
          layer2: layer2,
          layer3: layer3,
          layer4: layer4,
          layer1_label: layer1_label,
          layer2_label: layer2_label,
          layer3_label: layer3_label,
          layer4_label: layer4_label,
        }
      })
    } 
    // If report has layers directly
    else if (reportData.layers && Array.isArray(reportData.layers)) {
      segments = reportData.layers.map((layer: any, idx: number) => ({
        id: idx,
        timestamp: Math.floor(Date.now() / 1000) - (idx * 10),
        score: layer.score || 50,
        verdict: (layer.verdict || layer.status || "suspicious").toLowerCase() as SegmentResult['verdict'],
        layer1: layer.spectra0 || layer.layer1 || 0,
        layer2: layer.vit || layer.layer2 || 0,
        layer3: layer.rawnet2 || layer.layer3 || 0,
        layer4: layer.liveness || layer.layer4 || 0,
        layer1_label: layer.spectra0_label || layer.layer1_label || "Unknown",
        layer2_label: layer.vit_label || layer.layer2_label || "Unknown",
        layer3_label: layer.rawnet2_label || layer.layer3_label || "Unknown",
        layer4_label: layer.liveness_label || layer.layer4_label || "Unknown",
      }))
    }
    // If report is a single object with layer data
    else if (reportData.layers !== undefined) {
      const layers = reportData.layers
      const score = reportData.total_samples > 0 ? (reportData.total_real / reportData.total_samples) * 100 : 50
      const isDeepfake = reportData.total_fake > 0 && reportData.total_fake >= reportData.total_real
      
      segments = [{
        id: 0,
        timestamp: Math.floor(Date.now() / 1000),
        score: Math.round(score),
        verdict: isDeepfake ? "deepfake" : (reportData.total_samples > 0 ? "authentic" : "suspicious") as SegmentResult['verdict'],
        layer1: layers.spectra0 || layers.layer1 || 0,
        layer2: layers.vit || layers.layer2 || 0,
        layer3: layers.rawnet2 || layers.layer3 || 0,
        layer4: layers.liveness || layers.layer4 || 0,
        layer1_label: layers.spectra0_label || layers.layer1_label || "Unknown",
        layer2_label: layers.vit_label || layers.layer2_label || "Unknown",
        layer3_label: layers.rawnet2_label || layers.layer3_label || "Unknown",
        layer4_label: layers.liveness_label || layers.layer4_label || "Unknown",
      }]
    }
    // Fallback: try to extract from array
    else if (Array.isArray(reportData)) {
      segments = reportData
    }
    // Fallback: try to extract from results
    else if (reportData.results && Array.isArray(reportData.results)) {
      segments = reportData.results
    }
    // Fallback: single object
    else if (typeof reportData === 'object' && reportData !== null) {
      segments = [reportData]
    }

    let latestSegment: SegmentResult | null = null

    segments.forEach((seg: any, idx: number) => {
      const result: SegmentResult = {
        id: seg.id || seg.segment_id || idx,
        timestamp: seg.timestamp || Math.floor(Date.now() / 1000) - (idx * 10),
        score: seg.score || seg.confidence || seg.overall_score || 50,
        verdict: (seg.verdict || seg.label || seg.status || 'suspicious').toLowerCase() as SegmentResult['verdict'],
        layer1: seg.layer1 || seg.spectra0 || 0,
        layer2: seg.layer2 || seg.vit || 0,
        layer3: seg.layer3 || seg.rawnet2 || 0,
        layer4: seg.layer4 || seg.liveness || 0,
        layer1_label: seg.layer1_label || seg.spectra0_label || "Unknown",
        layer2_label: seg.layer2_label || seg.vit_label || "Unknown",
        layer3_label: seg.layer3_label || seg.rawnet2_label || "Unknown",
        layer4_label: seg.layer4_label || seg.liveness_label || "Unknown",
      }
      
      latestSegment = result
      setHistory(prev => {
        const exists = prev.some(p => p.id === result.id)
        if (exists) return prev
        return [result, ...prev.slice(0, 19)]
      })
    })

    if (latestSegment) {
      setCurrentSegment(latestSegment)
    }
  } catch (error) {
    console.error("Error processing report:", error)
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
  const [meetingName, setMeetingName] = useState<string | null>(null)
  
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const pollingRef = useRef<NodeJS.Timeout | null>(null)
  const isMounted = useRef(true)

  useEffect(() => {
    return () => {
      isMounted.current = false
      if (pollingRef.current) clearInterval(pollingRef.current)
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [])

  // ─── Stop detection when leaving page ──────────────────────────────────────
  useEffect(() => {
    return () => {
      const stopDetection = async () => {
        try {
          await fetch(`${process.env.NEXT_PUBLIC_API_URL}/deepmeet/detector/end`, {
            method: "POST"
          })
          console.log("✅ Detection stopped on page exit")
        } catch (e) {
          // silent
        }
      }
      stopDetection()
    }
  }, [])

  // ─── Stop detection on browser refresh/close ──────────────────────────────
  useEffect(() => {
    const handleBeforeUnload = () => {
      navigator.sendBeacon(
        `${process.env.NEXT_PUBLIC_API_URL}/deepmeet/detector/end`,
        new Blob()
      )
    }
    
    window.addEventListener('beforeunload', handleBeforeUnload)
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
    }
  }, [])

  // ─── Timer ──────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!isAnalyzing || isAborting) return
    timerRef.current = setInterval(() => setElapsed((p) => p + 1), 1000)
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [isAnalyzing, isAborting])

  // ─── Start Detection ──────────────────────────────────────────────────────
  const startAnalysis = useCallback(async () => {
    const newMeetingName = `meeting-${Date.now()}`
    setMeetingName(newMeetingName)
    localStorage.setItem("deepmeet-meeting", newMeetingName)

    try {
      console.log("🛑 Force stopping any existing detection...")
      
      for (let i = 0; i < 3; i++) {
        try {
          const stopRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/deepmeet/detector/end`, {
            method: "POST"
          })
          if (stopRes.ok) {
            console.log(`✅ Stopped existing detection (attempt ${i + 1})`)
            break
          }
        } catch (e) {
          console.warn(`⚠️ Stop attempt ${i + 1} failed:`, e)
        }
        await new Promise(resolve => setTimeout(resolve, 500))
      }

      await new Promise(resolve => setTimeout(resolve, 1000))

      console.log("🚀 Starting new detection...")
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/deepmeet/detector/start?meeting_name=${newMeetingName}`,
        { method: "POST" }
      )
      
      if (res.ok) {
        console.log("✅ Detection started for meeting:", newMeetingName)
      } else if (res.status === 409) {
        console.warn("⚠️ Detection still running, forcing restart...")
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}/deepmeet/detector/end`, {
          method: "POST"
        })
        await new Promise(resolve => setTimeout(resolve, 1000))
        const retryRes = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/deepmeet/detector/start?meeting_name=${newMeetingName}`,
          { method: "POST" }
        )
        if (retryRes.ok) {
          console.log("✅ Detection started on retry")
        } else {
          console.error("❌ Retry failed:", await retryRes.text())
          localStorage.removeItem("deepmeet-meeting")
          return
        }
      } else {
        console.error("❌ Failed to start detection:", await res.text())
        localStorage.removeItem("deepmeet-meeting")
        return
      }
    } catch (error) {
      console.error("Start detection error:", error)
      localStorage.removeItem("deepmeet-meeting")
      return
    }

    if (isMounted.current) {
      setSessionStarted(true)
      setIsAnalyzing(true)
      setIsAborting(false)
      setElapsed(0)
      setCurrentSegment(null)
      setHistory([])
    }
  }, [])

  // ─── Polling on results ──────────────────────────────────────────────────
  useEffect(() => {
    if (!isAnalyzing || !meetingName) return

    const pollReport = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/deepmeet/detector/report?meeting_name=${meetingName}`
        )
        
        if (res.status === 404) {
          console.log("⏳ No results yet, waiting...")
          return
        }
        
        if (!res.ok) {
          console.warn("Report fetch warning:", res.status)
          return
        }
        
        const data = await res.json()
        console.log("📥 Report data received:", data)
        
        if (data.report) {
          processReport(data.report, history, setHistory, setCurrentSegment)
        } else if (data.segments || data.results) {
          processReport(data, history, setHistory, setCurrentSegment)
        } else if (Array.isArray(data)) {
          processReport(data, history, setHistory, setCurrentSegment)
        } else {
          processReport(data, history, setHistory, setCurrentSegment)
        }
      } catch (error) {
        // silent fail - will retry on next interval
      }
    }

    pollReport()
    pollingRef.current = setInterval(pollReport, 5000)

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current)
    }
  }, [isAnalyzing, meetingName, history])

  // ─── End Detection ──────────────────────────────────────────────────────
  const abortAnalysis = useCallback(async () => {
    setIsAborting(true)
    setIsAnalyzing(false)
    
    if (pollingRef.current) clearInterval(pollingRef.current)
    if (timerRef.current) clearInterval(timerRef.current)

    try {
      await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/deepmeet/detector/end`,
        { method: "POST" }
      )
      console.log("✅ Detection stopped")
    } catch (error) {
      console.error("End detection error:", error)
    }

    setTimeout(() => {
      router.push("/results")
    }, 500)
  }, [router])

  // ─── Finish & Go to Results ──────────────────────────────────────────────
  const finishAndGoToResults = useCallback(async () => {
    setIsAnalyzing(false)
    
    if (pollingRef.current) clearInterval(pollingRef.current)
    if (timerRef.current) clearInterval(timerRef.current)

    try {
      await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/deepmeet/detector/end`,
        { method: "POST" }
      )
      console.log("✅ Detection stopped")
    } catch (error) {
      console.error("End detection error:", error)
    }

    router.push("/results")
  }, [router])

  // ─── Manual stop detection ──────────────────────────────────────────────
  const stopDetectionManually = useCallback(async () => {
    try {
      await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/deepmeet/detector/end`,
        { method: "POST" }
      )
      console.log("✅ Detection stopped manually")
      setIsAnalyzing(false)
      if (pollingRef.current) clearInterval(pollingRef.current)
      if (timerRef.current) clearInterval(timerRef.current)
    } catch (error) {
      console.error("Stop detection error:", error)
    }
  }, [])

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
                variant="outline"
                size="sm"
                onClick={stopDetectionManually}
                className="gap-1 h-7 px-3 border-red-300 text-red-600 hover:bg-red-50"
              >
                <Square className="h-3 w-3" />
                Stop
              </Button>
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

        {/* 4 Layers Grid - Real Results */}
        {currentSegment && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
            <div className="rounded-xl border border-border/50 bg-white/50 backdrop-blur-sm p-4 space-y-2">
              <span className="text-xs font-bold text-muted-foreground uppercase">Layer 1 · Spectra0</span>
              <div className="text-2xl font-bold">{currentSegment.layer1}%</div>
              <AnalysisMeter label="" value={currentSegment.layer1} color="primary" />
              <p className="text-[10px] text-muted-foreground">
                Weight: 0.42 · {currentSegment.layer1_label || "Analyzing..."}
              </p>
            </div>
            <div className="rounded-xl border border-border/50 bg-white/50 backdrop-blur-sm p-4 space-y-2">
              <span className="text-xs font-bold text-muted-foreground uppercase">Layer 2 · ViT</span>
              <div className="text-2xl font-bold">{currentSegment.layer2}%</div>
              <AnalysisMeter label="" value={currentSegment.layer2} color="primary" />
              <p className="text-[10px] text-muted-foreground">
                Weight: 0.26 · {currentSegment.layer2_label || "Analyzing..."}
              </p>
            </div>
            <div className="rounded-xl border border-border/50 bg-white/50 backdrop-blur-sm p-4 space-y-2">
              <span className="text-xs font-bold text-muted-foreground uppercase">Layer 3 · RawNet2</span>
              <div className="text-2xl font-bold">{currentSegment.layer3}%</div>
              <AnalysisMeter label="" value={currentSegment.layer3} color="primary" />
              <p className="text-[10px] text-muted-foreground">
                Weight: 0.172 · {currentSegment.layer3_label || "Analyzing..."}
              </p>
            </div>
            <div className="rounded-xl border border-border/50 bg-white/50 backdrop-blur-sm p-4 space-y-2">
              <span className="text-xs font-bold text-muted-foreground uppercase">Layer 4 · Liveness</span>
              <div className="text-2xl font-bold">{currentSegment.layer4}%</div>
              <AnalysisMeter label="" value={currentSegment.layer4} color="primary" />
              <p className="text-[10px] text-muted-foreground">
                Weight: 0.148 · {currentSegment.layer4_label || "Analyzing..."}
              </p>
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
                <SegmentHistoryItem 
                  key={`${segment.id}-${idx}`} 
                  segment={segment} 
                  index={idx} 
                />
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