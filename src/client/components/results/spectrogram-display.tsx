"use client"

import { useRef, useMemo } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { OrbitControls } from "@react-three/drei"
import * as THREE from "three"

function SpectrogramBars({ isDeepfake }: { isDeepfake: boolean }) {
  const groupRef = useRef<THREE.Group>(null)
  const barsCount = 64
  const rows = 32
  
  // Generate random heights for spectrogram visualization
  const heights = useMemo(() => {
    const h: number[][] = []
    for (let row = 0; row < rows; row++) {
      h[row] = []
      for (let i = 0; i < barsCount; i++) {
        // Create wave-like patterns with anomalies for deepfake
        const base = Math.sin((i / barsCount) * Math.PI * 4) * 0.5 + 0.5
        const noise = Math.random() * 0.3
        const anomaly = isDeepfake && Math.random() > 0.85 ? Math.random() * 0.5 : 0
        h[row][i] = base + noise + anomaly
      }
    }
    return h
  }, [isDeepfake])

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.05 - 0.3
    }
  })

  return (
    <group ref={groupRef} position={[0, 0, 0]}>
      {heights.map((row, rowIndex) =>
        row.map((height, colIndex) => {
          const x = (colIndex - barsCount / 2) * 0.12
          const z = (rowIndex - rows / 2) * 0.12
          const h = height * 1.5 + 0.1
          
          // Color gradient based on height and deepfake status
          const color = isDeepfake
            ? new THREE.Color().setHSL(0, 0.8, 0.3 + height * 0.4) // Red tones
            : new THREE.Color().setHSL(0.55 + height * 0.1, 0.7, 0.4 + height * 0.3) // Blue-cyan
          
          return (
            <mesh key={`${rowIndex}-${colIndex}`} position={[x, h / 2, z]}>
              <boxGeometry args={[0.08, h, 0.08]} />
              <meshStandardMaterial
                color={color}
                emissive={color}
                emissiveIntensity={0.3}
                metalness={0.5}
                roughness={0.3}
              />
            </mesh>
          )
        })
      )}
    </group>
  )
}

interface SpectrogramDisplayProps {
  isDeepfake: boolean
  label: string
}

export function SpectrogramDisplay({ isDeepfake, label }: SpectrogramDisplayProps) {
  return (
    <div className="relative h-64 w-full overflow-hidden rounded-xl border border-border/50 bg-gradient-to-b from-slate-900 to-slate-950">
      <Canvas camera={{ position: [0, 4, 6], fov: 50 }}>
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={0.5} />
        <pointLight 
          position={[-5, 5, 5]} 
          intensity={0.5} 
          color={isDeepfake ? "#ff4444" : "#4488ff"} 
        />
        <SpectrogramBars isDeepfake={isDeepfake} />
        <OrbitControls 
          enableZoom={false} 
          enablePan={false}
          autoRotate
          autoRotateSpeed={0.5}
          minPolarAngle={Math.PI / 4}
          maxPolarAngle={Math.PI / 2.5}
        />
      </Canvas>
      <div className="absolute bottom-3 left-3 rounded-lg bg-black/60 px-3 py-1.5 backdrop-blur-sm">
        <span className={`text-sm font-medium ${isDeepfake ? "text-red-400" : "text-emerald-400"}`}>
          {label}
        </span>
      </div>
    </div>
  )
}
