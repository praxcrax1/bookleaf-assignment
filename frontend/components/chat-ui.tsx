"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { getToken, clearToken } from "@/lib/auth-client"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert"
import ReactMarkdown from "react-markdown"

const API_BASE = "http://localhost:8000"

type ChatResponse = {
  answer?: string
  user_id?: string
  query?: string
  reasoning_steps?: { tool?: string; input?: any; output?: any }[]
  success?: boolean
  error?: string
  detail?: string
}

type Message =
  | { id: string; role: "user"; content: string }
  | { id: string; role: "assistant"; content: string; tools?: string[] }

export default function ChatUI() {
  const router = useRouter()
  const [token, setTokenState] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const t = getToken()
    if (!t) {
      router.push("/")
      return
    }
    setTokenState(t)
  }, [router])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, sending])

  const sendMessage = async () => {
    if (!input.trim() || !token) return
    setError(null)
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: input.trim() }
    setMessages((m) => [...m, userMsg])
    setInput("")
    setSending(true)

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ query: userMsg.content, verbose: true }),
      })

      const data: ChatResponse = await res.json().catch(() => ({ error: "Invalid JSON from server" }))
      if (res.status === 401) {
        setError("Your session has expired. Please log in again.")
        clearToken()
        router.push("/")
        return
      }
      if (!res.ok) {
        const detail = data?.detail || data?.error || `Request failed with status ${res.status}`
        setError(detail)
      } else {
        const tools = Array.from(new Set((data?.reasoning_steps || []).map((s) => s?.tool).filter(Boolean) as string[]))
        const assistantMsg: Message = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: data?.answer || "(no answer returned)",
          tools,
        }
        setMessages((m) => [...m, assistantMsg])
      }
    } catch (e: any) {
      setError(e?.message || "Network error")
    } finally {
      setSending(false)
    }
  }

  const onLogout = () => {
    clearToken()
    router.push("/")
  }

  const headerSubtitle = useMemo(
    () => "Ask publishing questions. Answers render in Markdown. Tools used are shown when available.",
    [],
  )

  return (
    <div className="w-full max-w-2xl mx-auto">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4">
          <div>
            <CardTitle className="text-balance">Book Leaf Assistant</CardTitle>
            <CardDescription className="text-pretty">{headerSubtitle}</CardDescription>
          </div>
          <Button variant="outline" onClick={onLogout}>
            Logout
          </Button>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex flex-col gap-4 max-h-[60vh] overflow-y-auto pr-2">
            {messages.length === 0 && (
              <div className="text-sm text-muted-foreground">
                Start by asking: “I forgot my login credentials. what do I do?”
              </div>
            )}
            {messages.map((m) =>
              m.role === "user" ? (
                <div
                  key={m.id}
                  className="self-end max-w-[85%] rounded-md px-3 py-2 bg-primary text-primary-foreground"
                >
                  <p className="text-pretty">{m.content}</p>
                </div>
              ) : (
                <div key={m.id} className="self-start max-w-[85%] rounded-md px-3 py-2 bg-muted">
                  <div className="prose prose-sm dark:prose-invert">
                    <ReactMarkdown>{m.content}</ReactMarkdown>
                  </div>
                  {m.tools && m.tools.length > 0 && (
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <span className="text-xs text-muted-foreground">Tools used:</span>
                      {m.tools.map((t) => (
                        <Badge key={t} variant="secondary" className="text-xs">
                          {t}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              ),
            )}
            <div ref={bottomRef} />
          </div>

          <div className="mt-4 flex items-end gap-2">
            <Textarea
              placeholder="Type your question…"
              className="min-h-[72px]"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                  e.preventDefault()
                  sendMessage()
                }
              }}
              disabled={!token || sending}
            />
            <Button onClick={sendMessage} disabled={!token || sending || !input.trim()}>
              {sending ? "Sending…" : "Send"}
            </Button>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Tip: Press Cmd/Ctrl+Enter to send. Requires a valid session token.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
