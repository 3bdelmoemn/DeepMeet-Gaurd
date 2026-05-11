"use client"

import { useCallback, useState } from "react"
import { Upload, FileAudio, X, Mic } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface AudioUploadZoneProps {
  onFileSelect: (file: File) => void
  selectedFile: File | null
  onClear: () => void
}

export function AudioUploadZone({ onFileSelect, selectedFile, onClear }: AudioUploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      const file = files[0]
      if (file.type.startsWith("audio/")) {
        onFileSelect(file)
      }
    }
  }, [onFileSelect])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      onFileSelect(files[0])
    }
  }, [onFileSelect])

  if (selectedFile) {
    return (
      <div className="glass-card p-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-violet-500 shadow-lg shadow-primary/25">
              <FileAudio className="h-7 w-7 text-white" />
            </div>
            <div>
              <p className="font-medium text-foreground">{selectedFile.name}</p>
              <p className="text-sm text-muted-foreground">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
          </div>
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={onClear}
            className="hover:bg-destructive/10 hover:text-destructive"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Waveform visualization placeholder */}
        <div className="mt-6 flex h-24 items-center justify-center gap-1 overflow-hidden rounded-xl bg-muted/50 px-4">
          {Array.from({ length: 50 }).map((_, i) => (
            <div
              key={i}
              className="w-1 rounded-full bg-gradient-to-t from-primary to-violet-500"
              style={{
                height: `${20 + Math.random() * 60}%`,
                opacity: 0.5 + Math.random() * 0.5,
              }}
            />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div
      className={cn(
        "glass-card relative cursor-pointer overflow-hidden p-12 transition-all duration-300",
        isDragging && "border-primary bg-primary/5 shadow-xl shadow-primary/10"
      )}
      onDragEnter={handleDragIn}
      onDragLeave={handleDragOut}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept="audio/*"
        onChange={handleFileInput}
        className="absolute inset-0 cursor-pointer opacity-0"
      />

      <div className="flex flex-col items-center text-center">
        {/* Icon */}
        <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-primary/10 to-violet-500/10">
          <Upload className={cn(
            "h-10 w-10 transition-all duration-300",
            isDragging ? "text-primary scale-110" : "text-muted-foreground"
          )} />
        </div>

        {/* Text */}
        <h3 className="mb-2 text-xl font-semibold text-foreground">
          {isDragging ? "Drop your audio file" : "Upload Audio File"}
        </h3>
        <p className="mb-6 max-w-sm text-muted-foreground">
          Drag and drop your audio file here, or click to browse
        </p>

        {/* Supported formats */}
        <div className="flex flex-wrap justify-center gap-2">
          {["MP3", "WAV", "M4A", "OGG", "FLAC"].map((format) => (
            <span
              key={format}
              className="rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground"
            >
              {format}
            </span>
          ))}
        </div>

        {/* Or record */}
        <div className="mt-8 flex items-center gap-4">
          <div className="h-px flex-1 bg-border" />
          <span className="text-sm text-muted-foreground">or</span>
          <div className="h-px flex-1 bg-border" />
        </div>

        <Button 
          variant="outline" 
          className="mt-6 gap-2"
          onClick={(e) => e.preventDefault()}
        >
          <Mic className="h-4 w-4" />
          Record Audio
        </Button>
      </div>
    </div>
  )
}
