"use client"

import { useState, useEffect, useRef, Suspense, useCallback } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { Environment, Float, MeshDistortMaterial, Sparkles } from "@react-three/drei"
import * as THREE from "three"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import {
  Shield,
  AlertTriangle,
  Clock,
  Mic,
  Zap,
  CheckCircle,
  TrendingUp,
  Activity,
  Square,
} from "lucide-react"

// ─── Types ─────────────────────────────────────────────────────────────────────
interface Message {
  type: "blue" | "red"
  text: string
  conf?: number
}

interface ConversationTurn {
  turn: number
  question: string
  answer: string
  timestamp: number
  tokens_sent: number
  tokens_recv: number
}

// ─── 3D Avatar: Blue Team ─────────────────────────────────────────────────────
function BlueAvatar({ isSpeaking }: { isSpeaking: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const ringRef = useRef<THREE.Mesh>(null)
  const glowRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (!meshRef.current || !ringRef.current) return
    meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.4) * 0.25
    const pulse = isSpeaking ? 1 + Math.sin(state.clock.elapsedTime * 8) * 0.08 : 1
    meshRef.current.scale.setScalar(pulse)
    ringRef.current.rotation.z = state.clock.elapsedTime * 0.5
    ringRef.current.rotation.x = state.clock.elapsedTime * 0.3
    if (glowRef.current) {
      glowRef.current.scale.setScalar(
        isSpeaking ? 1 + Math.sin(state.clock.elapsedTime * 6) * 0.2 : 1
      )
    }
  })

  return (
    <group>
      <mesh ref={glowRef}>
        <sphereGeometry args={[1.4, 32, 32]} />
        <meshBasicMaterial color="#6366f1" transparent opacity={isSpeaking ? 0.15 : 0.05} />
      </mesh>
      <mesh ref={meshRef}>
        <sphereGeometry args={[1.1, 64, 64]} />
        <MeshDistortMaterial
          color="#6366f1"
          emissive="#4338ca"
          emissiveIntensity={isSpeaking ? 0.8 : 0.4}
          metalness={0.6}
          roughness={0.1}
          distort={isSpeaking ? 0.35 : 0.12}
          speed={isSpeaking ? 4 : 1.5}
        />
      </mesh>
      <mesh ref={ringRef} rotation={[Math.PI / 3, 0, 0]}>
        <torusGeometry args={[1.7, 0.04, 16, 100]} />
        <meshStandardMaterial
          color="#a5b4fc"
          emissive="#818cf8"
          emissiveIntensity={isSpeaking ? 1.5 : 0.8}
        />
      </mesh>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[2.1, 0.02, 8, 64]} />
        <meshStandardMaterial
          color="#c7d2fe"
          emissive="#6366f1"
          emissiveIntensity={isSpeaking ? 1 : 0.5}
          transparent
          opacity={isSpeaking ? 0.8 : 0.5}
        />
      </mesh>
      {Array.from({ length: 12 }).map((_, i) => {
        const angle = (i / 12) * Math.PI * 2
        return (
          <mesh
            key={i}
            position={[Math.cos(angle) * 1.9, Math.sin(angle * 0.7) * 0.5, Math.sin(angle) * 1.9]}
          >
            <sphereGeometry args={[0.04, 8, 8]} />
            <meshStandardMaterial
              color="#818cf8"
              emissive="#6366f1"
              emissiveIntensity={isSpeaking ? 2 : 1}
            />
          </mesh>
        )
      })}
    </group>
  )
}

