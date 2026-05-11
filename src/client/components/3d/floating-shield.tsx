"use client"

import { useRef } from "react"
import { useFrame } from "@react-three/fiber"
import { MeshTransmissionMaterial, RoundedBox } from "@react-three/drei"
import type { Mesh, Group } from "three"

interface FloatingShieldProps {
  scale?: number
}

export function FloatingShield({ scale = 1 }: FloatingShieldProps) {
  const groupRef = useRef<Group>(null)
  const innerRef = useRef<Mesh>(null)
  const outerRef = useRef<Mesh>(null)

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.2
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.3) * 0.1
    }
    if (innerRef.current) {
      innerRef.current.rotation.z = state.clock.elapsedTime * 0.5
    }
    if (outerRef.current) {
      outerRef.current.rotation.z = -state.clock.elapsedTime * 0.3
    }
  })

  return (
    <group ref={groupRef} scale={scale}>
      {/* Outer glass shield */}
      <mesh ref={outerRef}>
        <torusGeometry args={[1.8, 0.08, 16, 100]} />
        <MeshTransmissionMaterial
          backside
          samples={16}
          thickness={0.2}
          chromaticAberration={0.1}
          anisotropy={0.3}
          distortion={0.2}
          distortionScale={0.5}
          temporalDistortion={0.1}
          color="#8b5cf6"
          transmission={0.95}
          roughness={0.1}
        />
      </mesh>

      {/* Inner rotating ring */}
      <mesh ref={innerRef}>
        <torusGeometry args={[1.2, 0.06, 16, 100]} />
        <meshStandardMaterial
          color="#06b6d4"
          emissive="#06b6d4"
          emissiveIntensity={0.5}
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>

      {/* Central core */}
      <RoundedBox args={[0.8, 0.8, 0.15]} radius={0.1} smoothness={4}>
        <MeshTransmissionMaterial
          backside
          samples={16}
          thickness={0.5}
          chromaticAberration={0.2}
          anisotropy={0.5}
          distortion={0.3}
          distortionScale={0.3}
          temporalDistortion={0.2}
          color="#6366f1"
          transmission={0.9}
          roughness={0.05}
        />
      </RoundedBox>

      {/* Shield icon shape */}
      <mesh position={[0, 0, 0.1]}>
        <planeGeometry args={[0.5, 0.6]} />
        <meshStandardMaterial
          color="#f43f5e"
          emissive="#f43f5e"
          emissiveIntensity={0.8}
          transparent
          opacity={0.9}
        />
      </mesh>

      {/* Orbiting particles */}
      {[...Array(8)].map((_, i) => (
        <OrbitingParticle key={i} index={i} />
      ))}
    </group>
  )
}

function OrbitingParticle({ index }: { index: number }) {
  const ref = useRef<Mesh>(null)
  const offset = (index / 8) * Math.PI * 2
  const radius = 2.2 + (index % 2) * 0.3

  useFrame((state) => {
    if (ref.current) {
      const time = state.clock.elapsedTime * 0.5 + offset
      ref.current.position.x = Math.cos(time) * radius
      ref.current.position.y = Math.sin(time) * radius
      ref.current.position.z = Math.sin(time * 2) * 0.3
    }
  })

  const colors = ["#8b5cf6", "#06b6d4", "#f43f5e", "#22d3ee"]

  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.05, 16, 16]} />
      <meshStandardMaterial
        color={colors[index % colors.length]}
        emissive={colors[index % colors.length]}
        emissiveIntensity={1}
      />
    </mesh>
  )
}
