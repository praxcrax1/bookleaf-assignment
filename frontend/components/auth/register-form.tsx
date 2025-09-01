"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { API_BASE } from "@/lib/api"

export function RegisterForm() {
  const [email, setEmail] = React.useState("")
  const [password, setPassword] = React.useState("")
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [success, setSuccess] = React.useState<string | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)
    try {
      // If your API doesn't have /register, update the path or remove this form.
      const res = await fetch(`${API_BASE}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })
      if (!res.ok) {
        const text = await res.text().catch(() => "")
        throw new Error(`Register failed (${res.status}): ${text || res.statusText || "Unknown error"}`)
      }
      await res.json().catch(() => ({}))
      setSuccess("Registration successful. You can now log in.")
    } catch (err: any) {
      setError(err?.message || "Registration failed.")
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
        <Label htmlFor="reg-email">Email</Label>
        <Input
          id="reg-email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="focus-visible:ring-green-600"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="reg-password">Password</Label>
        <Input
          id="reg-password"
          type="password"
          placeholder="Choose a strong password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="focus-visible:ring-green-600"
        />
      </div>

      <Button type="submit" disabled={loading} className="w-full bg-green-600 hover:bg-green-700">
        {loading ? "Creating account..." : "Create account"}
      </Button>

      <p className="text-xs text-gray-600">
        If your backend uses a different signup endpoint, set NEXT_PUBLIC_API_BASE_URL or adjust this path.
      </p>
    </form>
  )
}
