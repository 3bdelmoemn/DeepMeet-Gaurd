"use client"

import { useRef, useMemo } from "react"
import { useFrame } from "@react-three/fiber"
import { Sphere, MeshDistortMaterial, Float, Ring } from "@react-three/drei"
import type { Mesh, Group } from "three"
import * as THREE from "three"

interface AIAvatarProps {
  isSpeaking: boolean
  position?: [number, number, number]
}

export function AIAvatar({ isSpeaking, position = [0, 0, 0] }: AIAvatarProps) {
  const groupRef = useRef<Group>(null)
  const coreRef = useRef<Mesh>(null)
  const ring1Ref = useRef<Mesh>(null)
  const ring2Ref = useRef<Mesh>(null)
  const ring3Ref = useRef<Mesh>(null)

  // Particle positions for orbiting particles
  const particles = useMemo(() => {
    const count = 50
    const positions = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      const theta = (i / count) * Math.PI * 2
      const radius = 1.5 + Math.random() * 0.5
      positions[i * 3] = Math.cos(theta) * radius
      positions[i * 3 + 1] = (Math.random() - 0.5) * 1.5
      positions[i * 3 + 2] = Math.sin(theta) * radius
    }
    return positions
  }, [])

  useFrame((state) => {
    const t = state.clock.elapsedTime

    if (coreRef.current) {
      // Pulsing effect when speaking
      const scale = isSpeaking 
        ? 1 + Math.sin(t * 8) * 0.1 
        : 1 + Math.sin(t * 2) * 0.02
      coreRef.current.scale.setScalar(scale)
    }

    if (ring1Ref.current) {
      ring1Ref.current.rotation.x = t * 0.5
      ring1Ref.current.rotation.y = t * 0.3
    }
    if (ring2Ref.current) {
      ring2Ref.current.rotation.x = -t * 0.4
      ring2Ref.current.rotation.z = t * 0.2
    }
    if (ring3Ref.current) {
      ring3Ref.current.rotation.y = t * 0.6
      ring3Ref.current.rotation.z = -t * 0.3
    }

    if (groupRef.current) {
      groupRef.current.rotation.y = t * 0.1
    }
  })

  return (
    <group ref={groupRef} position={position}>
      <Float speed={2} rotationIntensity={0.2} floatIntensity={0.5}>
        {/* Core sphere - AI brain */}
        <Sphere ref={coreRef} args={[0.8, 64, 64]}>
          <MeshDistortMaterial
            color="#8b5cf6"
            attach="material"
            distort={isSpeaking ? 0.5 : 0.3}
            speed={isSpeaking ? 4 : 2}
            roughness={0.1}
            metalness={0.9}
            emissive="#8b5cf6"
            emissiveIntensity={isSpeaking ? 0.5 : 0.2}
          />
        </Sphere>

        {/* Inner glow sphere */}
        <Sphere args={[0.85, 32, 32]}>
          <meshBasicMaterial
            color="#c4b5fd"
            transparent
            opacity={isSpeaking ? 0.3 : 0.1}
          />
        </Sphere>

        {/* Orbiting rings */}
        <Ring ref={ring1Ref} args={[1.1, 1.15, 64]}>
          <meshBasicMaterial color="#06b6d4" transparent opacity={0.6} side={THREE.DoubleSide} />
        </Ring>
        
        <Ring ref={ring2Ref} args={[1.3, 1.35, 64]}>
          <meshBasicMaterial color="#8b5cf6" transparent opacity={0.4} side={THREE.DoubleSide} />
        </Ring>

        <Ring ref={ring3Ref} args={[1.5, 1.53, 64]}>
          <meshBasicMaterial color="#ec4899" transparent opacity={0.3} side={THREE.DoubleSide} />
        </Ring>

        {/* Orbiting particles */}
        <points>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={particles.length / 3}
              array={particles}
              itemSize={3}
            />
          </bufferGeometry>
          <pointsMaterial
            size={0.05}
            color={isSpeaking ? "#06b6d4" : "#8b5cf6"}
            transparent
            opacity={0.8}
            sizeAttenuation
          />
        </points>
      </Float>
    </group>
  )
}

export function SpeakingWaves({ isSpeaking }: { isSpeaking: boolean }) {
  const ref = useRef<Group>(null)

  useFrame((state) => {
    if (ref.current && isSpeaking) {
      ref.current.children.forEach((child, i) => {
        const mesh = child as Mesh
        const scale = 1 + Math.sin(state.clock.elapsedTime * 8 + i * 0.5) * 0.3
        mesh.scale.setScalar(scale)
      })
    }
  })

  if (!isSpeaking) return null

  return (
    <group ref={ref} position={[0, -1.5, 0]}>
      {[...Array(5)].map((_, i) => (
        <Ring key={i} args={[0.3 + i * 0.15, 0.32 + i * 0.15, 32]} rotation={[-Math.PI / 2, 0, 0]}>
          <meshBasicMaterial color="#8b5cf6" transparent opacity={0.3 - i * 0.05} side={THREE.DoubleSide} />
        </Ring>
      ))}
    </group>
  )
}
