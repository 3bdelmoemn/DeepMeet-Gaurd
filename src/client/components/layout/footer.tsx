import Link from "next/link"
import { Shield } from "lucide-react"

export function Footer() {
  return (
    <footer className="border-t border-border/50 bg-muted/30">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-8 md:flex-row">
          {/* Logo & Description */}
          <div className="flex flex-col items-center gap-3 md:items-start">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-violet-500">
                <Shield className="h-4 w-4 text-white" />
              </div>
              <span className="text-lg font-bold">
                <span className="bg-gradient-to-r from-primary to-violet-500 bg-clip-text text-transparent">Deep</span>
                <span className="text-foreground">Meet Guard</span>
              </span>
            </Link>
            <p className="max-w-xs text-center text-sm text-muted-foreground md:text-left">
              AI-powered deepfake detection and interview simulation platform.
            </p>
          </div>

          {/* Navigation Links */}
          <div className="flex flex-wrap justify-center gap-6 text-sm">
            <Link href="/" className="text-muted-foreground transition-colors hover:text-foreground">
              Home
            </Link>
            <Link href="/detection" className="text-muted-foreground transition-colors hover:text-foreground">
              Detection
            </Link>
            <Link href="/simulation" className="text-muted-foreground transition-colors hover:text-foreground">
              Simulation
            </Link>
            <Link href="/about" className="text-muted-foreground transition-colors hover:text-foreground">
              About
            </Link>
          </div>

          {/* Copyright */}
          <div className="text-center text-sm text-muted-foreground md:text-right">
            <p>&copy; {new Date().getFullYear()} DeepMeet Guard.</p>
            <p className="mt-1">All rights reserved.</p>
          </div>
        </div>
      </div>
    </footer>
  )
}
