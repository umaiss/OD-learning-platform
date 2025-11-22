/**
 * Learning Path API Routes
 */

import { apiPost } from "./client"

interface GenerateLearningPathRequest {
    learner_id: number
    skill_map: Record<string, string>
    experience: number
    role: string
}

interface GenerateLearningPathResponse {
    learner_id: number
    learning_plan_id: number
    duration_weeks: number
    weekly_goals: string[]
    milestones: string[]
    modules: Array<{
        name: string
        description: string
    }>
    message: string
}

/**
 * Generate learning path
 * POST /api/v1/learning-path/generate
 */
export async function generateLearningPathAPI(
    data: GenerateLearningPathRequest
): Promise<GenerateLearningPathResponse> {
    try {
        const response = await apiPost<GenerateLearningPathResponse>(
            "/api/v1/learning-path/generate",
            data
        )

        return response
    } catch (error: any) {
        if (error.message) {
            throw error
        }
        throw new Error("Failed to generate learning path. Please try again.")
    }
}

