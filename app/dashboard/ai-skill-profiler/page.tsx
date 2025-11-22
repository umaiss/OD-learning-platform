"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export default function AISkillProfilerPage() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const [currentRole, setCurrentRole] = useState("")
  const [stackInput, setStackInput] = useState("")
  const [primaryStack, setPrimaryStack] = useState<string[]>([])
  const [proficiency, setProficiency] = useState<string>("")
  const [learningGoals, setLearningGoals] = useState("")
  const [linkedInConnected, setLinkedInConnected] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleAddStack = () => {
    if (stackInput.trim()) {
      const items = stackInput.split(",").map(item => item.trim()).filter(item => item)
      setPrimaryStack([...primaryStack, ...items])
      setStackInput("")
    }
  }

  const handleRemoveStack = (index: number) => {
    setPrimaryStack(primaryStack.filter((_, i) => i !== index))
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault()
      handleAddStack()
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Save form data and navigate to insights page
    const formData = {
      currentRole,
      primaryStack,
      proficiency,
      learningGoals,
      linkedInConnected,
    }
    // Store in sessionStorage or pass as query params
    sessionStorage.setItem("profileData", JSON.stringify(formData))
    router.push("/dashboard/ai-skill-profiler/insights")
  }

  return (
    <DashboardLayout>
      <div className="space-y-8 max-w-4xl">
        {/* Header Section */}
        <div className={`space-y-1 animate-fade-in-up ${!mounted ? "opacity-0" : ""}`}>
          <h1 className="text-3xl font-semibold tracking-tight text-foreground">
            AI Skill Profiler
          </h1>
          <p className="text-sm text-muted-foreground">
            Complete your profile to get personalized AI-powered insights
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Current Role */}
          <Card className={`border-0 shadow-sm hover-lift animate-fade-in-up animate-delay-100 ${!mounted ? "opacity-0" : ""}`}>
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold">Current Role</CardTitle>
              <CardDescription className="text-xs">
                What is your current job title or role?
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Label htmlFor="currentRole">Current Role</Label>
                <Input
                  id="currentRole"
                  type="text"
                  placeholder="e.g., Frontend Developer, Full Stack Engineer"
                  value={currentRole}
                  onChange={(e) => setCurrentRole(e.target.value)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Primary Stack */}
          <Card className={`border-0 shadow-sm hover-lift animate-fade-in-up animate-delay-200 ${!mounted ? "opacity-0" : ""}`}>
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold">Primary Stack</CardTitle>
              <CardDescription className="text-xs">
                Enter your primary technologies separated by commas
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="primaryStack">Primary Stack</Label>
                <div className="flex gap-2">
                  <Input
                    id="primaryStack"
                    type="text"
                    placeholder="e.g., React, Node.js, TypeScript"
                    value={stackInput}
                    onChange={(e) => setStackInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                  />
                  <Button
                    type="button"
                    onClick={handleAddStack}
                    className="bg-primary hover:bg-primary/90 text-white"
                  >
                    Add
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">
                  Separate multiple technologies with commas
                </p>
              </div>
              {primaryStack.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {primaryStack.map((item, index) => (
                    <div
                      key={index}
                      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-primary/10 text-primary text-sm animate-scale-in transition-smooth"
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <span>{item}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveStack(index)}
                        className="hover:text-primary/70 transition-colors"
                      >
                        <svg
                          width="14"
                          height="14"
                          viewBox="0 0 14 14"
                          fill="none"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            d="M10.5 3.5L3.5 10.5M3.5 3.5L10.5 10.5"
                            stroke="currentColor"
                            strokeWidth="1.5"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Proficiency Level */}
          <Card className={`border-0 shadow-sm hover-lift animate-fade-in-up animate-delay-300 ${!mounted ? "opacity-0" : ""}`}>
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold">
                Rate your proficiency in current Development
              </CardTitle>
              <CardDescription className="text-xs">
                Select your current skill level
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { value: "beginner", label: "Beginner" },
                  { value: "intermediate", label: "Intermediate" },
                  { value: "advanced", label: "Advanced" },
                ].map((option) => (
                  <label
                    key={option.value}
                    className={cn(
                      "flex items-center space-x-3 p-4 rounded-lg border cursor-pointer transition-colors",
                      proficiency === option.value
                        ? "border-primary bg-primary/5"
                        : "border-border hover:bg-muted/50"
                    )}
                  >
                    <input
                      type="radio"
                      name="proficiency"
                      value={option.value}
                      checked={proficiency === option.value}
                      onChange={(e) => setProficiency(e.target.value)}
                      className="w-4 h-4 text-primary focus:ring-primary"
                    />
                    <span className="text-sm font-medium">{option.label}</span>
                  </label>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Learning Goals */}
          <Card className={`border-0 shadow-sm hover-lift animate-fade-in-up animate-delay-400 ${!mounted ? "opacity-0" : ""}`}>
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold">What are your learning goals?</CardTitle>
              <CardDescription className="text-xs">
                Describe what you want to achieve and learn
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Label htmlFor="learningGoals">Learning Goals</Label>
                <Textarea
                  id="learningGoals"
                  placeholder="e.g., I want to master React hooks, learn TypeScript advanced patterns, and improve my system design skills..."
                  value={learningGoals}
                  onChange={(e) => setLearningGoals(e.target.value)}
                  className="min-h-[150px]"
                />
              </div>
            </CardContent>
          </Card>

          {/* LinkedIn Connection */}
          <Card className={`border-0 shadow-sm hover-lift animate-fade-in-up animate-delay-500 ${!mounted ? "opacity-0" : ""}`}>
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold">
                Connect Your Accounts for AI-Powered Insights
              </CardTitle>
              <CardDescription className="text-xs">
                Connect your LinkedIn to get personalized recommendations based on your profile
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-lg border border-border">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded bg-[#0077B5] flex items-center justify-center">
                      <svg
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path
                          d="M20.447 20.452H16.893V14.883C16.893 13.555 16.866 11.846 15.041 11.846C13.188 11.846 12.905 13.291 12.905 14.785V20.452H9.351V9H12.765V10.561H12.811C13.288 9.661 14.448 8.711 16.181 8.711C19.782 8.711 20.448 11.081 20.448 14.166V20.452H20.447ZM5.337 7.433C4.193 7.433 3.274 6.507 3.274 5.367C3.274 4.224 4.194 3.305 5.337 3.305C6.477 3.305 7.401 4.224 7.401 5.367C7.401 6.507 6.476 7.433 5.337 7.433ZM7.119 20.452H3.555V9H7.119V20.452ZM22.225 0H1.771C0.792 0 0 0.774 0 1.729V22.271C0 23.227 0.792 24 1.771 24H22.222C23.2 24 24 23.227 24 22.271V1.729C24 0.774 23.2 0 22.222 0H22.225Z"
                          fill="white"
                        />
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm font-medium">LinkedIn</p>
                      <p className="text-xs text-muted-foreground">
                        {linkedInConnected
                          ? "Connected"
                          : "Connect your LinkedIn profile"}
                      </p>
                    </div>
                  </div>
                  <Button
                    type="button"
                    variant={linkedInConnected ? "outline" : "default"}
                    onClick={() => setLinkedInConnected(!linkedInConnected)}
                    className={cn(
                      linkedInConnected
                        ? ""
                        : "bg-[#0077B5] hover:bg-[#0077B5]/90 text-white"
                    )}
                  >
                    {linkedInConnected ? "Disconnect" : "Connect"}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Submit Button */}
          <div className="flex justify-end gap-4">
            <Button type="button" variant="outline">
              Cancel
            </Button>
            <Button type="submit" className="bg-primary hover:bg-primary/90 text-white">
              Generate Profile from AI
            </Button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  )
}