// ─── 3D Avatar: Red Team ──────────────────────────────────────────────────────
function RedAvatar({ isSpeaking, glitchLevel }: { isSpeaking: boolean; glitchLevel: number }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const crackRef = useRef<THREE.Mesh>(null)
  const glowRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (!meshRef.current || !crackRef.current) return
    meshRef.current.rotation.y =
      state.clock.elapsedTime * 0.6 + Math.sin(state.clock.elapsedTime * 12) * 0.05
    meshRef.current.position.x =
      glitchLevel > 0 ? Math.sin(state.clock.elapsedTime * 20) * 0.08 * glitchLevel : 0
    meshRef.current.scale.setScalar(
      isSpeaking ? 1 + Math.sin(state.clock.elapsedTime * 10) * 0.08 : 1
    )
    crackRef.current.rotation.z = state.clock.elapsedTime * -0.8
    if (glowRef.current) {
      glowRef.current.scale.setScalar(
        isSpeaking ? 1 + Math.sin(state.clock.elapsedTime * 8) * 0.2 : 1
      )
    }
  })

  return (
    <group>
      <mesh ref={glowRef}>
        <sphereGeometry args={[1.4, 32, 32]} />
        <meshBasicMaterial color="#ef4444" transparent opacity={isSpeaking ? 0.15 : 0.05} />
      </mesh>
      <mesh ref={meshRef}>
        <sphereGeometry args={[1.1, 64, 64]} />
        <MeshDistortMaterial
          color="#ef4444"
          emissive="#991b1b"
          emissiveIntensity={isSpeaking ? 0.8 : 0.5}
          metalness={0.3}
          roughness={0.2}
          distort={isSpeaking ? 0.5 : 0.2}
          speed={isSpeaking ? 6 : 2}
        />
      </mesh>
      <mesh ref={crackRef} rotation={[Math.PI / 4, 0, 0]}>
        <torusGeometry args={[1.7, 0.03, 8, 40, Math.PI * 1.6]} />
        <meshStandardMaterial
          color="#fca5a5"
          emissive="#ef4444"
          emissiveIntensity={isSpeaking ? 1.5 : 0.9}
        />
      </mesh>
      {[1.5, 1.9, 2.3].map((r, i) => (
        <mesh key={i} rotation={[Math.PI / 2 + i * 0.4, 0, i * 0.8]}>
          <torusGeometry args={[r, 0.015, 4, 32]} />
          <meshStandardMaterial
            color="#f87171"
            emissive="#dc2626"
            emissiveIntensity={isSpeaking ? 1 : 0.6}
            transparent
            opacity={isSpeaking ? 0.6 : 0.4}
          />
        </mesh>
      ))}
    </group>
  )
}

// ─── Finished 3D Screen ───────────────────────────────────────────────────────
function Finished3DScreen() {
  const groupRef = useRef<THREE.Group>(null)
  const sphereRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.8) * 0.5
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 1) * 0.3
    }
    if (sphereRef.current) {
      sphereRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 2) * 0.06)
    }
  })

  return (
    <group ref={groupRef}>
      <ambientLight intensity={0.3} />
      <pointLight position={[2, 2, 2]} intensity={0.5} color="#6366f1" />
      <pointLight position={[-2, -1, 1]} intensity={0.3} color="#a855f7" />
      <mesh ref={sphereRef}>
        <sphereGeometry args={[1.0, 64, 64]} />
        <MeshDistortMaterial
          color="#4f46e5"
          emissive="#312e81"
          emissiveIntensity={0.5}
          metalness={0.7}
          roughness={0.2}
          distort={0.15}
          speed={1.5}
        />
      </mesh>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[1.8, 0.04, 32, 100]} />
        <meshStandardMaterial color="#818cf8" emissive="#4f46e5" emissiveIntensity={0.3} transparent opacity={0.8} />
      </mesh>
      <mesh rotation={[Math.PI / 3, Math.PI / 6, 0]}>
        <torusGeometry args={[2.1, 0.03, 32, 100]} />
        <meshStandardMaterial color="#a5b4fc" emissive="#6366f1" emissiveIntensity={0.2} transparent opacity={0.6} />
      </mesh>
      <Sparkles count={80} scale={6} size={0.15} color="#818cf8" speed={0.5} />
    </group>
  )
}

