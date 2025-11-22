/**
 * Profile API Routes
 */

import { apiPost } from "./client"
import { LinkedinProfileMockData } from "@/constants/data"

interface GenerateProfileRequest {
    learner_id: number
    current_role: string
    primary_stack: string[]
    learning_goals: string
    skill_rate: Record<string, string>
    linkedin_profile: {
        id: number
        learnerId: number
        username: string
        fullName: string
        headline: string
        location: string
        endorsedSkills: Array<{
            skill: string
            endorsements: number
        }>
        connections: number
        followers: number
    }
}

interface GenerateProfileResponse {
    // Add response type based on backend response
    [key: string]: any
}

/**
 * Generate profile from AI
 * POST /api/v1/profile/generate
 */
export async function generateProfileAPI(
    data: {
        learnerId: number
        currentRole: string
        primaryStack: string[]
        learningGoals: string
        proficiency: string
        linkedInConnected: boolean
    }
): Promise<GenerateProfileResponse> {
    try {
        // Map proficiency to skill_rate format
        const skillRate: Record<string, string> = {
            proficiency: data.proficiency, // beginner, intermediate, advanced
        }

        // Prepare LinkedIn profile data
        // If LinkedIn is connected, use mock data, otherwise send empty/null
        const linkedinProfile = {
            id: LinkedinProfileMockData.id,
            learnerId: data.learnerId,
            username: LinkedinProfileMockData.username,
            fullName: LinkedinProfileMockData.fullName,
            headline: LinkedinProfileMockData.headline,
            location: LinkedinProfileMockData.location,
            endorsedSkills: LinkedinProfileMockData.endorsedSkills,
            connections: LinkedinProfileMockData.connections,
            followers: LinkedinProfileMockData.followers,
        }


        const requestData: GenerateProfileRequest = {
            learner_id: data.learnerId,
            current_role: data.currentRole,
            primary_stack: data.primaryStack,
            learning_goals: data.learningGoals,
            skill_rate: skillRate,
            linkedin_profile: linkedinProfile,
        }

        const response = await apiPost<GenerateProfileResponse>(
            "/api/v1/profile/generate",
            requestData
        )

        return response
    } catch (error: any) {
        if (error.message) {
            throw error
        }
        throw new Error("Failed to generate profile. Please try again.")
    }
}

