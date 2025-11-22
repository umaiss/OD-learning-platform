/**
 * API Routes for Authentication
 * Base URL is loaded from environment variable NEXT_PUBLIC_API_BASE_URL
 */

const getBaseUrl = () => {
    // In browser, use the environment variable
    if (typeof window !== "undefined") {
        return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
    }
    // On server, use the environment variable
    return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
}

const baseURL = getBaseUrl()

interface SignupRequest {
    name: string
    email: string
    password: string
}

interface SignupResponse {
    id: number
    email: string
    name: string
    role: string
    message: string
}

interface LoginRequest {
    email: string
    password: string
}

interface LoginResponse {
    access_token: string
    token_type: string
    user: {
        id: number
        name: string
        email: string
        role: string
    }
}

/**
 * Signup API call
 */
export async function signupAPI(data: SignupRequest): Promise<SignupResponse> {
    try {
        const response = await fetch(`${baseURL}/api/v1/auth/signup`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })

        const responseData = await response.json()

        if (!response.ok) {
            // Handle error response
            const errorMessage =
                responseData.detail ||
                responseData.message ||
                "Failed to create account. Please try again."
            throw new Error(errorMessage)
        }

        return responseData
    } catch (error: any) {
        // Handle network errors or other exceptions
        if (error.message) {
            throw error
        }
        throw new Error("Network error. Please check your connection and try again.")
    }
}

/**
 * Login API call
 * Uses /login endpoint with OAuth2PasswordRequestForm format
 * Sends form data with username (email) and password
 */
export async function loginAPI(data: LoginRequest): Promise<LoginResponse> {
    try {
        // OAuth2PasswordRequestForm expects form-urlencoded data
        const formData = new URLSearchParams()
        formData.append("username", data.email) // OAuth2 uses 'username' field for email
        formData.append("password", data.password)

        const response = await fetch(`${baseURL}/api/v1/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: formData.toString(),
        })

        const responseData = await response.json()
        console.log("responseData", responseData)

        if (!response.ok) {
            // Handle error response
            const errorMessage =
                responseData.detail ||
                responseData.message ||
                "Invalid email or password. Please try again."
            throw new Error(errorMessage)
        }

        return responseData
    } catch (error: any) {
        // Handle network errors or other exceptions
        if (error.message) {
            throw error
        }
        throw new Error("Network error. Please check your connection and try again.")
    }
}

/**
 * Get current user API call
 * Uses the API client which automatically adds the token
 */
export async function getCurrentUserAPI() {
    try {
        const { apiGet } = await import("./client")
        return await apiGet("/api/v1/auth/me")
    } catch (error: any) {
        if (error.message) {
            throw error
        }
        throw new Error("Network error. Please check your connection and try again.")
    }
}

