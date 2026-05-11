import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Hero3D } from "@/components/landing/hero-3d"
import { FeatureCard } from "@/components/landing/feature-card"
import { HowItWorks } from "@/components/landing/how-it-works"
import { TrustSection } from "@/components/landing/trust-section"
import { CTASection } from "@/components/landing/cta-section"
import { ArrowRight, ChevronDown } from "lucide-react"

export default function LandingPage() {
  return (
    <>
      {/* Hero Section */}
      <section className="relative flex min-h-screen items-center overflow-hidden pt-20">
        {/* 3D Background */}
        <Hero3D />

        {/* Gradient overlays */}
        <div className="pointer-events-none absolute inset-0 -z-5">
          <div className="absolute inset-0 bg-gradient-to-b from-background via-transparent to-background" />
          <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-transparent" />
        </div>

        <div className="relative mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            {/* Badge */}
            <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-2 backdrop-blur-sm">
              <span className="flex h-2 w-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-sm font-medium text-foreground">
                AI-Powered Voice Protection
              </span>
            </div>

            {/* Headline */}
            <h1 className="mb-6 text-balance text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
              Detect Deepfakes.{" "}
              <span className="bg-gradient-to-r from-primary via-violet-500 to-primary bg-clip-text text-transparent animate-gradient-shift bg-[length:200%_auto]">
                Ace Interviews.
              </span>
            </h1>

            {/* Subheadline */}
            <p className="mx-auto mb-10 max-w-2xl text-pretty text-lg text-muted-foreground sm:text-xl">
              Advanced AI technology to detect synthetic voices and prepare you for 
              high-stakes conversations. Stay protected. Stay confident.
            </p>

            {/* CTAs */}
            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button 
                asChild 
                size="lg"
                className="group h-14 px-8 text-base bg-gradient-to-r from-primary to-violet-500 shadow-xl shadow-primary/25 transition-all hover:shadow-2xl hover:shadow-primary/30"
              >
                <Link href="/detection">
                  Start Detection
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
                  Interview Simulation
                </Link>
              </Button>
            </div>

            {/* Stats */}
            <div className="mt-16 grid grid-cols-3 gap-8 border-t border-border/50 pt-8">
              <div>
                <div className="text-3xl font-bold text-foreground">99.2%</div>
                <div className="text-sm text-muted-foreground">Detection Accuracy</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-foreground">{"<"}3s</div>
                <div className="text-sm text-muted-foreground">Analysis Time</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-foreground">50K+</div>
                <div className="text-sm text-muted-foreground">Protected Users</div>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <ChevronDown className="h-6 w-6 text-muted-foreground" />
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-16 text-center">
            <span className="mb-4 inline-block rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
              Core Features
            </span>
            <h2 className="mb-4 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              Two Powerful Tools, One Platform
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
              Whether you need to verify voice authenticity or prepare for important meetings,
              we have you covered.
            </p>
          </div>

          <div className="grid gap-8 lg:grid-cols-2">
            <FeatureCard
              iconName="shield"
              title="Voice Detection"
              description="Upload any audio file and our AI will analyze it across three detection layers to determine if it's authentic or AI-generated. Get detailed confidence scores and breakdown reports."
              href="/detection"
              gradient="indigo"
            />
            <FeatureCard
              iconName="brain"
              title="Interview Simulation"
              description="Practice for interviews with our AI-powered simulator. Get personalized questions based on your profile, receive feedback on your responses, and track your improvement."
              href="/simulation"
              gradient="teal"
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <HowItWorks />

      {/* Trust Section */}
      <TrustSection />

      {/* Final CTA */}
      <CTASection />
    </>
  )
}
