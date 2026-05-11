"use client"

import dynamic from "next/dynamic"
import { Suspense } from "react"

const Scene3D = dynamic(() => import("@/components/3d/scene-3d").then(mod => ({ default: mod.Scene3D })), {
  ssr: false,
})

const FloatingShield = dynamic(() => import("@/components/3d/floating-shield").then(mod => ({ default: mod.FloatingShield })), {
  ssr: false,
})

const ParticleField = dynamic(() => import("@/components/3d/particle-field").then(mod => ({ default: mod.ParticleField })), {
  ssr: false,
})

const FloatWrapper = dynamic(() => import("@/components/3d/scene-3d").then(mod => ({ default: mod.FloatWrapper })), {
  ssr: false,
})

export function Hero3D() {
  return (
    <div className="absolute inset-0 -z-10">
      <Suspense fallback={<div className="h-full w-full bg-gradient-to-br from-primary/5 via-background to-violet-500/5" />}>
        <Scene3D className="h-full w-full" environment="lobby">
          <FloatWrapper speed={1.5} rotationIntensity={0.3} floatIntensity={0.8}>
            <FloatingShield scale={1.2} />
          </FloatWrapper>
          <ParticleField count={150} spread={12} color="#8b5cf6" size={0.03} />
          <ParticleField count={100} spread={10} color="#06b6d4" size={0.02} />
        </Scene3D>
      </Suspense>
    </div>
  )
}
