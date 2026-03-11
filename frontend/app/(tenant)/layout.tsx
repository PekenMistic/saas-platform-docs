'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store/useAuthStore'
import { useTenantStore } from '@/lib/store/useTenantStore'

export default function TenantLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { isAuthenticated, user, fetchMe } = useAuthStore()
  const { tenant, fetchCurrentTenant, getAppName, getPrimaryColor } = useTenantStore()

  useEffect(() => {
    fetchCurrentTenant()
    if (!user) fetchMe()
  }, [])

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, router])

  const primaryColor = getPrimaryColor()
  const appName = getAppName()

  return (
    <div style={{ '--color-primary': primaryColor } as React.CSSProperties}>
      <header className="sticky top-0 z-50 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-sm">
        <span className="font-bold text-lg" style={{ color: primaryColor }}>
          {appName}
        </span>
        <nav className="flex items-center gap-4 text-sm">
          <a href="/pos" className="text-gray-600 hover:text-gray-900">POS</a>
          <a href="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</a>
          <a href="/products" className="text-gray-600 hover:text-gray-900">Produk</a>
          <span className="text-gray-400">{user?.full_name || user?.email}</span>
        </nav>
      </header>

      <main className="container mx-auto px-4 py-6">
        {children}
      </main>
    </div>
  )
}
