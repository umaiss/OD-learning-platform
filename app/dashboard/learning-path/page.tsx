"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface LearningPathData {
    learner_id: number
    learning_plan_id?: number
    duration_weeks: number
    weekly_goals: string[]
    milestones: string[]
    modules: Array<{
        name: string
        description: string
    }>
    message: string
}

export default function LearningPathPage() {
    const router = useRouter()
    const [loading, setLoading] = useState(true)
    const [mounted, setMounted] = useState(false)
    const [learningPath, setLearningPath] = useState<LearningPathData | null>(null)
    const [error, setError] = useState("")

    useEffect(() => {
        // Get learning path data from sessionStorage
        const storedData = sessionStorage.getItem("learningPathData")

        if (!storedData) {
            setError("No learning path data found. Please generate your learning path first.")
            setLoading(false)
            return
        }

        try {
            const parsedData: LearningPathData = JSON.parse(storedData)
            setLearningPath(parsedData)
            setLoading(false)
            setTimeout(() => setMounted(true), 100)
        } catch (err: any) {
            setError("Failed to parse learning path data. Please try again.")
            setLoading(false)
        }
    }, [])

    if (loading) {
        return (
            <DashboardLayout>
                <div className="flex items-center justify-center min-h-[60vh]">
                    <div className="text-center space-y-4">
                        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
                        <p className="text-sm text-muted-foreground">
                            Loading your learning path...
                        </p>
                    </div>
                </div>
            </DashboardLayout>
        )
    }

    if (error || !learningPath) {
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
                        <h3 className="text-lg font-semibold">Unable to Load Learning Path</h3>
                        <p className="text-sm text-muted-foreground">{error || "No learning path data available"}</p>
                        <Button
                            onClick={() => router.push("/dashboard/ai-skill-profiler/insights")}
                            className="mt-4"
                        >
                            Generate Learning Path
                        </Button>
                    </div>
                </div>
            </DashboardLayout>
        )
    }

    // Group modules by week (assuming equal distribution)
    const modulesPerWeek = Math.ceil(learningPath.modules.length / learningPath.duration_weeks)
    const weeklyModules: Array<Array<{ name: string; description: string }>> = []

    for (let i = 0; i < learningPath.duration_weeks; i++) {
        const start = i * modulesPerWeek
        const end = Math.min(start + modulesPerWeek, learningPath.modules.length)
        weeklyModules.push(learningPath.modules.slice(start, end))
    }

    // Calculate hours and XP per week (example calculation)
    const hoursPerWeek = Math.ceil(8 / learningPath.duration_weeks) * 2 // Approximate 2 hours per module
    const xpPerWeek = 200 // Base XP per week

    return (
        <DashboardLayout>
            <div className="space-y-8 max-w-6xl">
                {/* Header */}
                <div className={`flex items-center justify-between animate-fade-in-up ${!mounted ? "opacity-0" : ""}`}>
                    <div className="space-y-1">
                        <h1 className="text-3xl font-semibold tracking-tight text-foreground">
                            Your Learning Path
                        </h1>
                        <p className="text-sm text-muted-foreground">
                            Personalized curriculum designed for your skill development
                        </p>
                    </div>
                    <Button
                        variant="outline"
                        onClick={() => router.push("/dashboard/ai-skill-profiler/insights")}
                        className="transition-smooth hover-lift"
                    >
                        Back to Insights
                    </Button>
                </div>

                {/* Course Header Card */}
                <div className={`relative overflow-hidden rounded-lg bg-gradient-to-r from-primary to-primary/80 p-6 text-primary-foreground animate-fade-in-up animate-delay-100 ${!mounted ? "opacity-0" : ""}`}>
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-2xl font-bold mb-2">Full-Stack Development Mastery</h2>
                            <p className="text-primary-foreground/80 text-sm">Backend, Cloud, and DevOps skills</p>
                        </div>
                        <div className="bg-primary/50 rounded-lg px-6 py-4 text-center">
                            <div className="text-3xl font-bold">{learningPath.duration_weeks}</div>
                            <div className="text-sm text-primary-foreground/80">Weeks</div>
                        </div>
                    </div>
                </div>

                {/* Weekly Timeline */}
                <div className="relative">
                    {/* Vertical Timeline Line */}
                    <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-border" />

                    <div className="space-y-8">
                        {weeklyModules.map((weekModules, weekIndex) => {
                            const weekNumber = weekIndex + 1
                            const weekGoal = learningPath.weekly_goals[weekIndex] || `Week ${weekNumber} Goals`
                            const totalModules = weekModules.length
                            const totalHours = totalModules * 2 // Approximate 2 hours per module
                            const totalXP = totalModules * 50 // Approximate 50 XP per module

                            return (
                                <div
                                    key={weekIndex}
                                    className={`relative flex gap-6 animate-fade-in-up`}
                                    style={{ animationDelay: `${(weekIndex + 1) * 0.1}s` }}
                                >
                                    {/* Timeline Dot */}
                                    <div className="relative z-10 flex-shrink-0">
                                        <div className="w-4 h-4 rounded-full bg-primary border-4 border-background" />
                                    </div>

                                    {/* Week Card */}
                                    <Card className="flex-1 border-0 shadow-sm hover-lift">
                                        <CardHeader className="pb-4">
                                            <CardTitle className="text-lg font-semibold text-primary">
                                                Week {weekNumber}: {weekGoal.split(":")[0] || weekGoal}
                                            </CardTitle>
                                            <CardDescription className="text-xs">
                                                {weekGoal}
                                            </CardDescription>
                                        </CardHeader>
                                        <CardContent className="space-y-4">
                                            {/* Modules List */}
                                            <div className="space-y-2">
                                                {weekModules.map((module, moduleIndex) => (
                                                    <div key={moduleIndex} className="p-3 rounded-lg bg-muted/50">
                                                        <h4 className="font-semibold text-sm mb-1">{module.name}</h4>
                                                        <p className="text-xs text-muted-foreground">{module.description}</p>
                                                    </div>
                                                ))}
                                            </div>

                                            {/* Week Stats */}
                                            <div className="flex gap-2 pt-2 border-t">
                                                <div className="px-3 py-1 rounded-md bg-primary/10 text-primary text-xs font-medium">
                                                    {totalModules} Modules
                                                </div>
                                                <div className="px-3 py-1 rounded-md bg-primary/10 text-primary text-xs font-medium">
                                                    {totalHours} hours
                                                </div>
                                                <div className="px-3 py-1 rounded-md bg-primary/10 text-primary text-xs font-medium">
                                                    {totalXP} XP
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </div>
                            )
                        })}
                    </div>
                </div>

                {/* Milestones Section */}
                {learningPath.milestones && learningPath.milestones.length > 0 && (
                    <Card className={`border-0 shadow-sm hover-lift animate-fade-in-up animate-delay-300 ${!mounted ? "opacity-0" : ""}`}>
                        <CardHeader className="pb-4">
                            <CardTitle className="text-base font-semibold">Key Milestones</CardTitle>
                            <CardDescription className="text-xs">
                                Important achievements throughout your learning journey
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {learningPath.milestones.map((milestone, index) => (
                                    <div
                                        key={index}
                                        className="flex items-start gap-3 p-3 rounded-lg border border-primary/20 bg-primary/5"
                                    >
                                        <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center flex-shrink-0 text-xs font-semibold">
                                            {index + 1}
                                        </div>
                                        <p className="text-sm text-foreground">{milestone}</p>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Action Buttons */}
                <div className="flex justify-end gap-4">
                    <Button
                        variant="outline"
                        onClick={() => router.push("/dashboard/ai-skill-profiler/insights")}
                    >
                        Back to Insights
                    </Button>
                    <Button className="bg-primary hover:bg-primary/90 text-white">
                        Start Learning
                    </Button>
                </div>
            </div>
        </DashboardLayout>
    )
}

