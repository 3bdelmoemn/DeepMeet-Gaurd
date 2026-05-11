"use client"

import { useRef } from "react"
import { useFrame } from "@react-three/fiber"
import { MeshDistortMaterial, Sphere } from "@react-three/drei"
import type { Mesh } from "three"

interface AbstractOrbProps {
  position?: [number, number, number]
  scale?: number
  color?: string
  speed?: number
  distort?: number
}

export function AbstractOrb({ 
  position = [0, 0, 0], 
  scale = 1, 
  color = "#8b5cf6",
  speed = 2,
  distort = 0.4
}: AbstractOrbProps) {
  const ref = useRef<Mesh>(null)

  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.x = state.clock.elapsedTime * 0.2
      ref.current.rotation.y = state.clock.elapsedTime * 0.3
    }
  })

  return (
    <Sphere ref={ref} args={[1, 64, 64]} position={position} scale={scale}>
      <MeshDistortMaterial
        color={color}
        attach="material"
        distort={distort}
        speed={speed}
        roughness={0.1}
        metalness={0.8}
        emissive={color}
        emissiveIntensity={0.2}
      />
    </Sphere>
  )
}

interface GlassOrbProps {
  position?: [number, number, number]
  scale?: number
}

export function GlassOrb({ position = [0, 0, 0], scale = 1 }: GlassOrbProps) {
  const ref = useRef<Mesh>(null)

  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.y = state.clock.elapsedTime * 0.1
    }
  })

  return (
    <Sphere ref={ref} args={[1, 64, 64]} position={position} scale={scale}>
      <meshPhysicalMaterial
        color="#ffffff"
        transmission={0.95}
        thickness={1.5}
        roughness={0}
        metalness={0}
        ior={1.5}
        reflectivity={0.5}
        envMapIntensity={1}
      />
    </Sphere>
  )
}
