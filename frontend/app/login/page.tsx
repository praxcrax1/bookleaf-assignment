"use client"

import * as React from "react"
import { Navbar } from "@/components/navbar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { LoginForm } from "@/components/auth/login-form"
import { RegisterForm } from "@/components/auth/register-form"
import { Button } from "@/components/ui/button"

export default function LoginPage() {
  const [tab, setTab] = React.useState<"login" | "register">("login")

  return (
    <main>
      <Navbar />
      <section className="mx-auto max-w-md px-4 py-10">
        <Card>
          <CardHeader>
            <CardTitle className="text-balance">BookLeaf Publishing</CardTitle>
            <CardDescription className="text-pretty">Login or create a new account.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2">
              <Button
                type="button"
                onClick={() => setTab("login")}
                className={`h-8 ${tab === "login" ? "bg-green-600 hover:bg-green-700" : "bg-gray-200 text-gray-800 hover:bg-gray-300"}`}
              >
                Login
              </Button>
              <Button
                type="button"
                onClick={() => setTab("register")}
                className={`h-8 ${tab === "register" ? "bg-green-600 hover:bg-green-700" : "bg-gray-200 text-gray-800 hover:bg-gray-300"}`}
              >
                Register
              </Button>
            </div>
            {tab === "login" ? <LoginForm /> : <RegisterForm />}
          </CardContent>
        </Card>
      </section>
    </main>
  )
}
