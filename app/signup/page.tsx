"use client"

import { useState, useEffect, useMemo } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { EyeIcon } from "@/components/ui/eye-icon"
import { useAuthStore } from "@/store/auth-store"
import { useShallow } from "zustand/react/shallow"

type PasswordStrength = "weak" | "fair" | "good" | "strong"

export default function SignupPage() {
  const router = useRouter()
  const { signup, isAuthenticated } = useAuthStore(
    useShallow((state) => ({
      signup: state.signup,
      isAuthenticated: state.isAuthenticated,
    }))
  )
  const [mounted, setMounted] = useState(false)
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [nameError, setNameError] = useState("")
  const [emailError, setEmailError] = useState("")
  const [passwordError, setPasswordError] = useState("")

  useEffect(() => {
    setMounted(true)
    // Redirect if already authenticated
    if (isAuthenticated) {
      router.push("/dashboard")
    }
  }, [isAuthenticated, router])

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const calculatePasswordStrength = (password: string): PasswordStrength => {
    if (password.length === 0) return "weak"
    if (password.length < 6) return "weak"

    let strength = 0
    if (password.length >= 8) strength++
    if (/[a-z]/.test(password)) strength++
    if (/[A-Z]/.test(password)) strength++
    if (/[0-9]/.test(password)) strength++
    if (/[^a-zA-Z0-9]/.test(password)) strength++

    if (strength <= 2) return "weak"
    if (strength === 3) return "fair"
    if (strength === 4) return "good"
    return "strong"
  }

  const passwordStrength = useMemo(() => calculatePasswordStrength(password), [password])

  const passwordRequirements = useMemo(() => {
    return {
      length: password.length >= 8,
      lowercase: /[a-z]/.test(password),
      uppercase: /[A-Z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[^a-zA-Z0-9]/.test(password)
    }
  }, [password])

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setName(value)
    if (value && value.trim().length < 2) {
      setNameError("Name must be at least 2 characters")
    } else {
      setNameError("")
    }
  }

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setEmail(value)
    if (value && !validateEmail(value)) {
      setEmailError("Please enter a valid email address")
    } else {
      setEmailError("")
    }
  }

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setPassword(value)
    if (value && value.length < 8) {
      setPasswordError("Password must be at least 8 characters")
    } else if (value && passwordStrength === "weak") {
      setPasswordError("Password is too weak. Please use a stronger password.")
    } else {
      setPasswordError("")
    }
  }

  const getStrengthColor = (strength: PasswordStrength) => {
    switch (strength) {
      case "weak":
        return "bg-destructive"
      case "fair":
        return "bg-orange-500"
      case "good":
        return "bg-yellow-500"
      case "strong":
        return "bg-primary"
      default:
        return "bg-muted"
    }
  }

  const getStrengthLabel = (strength: PasswordStrength) => {
    switch (strength) {
      case "weak":
        return "Weak"
      case "fair":
        return "Fair"
      case "good":
        return "Good"
      case "strong":
        return "Strong"
      default:
        return ""
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setNameError("")
    setEmailError("")
    setPasswordError("")

    // Client-side validation
    if (!name || name.trim().length < 2) {
      setNameError("Name must be at least 2 characters")
      return
    }
    if (!email) {
      setEmailError("Email is required")
      return
    }
    if (!validateEmail(email)) {
      setEmailError("Please enter a valid email address")
      return
    }
    if (!password) {
      setPasswordError("Password is required")
      return
    }
    if (password.length < 8) {
      setPasswordError("Password must be at least 8 characters")
      return
    }
    if (passwordStrength === "weak") {
      setPasswordError("Password is too weak. Please use a stronger password.")
      return
    }

    setLoading(true)

    try {
      await signup(name, email, password)
      // Navigate to login page after successful signup
      router.push("/login")
    } catch (err: any) {
      setError(err.message || "Failed to create account. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-background via-primary/5 to-background">
      {/* Left Section - Illustration Area */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary/10 via-primary/5 to-background items-center justify-center p-12 relative overflow-hidden">
        {/* Decorative background elements */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 right-20 w-72 h-72 bg-primary rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 left-20 w-96 h-96 bg-primary/50 rounded-full blur-3xl"></div>
        </div>

        <div className={`max-w-md text-center space-y-8 relative z-10 animate-slide-in-left ${!mounted ? "opacity-0" : ""}`}>
          <div className="w-full h-[400px] bg-gradient-to-br from-primary/20 via-primary/10 to-primary/5 rounded-3xl flex items-center justify-center shadow-2xl border border-primary/10 backdrop-blur-sm hover-lift">
            <div className="text-8xl animate-scale-in">✨</div>
          </div>
          <div className="space-y-4">
            <h2 className="text-3xl font-bold text-foreground animate-fade-in-up animate-delay-200">
              Start Your Journey
            </h2>
            <p className="text-lg text-muted-foreground animate-fade-in-up animate-delay-300">
              Join thousands of learners unlocking their potential with AI
            </p>
            <div className="flex items-center justify-center gap-2 pt-4 animate-fade-in-up animate-delay-400">
              <div className="w-2 h-2 bg-primary rounded-full"></div>
              <div className="w-2 h-2 bg-primary/60 rounded-full"></div>
              <div className="w-2 h-2 bg-primary/40 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Section - Signup Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-8 lg:p-12">
        <div className={`w-full max-w-md space-y-8 animate-slide-in-right ${!mounted ? "opacity-0" : ""}`}>
          {/* Logo */}
          <div className="flex items-center gap-3 animate-fade-in">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary/80 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-lg">AI</span>
            </div>
            <span className="text-2xl font-bold text-foreground">
              AI Skill Profiler
            </span>
          </div>

          {/* Form */}
          <div className="space-y-6">
            <div className="space-y-2">
              <h1 className="text-4xl font-bold text-foreground">
                Create account
              </h1>
              <p className="text-muted-foreground text-base">
                Enter your information to get started
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/20 animate-fade-in">
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-destructive flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-sm text-destructive font-medium">{error}</p>
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="name" className="text-sm font-semibold">
                  Full Name
                </Label>
                <Input
                  id="name"
                  type="text"
                  placeholder="John Doe"
                  value={name}
                  onChange={handleNameChange}
                  onBlur={() => {
                    if (name && name.trim().length < 2) {
                      setNameError("Name must be at least 2 characters")
                    }
                  }}
                  className={`h-12 transition-all ${nameError ? "border-destructive focus-visible:ring-destructive" : ""}`}
                  required
                  disabled={loading}
                />
                {nameError && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {nameError}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-semibold">
                  Email address
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={handleEmailChange}
                  onBlur={() => {
                    if (email && !validateEmail(email)) {
                      setEmailError("Please enter a valid email address")
                    }
                  }}
                  className={`h-12 transition-all ${emailError ? "border-destructive focus-visible:ring-destructive" : ""}`}
                  required
                  disabled={loading}
                />
                {emailError && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {emailError}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-semibold">
                  Password
                </Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Create a strong password"
                    value={password}
                    onChange={handlePasswordChange}
                    className={`h-12 pr-12 transition-all ${passwordError ? "border-destructive focus-visible:ring-destructive" : ""}`}
                    required
                    disabled={loading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-muted"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    <EyeIcon className="w-5 h-5" />
                  </button>
                </div>

                {/* Password Strength Indicator */}
                {password && (
                  <div className="space-y-2 pt-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Password strength</span>
                      <span className={`font-semibold ${passwordStrength === "strong" ? "text-primary" : passwordStrength === "good" ? "text-yellow-600" : passwordStrength === "fair" ? "text-orange-600" : "text-destructive"}`}>
                        {getStrengthLabel(passwordStrength)}
                      </span>
                    </div>
                    <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-300 ${getStrengthColor(passwordStrength)}`}
                        style={{
                          width: passwordStrength === "weak" ? "25%" : passwordStrength === "fair" ? "50%" : passwordStrength === "good" ? "75%" : "100%"
                        }}
                      />
                    </div>
                  </div>
                )}

                {/* Password Requirements */}
                {password && (
                  <div className="space-y-1.5 pt-1">
                    <p className="text-xs font-medium text-muted-foreground mb-2">Password requirements:</p>
                    <div className="space-y-1.5 text-xs">
                      <div className={`flex items-center gap-2 ${passwordRequirements.length ? "text-primary" : "text-muted-foreground"}`}>
                        <svg className={`w-4 h-4 flex-shrink-0 ${passwordRequirements.length ? "text-primary" : "text-muted-foreground"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          {passwordRequirements.length ? (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          ) : (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          )}
                        </svg>
                        <span>At least 8 characters</span>
                      </div>
                      <div className={`flex items-center gap-2 ${passwordRequirements.lowercase ? "text-primary" : "text-muted-foreground"}`}>
                        <svg className={`w-4 h-4 flex-shrink-0 ${passwordRequirements.lowercase ? "text-primary" : "text-muted-foreground"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          {passwordRequirements.lowercase ? (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          ) : (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          )}
                        </svg>
                        <span>One lowercase letter</span>
                      </div>
                      <div className={`flex items-center gap-2 ${passwordRequirements.uppercase ? "text-primary" : "text-muted-foreground"}`}>
                        <svg className={`w-4 h-4 flex-shrink-0 ${passwordRequirements.uppercase ? "text-primary" : "text-muted-foreground"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          {passwordRequirements.uppercase ? (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          ) : (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          )}
                        </svg>
                        <span>One uppercase letter</span>
                      </div>
                      <div className={`flex items-center gap-2 ${passwordRequirements.number ? "text-primary" : "text-muted-foreground"}`}>
                        <svg className={`w-4 h-4 flex-shrink-0 ${passwordRequirements.number ? "text-primary" : "text-muted-foreground"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          {passwordRequirements.number ? (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          ) : (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          )}
                        </svg>
                        <span>One number</span>
                      </div>
                      <div className={`flex items-center gap-2 ${passwordRequirements.special ? "text-primary" : "text-muted-foreground"}`}>
                        <svg className={`w-4 h-4 flex-shrink-0 ${passwordRequirements.special ? "text-primary" : "text-muted-foreground"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          {passwordRequirements.special ? (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          ) : (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          )}
                        </svg>
                        <span>One special character</span>
                      </div>
                    </div>
                  </div>
                )}

                {passwordError && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {passwordError}
                  </p>
                )}
              </div>

              <Button
                type="submit"
                className="w-full h-12 text-base font-semibold bg-primary hover:bg-primary/90 text-white shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading || !!nameError || !!emailError || !!passwordError || passwordStrength === "weak"}
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Creating account...
                  </span>
                ) : (
                  "Create account"
                )}
              </Button>
            </form>

            {/* Social Signup */}
            <div className="space-y-4">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-background px-3 text-muted-foreground font-medium">
                    or continue with
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <button
                  type="button"
                  className="h-12 rounded-lg border border-border hover:bg-muted hover:border-primary/20 transition-all flex items-center justify-center group hover-lift"
                  aria-label="Sign up with Google"
                >
                  <svg className="w-5 h-5 text-foreground group-hover:text-primary transition-colors" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                  </svg>
                </button>
                <button
                  type="button"
                  className="h-12 rounded-lg border border-border hover:bg-muted hover:border-primary/20 transition-all flex items-center justify-center group hover-lift"
                  aria-label="Sign up with GitHub"
                >
                  <svg className="w-5 h-5 text-foreground group-hover:text-primary transition-colors" fill="currentColor" viewBox="0 0 24 24">
                    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                  </svg>
                </button>
                <button
                  type="button"
                  className="h-12 rounded-lg border border-border hover:bg-muted hover:border-primary/20 transition-all flex items-center justify-center group hover-lift"
                  aria-label="Sign up with Microsoft"
                >
                  <svg className="w-5 h-5 text-foreground group-hover:text-primary transition-colors" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M0 0h11.377v11.372H0z" fill="#f25022" />
                    <path d="M12.623 0H24v11.372H12.623z" fill="#00a4ef" />
                    <path d="M0 12.628h11.377V24H0z" fill="#7fba00" />
                    <path d="M12.623 12.628H24V24H12.623z" fill="#ffb900" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Terms and Privacy */}
            <p className="text-xs text-center text-muted-foreground leading-relaxed">
              By creating an account, you agree to AI Skill Profiler's{" "}
              <Link href="/terms" className="text-primary hover:underline font-medium">
                Terms of Service
              </Link>{" "}
              and{" "}
              <Link href="/privacy" className="text-primary hover:underline font-medium">
                Privacy Policy
              </Link>
            </p>

            {/* Login link */}
            <div className="text-center text-sm text-muted-foreground pt-2">
              Already have an account?{" "}
              <Link
                href="/login"
                className="font-semibold text-primary hover:underline transition-colors"
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
