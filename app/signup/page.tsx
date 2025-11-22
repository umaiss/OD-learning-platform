"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { EyeIcon } from "@/components/ui/eye-icon"

export default function SignupPage() {
  const [mounted, setMounted] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle signup logic here
    console.log("Signup:", { email, password })
  }

  return (
    <div className="flex min-h-screen">
      {/* Left Section - Illustration Area */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-green-50 to-green-100 items-center justify-center p-12">
        <div className={`max-w-md text-center space-y-6 animate-slide-in-left ${!mounted ? "opacity-0" : ""}`}>
          <div className="w-full h-96 bg-gradient-to-br from-green-200 to-green-300 rounded-2xl flex items-center justify-center shadow-lg animate-scale-in">
            <div className="text-green-600 text-6xl">👨‍💻</div>
          </div>
          <h2 className="text-2xl font-semibold text-green-800 animate-fade-in-up animate-delay-200">
            Start Your Journey
          </h2>
          <p className="text-green-700 animate-fade-in-up animate-delay-300">
            Join AI Skill Profiler and unlock your potential
          </p>
        </div>
      </div>

      {/* Right Section - Signup Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-white">
        <div className={`w-full max-w-md space-y-8 animate-slide-in-right ${!mounted ? "opacity-0" : ""}`}>
          {/* Logo */}
          <div className="flex items-center gap-2 animate-fade-in">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">AI</span>
            </div>
            <span className="text-2xl font-semibold text-primary lowercase">
              AI Skill Profiler
            </span>
          </div>

          {/* Form */}
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">
                Create account
              </h1>
              <p className="text-muted-foreground">
                Enter your information to get started
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium">
                  Email address
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="h-11"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium">
                  Password
                </Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Create a password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="h-11 pr-10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <EyeIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <Button type="submit" className="w-full h-11 bg-primary hover:bg-primary/90 text-white">
                Create account
              </Button>
            </form>

            {/* Social Signup */}
            <div className="space-y-4">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-muted-foreground">
                    or sign up with
                  </span>
                </div>
              </div>

              <div className="flex justify-center gap-4">
                <button
                  type="button"
                  className="w-12 h-12 rounded-full border border-border hover:bg-muted transition-colors flex items-center justify-center text-sm font-semibold"
                >
                  G
                </button>
                <button
                  type="button"
                  className="w-12 h-12 rounded-full border border-border hover:bg-muted transition-colors flex items-center justify-center"
                >
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                  </svg>
                </button>
                <button
                  type="button"
                  className="w-12 h-12 rounded-full border border-border hover:bg-muted transition-colors flex items-center justify-center text-sm font-semibold"
                >
                  C
                </button>
              </div>
            </div>

            {/* Terms and Privacy */}
            <p className="text-xs text-center text-muted-foreground">
              By creating an account you agree to AI Skill Profiler's{" "}
              <Link href="/terms" className="text-primary hover:underline">
                Terms of Services
              </Link>{" "}
              and{" "}
              <Link href="/privacy" className="text-primary hover:underline">
                Privacy Policy
              </Link>
              .
            </p>

            {/* Login link */}
            <div className="text-center text-sm text-muted-foreground">
              Have an account?{" "}
              <Link
                href="/login"
                className="font-medium text-primary hover:underline"
              >
                Log in
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
