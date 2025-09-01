"use client"

import { useEffect, useState } from "react"

const TOKEN_KEY = "access_token"

export function useToken() {
  const [token, setTokenState] = useState<string | null>(null)

  useEffect(() => {
    try {
      const t = localStorage.getItem(TOKEN_KEY)
      if (t) setTokenState(t)
    } catch {}
  }, [])

  const setToken = (value: string) => {
    setTokenState(value)
    try {
      localStorage.setItem(TOKEN_KEY, value)
    } catch {}
  }

  const clearToken = () => {
    setTokenState(null)
    try {
      localStorage.removeItem(TOKEN_KEY)
    } catch {}
  }

  return { token, setToken, clearToken }
}