// ─── Message Bubble ───────────────────────────────────────────────────────────
function MessageBubble({
  text, side, index, confidence,
}: {
  text: string; side: "blue" | "red"; index: number; confidence?: number
}) {
  const isBlue = side === "blue"
  if (!text) return null

  return (
    <div
      className={cn("flex gap-3 animate-slide-up", isBlue ? "flex-row" : "flex-row-reverse")}
      style={{ animationDelay: `${index * 80}ms` }}
    >
      <div className={cn(
        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-lg",
        isBlue
          ? "bg-gradient-to-br from-indigo-500 to-violet-500"
          : "bg-gradient-to-br from-red-500 to-orange-500",
      )}>
        {isBlue
          ? <Shield className="h-4 w-4 text-white" />
          : <AlertTriangle className="h-4 w-4 text-white" />}
      </div>

      <div className={cn("flex-1 max-w-[85%]", !isBlue && "flex flex-col items-end")}>
        <span className={cn(
          "text-[10px] font-bold uppercase tracking-widest mb-1",
          isBlue ? "text-indigo-500" : "text-red-500",
        )}>
          {isBlue
            ? "🔵 BLUE TEAM (Interviewer - Real Human)"
            : "🔴 RED TEAM (AI Attacker - Cloned Voice)"}
        </span>
        <div className={cn(
          "rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm relative overflow-hidden",
          isBlue
            ? "bg-indigo-50 border border-indigo-200 text-indigo-900 rounded-tl-sm"
            : "bg-red-50 border border-red-200 text-red-900 rounded-tr-sm",
        )}>
          {!isBlue && (
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-red-200/20 to-transparent animate-gradient-shift pointer-events-none" />
          )}
          <p className="relative">{text}</p>
        </div>
        {!isBlue && confidence !== undefined && (
          <div className="flex items-center gap-1 mt-1.5 px-2 py-0.5 rounded-full bg-red-100 border border-red-200 w-fit">
            <TrendingUp className="h-3 w-3 text-red-600" />
            <span className="text-[10px] font-bold text-red-700">{confidence}% AI-synthesized</span>
          </div>
        )}
      </div>
    </div>
  )
}

// ─── Avatar Containers ────────────────────────────────────────────────────────
const BlueAvatarContainer = ({ isActive }: { isActive: boolean }) => (
  <Canvas camera={{ position: [0, 0, 4.5], fov: 50 }}>
    <Suspense fallback={null}>
      <ambientLight intensity={0.6} />
      <directionalLight position={[3, 3, 3]} intensity={1.2} />
      <pointLight position={[-3, 2, 2]} intensity={0.8} color="#6366f1" />
      <Environment preset="studio" />
      <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.4}>
        <BlueAvatar isSpeaking={isActive} />
      </Float>
    </Suspense>
  </Canvas>
)

const RedAvatarContainer = ({
  isActive, glitchLevel,
}: { isActive: boolean; glitchLevel: number }) => (
  <Canvas camera={{ position: [0, 0, 4.5], fov: 50 }}>
    <Suspense fallback={null}>
      <ambientLight intensity={0.4} />
      <directionalLight position={[3, 3, 3]} intensity={0.8} />
      <pointLight position={[-3, 2, 2]} intensity={1} color="#ef4444" />
      <Environment preset="dawn" />
      <Float speed={2.5} rotationIntensity={0.4} floatIntensity={0.6}>
        <RedAvatar isSpeaking={isActive} glitchLevel={glitchLevel} />
      </Float>
    </Suspense>
  </Canvas>
)

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function MeetingPage() {
  const [elapsed, setElapsed] = useState(0)
  const [blueActive, setBlueActive] = useState(false)
  const [redActive, setRedActive] = useState(false)
  const [glitchLevel, setGlitchLevel] = useState(0)
  const [messages, setMessages] = useState<Message[]>([])
  const [isFinished, setIsFinished] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [userId, setUserId] = useState<string | null>(null)
  const [simStarted, setSimStarted] = useState(false)
  const [backendSpeaker, setBackendSpeaker] = useState<string | null>(null)
  const [backendState, setBackendState] = useState("IDLE")
  const seenTurnsRef = useRef<Set<number>>(new Set())
  const transcriptRef = useRef<HTMLDivElement>(null)
  const blueTimerRef = useRef<NodeJS.Timeout | null>(null)
  const redTimerRef = useRef<NodeJS.Timeout | null>(null)

  const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

  // ─── Get userId ───────────────────────────────────────────────────────────
  useEffect(() => {
    const id = localStorage.getItem("deepmeet-user-id")
    console.log("🔍 Retrieved user_id from localStorage:", id)
    setUserId(id)
    if (!id) {
      console.warn("⚠️ No user_id found in localStorage")
    }
  }, [])

  // ─── Timer ────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (isFinished) return
    const t = setInterval(() => setElapsed((p) => p + 1), 1000)
    return () => clearInterval(t)
  }, [isFinished])

  // ─── Auto-scroll ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (transcriptRef.current)
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight
  }, [messages])

  // ─── Avatar helpers ───────────────────────────────────────────────────────
  const clearBlueTimer = () => {
    if (blueTimerRef.current) { clearTimeout(blueTimerRef.current); blueTimerRef.current = null }
  }
  const clearRedTimer = () => {
    if (redTimerRef.current) { clearTimeout(redTimerRef.current); redTimerRef.current = null }
  }

  const activateBlue = useCallback((duration = 2500) => {
    clearBlueTimer()
    setBlueActive(true)
    blueTimerRef.current = setTimeout(() => setBlueActive(false), duration)
  }, [])

  const activateRed = useCallback((duration = 4000) => {
    clearRedTimer()
    setRedActive(true)
    setGlitchLevel(0.5)
    redTimerRef.current = setTimeout(() => { setRedActive(false); setGlitchLevel(0) }, duration)
  }, [])

  // ─── STEP 1: Stop detector and start simulation ──────────────────────────
  useEffect(() => {
    if (!userId || simStarted) return

    const boot = async () => {
      try {
        console.log("🚀 Stopping detector and starting simulation for user:", userId)
        
        // Stop detector
        await fetch(`${API}/deepmeet/detector/end`, { method: "POST" })
        console.log("✅ Detector stop request sent")
      } catch {
        // silent — 409 if no detector running
      }

      try {
        const res = await fetch(
          `${API}/deepmeet/simulator/communication/start?user_id=${userId}`,
          { method: "POST" },
        )
        if (res.ok) {
          console.log("✅ Simulation started successfully")
          setSimStarted(true)
          setIsListening(true)
        } else if (res.status === 409) {
          console.log("✅ Simulation already running")
          setSimStarted(true)
          setIsListening(true)
        } else {
          const errorText = await res.text()
          console.warn("⚠️ Start simulation warning:", res.status, errorText)
        }
      } catch (err) {
        console.error("❌ Start simulation error:", err)
      }
    }

    boot()
  }, [userId, simStarted, API])

  // ─── STEP 2: Poll for messages from backend ──────────────────────────────
