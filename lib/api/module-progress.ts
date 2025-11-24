/**
 * Module Progress API Routes
 */

import { apiPost } from "./client"

interface CompleteWeekRequest {
    learner_id: number
    learning_plan_id: number
    week_number: number
}

interface CompleteWeekResponse {
    learner_id: number
    learning_plan_id: number
    week_number: number
    is_completed: boolean
    completed_at: string
    message: string
}

/**
 * Mark a week as completed
 * POST /api/v1/module-progress/complete-week
 */
export async function completeWeekAPI(
    data: CompleteWeekRequest
): Promise<CompleteWeekResponse> {
    try {
        const response = await apiPost<CompleteWeekResponse>(
            "/api/v1/module-progress/complete-week",
            data
        )

        return response
    } catch (error: any) {
        if (error.message) {
            throw error
        }
        throw new Error("Failed to complete week. Please try again.")
    }
}

