export const TOKEN_KEY = "blp_token"

export function getToken(): string | null {
  if (typeof window === "undefined") return null
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function setToken(token: string) {
  if (typeof window === "undefined") return
  try {
    localStorage.setItem(TOKEN_KEY, token)
  } catch {}
}

export function clearToken() {
  if (typeof window === "undefined") return
  try {
    localStorage.removeItem(TOKEN_KEY)
  } catch {}
}
