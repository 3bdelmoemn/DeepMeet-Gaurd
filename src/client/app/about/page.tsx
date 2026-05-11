import Link from "next/link"
import { Button } from "@/components/ui/button"
import { 
  Shield, Brain, Lock, Zap, Users, Building, 
  GraduationCap, Briefcase, ArrowRight, Activity, Waves, Cpu
} from "lucide-react"

const detectionLayers = [
  {
    icon: Activity,
    title: "Audio Characteristics",
    description: "Analyzes frequency patterns, spectral features, and audio artifacts that are common in AI-generated speech.",
    color: "from-primary to-violet-500"
  },
  {
    icon: Waves,
    title: "Voice Pattern Analysis",
    description: "Examines natural speech patterns, breathing rhythms, and micro-variations that distinguish human speech.",
    color: "from-teal-400 to-cyan-400"
  },
  {
    icon: Cpu,
    title: "AI Model Confidence",
    description: "Deep neural networks trained on millions of samples to detect synthetic voice markers.",
    color: "from-rose-400 to-orange-400"
  }
]

const useCases = [
  {
    icon: Building,
    title: "Enterprises",
    description: "Protect your organization from voice-based fraud and social engineering attacks."
  },
  {
    icon: Users,
    title: "Individuals",
    description: "Verify the authenticity of calls from unknown numbers or suspicious contacts."
  },
  {
    icon: Briefcase,
    title: "HR Teams",
    description: "Ensure interview integrity and prepare candidates for their best performance."
  },
  {
    icon: GraduationCap,
    title: "Job Seekers",
    description: "Practice and improve your interview skills with AI-powered feedback."
  }
]

const securityFeatures = [
  {
    title: "End-to-End Encryption",
    description: "All audio files are encrypted in transit and at rest."
  },
  {
    title: "No Data Storage",
    description: "We don't store your audio files after analysis is complete."
  },
  {
    title: "GDPR Compliant",
    description: "Full compliance with European data protection regulations."
  },
  {
    title: "SOC 2 Type II",
    description: "Enterprise-grade security certifications and audits."
  }
]

export default function AboutPage() {
  return (
    <div className="min-h-screen pt-28 pb-16">
      {/* Background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-violet-500/5 via-background to-background" />
        <div className="absolute left-1/4 top-1/4 h-96 w-96 rounded-full bg-violet-500/5 blur-3xl" />
        <div className="absolute right-1/4 bottom-1/4 h-96 w-96 rounded-full bg-primary/5 blur-3xl" />
      </div>

      {/* Hero */}
      <section className="mx-auto max-w-7xl px-4 text-center sm:px-6 lg:px-8">
        <span className="mb-4 inline-block rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
          About DeepMeet Guard
        </span>
        <h1 className="mb-6 text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          The Technology Behind{" "}
          <span className="bg-gradient-to-r from-primary to-violet-500 bg-clip-text text-transparent">
            Voice Protection
          </span>
        </h1>
        <p className="mx-auto max-w-3xl text-lg text-muted-foreground">
          DeepMeet Guard combines state-of-the-art machine learning with advanced audio analysis 
          to detect AI-generated voices and help you prepare for important conversations.
        </p>
      </section>

      {/* Detection Technology */}
      <section className="mx-auto mt-24 max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-12 text-center">
          <h2 className="mb-4 text-3xl font-bold text-foreground">
            4-Layer Detection System
          </h2>
          <p className="mx-auto max-w-2xl text-muted-foreground">
            Our multi-layered approach ensures the highest accuracy in deepfake detection
          </p>
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          {detectionLayers.map((layer, index) => (
            <div key={index} className="glass-card p-8 text-center">
              <div className={`mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br ${layer.color} shadow-lg`}>
                <layer.icon className="h-8 w-8 text-white" />
              </div>
              <h3 className="mb-3 text-xl font-semibold text-foreground">
                {layer.title}
              </h3>
              <p className="leading-relaxed text-muted-foreground">
                {layer.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Simulation Engine */}
      <section className="mx-auto mt-24 max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="glass-card overflow-hidden">
          <div className="grid items-center gap-8 lg:grid-cols-2">
            <div className="p-8 lg:p-12">
              <div className="mb-6 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-teal-400 to-cyan-400">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <h2 className="mb-4 text-3xl font-bold text-foreground">
                AI-Powered Interview Simulation
              </h2>
              <p className="mb-6 leading-relaxed text-muted-foreground">
                Our interview simulator uses advanced natural language processing to generate 
                relevant questions based on your profile, experience, and target role. Get 
                real-time feedback on your responses and track your improvement over time.
              </p>
              <ul className="space-y-3">
                {[
                  "Personalized questions based on your background",
                  "Real-time voice analysis and feedback",
                  "Detailed performance metrics and insights",
                  "Practice with industry-specific scenarios"
                ].map((feature, index) => (
                  <li key={index} className="flex items-center gap-3">
                    <div className="flex h-6 w-6 items-center justify-center rounded-full bg-teal-500/10">
                      <Zap className="h-3 w-3 text-teal-500" />
                    </div>
                    <span className="text-foreground">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="relative h-64 bg-gradient-to-br from-teal-500/10 via-cyan-500/5 to-transparent lg:h-full">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="relative">
                  <div className="absolute inset-0 animate-ping rounded-full bg-teal-500/20" />
                  <div className="relative flex h-32 w-32 items-center justify-center rounded-full bg-gradient-to-br from-teal-400 to-cyan-400 shadow-2xl shadow-teal-500/30">
                    <Brain className="h-16 w-16 text-white" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Security */}
      <section className="mx-auto mt-24 max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-12 text-center">
          <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
            <Lock className="h-6 w-6 text-primary" />
          </div>
          <h2 className="mb-4 text-3xl font-bold text-foreground">
            Security & Privacy First
          </h2>
          <p className="mx-auto max-w-2xl text-muted-foreground">
            Your data security is our top priority. We&apos;ve built DeepMeet Guard with 
            enterprise-grade security from the ground up.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {securityFeatures.map((feature, index) => (
            <div key={index} className="glass-card p-6 text-center">
              <div className="mx-auto mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                <Shield className="h-5 w-5 text-primary" />
              </div>
              <h3 className="mb-2 font-semibold text-foreground">{feature.title}</h3>
              <p className="text-sm text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Use Cases */}
      <section className="mx-auto mt-24 max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-12 text-center">
          <h2 className="mb-4 text-3xl font-bold text-foreground">
            Who Uses DeepMeet Guard?
          </h2>
          <p className="mx-auto max-w-2xl text-muted-foreground">
            From enterprises to individuals, our platform serves diverse needs
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {useCases.map((useCase, index) => (
            <div key={index} className="glass-card p-6">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-violet-500/10">
                <useCase.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="mb-2 font-semibold text-foreground">{useCase.title}</h3>
              <p className="text-sm text-muted-foreground">{useCase.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto mt-24 max-w-4xl px-4 text-center sm:px-6 lg:px-8">
        <div className="glass-card p-12">
          <h2 className="mb-4 text-3xl font-bold text-foreground">
            Ready to Get Started?
          </h2>
          <p className="mb-8 text-muted-foreground">
            Try DeepMeet Guard today and experience the future of voice protection
          </p>
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button 
              asChild 
              size="lg"
              className="h-12 px-8 bg-gradient-to-r from-primary to-violet-500 shadow-lg shadow-primary/25"
            >
              <Link href="/detection">
                Try Voice Detection
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button 
              asChild 
              variant="outline" 
              size="lg"
              className="h-12 px-8"
            >
              <Link href="/simulation">
                Start Interview Prep
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  )
}
