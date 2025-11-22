import { create } from "zustand"
import { persist } from "zustand/middleware"
import { signupAPI, loginAPI } from "@/lib/api/auth"

interface User {
    id: string
    name: string
    email: string
    learner_id: number
}

interface AuthState {
    user: User | null
    token: string | null
    isAuthenticated: boolean
    login: (email: string, password: string) => Promise<void>
    signup: (name: string, email: string, password: string) => Promise<void>
    logout: () => void
    checkAuth: () => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            token: null,
            isAuthenticated: false,

            signup: async (name: string, email: string, password: string) => {
                try {
                    // Call the actual API endpoint
                    const response = await signupAPI({ name, email, password })

                    // Signup successful - don't auto-login
                    // User will need to login manually after signup
                    // The API should return success message or user data
                } catch (error) {
                    throw error
                }
            },

            login: async (email: string, password: string) => {
                try {
                    // Call the actual API endpoint
                    const response = await loginAPI({ email, password })

                    // Extract token and user from response
                    const token = response.access_token
                    const user: User = {
                        id: response.user.id.toString(),
                        name: response.user.name,
                        email: response.user.email,
                        learner_id: response.user.learner_id,
                    }

                    set({
                        user,
                        token,
                        isAuthenticated: true,
                    })
                } catch (error) {
                    throw error
                }
            },

            logout: () => {
                set({
                    user: null,
                    token: null,
                    isAuthenticated: false,
                })
            },

            checkAuth: () => {
                // This will be called on app load to check if user is authenticated
                // The persist middleware handles restoring state from localStorage
            },
        }),
        {
            name: "auth-storage", // unique name for localStorage key
            partialize: (state) => ({
                user: state.user,
                token: state.token,
                isAuthenticated: state.isAuthenticated,
            }),
        }
    )
)

