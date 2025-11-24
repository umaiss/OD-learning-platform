"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { Sidebar } from "@/components/ui/sidebar"
import {
  HomeIcon,
  SkillsIcon,
  AssessmentIcon,
  ProgressIcon,
  SettingsIcon,
  AISkillProfilerIcon,
  StarIcon,
} from "@/components/icons"
import { Button } from "@/components/ui/button"
import { LogoutIcon } from "@/components/icons"
import { useAuthStore } from "@/store/auth-store"
import { useShallow } from "zustand/react/shallow"

interface DashboardLayoutProps {
  children: React.ReactNode
}

const sidebarItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: <HomeIcon />,
  },
  {
    title: "AI Skill Profiler",
    href: "/dashboard/ai-skill-profiler",
    icon: <AISkillProfilerIcon />,
  },
  {
    title: "Start Journey",
    href: "/dashboard/star-journey",
    icon: <StarIcon />,
  },
  {
    title: "My Skills",
    href: "/dashboard/skills",
    icon: <SkillsIcon />,
  },
  {
    title: "Assessments",
    href: "/dashboard/assessments",
    icon: <AssessmentIcon />,
  },
  {
    title: "Progress",
    href: "/dashboard/progress",
    icon: <ProgressIcon />,
  },
  {
    title: "Settings",
    href: "/dashboard/settings",
    icon: <SettingsIcon />,
  },
]

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter()
  const { user, isAuthenticated, logout } = useAuthStore(
    useShallow((state) => ({
      user: state.user,
      isAuthenticated: state.isAuthenticated,
      logout: state.logout,
    }))
  )
  const [sidebarOpen, setSidebarOpen] = React.useState(false)

  React.useEffect(() => {
    // Redirect to login if not authenticated
    if (!isAuthenticated) {
      router.push("/login")
    }
  }, [isAuthenticated, router])

  const handleLogout = () => {
    logout()
    router.push("/login")
  }

  // Don't render if not authenticated
  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
        `}
      >
        <Sidebar items={sidebarItems} />
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 border-b bg-background flex items-center justify-between px-4 lg:px-6">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M2.5 5H17.5M2.5 10H17.5M2.5 15H17.5"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </Button>

          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon">
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M10 2.5C6.19167 2.5 3.125 5.56667 3.125 9.375C3.125 13.1833 6.19167 16.25 10 16.25C13.8083 16.25 16.875 13.1833 16.875 9.375C16.875 5.56667 13.8083 2.5 10 2.5ZM10 14.5833C7.24167 14.5833 5 12.3417 5 9.58333C5 6.825 7.24167 4.58333 10 4.58333C12.7583 4.58333 15 6.825 15 9.58333C15 12.3417 12.7583 14.5833 10 14.5833ZM10 6.66667C8.61667 6.66667 7.5 7.78333 7.5 9.16667C7.5 10.55 8.61667 11.6667 10 11.6667C11.3833 11.6667 12.5 10.55 12.5 9.16667C12.5 7.78333 11.3833 6.66667 10 6.66667Z"
                  fill="currentColor"
                />
              </svg>
            </Button>
            <Button variant="ghost" size="icon">
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M10 2.5C8.625 2.5 7.5 3.625 7.5 5C7.5 6.375 8.625 7.5 10 7.5C11.375 7.5 12.5 6.375 12.5 5C12.5 3.625 11.375 2.5 10 2.5ZM10 8.75C7.925 8.75 6.25 10.425 6.25 12.5V15H13.75V12.5C13.75 10.425 12.075 8.75 10 8.75Z"
                  fill="currentColor"
                />
              </svg>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="gap-2"
              onClick={handleLogout}
            >
              <LogoutIcon />
              <span className="hidden sm:inline">Logout</span>
            </Button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto bg-background p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

