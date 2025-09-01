import Link from "next/link"
import { Navbar } from "@/components/navbar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function Home() {
  return (
    <main>
      <Navbar />
      <section className="mx-auto max-w-3xl px-4 py-10">
        <Card>
          <CardHeader>
            <CardTitle className="text-balance">BookLeaf Publishing Frontend</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-start gap-3">
            <p className="text-gray-700">Minimal login/register and chat interface.</p>
            <div className="flex items-center gap-3">
              <Button asChild className="bg-green-600 hover:bg-green-700">
                <Link href="/login">Go to Login / Register</Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href="/chat">Open Chat</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </section>
    </main>
  )
}
