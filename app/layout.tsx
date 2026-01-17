import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'FishVault - Secrets Manager',
  description: 'Identity-themed secrets manager'
}

export default function RootLayout({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

