"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <DashboardLayout>
      <div className="space-y-8 max-w-7xl">
        {/* Welcome Section */}
        <div className={`space-y-1 animate-fade-in-up ${!mounted ? "opacity-0" : ""}`}>
          <h1 className="text-3xl font-semibold tracking-tight text-foreground">
            Welcome back
          </h1>
          <p className="text-sm text-muted-foreground">
            Here's an overview of your skills and progress
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card className={`border-0 shadow-sm hover-lift animate-fade-in animate-delay-100 ${!mounted ? "opacity-0" : ""}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Skills
              </CardTitle>
              <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  className="h-4 w-4 text-primary"
                >
                  <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                </svg>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-semibold tracking-tight">24</div>
              <p className="text-xs text-muted-foreground mt-1">
                +3 from last month
              </p>
            </CardContent>
          </Card>

          <Card className={`border-0 shadow-sm hover-lift animate-fade-in animate-delay-200 ${!mounted ? "opacity-0" : ""}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Assessments
              </CardTitle>
              <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  className="h-4 w-4 text-primary"
                >
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-semibold tracking-tight">12</div>
              <p className="text-xs text-muted-foreground mt-1">
                +2 this week
              </p>
            </CardContent>
          </Card>

          <Card className={`border-0 shadow-sm hover-lift animate-fade-in animate-delay-300 ${!mounted ? "opacity-0" : ""}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Skill Level
              </CardTitle>
              <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  className="h-4 w-4 text-primary"
                >
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                </svg>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-semibold tracking-tight">Advanced</div>
              <p className="text-xs text-muted-foreground mt-1">
                Top 15% of users
              </p>
            </CardContent>
          </Card>

          <Card className={`border-0 shadow-sm hover-lift animate-fade-in animate-delay-400 ${!mounted ? "opacity-0" : ""}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Learning Streak
              </CardTitle>
              <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  className="h-4 w-4 text-primary"
                >
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                </svg>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-semibold tracking-tight">7 days</div>
              <p className="text-xs text-muted-foreground mt-1">
                Keep it up!
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <div className="grid gap-6 md:grid-cols-2">
          <Card className={`border-0 shadow-sm hover-lift animate-fade-in-up animate-delay-300 ${!mounted ? "opacity-0" : ""}`}>
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold">Recent Assessments</CardTitle>
              <CardDescription className="text-xs">
                Your latest skill assessments
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-5">
                <div className="flex items-center justify-between py-2 border-b last:border-0">
                  <div className="space-y-0.5">
                    <p className="text-sm font-medium">JavaScript Fundamentals</p>
                    <p className="text-xs text-muted-foreground">2 days ago</p>
                  </div>
                  <div className="text-sm font-semibold text-primary">85%</div>
                </div>
                <div className="flex items-center justify-between py-2 border-b last:border-0">
                  <div className="space-y-0.5">
                    <p className="text-sm font-medium">React Advanced</p>
                    <p className="text-xs text-muted-foreground">5 days ago</p>
                  </div>
                  <div className="text-sm font-semibold text-primary">92%</div>
                </div>
                <div className="flex items-center justify-between py-2">
                  <div className="space-y-0.5">
                    <p className="text-sm font-medium">TypeScript Basics</p>
                    <p className="text-xs text-muted-foreground">1 week ago</p>
                  </div>
                  <div className="text-sm font-semibold text-primary">78%</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className={`border-0 shadow-sm hover-lift animate-fade-in-up animate-delay-400 ${!mounted ? "opacity-0" : ""}`}>
            <CardHeader className="pb-4">
              <CardTitle className="text-base font-semibold">Top Skills</CardTitle>
              <CardDescription className="text-xs">
                Your strongest skill areas
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-5">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">React</span>
                    <span className="text-muted-foreground">95%</span>
                  </div>
                  <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                    <div className="h-full bg-primary rounded-full transition-all" style={{ width: "95%" }} />
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">JavaScript</span>
                    <span className="text-muted-foreground">88%</span>
                  </div>
                  <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                    <div className="h-full bg-primary rounded-full transition-all" style={{ width: "88%" }} />
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">TypeScript</span>
                    <span className="text-muted-foreground">82%</span>
                  </div>
                  <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                    <div className="h-full bg-primary rounded-full transition-all" style={{ width: "82%" }} />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card className={`border-0 shadow-sm hover-lift animate-fade-in-up animate-delay-500 ${!mounted ? "opacity-0" : ""}`}>
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold">Quick Actions</CardTitle>
            <CardDescription className="text-xs">
              Get started with these actions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Button size="sm" className="bg-primary hover:bg-primary/90 text-white">
                Start New Assessment
              </Button>
              <Button size="sm" variant="outline">
                View All Skills
              </Button>
              <Button size="sm" variant="outline">
                View Progress Report
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

