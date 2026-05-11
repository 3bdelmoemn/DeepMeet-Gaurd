"use client"

import Link from "next/link"
import { cn } from "@/lib/utils"
import { ArrowRight, Shield, Brain, Mic } from "lucide-react"

interface FeatureCardProps {
  iconName: "shield" | "brain" | "mic"
  title: string
  description: string
  href: string
  gradient: "indigo" | "teal" | "coral"
}

const gradientMap = {
  indigo: "from-primary to-violet-500",
  teal: "from-teal-400 to-cyan-400",
  coral: "from-rose-400 to-orange-400",
}

const glowMap = {
  indigo: "group-hover:shadow-primary/20",
  teal: "group-hover:shadow-teal-400/20",
  coral: "group-hover:shadow-rose-400/20",
}

const iconMap = {
  shield: Shield,
  brain: Brain,
  mic: Mic,
}

export function FeatureCard({ iconName, title, description, href, gradient }: FeatureCardProps) {
  const Icon = iconMap[iconName]
  return (
    <Link 
      href={href}
      className="group relative block"
    >
      <div className={cn(
        "glass-card relative overflow-hidden p-8 transition-all duration-500",
        "hover:-translate-y-2 hover:shadow-2xl",
        glowMap[gradient]
      )}>
        {/* Gradient background on hover */}
        <div className={cn(
          "absolute inset-0 bg-gradient-to-br opacity-0 transition-opacity duration-500 group-hover:opacity-5",
          gradientMap[gradient]
        )} />

        {/* Icon */}
        <div className={cn(
          "mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br shadow-lg",
          gradientMap[gradient]
        )}>
          <Icon className="h-7 w-7 text-white" />
        </div>

        {/* Content */}
        <h3 className="mb-3 text-xl font-semibold text-foreground">
          {title}
        </h3>
        <p className="mb-6 leading-relaxed text-muted-foreground">
          {description}
        </p>

        {/* Link */}
        <div className="flex items-center gap-2 text-sm font-medium">
          <span className={cn(
            "bg-gradient-to-r bg-clip-text text-transparent",
            gradientMap[gradient]
          )}>
            Learn more
          </span>
          <ArrowRight className={cn(
            "h-4 w-4 transition-transform group-hover:translate-x-1",
            "text-primary"
          )} />
        </div>
      </div>
    </Link>
  )
}
