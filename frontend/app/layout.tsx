import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SaaS POS Platform',
  description: 'Enterprise Multi-Tenant Point-of-Sale Platform',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'SaaS POS',
  },
}

export const viewport: Viewport = {
  themeColor: '#1A237E',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body className="min-h-screen bg-gray-50 antialiased">{children}</body>
    </html>
  )
}
