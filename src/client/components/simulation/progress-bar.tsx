"use client"

import { cn } from "@/lib/utils"
import { Check } from "lucide-react"

interface ProgressBarProps {
  currentStep: number
  totalSteps: number
  steps: string[]
}

export function ProgressBar({ currentStep, totalSteps, steps }: ProgressBarProps) {
  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={index} className="flex items-center">
            {/* Step indicator */}
            <div className="flex flex-col items-center">
              <div className={cn(
                "flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all duration-300",
                index < currentStep 
                  ? "border-primary bg-primary text-white" 
                  : index === currentStep
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-muted bg-background text-muted-foreground"
              )}>
                {index < currentStep ? (
                  <Check className="h-5 w-5" />
                ) : (
                  <span className="text-sm font-semibold">{index + 1}</span>
                )}
              </div>
              <span className={cn(
                "mt-2 text-xs font-medium transition-colors",
                index <= currentStep ? "text-foreground" : "text-muted-foreground"
              )}>
                {step}
              </span>
            </div>

            {/* Connector line */}
            {index < totalSteps - 1 && (
              <div className={cn(
                "mx-4 hidden h-0.5 w-16 transition-colors lg:block",
                index < currentStep ? "bg-primary" : "bg-muted"
              )} />
            )}
          </div>
        ))}
      </div>

      {/* Mobile progress bar */}
      <div className="mt-4 lg:hidden">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Step {currentStep + 1} of {totalSteps}</span>
          <span className="font-medium text-foreground">{steps[currentStep]}</span>
        </div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-muted">
          <div 
            className="h-full rounded-full bg-gradient-to-r from-primary to-violet-500"
            style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
          />
        </div>
      </div>
    </div>
  )
}
