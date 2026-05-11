"use client"

import { Upload, Cpu, CheckCircle } from "lucide-react"

const steps = [
  {
    icon: Upload,
    title: "Upload Audio or life simulation",
    description: "Simply drag and drop your audio file or record directly from your device or start red vs blue simulation.",
    number: "01"
  },
  {
    icon: Cpu,
    title: "AI Analysis",
    description: "Our 4-layer AI model analyzes voice patterns, audio characteristics, and authenticity markers.",
    number: "02"
  },
  {
    icon: CheckCircle,
    title: "Get Results",
    description: "Receive a detailed breakdown with confidence scores and actionable insights.",
    number: "03"
  }
]

export function HowItWorks() {
  return (
    <section className="relative py-24">
      {/* Background gradient */}
      <div className="absolute inset-0 -z-10 bg-gradient-to-b from-background via-muted/30 to-background" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-16 text-center">
          <span className="mb-4 inline-block rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
            Simple Process
          </span>
          <h2 className="mb-4 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            How It Works
          </h2>
          <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
            Get accurate deepfake detection results in three simple steps
          </p>
        </div>

        <div className="relative">
          {/* Connecting line */}
          <div className="absolute left-1/2 top-20 hidden h-0.5 w-[60%] -translate-x-1/2 bg-gradient-to-r from-primary/20 via-primary to-primary/20 lg:block" />

          <div className="grid gap-8 lg:grid-cols-3">
            {steps.map((step, index) => (
              <div 
                key={index}
                className="group relative"
                style={{ animationDelay: `${index * 150}ms` }}
              >
                <div className="glass-card relative overflow-hidden p-8 text-center transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
                  {/* Step number */}
                  <span className="absolute right-4 top-4 text-5xl font-bold text-primary/10">
                    {step.number}
                  </span>

                  {/* Icon container */}
                  <div className="relative mx-auto mb-6 flex h-16 w-16 items-center justify-center">
                    <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary to-violet-500 opacity-20 blur-xl transition-all group-hover:opacity-40" />
                    <div className="relative flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-violet-500 shadow-lg shadow-primary/25">
                      <step.icon className="h-7 w-7 text-white" />
                    </div>
                  </div>

                  {/* Content */}
                  <h3 className="mb-3 text-xl font-semibold text-foreground">
                    {step.title}
                  </h3>
                  <p className="leading-relaxed text-muted-foreground">
                    {step.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
