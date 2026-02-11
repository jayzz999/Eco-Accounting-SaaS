'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, FileText, Leaf, AlertCircle } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { formatEmissions, formatNumber } from '@/lib/utils'
import apiClient, { DashboardStats } from '@/lib/api'

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const data = await apiClient.getDashboardStats()
      // Transform emissions_by_month to match chart format
      const transformedData = {
        ...data,
        emissions_by_month: data.emissions_by_month.map((item: any) => ({
          month: item.month,
          value: item.emissions
        }))
      }
      setStats(transformedData)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-gray-600">Failed to load dashboard data</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Overview of your environmental impact</p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Emissions</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {formatNumber(stats.total_emissions / 1000, 1)}
              </p>
              <p className="text-sm text-gray-500">tonnes CO₂e</p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-red-100">
              <Leaf className="h-6 w-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">This Month</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {formatNumber(stats.current_month_emissions / 1000, 1)}
              </p>
              <div className="flex items-center mt-1">
                {stats.emissions_change > 0 ? (
                  <>
                    <TrendingUp className="h-4 w-4 text-red-600 mr-1" />
                    <span className="text-sm text-red-600">+{formatNumber(stats.emissions_change, 1)}%</span>
                  </>
                ) : (
                  <>
                    <TrendingDown className="h-4 w-4 text-green-600 mr-1" />
                    <span className="text-sm text-green-600">{formatNumber(stats.emissions_change, 1)}%</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Bills Processed</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{stats.total_bills}</p>
              <p className="text-sm text-gray-500">utility bills</p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Compliance Status</p>
              <p className="mt-2 text-2xl font-bold text-green-600 capitalize">
                {stats.compliance_status}
              </p>
              <p className="text-sm text-gray-500">All checks passed</p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100">
              <AlertCircle className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Emissions Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stats.emissions_by_month}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#2563eb"
                strokeWidth={2}
                name="CO₂e (kg)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Emissions by Month</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.emissions_by_month}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#10b981" name="CO₂e (kg)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 p-6 text-white">
        <h3 className="text-xl font-semibold mb-2">Ready to reduce your carbon footprint?</h3>
        <p className="mb-4">Upload your latest utility bills to track your progress</p>
        <a
          href="/dashboard/bills/upload"
          className="inline-block rounded-lg bg-white px-6 py-2 text-blue-600 font-semibold hover:bg-gray-100 transition-colors"
        >
          Upload Bill
        </a>
      </div>
    </div>
  )
}
