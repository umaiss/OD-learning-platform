/**
 * Content API Routes
 */

import { apiPost } from "./client"

interface GenerateContentRequest {
    learner_id: number
    module_name: string
}

interface QuizQuestion {
    question: string
    options: string[]
    answer: string
}

interface GenerateContentResponse {
    learner_id: number
    content_id: number
    module_name: string
    lesson_text: string
    quiz: QuizQuestion[]
    message: string
}

/**
 * Generate content for a module
 * POST /api/v1/content/generate
 */
export async function generateContentAPI(
    data: GenerateContentRequest
): Promise<GenerateContentResponse> {
    try {
        const response = await apiPost<GenerateContentResponse>(
            "/api/v1/content/generate",
            data
        )

        return response
    } catch (error: any) {
        if (error.message) {
            throw error
        }
        throw new Error("Failed to generate content. Please try again.")
    }
}

interface GenerateWeekQuizRequest {
    learner_id: number
    learning_plan_id: number
    week_number: number
}

interface QuizQuestion {
    question: string
    options: string[]
    answer: string
}

interface GenerateWeekQuizResponse {
    learner_id: number
    learning_plan_id: number
    week_number: number
    quiz: QuizQuestion[]
    message: string
}

/**
 * Generate quiz for a specific week
 * POST /api/v1/content/generate-week-quiz
 */
export async function generateWeekQuizAPI(
    data: GenerateWeekQuizRequest
): Promise<GenerateWeekQuizResponse> {
    try {
        const response = await apiPost<GenerateWeekQuizResponse>(
            "/api/v1/content/generate-week-quiz",
            data
        )

        return response
    } catch (error: any) {
        if (error.message) {
            throw error
        }
        throw new Error("Failed to generate week quiz. Please try again.")
    }
}

