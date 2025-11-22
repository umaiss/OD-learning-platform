"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface SkillData {
  skill: string
  level: number
  category: string
}

export default function AISkillInsightsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)

  // Mock AI insights data - in real app, this would come from API
  const [insights] = useState({
    remarks: "Based on your LinkedIn profile analysis, you demonstrate strong expertise in modern web development technologies. Your profile shows consistent growth in React and JavaScript ecosystems, with notable contributions to open-source projects. Your experience spans both frontend and backend development, indicating a well-rounded skill set.",
    strengths: [
      {
        title: "Frontend Expertise",
        description: "Strong proficiency in React, JavaScript, and modern UI frameworks. Demonstrated ability to build scalable and performant user interfaces.",
      },
      {
        title: "Full-Stack Capability",
        description: "Proven experience in both frontend and backend development, with expertise in Node.js and RESTful API design.",
      },
      {
        title: "Problem-Solving Skills",
        description: "Active contributor to technical discussions and problem-solving in team environments. Strong analytical thinking.",
      },
      {
        title: "Continuous Learning",
        description: "Shows commitment to staying updated with latest technologies and best practices in software development.",
      },
    ],
    growthAreas: [
      {
        title: "System Design & Architecture",
        description: "Consider deepening your knowledge in distributed systems, microservices architecture, and scalability patterns.",
        priority: "High",
      },
      {
        title: "DevOps & Cloud Technologies",
        description: "Expand your expertise in CI/CD pipelines, containerization (Docker/Kubernetes), and cloud platforms (AWS/Azure/GCP).",
        priority: "Medium",
      },
      {
        title: "Advanced TypeScript",
        description: "While you have TypeScript experience, advancing to advanced patterns, generics, and type system mastery would be beneficial.",
        priority: "Medium",
      },
      {
        title: "Testing & Quality Assurance",
        description: "Enhance your skills in automated testing, test-driven development, and quality assurance methodologies.",
        priority: "Low",
      },
    ],
    skillMap: [
      { skill: "React", level: 92, category: "Frontend" },
      { skill: "JavaScript", level: 88, category: "Frontend" },
      { skill: "TypeScript", level: 75, category: "Frontend" },
      { skill: "Node.js", level: 82, category: "Backend" },
      { skill: "Express.js", level: 78, category: "Backend" },
      { skill: "MongoDB", level: 70, category: "Backend" },
      { skill: "PostgreSQL", level: 65, category: "Backend" },
      { skill: "Git", level: 85, category: "Tools" },
      { skill: "Docker", level: 60, category: "DevOps" },
      { skill: "AWS", level: 55, category: "DevOps" },
      { skill: "CI/CD", level: 58, category: "DevOps" },
      { skill: "System Design", level: 50, category: "Architecture" },
    ],
  })

  useEffect(() => {
    // Simulate AI processing time
    const timer = setTimeout(() => {
      setLoading(false)
      setTimeout(() => setMounted(true), 100)
    }, 2000)
    return () => clearTimeout(timer)
  }, [])

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-sm text-muted-foreground">
              AI is analyzing your LinkedIn profile...
            </p>
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
                          ${
                            area.priority === "High"
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
          <Button
            variant="outline"
            onClick={() => router.push("/dashboard/ai-skill-profiler")}
          >
            Update Profile
          </Button>
          <Button className="bg-primary hover:bg-primary/90 text-white">
            Download Report
          </Button>
        </div>
      </div>
    </DashboardLayout>
  )
}

