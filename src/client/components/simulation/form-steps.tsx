"use client"

import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { Plus, X, Upload, FileAudio } from "lucide-react"
import type { SimulationFormData } from "@/lib/simulation-types"

interface StepProps {
  data: SimulationFormData
  updateData: (updates: Partial<SimulationFormData>) => void
}

// Step 1: Personal Profile
export function PersonalProfileStep({ data, updateData }: StepProps) {
  const skills = [
    "JavaScript", "TypeScript", "React", "Node.js", "Python", 
    "Java", "Go", "SQL", "AWS", "Docker", "Kubernetes", "GraphQL"
  ]

  const toggleSkill = (skill: string) => {
    const currentSkills = data.skills || []
    if (currentSkills.includes(skill)) {
      updateData({ skills: currentSkills.filter(s => s !== skill) })
    } else {
      updateData({ skills: [...currentSkills, skill] })
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-6 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="name">Full Name</Label>
          <Input
            id="name"
            placeholder="John Doe"
            value={data.name || ""}
            onChange={(e) => updateData({ name: e.target.value })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="currentRole">Current Role</Label>
          <Input
            id="currentRole"
            placeholder="Software Engineer"
            value={data.currentRole || ""}
            onChange={(e) => updateData({ currentRole: e.target.value })}
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="yearsExperience">Years of Experience</Label>
        <Input
          id="yearsExperience"
          type="number"
          placeholder="5"
          value={data.yearsExperience || ""}
          onChange={(e) => updateData({ yearsExperience: parseInt(e.target.value) || 0 })}
        />
      </div>

      <div className="space-y-3">
        <Label>Technical Skills</Label>
        <div className="flex flex-wrap gap-2">
          {skills.map((skill) => (
            <button
              key={skill}
              type="button"
              onClick={() => toggleSkill(skill)}
              className={cn(
                "rounded-full px-4 py-2 text-sm font-medium transition-all",
                data.skills?.includes(skill)
                  ? "bg-primary text-white shadow-lg shadow-primary/25"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              )}
            >
              {skill}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

// Step 2: Experience
export function ExperienceStep({ data, updateData }: StepProps) {
  const addExperience = () => {
    const experiences = data.experiences || []
    updateData({
      experiences: [...experiences, { company: "", role: "", duration: "", description: "" }]
    })
  }

  const updateExperience = (index: number, field: string, value: string) => {
    const experiences = [...(data.experiences || [])]
    experiences[index] = { ...experiences[index], [field]: value }
    updateData({ experiences })
  }

  const removeExperience = (index: number) => {
    const experiences = (data.experiences || []).filter((_, i) => i !== index)
    updateData({ experiences })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Label className="text-base">Work Experience</Label>
        <Button type="button" variant="outline" size="sm" onClick={addExperience}>
          <Plus className="mr-2 h-4 w-4" />
          Add Experience
        </Button>
      </div>

      {(data.experiences || []).map((exp, index) => (
        <div key={index} className="relative rounded-xl border border-border bg-muted/30 p-6">
          <button
            type="button"
            onClick={() => removeExperience(index)}
            className="absolute right-4 top-4 text-muted-foreground hover:text-destructive"
          >
            <X className="h-4 w-4" />
          </button>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label>Company</Label>
              <Input
                placeholder="Acme Inc."
                value={exp.company}
                onChange={(e) => updateExperience(index, "company", e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Role</Label>
              <Input
                placeholder="Senior Developer"
                value={exp.role}
                onChange={(e) => updateExperience(index, "role", e.target.value)}
              />
            </div>
          </div>

          <div className="mt-4 space-y-2">
            <Label>Duration</Label>
            <Input
              placeholder="2020 - Present"
              value={exp.duration}
              onChange={(e) => updateExperience(index, "duration", e.target.value)}
            />
          </div>

          <div className="mt-4 space-y-2">
            <Label>Description</Label>
            <Textarea
              placeholder="Key achievements and responsibilities..."
              value={exp.description}
              onChange={(e) => updateExperience(index, "description", e.target.value)}
              rows={3}
            />
          </div>
        </div>
      ))}

      {(!data.experiences || data.experiences.length === 0) && (
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-border py-12 text-center">
          <p className="text-muted-foreground">No experience added yet</p>
          <Button type="button" variant="link" onClick={addExperience}>
            Add your first experience
          </Button>
        </div>
      )}
    </div>
  )
}

// Step 3: Projects & Strengths
export function ProjectsStrengthsStep({ data, updateData }: StepProps) {
  const strengthOptions = [
    "Problem Solving", "Communication", "Leadership", "Teamwork",
    "Adaptability", "Critical Thinking", "Time Management", "Creativity"
  ]

  const improvementOptions = [
    "Public Speaking", "Technical Writing", "Delegation", "Patience",
    "Detail Orientation", "Stress Management", "Networking", "Assertiveness"
  ]

  const addProject = () => {
    const projects = data.projects || []
    updateData({
      projects: [...projects, { title: "", description: "", technologies: "" }]
    })
  }

  const updateProject = (index: number, field: string, value: string) => {
    const projects = [...(data.projects || [])]
    projects[index] = { ...projects[index], [field]: value }
    updateData({ projects })
  }

  const removeProject = (index: number) => {
    const projects = (data.projects || []).filter((_, i) => i !== index)
    updateData({ projects })
  }

  const toggleStrength = (strength: string) => {
    const current = data.strengths || []
    if (current.includes(strength)) {
      updateData({ strengths: current.filter(s => s !== strength) })
    } else {
      updateData({ strengths: [...current, strength] })
    }
  }

  const toggleImprovement = (area: string) => {
    const current = data.areasToImprove || []
    if (current.includes(area)) {
      updateData({ areasToImprove: current.filter(a => a !== area) })
    } else {
      updateData({ areasToImprove: [...current, area] })
    }
  }

  return (
    <div className="space-y-8">
      {/* Projects */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Label className="text-base">Key Projects</Label>
          <Button type="button" variant="outline" size="sm" onClick={addProject}>
            <Plus className="mr-2 h-4 w-4" />
            Add Project
          </Button>
        </div>

        {(data.projects || []).map((project, index) => (
          <div key={index} className="relative rounded-xl border border-border bg-muted/30 p-6">
            <button
              type="button"
              onClick={() => removeProject(index)}
              className="absolute right-4 top-4 text-muted-foreground hover:text-destructive"
            >
              <X className="h-4 w-4" />
            </button>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Project Title</Label>
                <Input
                  placeholder="E-commerce Platform"
                  value={project.title}
                  onChange={(e) => updateProject(index, "title", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Description</Label>
                <Textarea
                  placeholder="What did you build and what impact did it have?"
                  value={project.description}
                  onChange={(e) => updateProject(index, "description", e.target.value)}
                  rows={2}
                />
              </div>
              <div className="space-y-2">
                <Label>Technologies Used</Label>
                <Input
                  placeholder="React, Node.js, PostgreSQL"
                  value={project.technologies}
                  onChange={(e) => updateProject(index, "technologies", e.target.value)}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Strengths */}
      <div className="space-y-3">
        <Label className="text-base">Your Strengths</Label>
        <div className="flex flex-wrap gap-2">
          {strengthOptions.map((strength) => (
            <button
              key={strength}
              type="button"
              onClick={() => toggleStrength(strength)}
              className={cn(
                "rounded-full px-4 py-2 text-sm font-medium transition-all",
                data.strengths?.includes(strength)
                  ? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/25"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              )}
            >
              {strength}
            </button>
          ))}
        </div>
      </div>

      {/* Areas to Improve */}
      <div className="space-y-3">
        <Label className="text-base">Areas to Improve</Label>
        <div className="flex flex-wrap gap-2">
          {improvementOptions.map((area) => (
            <button
              key={area}
              type="button"
              onClick={() => toggleImprovement(area)}
              className={cn(
                "rounded-full px-4 py-2 text-sm font-medium transition-all",
                data.areasToImprove?.includes(area)
                  ? "bg-amber-500 text-white shadow-lg shadow-amber-500/25"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              )}
            >
              {area}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

// Step 4: Target Company
export function TargetCompanyStep({ data, updateData }: StepProps) {
  const industries = [
    "Technology", "Finance", "Healthcare", "E-commerce", 
    "Education", "Entertainment", "Consulting", "Other"
  ]

  return (
    <div className="space-y-6">
      <div className="grid gap-6 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="companyName">Company Name</Label>
          <Input
            id="companyName"
            placeholder="Google, Meta, etc."
            value={data.targetCompany?.name || ""}
            onChange={(e) => updateData({ 
              targetCompany: { ...data.targetCompany, name: e.target.value } 
            })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="industry">Industry</Label>
          <select
            id="industry"
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={data.targetCompany?.industry || ""}
            onChange={(e) => updateData({ 
              targetCompany: { ...data.targetCompany, industry: e.target.value } 
            })}
          >
            <option value="">Select industry</option>
            {industries.map((industry) => (
              <option key={industry} value={industry}>{industry}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="targetRole">Target Role</Label>
        <Input
          id="targetRole"
          placeholder="Senior Software Engineer"
          value={data.targetCompany?.role || ""}
          onChange={(e) => updateData({ 
            targetCompany: { ...data.targetCompany, role: e.target.value } 
          })}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="techStack">Required Tech Stack</Label>
        <Input
          id="techStack"
          placeholder="React, TypeScript, AWS, etc."
          value={data.targetCompany?.techStack || ""}
          onChange={(e) => updateData({ 
            targetCompany: { ...data.targetCompany, techStack: e.target.value } 
          })}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="responsibilities">Key Responsibilities</Label>
        <Textarea
          id="responsibilities"
          placeholder="What are the main responsibilities of this role?"
          value={data.targetCompany?.responsibilities || ""}
          onChange={(e) => updateData({ 
            targetCompany: { ...data.targetCompany, responsibilities: e.target.value } 
          })}
          rows={4}
        />
      </div>
    </div>
  )
}

// Step 5: Voice Setup
export function VoiceSetupStep({ data, updateData }: StepProps) {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      updateData({ voiceFile: file })
    }
  }

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <Label className="text-base">Reference Audio (Optional)</Label>
        <p className="text-sm text-muted-foreground">
          Upload a sample of your voice to personalize the interview simulation
        </p>

        <div className="relative">
          {data.voiceFile ? (
            <div className="flex items-center gap-4 rounded-xl border border-border bg-muted/30 p-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-violet-500">
                <FileAudio className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <p className="font-medium text-foreground">{data.voiceFile.name}</p>
                <p className="text-sm text-muted-foreground">
                  {(data.voiceFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
              <Button 
                type="button" 
                variant="ghost" 
                size="sm"
                onClick={() => updateData({ voiceFile: undefined })}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <label className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-border py-12 transition-colors hover:border-primary/50 hover:bg-primary/5">
              <Upload className="mb-4 h-10 w-10 text-muted-foreground" />
              <p className="mb-2 font-medium text-foreground">Upload audio file</p>
              <p className="text-sm text-muted-foreground">MP3, WAV, M4A up to 10MB</p>
              <input
                type="file"
                accept="audio/*"
                className="hidden"
                onChange={handleFileChange}
              />
            </label>
          )}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="referenceText">Reference Text (Optional)</Label>
        <p className="text-sm text-muted-foreground">
          Provide a brief introduction or elevator pitch you&apos;d like to practice
        </p>
        <Textarea
          id="referenceText"
          placeholder="Hi, I'm [Name] and I'm excited about this opportunity because..."
          value={data.referenceText || ""}
          onChange={(e) => updateData({ referenceText: e.target.value })}
          rows={4}
        />
      </div>

      <div className="rounded-xl bg-primary/5 p-6">
        <h4 className="mb-2 font-medium text-foreground">Ready to Start</h4>
        <p className="text-sm text-muted-foreground">
          Once you submit, our AI will generate personalized interview questions based on your 
          profile, experience, and target role. You&apos;ll receive detailed feedback on your responses.
        </p>
      </div>
    </div>
  )
}
