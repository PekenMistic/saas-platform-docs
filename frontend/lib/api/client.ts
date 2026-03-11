import axios, { AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function getTenantDomain(): string {
  if (typeof window === 'undefined') return ''
  return window.location.hostname
}

function getAccessToken(): string | null {
  if (typeof document === 'undefined') return null
  const match = document.cookie.match(/(?:^|;\s*)access_token=([^;]*)/)
  return match ? decodeURIComponent(match[1]) : null
}

function setTokenCookies(access: string, refresh: string) {
  const secure = window.location.protocol === 'https:' ? '; Secure' : ''
  document.cookie = `access_token=${encodeURIComponent(access)}; path=/; SameSite=Lax${secure}`
  document.cookie = `refresh_token=${encodeURIComponent(refresh)}; path=/; SameSite=Lax${secure}`
}

function clearTokenCookies() {
  document.cookie = 'access_token=; path=/; Max-Age=0'
  document.cookie = 'refresh_token=; path=/; Max-Age=0'
}

const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  const domain = getTenantDomain()
  if (domain) {
    config.headers['X-Tenant-Domain'] = domain
  }
  return config
})

let isRefreshing = false
let refreshQueue: Array<{ resolve: (token: string) => void; reject: (err: unknown) => void }> = []

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push({
            resolve: (token) => {
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`
              }
              resolve(apiClient(originalRequest))
            },
            reject,
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const refreshMatch = document.cookie.match(/(?:^|;\s*)refresh_token=([^;]*)/)
        const refreshToken = refreshMatch ? decodeURIComponent(refreshMatch[1]) : null

        if (!refreshToken) throw new Error('No refresh token')

        const { data } = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh/`, {
          refresh: refreshToken,
        })

        setTokenCookies(data.access, data.refresh || refreshToken)
        refreshQueue.forEach(({ resolve }) => resolve(data.access))
        refreshQueue = []

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${data.access}`
        }
        return apiClient(originalRequest)
      } catch (refreshError) {
        refreshQueue.forEach(({ reject }) => reject(refreshError))
        refreshQueue = []
        clearTokenCookies()
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export { apiClient, setTokenCookies, clearTokenCookies }
export default apiClient
