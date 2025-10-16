import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Student Identification System',
  description: 'AI-Powered Student Identification using GFPGAN + AdaFace + FAISS',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
