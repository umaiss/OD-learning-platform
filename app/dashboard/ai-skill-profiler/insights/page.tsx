"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { saveProfileAPI } from "@/lib/api/profile"
import { generateLearningPathAPI } from "@/lib/api/learning-path"
import { useAuthStore } from "@/store/auth-store"
import { useShallow } from "zustand/react/shallow"

interface SkillData {
  skill: string
  level: number
  category: string
}

interface APIResponse {
  learner_id: number
  ai_analysis: string
  strengths: string[]
  growth_areas: string[]
  skill_map: Record<string, string>
  message: string
}

export default function AISkillInsightsPage() {
  const router = useRouter()
  const { user } = useAuthStore(
    useShallow((state) => ({
      user: state.user,
    }))
  )
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)
  const [insights, setInsights] = useState<{
    remarks: string
    strengths: Array<{ title: string; description: string }>
    growthAreas: Array<{ title: string; description: string; priority: string }>
    skillMap: SkillData[]
  } | null>(null)
  const [error, setError] = useState("")
  const [generatingPath, setGeneratingPath] = useState(false)
  const [apiResponse, setApiResponse] = useState<any>(null)

  useEffect(() => {
    // Get data from sessionStorage
    const storedData = sessionStorage.getItem("profileData")

    if (!storedData) {
      setError("No profile data found. Please generate your profile first.")
      setLoading(false)
      return
    }

    try {
      const parsedData = JSON.parse(storedData)
      const apiResponse: APIResponse = parsedData.generatedData

      if (!apiResponse) {
        setError("Invalid profile data. Please generate your profile again.")
        setLoading(false)
        return
      }

      // Map API response to UI format
      const mappedInsights = {
        remarks: apiResponse.ai_analysis || "No analysis available.",

        // Map strengths array to objects with title and description
        strengths: apiResponse.strengths.map((strength) => ({
          title: strength,
          description: `Strong proficiency in ${strength}. This is one of your key technical strengths based on your profile analysis.`,
        })),

        // Map growth_areas array to objects with title, description, and priority
        growthAreas: apiResponse.growth_areas.map((area, index) => {
          // Assign priority based on position (first items are higher priority)
          let priority = "Low"
          if (index < 2) priority = "High"
          else if (index < 4) priority = "Medium"

          return {
            title: area,
            description: `Focus on developing your skills in ${area}. This area presents an opportunity for growth and career advancement.`,
            priority,
          }
        }),

        // Map skill_map object to array with levels and categories
        skillMap: Object.entries(apiResponse.skill_map || {}).map(([skill, level]) => {
          // Convert proficiency level to percentage
          const levelMap: Record<string, number> = {
            beginner: 0,
            intermediate: 40,
            advanced: 75,
            expert: 90,
          }

          // Determine category based on skill name
          const getCategory = (skillName: string): string => {
            const lowerSkill = skillName.toLowerCase()
            if (lowerSkill.includes("react") || lowerSkill.includes("frontend") || lowerSkill.includes("ui") || lowerSkill.includes("vue") || lowerSkill.includes("angular")) {
              return "Frontend"
            }
            if (lowerSkill.includes("node") || lowerSkill.includes("backend") || lowerSkill.includes("api") || lowerSkill.includes("server")) {
              return "Backend"
            }
            if (lowerSkill.includes("aws") || lowerSkill.includes("devops") || lowerSkill.includes("docker") || lowerSkill.includes("kubernetes") || lowerSkill.includes("ci/cd")) {
              return "DevOps"
            }
            if (lowerSkill.includes("architecture") || lowerSkill.includes("design") || lowerSkill.includes("system")) {
              return "Architecture"
            }
            if (lowerSkill.includes("management") || lowerSkill.includes("leadership") || lowerSkill.includes("project")) {
              return "Management"
            }
            return "Other"
          }

          return {
            skill,
            level: levelMap[level.toLowerCase()] || 50,
            category: getCategory(skill),
          }
        }),
      }

      setInsights(mappedInsights)
      setApiResponse(apiResponse) // Store original API response for later use
      setLoading(false)
      setTimeout(() => setMounted(true), 100)
    } catch (err: any) {
      setError("Failed to parse profile data. Please try again.")
      setLoading(false)
    }
  }, [])

  const handleGenerateLearningPath = async () => {
    if (!apiResponse) {
      setError("Missing profile data. Please generate your profile again.")
      return
    }

    setGeneratingPath(true)
    setError("")

    try {
      // Get original form data from sessionStorage to get experience and role
      const storedData = sessionStorage.getItem("profileData")
      const formData = storedData ? JSON.parse(storedData) : null

      // First, save the profile
      await saveProfileAPI({
        learner_id: apiResponse.learner_id,
        ai_analysis: apiResponse.ai_analysis,
        strengths: apiResponse.strengths,
        growth_areas: apiResponse.growth_areas,
        skill_map: apiResponse.skill_map,
      })

      // Then, generate the learning path
      // Use experience from form data or default to 0
      // Use role from form data (currentRole) or default to "developer"
      const experience = formData?.experience || 0
      const role = formData?.currentRole || "developer"

      const learningPathResponse = await generateLearningPathAPI({
        learner_id: apiResponse.learner_id,
        skill_map: apiResponse.skill_map,
        experience: experience,
        role: role,
      })

      // Store learning path response
      sessionStorage.setItem("learningPathData", JSON.stringify(learningPathResponse))

      // Navigate to learning path page or show success message
      // You can create a new page for learning path or show it in a modal
      router.push("/dashboard/learning-path")
    } catch (err: any) {
      setError(err.message || "Failed to generate learning path. Please try again.")
    } finally {
      setGeneratingPath(false)
    }
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-sm text-muted-foreground">
              Loading your AI-generated insights...
            </p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (error || !insights) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4 max-w-md">
            <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center mx-auto">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold">Unable to Load Insights</h3>
            <p className="text-sm text-muted-foreground">{error || "No insights data available"}</p>
            <Button
              onClick={() => router.push("/dashboard/ai-skill-profiler")}
              className="mt-4"
            >
              Generate Profile
            </Button>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      Frontend: "bg-blue-500",
      Backend: "bg-green-500",
      DevOps: "bg-purple-500",
      Tools: "bg-orange-500",
      Architecture: "bg-pink-500",
      Management: "bg-indigo-500",
      Other: "bg-gray-500",
    }
    return colors[category] || "bg-gray-500"
  }

  const categories = Array.from(new Set(insights.skillMap.map((s) => s.category)))

  return (
    <DashboardLayout>
      <div className="space-y-8 max-w-7xl">
        {/* Header */}
        <div className={`flex items-center justify-between animate-fade-in-up ${!mounted ? "opacity-0" : ""}`}>
          <div className="space-y-1">
            <h1 className="text-3xl font-semibold tracking-tight text-foreground">
              AI Skill Insights
            </h1>
            <p className="text-sm text-muted-foreground">
              Personalized insights based on your LinkedIn profile analysis
            </p>
          </div>
          <Button
            variant="outline"
            onClick={() => router.push("/dashboard/ai-skill-profiler")}
            className="transition-smooth hover-lift"
          >
            Back to Profile
          </Button>
        </div>

        {/* AI Remarks */}
        <Card className={`border-0 shadow-sm hover-lift animate-fade-in-up animate-delay-100 ${!mounted ? "opacity-0" : ""}`}>
          <CardHeader className="pb-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 20 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M10 2.5C8.34167 2.5 6.875 3.34167 5.91667 4.66667C5.625 4.33333 5.25 4.08333 4.83333 3.95833C4.41667 3.83333 3.95833 3.83333 3.54167 3.95833C2.70833 3.95833 1.95833 4.375 1.45833 5.04167C0.958333 5.70833 0.75 6.54167 0.875 7.33333C0.416667 7.70833 0.125 8.25 0.125 8.875C0.125 9.5 0.416667 10.0417 0.875 10.4167C0.75 11.2083 0.958333 12.0417 1.45833 12.7083C1.95833 13.375 2.70833 13.7917 3.54167 13.7917C3.95833 13.7917 4.41667 13.7917 4.83333 13.6667C5.25 13.5417 5.625 13.2917 5.91667 12.9583C6.875 14.2833 8.34167 15.125 10 15.125C11.6583 15.125 13.125 14.2833 14.0833 12.9583C14.375 13.2917 14.75 13.5417 15.1667 13.6667C15.5833 13.7917 16.0417 13.7917 16.4583 13.7917C17.2917 13.7917 18.0417 13.375 18.5417 12.7083C19.0417 12.0417 19.25 11.2083 19.125 10.4167C19.5833 10.0417 19.875 9.5 19.875 8.875C19.875 8.25 19.5833 7.70833 19.125 7.33333C19.25 6.54167 19.0417 5.70833 18.5417 5.04167C18.0417 4.375 17.2917 3.95833 16.4583 3.95833C16.0417 3.95833 15.5833 3.83333 15.1667 3.95833C14.75 4.08333 14.375 4.33333 14.0833 4.66667C13.125 3.34167 11.6583 2.5 10 2.5Z"
                    fill="currentColor"
                  />
                </svg>
              </div>
              <CardTitle className="text-base font-semibold">AI Analysis & Remarks</CardTitle>
            </div>
            <CardDescription className="text-xs">
              Comprehensive analysis of your LinkedIn profile
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none">
              <p className="text-sm text-foreground leading-relaxed">
                {insights.remarks}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Strengths and Growth Areas Grid */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* Strengths */}
          <Card className={`border-0 shadow-sm hover-lift animate-fade-in-up animate-delay-200 ${!mounted ? "opacity-0" : ""}`}>
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold">Your Strengths</CardTitle>
              <CardDescription className="text-xs">
                Areas where you excel based on your profile
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {insights.strengths.map((strength, index) => (
                  <div
                    key={index}
                    className="p-4 rounded-lg border border-primary/20 bg-primary/5 animate-fade-in transition-smooth hover-lift"
                    style={{ animationDelay: `${(index + 1) * 0.1}s` }}
                  >
                    <h4 className="text-sm font-semibold text-primary mb-2">
                      {strength.title}
                    </h4>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {strength.description}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Growth Areas */}
          <Card className={`border-0 shadow-sm hover-lift animate-fade-in-up animate-delay-300 ${!mounted ? "opacity-0" : ""}`}>
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold">Growth Areas</CardTitle>
              <CardDescription className="text-xs">
                Opportunities for skill development
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {insights.growthAreas.map((area, index) => (
                  <div
                    key={index}
                    className="p-4 rounded-lg border border-border animate-fade-in transition-smooth hover-lift"
                    style={{ animationDelay: `${(index + 1) * 0.1}s` }}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="text-sm font-semibold">{area.title}</h4>
                      <span
                        className={`
                          text-xs px-2 py-0.5 rounded
                          ${area.priority === "High"
                            ? "bg-red-100 text-red-700"
                            : area.priority === "Medium"
                              ? "bg-yellow-100 text-yellow-700"
                              : "bg-blue-100 text-blue-700"
                          }
                        `}
                      >
                        {area.priority}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {area.description}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Skill Map Graph */}
        <Card className={`border-0 shadow-sm hover-lift animate-fade-in-up animate-delay-400 ${!mounted ? "opacity-0" : ""}`}>
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold">Skill Map</CardTitle>
            <CardDescription className="text-xs">
              Visual representation of your skills across different categories
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Category Legend */}
              <div className="flex flex-wrap gap-3">
                {categories.map((category) => (
                  <div key={category} className="flex items-center gap-2">
                    <div
                      className={`w-3 h-3 rounded ${getCategoryColor(category)}`}
                    />
                    <span className="text-xs text-muted-foreground">{category}</span>
                  </div>
                ))}
              </div>

              {/* Skill Bars by Category */}
              {categories.map((category) => {
                const categorySkills = insights.skillMap.filter(
                  (s) => s.category === category
                )
                console.log("categorySkills", categorySkills)
                return (
                  <div key={category} className="space-y-3">
                    <h4 className="text-sm font-semibold text-foreground">{category}</h4>
                    <div className="space-y-2">
                      {categorySkills.map((skill, index) => (
                        <div key={index} className="space-y-1">
                          <div className="flex items-center justify-between text-sm">
                            <span className="font-medium">{skill.skill}</span>
                            <span className="text-muted-foreground">{skill.level}%</span>
                          </div>
                          <div className="h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className={`h-full ${getCategoryColor(category)} rounded-full transition-all duration-1000 ease-out`}
                              style={{
                                width: `${skill.level}%`,
                                animation: `fadeIn 0.5s ease-out ${index * 0.1}s both`
                              }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex justify-end gap-4">
          {error && (
            <div className="flex-1 p-3 rounded-md bg-destructive/10 border border-destructive/20">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}
          <Button
            variant="outline"
            onClick={() => router.push("/dashboard/ai-skill-profiler")}
            disabled={generatingPath}
          >
            Update Profile
          </Button>
          <Button
            className="bg-primary hover:bg-primary/90 text-white"
            onClick={handleGenerateLearningPath}
            disabled={generatingPath || !apiResponse}
          >
            {generatingPath ? "Generating..." : "Generate Learning Path"}
          </Button>
        </div>
      </div>
    </DashboardLayout>
  )
}

