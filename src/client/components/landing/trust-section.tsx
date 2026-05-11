"use client"

import { Shield, Lock, Zap, Brain } from "lucide-react"

const trustItems = [
  {
    icon: Shield,
    title: "Enterprise Grade",
    description: "Built for security-critical applications"
  },
  {
    icon: Lock,
    title: "Privacy First",
    description: "Your data never leaves your control"
  },
  {
    icon: Zap,
    title: "Real-time Analysis",
    description: "Results in under 3 seconds"
  },
  {
    icon: Brain,
    title: "AI Powered",
    description: "State-of-the-art neural networks"
  }
]

export function TrustSection() {
  return (
    <section className="py-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="glass-card overflow-hidden p-8 lg:p-12">
          <div className="mb-10 text-center">
            <h2 className="mb-3 text-2xl font-bold text-foreground sm:text-3xl">
              Trusted Technology
            </h2>
            <p className="text-muted-foreground">
              Built with security and performance at its core
            </p>
          </div>

          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {trustItems.map((item, index) => (
              <div 
                key={index}
                className="group text-center"
              >
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 transition-colors group-hover:bg-primary/20">
                  <item.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="mb-1 font-semibold text-foreground">
                  {item.title}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
