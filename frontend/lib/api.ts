export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"

export type LoginResponse = {
  access_token: string
  token_type: string
}

export async function loginRequest(email: string, password: string) {
  const res = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  })

  if (!res.ok) {
    const text = await res.text().catch(() => "")
    throw new Error(`Login failed (${res.status}): ${text || res.statusText || "Unknown error"}`)
  }

  const data = (await res.json()) as LoginResponse
  if (!data?.access_token) {
    throw new Error("Login response missing access_token.")
  }
  return data
}

export type ChatReasoningStep = {
  tool?: string
  input?: string
  output?: string
}

export type ChatResponse = {
  answer?: string
  user_id?: string
  query?: string
  reasoning_steps?: ChatReasoningStep[]
  success?: boolean
}

export async function chatRequest(query: string, token?: string) {
  const headers: Record<string, string> = { "Content-Type": "application/json" }
  if (token) headers["Authorization"] = `Bearer ${token}`

  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers,
    body: JSON.stringify({ query, verbose: true }),
  })

  if (!res.ok) {
    const text = await res.text().catch(() => "")
    throw new Error(`Chat failed (${res.status}): ${text || res.statusText || "Unknown error"}`)
  }

  const data = (await res.json()) as ChatResponse
  return data
}
