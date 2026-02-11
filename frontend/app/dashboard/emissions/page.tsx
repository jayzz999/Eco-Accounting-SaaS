'use client'

import { useState, useEffect } from 'react'
import { Leaf, TrendingUp, Calendar } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

export default function EmissionsPage() {
  const [emissions, setEmissions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchEmissions()
  }, [])

  const fetchEmissions = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/emissions`)
      if (response.ok) {
        const data = await response.json()
        setEmissions(data)
      }
    } catch (error) {
      console.error('Failed to fetch emissions:', error)
    } finally {
      setLoading(false)
    }
  }

  const totalEmissions = emissions.reduce((sum, e) => sum + e.total_co2e, 0)

  const byScope = emissions.reduce((acc, e) => {
    const scope = e.category || 'Other'
    acc[scope] = (acc[scope] || 0) + e.total_co2e
    return acc
  }, {} as Record<string, number>)

  const scopeData = Object.entries(byScope).map(([name, value]) => ({ name, value }))

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444']

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-gray-600">Loading emissions data...</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Carbon Emissions</h1>
        <p className="mt-2 text-gray-600">Track and analyze your carbon footprint</p>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Emissions</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {(totalEmissions / 1000).toFixed(2)}
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
              <p className="text-sm font-medium text-gray-600">Records</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{emissions.length}</p>
              <p className="text-sm text-gray-500">emission entries</p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
              <TrendingUp className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg per Bill</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {emissions.length > 0 ? (totalEmissions / emissions.length).toFixed(0) : 0}
              </p>
              <p className="text-sm text-gray-500">kg CO₂e</p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100">
              <Calendar className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid gap-6 md:grid-cols-2 mb-8">
        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Emissions by Scope</h3>
          {scopeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={scopeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${(entry.value / 1000).toFixed(1)}t`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {scopeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: any) => `${(value / 1000).toFixed(2)} tonnes`} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-12">No emission data available</p>
          )}
        </div>

        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Emissions</h3>
          <div className="space-y-3">
            {emissions.slice(0, 5).map((emission) => (
              <div key={emission.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">
                    {emission.consumption_amount} {emission.consumption_unit}
                  </p>
                  <p className="text-sm text-gray-600">{emission.category}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">{(emission.total_co2e / 1000).toFixed(2)}t</p>
                  <p className="text-sm text-gray-500">CO₂e</p>
                </div>
              </div>
            ))}
            {emissions.length === 0 && (
              <p className="text-gray-500 text-center py-8">No emissions recorded yet. Upload bills to start tracking.</p>
            )}
          </div>
        </div>
      </div>

      {/* Emissions Table */}
      <div className="rounded-lg bg-white shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">All Emissions</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Source
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Scope
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Consumption
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Emission Factor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total CO₂e
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {emissions.map((emission) => (
                <tr key={emission.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {emission.source_type || 'Unknown'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {emission.category}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {emission.consumption_amount} {emission.consumption_unit}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {emission.emission_factor.toFixed(3)} kg/unit
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {(emission.total_co2e / 1000).toFixed(3)} tonnes
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {emissions.length === 0 && (
            <div className="text-center py-12">
              <Leaf className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-4 text-gray-500">No emissions data available</p>
              <p className="text-sm text-gray-400">Upload bills to start tracking your carbon footprint</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
