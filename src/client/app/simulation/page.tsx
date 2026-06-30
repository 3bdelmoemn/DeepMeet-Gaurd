// ============================================================
// FILE: src/client/app/simulation/page.tsx
// ============================================================

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

  useEffect(() => {
    if (typeof window === "undefined") return
    const toSave = { ...formData }
    delete toSave.voiceFile
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
      // Transform experiences to array of strings
      const experienceStrings = (formData.experiences || [])
        .filter(exp => exp.company || exp.role)
        .map(exp => `${exp.role} at ${exp.company} (${exp.duration || 'N/A'})`)

      // Transform projects to array of strings
      const projectStrings = (formData.projects || [])
        .filter(proj => proj.name || proj.description)
        .map(proj => `${proj.name}: ${proj.description || ''}`)

      const payload = {
        user_info: {
          name: formData.name || "",
          role: formData.currentRole || "",
          skills: formData.skills || [],
          experience: experienceStrings,
          education: formData.education || "",
          projects: projectStrings,
          strengths: formData.strengths || [],
          weaknesses: formData.areasToImprove || [],
        },
        organization_info: {
          company: formData.targetCompany?.name || "",
          industry: formData.targetCompany?.industry || "",
          tech_stack: formData.targetCompany?.techStack
            ? [formData.targetCompany.techStack]
            : [],
          role: formData.targetCompany?.role || "",
          responsibilities: formData.targetCompany?.responsibilities
            ? [formData.targetCompany.responsibilities]
            : [],
        },
      }

      console.log("📤 Sending payload:", JSON.stringify(payload, null, 2))

      // 1. Upload info and get user_id
      const infoRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/deepmeet/simulator/data/upload/info`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      )

      if (!infoRes.ok) {
        const errorText = await infoRes.text()
        console.error("❌ Server error response:", errorText)
        throw new Error(`Info upload failed: ${infoRes.status} - ${errorText}`)
      }

      const infoData = await infoRes.json()
      console.log("📥 Full response from server:", infoData)

      const userId = infoData.user_id

      if (!userId) {
        throw new Error("No user_id returned from server")
      }

      localStorage.setItem("deepmeet-user-id", userId)
      console.log("✅ user_id saved:", userId)

      // 2. Upload voice file (if exists)
      if (formData.voiceFile) {
        const storedUserId = localStorage.getItem("deepmeet-user-id")
        if (!storedUserId || storedUserId === 'undefined' || storedUserId.trim() === '') {
          throw new Error("No valid user_id found in localStorage")
        }

        const voiceFormData = new FormData()
        voiceFormData.append("user_id", storedUserId)
        voiceFormData.append("audio", formData.voiceFile)

        let refText = formData.referenceText?.trim()
        if (!refText) {
          refText = "Hello, this is a voice reference for the interview simulation."
        }

        const refBlob = new Blob([refText], { type: "text/plain" })
        voiceFormData.append("reference_text", refBlob, "reference.txt")

        console.log("📤 Uploading voice for user_id:", storedUserId)

        const refRes = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/deepmeet/simulator/data/upload/references`,
          { method: "POST", body: voiceFormData }
        )

        if (!refRes.ok) {
          const errorText = await refRes.text()
          console.error("❌ Voice upload error:", errorText)
          throw new Error(`Voice upload failed: ${refRes.status} - ${errorText}`)
        }

        console.log("✅ Voice uploaded successfully")
      }

      // 3. Impersonate
      console.log("📤 Starting impersonate for user_id:", userId)
      const impersonateRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/deepmeet/simulator/setup/impersonate?user_id=${userId}`,
        { method: "POST" }
      )

      if (!impersonateRes.ok) {
        const errorText = await impersonateRes.text()
        console.warn("Impersonate warning:", impersonateRes.status, errorText)
      } else {
        console.log("✅ Impersonate successful")
      }

      // 4. Clone
      console.log("📤 Starting clone for user_id:", userId)
      const cloneRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/deepmeet/simulator/setup/clone?user_id=${userId}`,
        { method: "POST" }
      )

      if (!cloneRes.ok) {
        const errorText = await cloneRes.text()
        console.warn("Clone warning:", cloneRes.status, errorText)
      } else {
        console.log("✅ Clone successful")
      }

      // 5. Stop any running detector before navigating
      try {
        await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/deepmeet/detector/end`,
          { method: "POST" }
        ).catch(() => {})
        console.log("✅ Detector stopped")
      } catch (e) {
        console.warn("⚠️ Could not stop detector:", e)
      }

      // 6. Navigate to meeting
      console.log("🚀 Navigating to /simulation/meeting")
      router.push("/simulation/meeting")

    } catch (error) {
      console.error("❌ Submission error:", error)
      alert(error instanceof Error ? error.message : "Failed to setup interview. Please try again.")
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