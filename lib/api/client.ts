/**
 * API Client Utility
 * Automatically adds authentication token to request headers
 */

import { useAuthStore } from "@/store/auth-store"

const getBaseUrl = () => {
    if (typeof window !== "undefined") {
        return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
    }
    return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
}

const baseURL = getBaseUrl()

interface RequestOptions extends RequestInit {
    requireAuth?: boolean
}

/**
 * Get the current auth token from Zustand store
 * This function can be called from components or API functions
 */
export function getAuthToken(): string | null {
    if (typeof window === "undefined") {
        return null
    }
    return useAuthStore.getState().token
}

/**
 * API client function that automatically adds auth token to headers
 * @param endpoint - API endpoint (e.g., "/api/v1/profile")
 * @param options - Fetch options with optional requireAuth flag
 */
export async function apiClient(
    endpoint: string,
    options: RequestOptions = {}
): Promise<Response> {
    const { requireAuth = true, headers = {}, ...fetchOptions } = options

    // Build headers as a Record
    const requestHeaders: Record<string, string> = {
        "Content-Type": "application/json",
        ...(headers as Record<string, string>),
    }

    // Add authorization token if required
    if (requireAuth) {
        const token = getAuthToken()
        if (token) {
            requestHeaders.Authorization = `Bearer ${token}`
        } else {
            throw new Error("Authentication required. Please login first.")
        }
    }

    // Make the request
    const response = await fetch(`${baseURL}${endpoint}`, {
        ...fetchOptions,
        headers: requestHeaders,
    })

    return response
}

/**
 * Helper function for GET requests
 */
export async function apiGet<T = any>(
    endpoint: string,
    options: RequestOptions = {}
): Promise<T> {
    const response = await apiClient(endpoint, {
        ...options,
        method: "GET",
    })

    const data = await response.json()

    if (!response.ok) {
        throw new Error(data.detail || data.message || "Request failed")
    }

    return data
}

/**
 * Helper function for POST requests
 */
export async function apiPost<T = any>(
    endpoint: string,
    body?: any,
    options: RequestOptions = {}
): Promise<T> {
    const response = await apiClient(endpoint, {
        ...options,
        method: "POST",
        body: body ? JSON.stringify(body) : undefined,
    })

    const data = await response.json()

    if (!response.ok) {
        throw new Error(data.detail || data.message || "Request failed")
    }

    return data
}

/**
 * Helper function for PUT requests
 */
export async function apiPut<T = any>(
    endpoint: string,
    body?: any,
    options: RequestOptions = {}
): Promise<T> {
    const response = await apiClient(endpoint, {
        ...options,
        method: "PUT",
        body: body ? JSON.stringify(body) : undefined,
    })

    const data = await response.json()

    if (!response.ok) {
        throw new Error(data.detail || data.message || "Request failed")
    }

    return data
}

/**
 * Helper function for DELETE requests
 */
export async function apiDelete<T = any>(
    endpoint: string,
    options: RequestOptions = {}
): Promise<T> {
    const response = await apiClient(endpoint, {
        ...options,
        method: "DELETE",
    })

    const data = await response.json()

    if (!response.ok) {
        throw new Error(data.detail || data.message || "Request failed")
    }

    return data
}

