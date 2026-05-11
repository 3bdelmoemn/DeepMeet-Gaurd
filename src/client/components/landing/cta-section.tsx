"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowRight, Sparkles } from "lucide-react"

export function CTASection() {
  return (
    <section className="relative overflow-hidden py-24">
      {/* Background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-violet-500/5 to-background" />
        <div className="absolute bottom-0 left-1/4 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute right-1/4 top-0 h-96 w-96 rounded-full bg-violet-500/10 blur-3xl" />
      </div>

      <div className="mx-auto max-w-4xl px-4 text-center sm:px-6 lg:px-8">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2">
          <Sparkles className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium text-primary">Start protecting yourself today</span>
        </div>

        <h2 className="mb-6 text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          Ready to Detect{" "}
          <span className="bg-gradient-to-r from-primary to-violet-500 bg-clip-text text-transparent">
            Deepfakes?
          </span>
        </h2>

        <p className="mx-auto mb-10 max-w-2xl text-lg text-muted-foreground">
          Join thousands of users who trust DeepMeet Guard to protect their communications 
          and prepare for important one-to-one conversations.
        </p>

        <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Button 
            asChild 
            size="lg"
            className="group h-14 px-8 text-base bg-gradient-to-r from-primary to-violet-500 shadow-xl shadow-primary/25 transition-all hover:shadow-2xl hover:shadow-primary/30"
          >
            <Link href="/detection">
              Try Voice Detection
              <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
            </Link>
          </Button>
          <Button 
            asChild 
            variant="outline" 
            size="lg"
            className="h-14 px-8 text-base border-primary/20 hover:bg-primary/5"
          >
            <Link href="/simulation">
              Start Interview Prep
            </Link>
          </Button>
        </div>

        <p className="mt-8 text-sm text-muted-foreground">
          No account required. Free to try.
        </p>
      </div>
    </section>
  )
}
