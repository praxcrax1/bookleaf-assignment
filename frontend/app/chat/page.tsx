"use client"

import * as React from "react"
import { Navbar } from "@/components/navbar"
import { useToken } from "@/lib/use-token"
import { chatRequest, type ChatResponse } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

type Message = {
  role: "user" | "assistant"
  content: string
  tools?: string[]
}

export default function ChatPage() {
  const { token } = useToken()
  const [messages, setMessages] = React.useState<Message[]>([])
  const [input, setInput] = React.useState("I forgot my login credentials. what do i do?")
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  async function sendMessage() {
    if (!input.trim()) return
    setError(null)
    setLoading(true)

    setMessages((prev) => [...prev, { role: "user", content: input }])

    try {
      const res: ChatResponse = await chatRequest(input, token || undefined)
      const tools = res?.reasoning_steps?.map((s) => s?.tool).filter(Boolean) as string[] | undefined

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res?.answer || "(No answer provided.)",
          tools,
        },
      ])
      setInput("")
    } catch (err: any) {
      setError(err?.message || "Something went wrong sending your message.")
    } finally {
      setLoading(false)
    }
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    void sendMessage()
  }

  return (
    <main>
      <Navbar />
      <section className="mx-auto max-w-3xl px-4 py-8">
        <Card>
          <CardHeader className="flex items-center justify-between">
            <CardTitle className="text-balance">Support Chat</CardTitle>
            <span className="text-xs text-gray-600">{token ? "Authenticated" : "Guest"}</span>
          </CardHeader>
          <CardContent className="space-y-4">
            {error ? (
              <Alert variant="destructive">
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            ) : null}

            <div className="h-72 w-full overflow-y-auto rounded-md border bg-white p-4" role="log" aria-live="polite">
              {messages.length === 0 ? (
                <p className="text-sm text-gray-600">
                  Ask a question to get started. If provided by the backend, tools used will be listed with each
                  response.
                </p>
              ) : (
                <ul className="space-y-4">
                  {messages.map((m, idx) => (
                    <li key={idx} className="space-y-2">
                      <div className={m.role === "user" ? "font-medium text-gray-900" : "text-gray-800"}>
                        {m.role === "user" ? "You" : "Assistant"}
                      </div>
                      <div className="whitespace-pre-wrap rounded-md bg-gray-50 p-3 text-sm text-gray-800">
                        {m.content}
                      </div>
                      {m.role === "assistant" && m.tools && m.tools.length > 0 ? (
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-xs text-gray-600">Tools used:</span>
                          {Array.from(new Set(m.tools)).map((t, i) => (
                            <span
                              key={`${t}-${i}`}
                              className="rounded bg-green-600 px-2 py-0.5 text-xs font-medium text-white"
                            >
                              {t}
                            </span>
                          ))}
                        </div>
                      ) : null}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <form onSubmit={onSubmit} className="space-y-3">
              <label htmlFor="chat-input" className="sr-only">
                Your message
              </label>
              <Textarea
                id="chat-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
                className="min-h-20 focus-visible:ring-green-600"
                disabled={loading}
              />
              <div className="flex items-center justify-end">
                <Button type="submit" disabled={loading || !input.trim()} className="bg-green-600 hover:bg-green-700">
                  {loading ? "Sending..." : "Send"}
                </Button>
              </div>
              <p className="text-xs text-gray-600">
                We send {"{ query, verbose: true }"} to /chat. If a token exists, we include Authorization: Bearer.
              </p>
            </form>
          </CardContent>
        </Card>
      </section>
    </main>
  )
}
