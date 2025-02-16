import type React from "react"
import "./globals.css"
import { Inter } from "next/font/google"

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "Subject Monitoring System",
  description: "Monitor subject vitals and status",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <header className="bg-blue-600 text-white p-4">
          <h1 className="text-2xl font-bold">Subject Monitoring System</h1>
        </header>
        <main className="container mx-auto p-4">{children}</main>
      </body>
    </html>
  )
}



import './globals.css'