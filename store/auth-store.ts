import { create } from "zustand"
import { persist } from "zustand/middleware"

interface User {
    id: string
    name: string
    email: string
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

// Mock API functions - replace with actual API calls
const mockSignup = async (name: string, email: string, password: string) => {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // In real app, this would be an API call to your backend
    // For now, we'll just create a mock token
    const token = `mock_token_${Date.now()}`
    const user = {
        id: `user_${Date.now()}`,
        name,
        email,
    }

    return { token, user }
}

const mockLogin = async (email: string, password: string) => {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // In real app, this would be an API call to your backend
    // For now, we'll check localStorage for registered users
    if (typeof window === "undefined") {
        throw new Error("Invalid email or password")
    }

    const storedUsers = localStorage.getItem("registered_users")
    const users = storedUsers ? JSON.parse(storedUsers) : []

    const user = users.find((u: any) => u.email === email && u.password === password)

    if (!user) {
        throw new Error("Invalid email or password")
    }

    const token = `mock_token_${Date.now()}`

    return { token, user: { id: user.id, name: user.name, email: user.email } }
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            token: null,
            isAuthenticated: false,

            signup: async (name: string, email: string, password: string) => {
                try {
                    // Store user in localStorage for demo purposes
                    if (typeof window !== "undefined") {
                        const storedUsers = localStorage.getItem("registered_users")
                        const users = storedUsers ? JSON.parse(storedUsers) : []

                        // Check if user already exists
                        if (users.find((u: any) => u.email === email)) {
                            throw new Error("User with this email already exists")
                        }

                        const newUser = {
                            id: `user_${Date.now()}`,
                            name,
                            email,
                            password, // In real app, this should be hashed
                        }

                        users.push(newUser)
                        localStorage.setItem("registered_users", JSON.stringify(users))
                    }

                    // Don't auto-login after signup, just return success
                    // User will need to login manually
                } catch (error) {
                    throw error
                }
            },

            login: async (email: string, password: string) => {
                try {
                    const { token, user } = await mockLogin(email, password)

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

