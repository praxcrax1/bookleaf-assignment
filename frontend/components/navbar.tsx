"use client"

import Link from "next/link"
import { useToken } from "@/lib/use-token"
import { Button } from "@/components/ui/button"

export function Navbar() {
  const { token, clearToken } = useToken()

  return (
    <header className="w-full border-b bg-white">
      <nav className="mx-auto flex max-w-3xl items-center justify-between px-4 py-3">
        <Link href="/" className="font-semibold tracking-tight text-green-700">
          BookLeaf
        </Link>
        <div className="flex items-center gap-3">
          <Link href="/chat" className="text-sm text-gray-700 hover:text-green-700">
            Chat
          </Link>
          <Link href="/login" className="text-sm text-gray-700 hover:text-green-700">
            Login / Register
          </Link>
          {token ? (
            <Button onClick={clearToken} className="bg-red-600 hover:bg-red-700 text-white">
              Logout
            </Button>
          ) : null}
        </div>
      </nav>
    </header>
  )
}
