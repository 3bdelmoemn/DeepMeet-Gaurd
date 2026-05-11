"use client"

import { Canvas } from "@react-three/fiber"
import { Environment, Float, OrbitControls } from "@react-three/drei"
import { Suspense, type ReactNode } from "react"

interface Scene3DProps {
  children: ReactNode
  className?: string
  controls?: boolean
  environment?: "apartment" | "city" | "dawn" | "forest" | "lobby" | "night" | "park" | "studio" | "sunset" | "warehouse"
}

export function Scene3D({ 
  children, 
  className = "w-full h-full", 
  controls = false,
  environment = "lobby"
}: Scene3DProps) {
  return (
    <div className={className}>
      <Canvas
        camera={{ position: [0, 0, 5], fov: 45 }}
        gl={{ antialias: true, alpha: true }}
        style={{ background: "transparent" }}
      >
        <Suspense fallback={null}>
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          <pointLight position={[-10, -10, -5]} intensity={0.5} color="#8b5cf6" />
          <Environment preset={environment} />
          {children}
          {controls && <OrbitControls enableZoom={false} enablePan={false} />}
        </Suspense>
      </Canvas>
    </div>
  )
}

interface FloatWrapperProps {
  children: ReactNode
  speed?: number
  rotationIntensity?: number
  floatIntensity?: number
}

export function FloatWrapper({ 
  children, 
  speed = 2, 
  rotationIntensity = 0.5, 
  floatIntensity = 1 
}: FloatWrapperProps) {
  return (
    <Float speed={speed} rotationIntensity={rotationIntensity} floatIntensity={floatIntensity}>
      {children}
    </Float>
  )
}
