"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { loginRequest } from "@/lib/api"
import { useToken } from "@/lib/use-token"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export function LoginForm() {
  const router = useRouter()
  const { setToken } = useToken()
  const [email, setEmail] = React.useState("alice@example.com")
  const [password, setPassword] = React.useState("password123")
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [success, setSuccess] = React.useState<string | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)
    try {
      const data = await loginRequest(email, password)
      setToken(data.access_token)
      setSuccess("Logged in successfully.")
      setTimeout(() => router.push("/chat"), 500)
    } catch (err: any) {
      setError(err?.message || "Login failed.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      {error ? (
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}
      {success ? (
        <Alert>
          <AlertTitle>Success</AlertTitle>
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      ) : null}

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="alice@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="focus-visible:ring-green-600"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <Input
          id="password"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="focus-visible:ring-green-600"
        />
      </div>

      <Button type="submit" disabled={loading} className="w-full bg-green-600 hover:bg-green-700">
        {loading ? "Logging in..." : "Login"}
      </Button>

      <p className="text-xs text-gray-600">We store your access token locally for future API calls.</p>
    </form>
  )
}