// ─── STEP 2: Poll for messages from backend ──────────────────────────
useEffect(() => {
  if (!userId) return

  const pollConversation = async () => {
    try {
      // Live state — خفيف، كل 500ms مقبول
      const liveRes = await fetch(`${API}/deepmeet/simulator/communication/live`)
      if (liveRes.ok) {
        const liveData = await liveRes.json()
        setBackendSpeaker(liveData.speaker)
        setBackendState(liveData.state)

        if (liveData.speaker === "interviewer") {
          setBlueActive(true); setRedActive(false); setGlitchLevel(0)
        } else if (liveData.speaker === "interviewee") {
          setBlueActive(false); setRedActive(true); setGlitchLevel(0.5)
        } else {
          setBlueActive(false); setRedActive(false); setGlitchLevel(0)
        }
      }
    } catch (err) {
      console.error("Live poll error", err)
    }
  }

  // ✅ Report poll منفصل وأبطأ — مش محتاج يتحدث كل 500ms
  const pollReport = async () => {
    try {
      const reportRes = await fetch(
        `${API}/deepmeet/simulator/communication/report?user_id=${userId}`,
        { method: "POST" }
      )
      if (!reportRes.ok) return

      const reportData = await reportRes.json()
      const turns = reportData.report || []

      turns.forEach((turn: ConversationTurn) => {
        if (seenTurnsRef.current.has(turn.turn)) return
        seenTurnsRef.current.add(turn.turn)

        const newMessages: Message[] = []
        if (turn.question?.trim()) {
          newMessages.push({ type: "blue", text: turn.question.trim() })
        }
        if (turn.answer?.trim()) {
          newMessages.push({
            type: "red",
            text: turn.answer.trim(),
            conf: Math.floor(Math.random() * 50) + 50,
          })
        }
        if (newMessages.length > 0) {
          setMessages(prev => [...prev, ...newMessages])
        }
      })
    } catch (err) {
      console.error("Report poll error", err)
    }
  }

  // ✅ Live: كل 500ms | Report: كل 2000ms
  const liveInterval = setInterval(pollConversation, 500)
  const reportInterval = setInterval(pollReport, 2000)

  // شغّل مرة فوراً
  pollConversation()
  pollReport()

  return () => {
    clearInterval(liveInterval)
    clearInterval(reportInterval)
  }
}, [userId, API])
  // ─── Health check ─────────────────────────────────────────────────────────
  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch(`${API}/deepmeet/health`)
        const data = await res.json()
        
        if (data.listening_active !== undefined) {
          setIsListening(data.listening_active)
        }
      } catch {
        // silent fail
      }
    }
    check()
    const interval = setInterval(check, 5000)
    return () => clearInterval(interval)
  }, [API])

  // ─── Stop simulation ───────────────────────────────────────────────────────
  const stopSimulation = async () => {
    if (userId) {
      try {
        await fetch(
          `${API}/deepmeet/simulator/communication/end?user_id=${userId}`,
          { method: "POST" },
        )
        console.log("✅ Simulation stopped")
      } catch {
        // silent
      }
    }
    setIsFinished(true)
  }

  const formatTime = (s: number) =>
    `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`

  // ─── Finished Screen ───────────────────────────────────────────────────────
  if (isFinished) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 flex flex-col items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 opacity-70">
          <Canvas camera={{ position: [0, 0, 7], fov: 45 }}>
            <Environment preset="night" />
            <Finished3DScreen />
          </Canvas>
        </div>
        <div className="relative z-10 text-center space-y-6 bg-black/30 backdrop-blur-sm rounded-2xl p-8 mx-4">
          <div className="animate-bounce">
            <Shield className="h-16 w-16 text-indigo-400 mx-auto" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white drop-shadow-lg">
            Simulation Complete
          </h1>
          <p className="text-indigo-200 text-base max-w-md mx-auto">
            The voice clone attack has been successfully detected and neutralized.
          </p>
          <div className="flex gap-4 justify-center pt-4">
            <Button
              onClick={() => (window.location.href = "/simulation")}
              className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-6 py-5 text-base shadow-xl"
            >
              Start New Simulation
            </Button>
          </div>
        </div>
        <div className="absolute bottom-8 left-0 right-0 text-center text-indigo-300/40 text-xs">
          Simulation Completed • Session Ended
        </div>
      </div>
    )
  }

  // ─── Main Render ───────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50/30 pt-16">

      {/* Top Status Bar */}
      <div className="fixed top-16 left-0 right-0 z-50 bg-white/90 backdrop-blur-xl border-b border-border/60 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-2.5 flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className={cn(
                "h-2.5 w-2.5 rounded-full",
                isListening ? "bg-green-500 animate-pulse" : "bg-amber-500 animate-pulse",
              )} />
              <span className="text-sm font-bold text-foreground">
                {
                  backendState === "LISTENING"
                   ? "LISTENING"

                  : backendState === "PROCESSING"
                  ? "THINKING"

                  : backendState === "SPEAKING"
                  ? "SPEAKING"

                  : backendState === "COOLDOWN"
                  ? "COOLDOWN"

                  : "STARTING..."
                }
              </span>
            </div>
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Clock className="h-3.5 w-3.5" />
              <span className="font-mono text-sm">{formatTime(elapsed)}</span>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-3">
            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-xs font-bold text-indigo-700">
              <Shield className="h-3.5 w-3.5" /> Blue Team — Interviewer
            </span>
            <span className="text-muted-foreground font-light">vs</span>
            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-50 border border-red-200 text-xs font-bold text-red-700">
              <AlertTriangle className="h-3.5 w-3.5" /> Red Team — Attacker
            </span>
          </div>

          <Button
            variant="destructive"
            size="sm"
            onClick={stopSimulation}
            className="gap-1 h-7 px-3"
          >
            <Square className="h-3 w-3" />
            End Session
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 pt-16 pb-12">
        <div className="grid lg:grid-cols-[1fr_420px] gap-6 items-start">

          {/* Left — Avatars */}
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">

              {/* 🔵 Blue Team */}
              <div className="space-y-3">
                <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-indigo-50 border border-indigo-200">
                  <Shield className="h-4 w-4 text-indigo-600" />
                  <div>
                    <p className="text-xs font-bold text-indigo-700">Blue Team</p>
                    <p className="text-[10px] text-indigo-500">Human Interviewer</p>
                  </div>
                  <CheckCircle className="h-4 w-4 text-emerald-500 ml-auto" />
                </div>
                <div
                  className="rounded-2xl overflow-hidden border border-indigo-100 shadow-lg shadow-indigo-100/60 bg-gradient-to-b from-indigo-50 to-white"
                  style={{ height: 320 }}
                >
                  <BlueAvatarContainer isActive={blueActive} />
                </div>
                <div className={cn(
                  "flex items-center justify-center gap-2 py-2 rounded-xl text-xs font-semibold transition-all duration-300",
                  blueActive
                    ? "bg-indigo-100 border border-indigo-300 text-indigo-700"
                    : "bg-muted/50 border border-border/40 text-muted-foreground",
                )}>
                  <Mic className={cn("h-3.5 w-3.5", blueActive && "animate-pulse")} />
                  {
                   backendSpeaker === "interviewer"
                    ? "Speaking..."
                    : "Idle"
                    }
                </div>
              </div>

              {/* 🔴 Red Team */}
              <div className="space-y-3">
                <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-red-50 border border-red-200">
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                  <div>
                    <p className="text-xs font-bold text-red-700">Red Team</p>
                    <p className="text-[10px] text-red-500">Voice Clone Attacker</p>
                  </div>
                </div>
                <div
                  className="rounded-2xl overflow-hidden border-2 border-red-200 shadow-lg shadow-red-100/60 bg-gradient-to-b from-red-50 to-white relative"
                  style={{ height: 320 }}
                >
                  <RedAvatarContainer isActive={redActive} glitchLevel={glitchLevel} />
                  {glitchLevel > 0.5 && (
                    <div className="absolute inset-0 pointer-events-none rounded-2xl overflow-hidden">
                      {Array.from({ length: 6 }).map((_, i) => (
                        <div
                          key={i}
                          className="absolute left-0 right-0 h-px bg-red-400/30 animate-pulse"
                          style={{ top: `${15 + i * 14}%`, animationDelay: `${i * 0.1}s` }}
                        />
                      ))}
                    </div>
                  )}
                </div>
                <div className={cn(
                  "flex items-center justify-center gap-2 py-2 rounded-xl text-xs font-semibold transition-all duration-300",
                  redActive
                    ? "bg-red-100 border border-red-300 text-red-700"
                    : "bg-muted/50 border border-border/40 text-muted-foreground",
                )}>
                  <Zap className={cn("h-3.5 w-3.5", redActive && "animate-pulse")} />
                  {
 backendSpeaker === "interviewee"
 ? "Speaking with Cloned Voice"
 : "Idle"
}
                </div>
              </div>
            </div>
          </div>

          {/* Right — Live Transcript */}
          <div className="flex flex-col gap-3 lg:sticky lg:top-36">
            <div className="glass-card overflow-hidden">
              <div className="flex items-center gap-3 px-5 py-4 border-b border-border/50 bg-gradient-to-r from-indigo-50 to-red-50/30">
                <Activity className="h-4 w-4 text-primary" />
                <h2 className="font-bold text-sm text-foreground">Live Transcript</h2>
                <div className="ml-auto flex items-center gap-1.5">
                  <span className={cn(
                    "h-2 w-2 rounded-full",
                    simStarted ? "bg-green-500 animate-pulse" : "bg-amber-500 animate-pulse",
                  )} />
                  <span className="text-xs text-muted-foreground font-medium">
                    {simStarted ? "Live" : "Starting..."}
                  </span>
                </div>
              </div>

              <div className="p-4 bg-yellow-50/50 border-b border-yellow-100 text-center">
                <Mic className="h-4 w-4 text-yellow-600 inline mr-2" />
                <span className="text-xs text-yellow-700">
                  {simStarted
                    ? "🎤 Speak into your microphone — the AI will respond automatically"
                    : "⏳ Starting simulation, please wait..."}
                </span>
              </div>

              <div
                ref={transcriptRef}
                className="p-5 space-y-4 overflow-y-auto"
                style={{ maxHeight: "calc(100vh - 380px)", minHeight: 420 }}
              >
                {messages.length === 0 && (
                  <div className="flex flex-col items-center justify-center py-10 text-center">
                    <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mb-3">
                      <Mic className="h-5 w-5 text-muted-foreground" />
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {simStarted
                        ? "Say something to start the conversation..."
                        : "Initializing simulation..."}
                    </p>
                  </div>
                )}

                {messages.map((msg, i) => (
                  <MessageBubble
                    key={`${msg.type}-${i}`}
                    text={msg.text}
                    side={msg.type}
                    index={i}
                    confidence={msg.conf}
                  />
                ))}

                {simStarted && messages.length > 0 && !redActive && (
                  <div className="flex items-center justify-center gap-2 py-2">
                    <div className="flex gap-1">
                      {[0, 1, 2].map((i) => (
                        <span
                          key={i}
                          className="h-2 w-2 rounded-full bg-green-500 animate-bounce"
                          style={{ animationDelay: `${i * 0.15}s` }}
                        />
                      ))}
                    </div>
                    <span className="text-xs text-green-600">Listening for your voice...</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}