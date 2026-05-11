"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ProgressBar } from "@/components/simulation/progress-bar"
import {
  PersonalProfileStep,
  ExperienceStep,
  ProjectsStrengthsStep,
  TargetCompanyStep,
  VoiceSetupStep,
} from "@/components/simulation/form-steps"
import { ArrowLeft, ArrowRight, Loader2 } from "lucide-react"
import type { SimulationFormData } from "@/lib/simulation-types"

const STEPS = ["Profile", "Experience", "Projects", "Target", "Voice"]
const STORAGE_KEY = "deepmeet-simulation-data"

export default function SimulationPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState<SimulationFormData>({})

  // ✅ localStorage guard for SSR
  useEffect(() => {
    if (typeof window === "undefined") return
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        setFormData(JSON.parse(saved))
      } catch {
        // ignore parse errors
      }
    }
  }, [])

  // ✅ Save to localStorage with SSR guard
  useEffect(() => {
    if (typeof window === "undefined") return
    const toSave = { ...formData }
    delete toSave.voiceFile // File objects can't be serialized
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave))
  }, [formData])

  const updateData = (updates: Partial<SimulationFormData>) => {
    setFormData((prev) => ({ ...prev, ...updates }))
  }

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep((prev) => prev + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1)
    }
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)

    try {
      const payload = {
        user_info: {
          name: formData.name || "",
          current_role: formData.currentRole || "",
          years_of_experience: formData.yearsExperience || 0,
          skills: formData.skills || [],
          experiences: formData.experiences || [],
          projects: formData.projects || [],
          strengths: formData.strengths || [],
          areas_to_improve: formData.areasToImprove || [],
        },
        organization_info: {
          company: formData.targetCompany?.name || "",
          industry: formData.targetCompany?.industry || "",
          tech_stack: formData.targetCompany?.techStack || "",
          role: formData.targetCompany?.role || "",
          responsibilities: formData.targetCompany?.responsibilities || "",
        },
      }

      // 1. Upload voice first
      if (formData.voiceFile) {
        console.log("📤 Uploading voice file...")
        const voiceFormData = new FormData()
        voiceFormData.append("audio", formData.voiceFile)
        voiceFormData.append("reference_text", formData.referenceText || "")

        const voiceResponse = await fetch("http://localhost:8000/api/upload-voice", {
          method: "POST",
          body: voiceFormData,
        })

        if (!voiceResponse.ok) {
          const errorData = await voiceResponse.json()
          throw new Error(errorData.detail || "Voice upload failed")
        }
        console.log("✅ Voice uploaded successfully")
      }

      // 2. Setup
      console.log("📤 Sending setup request...")
      const setupResponse = await fetch("http://localhost:8000/api/setup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      if (!setupResponse.ok) {
        const errorData = await setupResponse.json()
        throw new Error(errorData.detail || "Setup failed")
      }
      console.log("✅ Setup completed successfully")

      // Clear saved data
      if (typeof window !== "undefined") {
        localStorage.removeItem(STORAGE_KEY)
      }

      router.push("/simulation/meeting")
    } catch (error) {
      console.error("Submission error:", error)
      alert("Failed to setup interview. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 0: return <PersonalProfileStep data={formData} updateData={updateData} />
      case 1: return <ExperienceStep data={formData} updateData={updateData} />
      case 2: return <ProjectsStrengthsStep data={formData} updateData={updateData} />
      case 3: return <TargetCompanyStep data={formData} updateData={updateData} />
      case 4: return <VoiceSetupStep data={formData} updateData={updateData} />
      default: return null
    }
  }

  return (
    <div className="min-h-screen pt-28 pb-16">
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-teal-500/5 via-background to-background" />
        <div className="absolute left-1/3 top-1/4 h-96 w-96 rounded-full bg-teal-500/5 blur-3xl" />
        <div className="absolute right-1/3 bottom-1/4 h-96 w-96 rounded-full bg-cyan-500/5 blur-3xl" />
      </div>

      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="mb-8 text-center">
          <span className="mb-4 inline-block rounded-full bg-teal-500/10 px-4 py-1.5 text-sm font-medium text-teal-600">
            Interview Simulation
          </span>
          <h1 className="mb-4 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Set Up Your Interview
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
            Tell us about yourself and your target role to get personalized interview practice
          </p>
        </div>

        <div className="mb-8">
          <ProgressBar currentStep={currentStep} totalSteps={STEPS.length} steps={STEPS} />
        </div>

        <div className="glass-card p-8">
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-foreground">
              {currentStep === 0 && "Personal Profile"}
              {currentStep === 1 && "Work Experience"}
              {currentStep === 2 && "Projects & Strengths"}
              {currentStep === 3 && "Target Company"}
              {currentStep === 4 && "Voice Setup"}
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              {currentStep === 0 && "Tell us about yourself and your skills"}
              {currentStep === 1 && "Add your relevant work experience"}
              {currentStep === 2 && "Highlight your key projects and strengths"}
              {currentStep === 3 && "Specify the company and role you're targeting"}
              {currentStep === 4 && "Optionally add voice samples for personalization"}
            </p>
          </div>

          {renderStep()}

          <div className="mt-8 flex items-center justify-between border-t border-border pt-6">
            <Button
              type="button"
              variant="outline"
              onClick={handleBack}
              disabled={currentStep === 0}
              className="gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Button>

            {currentStep < STEPS.length - 1 ? (
              <Button
                type="button"
                onClick={handleNext}
                className="gap-2 bg-gradient-to-r from-teal-500 to-cyan-500 shadow-lg shadow-teal-500/25"
              >
                Next
                <ArrowRight className="h-4 w-4" />
              </Button>
            ) : (
              <Button
                type="button"
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="gap-2 bg-gradient-to-r from-teal-500 to-cyan-500 shadow-lg shadow-teal-500/25"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    Start Simulation
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}