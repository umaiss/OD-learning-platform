"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function Home() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <div className="flex min-h-screen">
      {/* Left Section - Hero Content */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-green-50 to-green-100 items-center justify-center p-12">
        <div className={`max-w-lg space-y-8 animate-slide-in-left ${!mounted ? "opacity-0" : ""}`}>
          <div className="space-y-4 animate-fade-in-up">
            <h1 className="text-5xl font-bold text-green-800 leading-tight">
              Discover Your Skills with AI
            </h1>
            <p className="text-lg text-green-700 animate-fade-in-up animate-delay-200">
              AI Skill Profiler helps you identify, track, and enhance your skills
              with intelligent insights powered by artificial intelligence.
            </p>
          </div>
          <div className="flex flex-col gap-4 animate-fade-in-up animate-delay-300">
            <div className="flex items-center gap-3 text-green-700 transition-smooth hover:translate-x-1">
              <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
              <span>AI-powered skill assessment</span>
            </div>
            <div className="flex items-center gap-3 text-green-700 transition-smooth hover:translate-x-1">
              <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: "0.2s" }} />
              <span>Personalized learning paths</span>
            </div>
            <div className="flex items-center gap-3 text-green-700 transition-smooth hover:translate-x-1">
              <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: "0.4s" }} />
              <span>Real-time progress tracking</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Section - CTA */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-white">
        <div className={`w-full max-w-md space-y-8 animate-slide-in-right ${!mounted ? "opacity-0" : ""}`}>
          {/* Logo */}
          <div className="flex items-center gap-2 animate-fade-in">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center animate-scale-in">
              <span className="text-white font-bold text-xl">AI</span>
            </div>
            <span className="text-3xl font-semibold text-primary lowercase animate-fade-in animate-delay-100">
              AI Skill Profiler
            </span>
          </div>

          {/* Main Content */}
          <div className="space-y-6 animate-fade-in-up animate-delay-200">
            <div className="space-y-2">
              <h2 className="text-4xl font-bold text-foreground">
                Welcome to AI Skill Profiler
              </h2>
              <p className="text-lg text-muted-foreground">
                Start your journey to discover and enhance your skills today
              </p>
            </div>

            <div className="flex flex-col gap-4 pt-4">
              <Link href="/signup">
                <Button size="lg" className="w-full h-12 bg-primary hover:bg-primary/90 text-white text-base transition-smooth hover-lift">
                  Get Started
                </Button>
              </Link>
              <Link href="/login">
                <Button variant="outline" size="lg" className="w-full h-12 text-base transition-smooth hover-lift">
                  Sign In
                </Button>
              </Link>
            </div>

            {/* Features */}
            <div className="pt-8 space-y-4 border-t">
              <h3 className="font-semibold text-foreground">Why choose us?</h3>
              <div className="space-y-3 text-sm text-muted-foreground">
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <div className="w-2 h-2 bg-primary rounded-full" />
                  </div>
                  <span>AI-powered insights to identify your strengths</span>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <div className="w-2 h-2 bg-primary rounded-full" />
                  </div>
                  <span>Personalized recommendations for skill development</span>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <div className="w-2 h-2 bg-primary rounded-full" />
                  </div>
                  <span>Track your progress and achieve your goals</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
