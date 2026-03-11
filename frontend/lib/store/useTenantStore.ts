import { create } from 'zustand'
import { apiClient } from '@/lib/api/client'

interface TenantBranding {
  primary_color?: string
  logo_url?: string
  app_name?: string
}

interface TenantSettings {
  branding?: TenantBranding
  features?: Record<string, boolean>
  regional?: {
    timezone?: string
    currency?: string
    locale?: string
  }
}

interface TenantInfo {
  id: string
  name: string
  slug: string
  business_type_code: string
  plan_tier: string
  status: string
  settings: TenantSettings
}

interface TenantState {
  tenant: TenantInfo | null
  isLoading: boolean
  error: string | null

  fetchCurrentTenant: () => Promise<void>
  getAppName: () => string
  getPrimaryColor: () => string
}

export const useTenantStore = create<TenantState>((set, get) => ({
  tenant: null,
  isLoading: false,
  error: null,

  fetchCurrentTenant: async () => {
    set({ isLoading: true, error: null })
    try {
      const { data } = await apiClient.get('/tenants/current/')
      set({ tenant: data, isLoading: false })
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Failed to load tenant info.'
      set({ error: message, isLoading: false })
    }
  },

  getAppName: () => {
    const tenant = get().tenant
    return tenant?.settings?.branding?.app_name || tenant?.name || 'SaaS POS'
  },

  getPrimaryColor: () => {
    const tenant = get().tenant
    return tenant?.settings?.branding?.primary_color || '#1A237E'
  },
}))
