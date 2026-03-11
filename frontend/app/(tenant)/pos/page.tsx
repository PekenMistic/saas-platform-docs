'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api/client'

interface FlowSchema {
  business_type: string
  version: string
  flow_schema: {
    transaction_flow: Array<{
      key: string
      label: string
      component: string
    }>
  }
}

export default function POSPage() {
  const [schema, setSchema] = useState<FlowSchema | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiClient
      .get('/flow/schema/')
      .then(({ data }) => {
        setSchema(data)
        setLoading(false)
      })
      .catch(() => {
        setError('Failed to load POS schema. Please refresh.')
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading POS...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4 text-red-700">{error}</div>
    )
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Point of Sale</h1>
      {schema && (
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-500 mb-4">
            Business Type: <strong>{schema.business_type}</strong> ({schema.version})
          </p>
          <div className="space-y-2">
            {schema.flow_schema.transaction_flow.map((step, idx) => (
              <div key={step.key} className="flex items-center gap-3 p-3 rounded border border-gray-200">
                <span className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-xs font-bold">
                  {idx + 1}
                </span>
                <span className="text-sm font-medium text-gray-700">{step.label}</span>
                <span className="text-xs text-gray-400 ml-auto">{step.component}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
