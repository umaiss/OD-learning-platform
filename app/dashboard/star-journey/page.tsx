"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { generateContentAPI, generateWeekQuizAPI } from "@/lib/api/content"
import { completeWeekAPI } from "@/lib/api/module-progress"
import { useAuthStore } from "@/store/auth-store"
import { useShallow } from "zustand/react/shallow"

interface Module {
    name: string
    description: string
    learning_materials?: Array<{
        title: string
        url: string
        platform: string
        type?: string
        estimated_hours?: number
        description?: string
    }>
    content?: {
        lesson_text: string
        quiz: Array<{
            question: string
            options: string[]
            answer: string
        }>
    }
    loading?: boolean
    error?: string
}

interface WeekData {
    week: number
    goals: string[]
    modules: Module[]
    xp: number
    milestones: string[]
    is_completed?: boolean
    quiz?: Array<{
        question: string
        options: string[]
        answer: string
    }>
    loadingQuiz?: boolean
    loadingComplete?: boolean
}

interface LearningPathData {
    learner_id: number
    learning_plan_id: number
    duration_weeks: number
    weekly_goals: WeekData[]
    message: string
}

export default function StarJourneyPage() {
    const router = useRouter()
    const { user } = useAuthStore(
        useShallow((state) => ({
            user: state.user,
        }))
    )
    const [loading, setLoading] = useState(true)
    const [mounted, setMounted] = useState(false)
    const [learningPath, setLearningPath] = useState<LearningPathData | null>(null)
    const [error, setError] = useState("")
    const [expandedWeek, setExpandedWeek] = useState<number | null>(null)
    const [expandedModule, setExpandedModule] = useState<{ week: number; moduleIndex: number } | null>(null)
    const [showWeekQuiz, setShowWeekQuiz] = useState<number | null>(null)

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

    const handleGenerateContent = async (weekIndex: number, moduleIndex: number) => {
        if (!learningPath || !user?.learner_id) return

        const week = learningPath.weekly_goals[weekIndex]
        const module = week.modules[moduleIndex]

        // Update loading state for this specific module
        setLearningPath((prev) => {
            if (!prev) return prev
            const updated = { ...prev }
            updated.weekly_goals[weekIndex].modules[moduleIndex] = {
                ...module,
                loading: true,
                error: undefined,
            }
            return updated
        })

        try {
            const response = await generateContentAPI({
                learner_id: user.learner_id,
                module_name: module.name,
            })

            // Update the module with content
            setLearningPath((prev) => {
                if (!prev) return prev
                const updated = { ...prev }
                updated.weekly_goals[weekIndex].modules[moduleIndex] = {
                    ...module,
                    content: {
                        lesson_text: response.lesson_text,
                        quiz: response.quiz,
                    },
                    loading: false,
                }
                return updated
            })

            // Expand the module to show content
            setExpandedModule({ week: weekIndex, moduleIndex })
        } catch (err: any) {
            setLearningPath((prev) => {
                if (!prev) return prev
                const updated = { ...prev }
                updated.weekly_goals[weekIndex].modules[moduleIndex] = {
                    ...module,
                    loading: false,
                    error: err.message || "Failed to generate content",
                }
                return updated
            })
        }
    }

    const handleCompleteWeek = async (weekIndex: number) => {
        if (!learningPath || !user?.learner_id) return

        const week = learningPath.weekly_goals[weekIndex]

        // Update loading state
        setLearningPath((prev) => {
            if (!prev) return prev
            const updated = { ...prev }
            updated.weekly_goals[weekIndex] = {
                ...week,
                loadingComplete: true,
            }
            return updated
        })

        try {
            await completeWeekAPI({
                learner_id: user.learner_id,
                learning_plan_id: learningPath.learning_plan_id,
                week_number: week.week,
            })

            // Update week as completed
            setLearningPath((prev) => {
                if (!prev) return prev
                const updated = { ...prev }
                updated.weekly_goals[weekIndex] = {
                    ...week,
                    is_completed: true,
                    loadingComplete: false,
                }
                return updated
            })
        } catch (err: any) {
            setLearningPath((prev) => {
                if (!prev) return prev
                const updated = { ...prev }
                updated.weekly_goals[weekIndex] = {
                    ...week,
                    loadingComplete: false,
                }
                return updated
            })
            alert(err.message || "Failed to complete week. Please try again.")
        }
    }

    const handleGenerateWeekQuiz = async (weekIndex: number) => {
        if (!learningPath || !user?.learner_id) return

        const week = learningPath.weekly_goals[weekIndex]

        // Update loading state
        setLearningPath((prev) => {
            if (!prev) return prev
            const updated = { ...prev }
            updated.weekly_goals[weekIndex] = {
                ...week,
                loadingQuiz: true,
            }
            return updated
        })

        try {
            const response = await generateWeekQuizAPI({
                learner_id: user.learner_id,
                learning_plan_id: learningPath.learning_plan_id,
                week_number: week.week,
            })

            // Update week with quiz
            setLearningPath((prev) => {
                if (!prev) return prev
                const updated = { ...prev }
                updated.weekly_goals[weekIndex] = {
                    ...week,
                    quiz: response.quiz,
                    loadingQuiz: false,
                }
                return updated
            })

            // Show the quiz
            setShowWeekQuiz(weekIndex)
        } catch (err: any) {
            setLearningPath((prev) => {
                if (!prev) return prev
                const updated = { ...prev }
                updated.weekly_goals[weekIndex] = {
                    ...week,
                    loadingQuiz: false,
                }
                return updated
            })
            alert(err.message || "Failed to generate quiz. Please try again.")
        }
    }

    if (loading) {
        return (
            <DashboardLayout>
                <div className="flex items-center justify-center min-h-[60vh]">
                    <div className="text-center space-y-4">
                        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
                        <p className="text-sm text-muted-foreground">
                            Loading your journey...
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
                        <h3 className="text-lg font-semibold">Unable to Load Journey</h3>
                        <p className="text-sm text-muted-foreground">{error || "No learning path data available"}</p>
                        <Button
                            onClick={() => router.push("/dashboard/learning-path")}
                            className="mt-4"
                        >
                            Go to Learning Path
                        </Button>
                    </div>
                </div>
            </DashboardLayout>
        )
    }

    return (
        <DashboardLayout>
            <div className="space-y-8 max-w-6xl">
                {/* Header */}
                <div className={`flex items-center justify-between animate-fade-in-up ${!mounted ? "opacity-0" : ""}`}>
                    <div className="space-y-1">
                        <h1 className="text-3xl font-semibold tracking-tight text-foreground">
                            ⭐ Start Journey
                        </h1>
                        <p className="text-sm text-muted-foreground">
                            Explore your learning path week by week with interactive content
                        </p>
                    </div>
                    <Button
                        variant="outline"
                        onClick={() => router.push("/dashboard/learning-path")}
                        className="transition-smooth hover-lift"
                    >
                        Back to Learning Path
                    </Button>
                </div>

                {/* Weekly Content */}
                <div className="space-y-6">
                    {learningPath.weekly_goals.map((week, weekIndex) => (
                        <Card
                            key={week.week}
                            className={`transition-smooth hover-lift animate-fade-in-up animate-delay-${weekIndex * 100} ${!mounted ? "opacity-0" : ""}`}
                        >
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <CardTitle className="text-xl">
                                            Week {week.week}
                                        </CardTitle>
                                        <CardDescription className="mt-2">
                                            {week.goals.join(" • ")}
                                        </CardDescription>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {week.is_completed && (
                                            <span className="text-sm font-medium text-green-600 flex items-center gap-1">
                                                <svg
                                                    width="16"
                                                    height="16"
                                                    viewBox="0 0 16 16"
                                                    fill="none"
                                                    xmlns="http://www.w3.org/2000/svg"
                                                >
                                                    <path
                                                        d="M13.3333 4L6 11.3333L2.66667 8"
                                                        stroke="currentColor"
                                                        strokeWidth="2"
                                                        strokeLinecap="round"
                                                        strokeLinejoin="round"
                                                    />
                                                </svg>
                                                Completed
                                            </span>
                                        )}
                                        <span className="text-sm font-medium text-primary">
                                            {week.xp} XP
                                        </span>
                                        {!week.is_completed && (
                                            <Button
                                                size="sm"
                                                onClick={() => handleCompleteWeek(weekIndex)}
                                                disabled={week.loadingComplete}
                                                className="bg-green-600 hover:bg-green-700 text-white"
                                            >
                                                {week.loadingComplete ? "Completing..." : "Complete Week"}
                                            </Button>
                                        )}
                                        {week.is_completed && !week.quiz && (
                                            <Button
                                                size="sm"
                                                variant="outline"
                                                onClick={() => handleGenerateWeekQuiz(weekIndex)}
                                                disabled={week.loadingQuiz}
                                            >
                                                {week.loadingQuiz ? "Generating..." : "Generate Quiz"}
                                            </Button>
                                        )}
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => setExpandedWeek(expandedWeek === weekIndex ? null : weekIndex)}
                                        >
                                            {expandedWeek === weekIndex ? "Collapse" : "Expand"}
                                        </Button>
                                    </div>
                                </div>
                            </CardHeader>

                            {expandedWeek === weekIndex && (
                                <CardContent className="space-y-6">
                                    {/* Modules */}
                                    <div className="space-y-4">
                                        <h3 className="font-semibold text-lg">Modules</h3>
                                        {week.modules.map((module, moduleIndex) => {
                                            const isExpanded = expandedModule?.week === weekIndex && expandedModule?.moduleIndex === moduleIndex
                                            const hasContent = !!module.content

                                            return (
                                                <Card key={moduleIndex} className="border-l-4 border-l-primary">
                                                    <CardHeader>
                                                        <div className="flex items-start justify-between">
                                                            <div className="flex-1">
                                                                <CardTitle className="text-base">{module.name}</CardTitle>
                                                                <CardDescription className="mt-1">
                                                                    {module.description}
                                                                </CardDescription>
                                                            </div>
                                                            <div className="flex gap-2">
                                                                {!hasContent && (
                                                                    <Button
                                                                        size="sm"
                                                                        onClick={() => handleGenerateContent(weekIndex, moduleIndex)}
                                                                        disabled={module.loading}
                                                                    >
                                                                        {module.loading ? "Generating..." : "Generate Content"}
                                                                    </Button>
                                                                )}
                                                                {hasContent && (
                                                                    <Button
                                                                        variant="outline"
                                                                        size="sm"
                                                                        onClick={() => setExpandedModule(
                                                                            isExpanded
                                                                                ? null
                                                                                : { week: weekIndex, moduleIndex }
                                                                        )}
                                                                    >
                                                                        {isExpanded ? "Hide Content" : "View Content"}
                                                                    </Button>
                                                                )}
                                                            </div>
                                                        </div>
                                                        {module.error && (
                                                            <p className="text-sm text-destructive mt-2">{module.error}</p>
                                                        )}
                                                    </CardHeader>

                                                    {/* Learning Materials */}
                                                    {module.learning_materials && module.learning_materials.length > 0 && (
                                                        <CardContent>
                                                            <h4 className="text-sm font-semibold mb-2">Learning Materials</h4>
                                                            <div className="space-y-2">
                                                                {module.learning_materials.map((material, idx) => (
                                                                    <a
                                                                        key={idx}
                                                                        href={material.url}
                                                                        target="_blank"
                                                                        rel="noopener noreferrer"
                                                                        className="block p-3 rounded-lg border hover:bg-accent transition-colors"
                                                                    >
                                                                        <div className="flex items-center justify-between">
                                                                            <div>
                                                                                <p className="font-medium text-sm">{material.title}</p>
                                                                                <p className="text-xs text-muted-foreground mt-1">
                                                                                    {material.platform} {material.estimated_hours && `• ${material.estimated_hours} hours`}
                                                                                </p>
                                                                            </div>
                                                                            <svg
                                                                                width="16"
                                                                                height="16"
                                                                                viewBox="0 0 16 16"
                                                                                fill="none"
                                                                                xmlns="http://www.w3.org/2000/svg"
                                                                            >
                                                                                <path
                                                                                    d="M6 3H3C2.44772 3 2 3.44772 2 4V13C2 13.5523 2.44772 14 3 14H12C12.5523 14 13 13.5523 13 13V10M10 2H14M14 2V6M14 2L6 10"
                                                                                    stroke="currentColor"
                                                                                    strokeWidth="1.5"
                                                                                    strokeLinecap="round"
                                                                                    strokeLinejoin="round"
                                                                                />
                                                                            </svg>
                                                                        </div>
                                                                    </a>
                                                                ))}
                                                            </div>
                                                        </CardContent>
                                                    )}

                                                    {/* Generated Content */}
                                                    {isExpanded && hasContent && module.content && (
                                                        <CardContent className="border-t pt-4 space-y-4">
                                                            {/* Lesson Text */}
                                                            <div>
                                                                <h4 className="font-semibold mb-2">Lesson Content</h4>
                                                                <div className="prose prose-sm max-w-none p-4 bg-muted rounded-lg">
                                                                    <p className="whitespace-pre-wrap text-sm leading-relaxed">
                                                                        {module.content.lesson_text}
                                                                    </p>
                                                                </div>
                                                            </div>

                                                            {/* Quiz */}
                                                            {module.content.quiz && module.content.quiz.length > 0 && (
                                                                <div>
                                                                    <h4 className="font-semibold mb-3">Quiz</h4>
                                                                    <div className="space-y-4">
                                                                        {module.content.quiz.map((quizItem, quizIdx) => (
                                                                            <Card key={quizIdx} className="bg-muted/50">
                                                                                <CardContent className="pt-4">
                                                                                    <p className="font-medium mb-3">
                                                                                        {quizIdx + 1}. {quizItem.question}
                                                                                    </p>
                                                                                    <div className="space-y-2">
                                                                                        {quizItem.options.map((option, optIdx) => (
                                                                                            <div
                                                                                                key={optIdx}
                                                                                                className={`p-2 rounded border ${option === quizItem.answer
                                                                                                    ? "bg-primary/10 border-primary"
                                                                                                    : "bg-background"
                                                                                                    }`}
                                                                                            >
                                                                                                <div className="flex items-center gap-2">
                                                                                                    <span className="text-xs font-medium">
                                                                                                        {String.fromCharCode(65 + optIdx)}.
                                                                                                    </span>
                                                                                                    <span className="text-sm">{option}</span>
                                                                                                    {option === quizItem.answer && (
                                                                                                        <span className="ml-auto text-xs text-primary font-medium">
                                                                                                            ✓ Correct
                                                                                                        </span>
                                                                                                    )}
                                                                                                </div>
                                                                                            </div>
                                                                                        ))}
                                                                                    </div>
                                                                                </CardContent>
                                                                            </Card>
                                                                        ))}
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </CardContent>
                                                    )}
                                                </Card>
                                            )
                                        })}
                                    </div>

                                    {/* Milestones */}
                                    {week.milestones && week.milestones.length > 0 && (
                                        <div>
                                            <h3 className="font-semibold text-lg mb-3">Milestones</h3>
                                            <div className="space-y-2">
                                                {week.milestones.map((milestone, idx) => (
                                                    <div key={idx} className="flex items-center gap-2 p-2 rounded-lg bg-primary/5">
                                                        <svg
                                                            width="16"
                                                            height="16"
                                                            viewBox="0 0 16 16"
                                                            fill="none"
                                                            xmlns="http://www.w3.org/2000/svg"
                                                        >
                                                            <path
                                                                d="M13.3333 4L6 11.3333L2.66667 8"
                                                                stroke="currentColor"
                                                                strokeWidth="2"
                                                                strokeLinecap="round"
                                                                strokeLinejoin="round"
                                                            />
                                                        </svg>
                                                        <span className="text-sm">{milestone}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Week Quiz */}
                                    {week.quiz && week.quiz.length > 0 && (
                                        <div>
                                            <div className="flex items-center justify-between mb-3">
                                                <h3 className="font-semibold text-lg">Week Quiz</h3>
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => setShowWeekQuiz(showWeekQuiz === weekIndex ? null : weekIndex)}
                                                >
                                                    {showWeekQuiz === weekIndex ? "Hide Quiz" : "Show Quiz"}
                                                </Button>
                                            </div>
                                            {showWeekQuiz === weekIndex && (
                                                <div className="space-y-4">
                                                    {week.quiz.map((quizItem, quizIdx) => (
                                                        <Card key={quizIdx} className="bg-muted/50">
                                                            <CardContent className="pt-4">
                                                                <p className="font-medium mb-3">
                                                                    {quizIdx + 1}. {quizItem.question}
                                                                </p>
                                                                <div className="space-y-2">
                                                                    {quizItem.options.map((option, optIdx) => (
                                                                        <div
                                                                            key={optIdx}
                                                                            className={`p-2 rounded border ${option === quizItem.answer
                                                                                ? "bg-primary/10 border-primary"
                                                                                : "bg-background"
                                                                                }`}
                                                                        >
                                                                            <div className="flex items-center gap-2">
                                                                                <span className="text-xs font-medium">
                                                                                    {String.fromCharCode(65 + optIdx)}.
                                                                                </span>
                                                                                <span className="text-sm">{option}</span>
                                                                                {option === quizItem.answer && (
                                                                                    <span className="ml-auto text-xs text-primary font-medium">
                                                                                        ✓ Correct
                                                                                    </span>
                                                                                )}
                                                                            </div>
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            </CardContent>
                                                        </Card>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </CardContent>
                            )}
                        </Card>
                    ))}
                </div>
            </div>
        </DashboardLayout>
    )
}

