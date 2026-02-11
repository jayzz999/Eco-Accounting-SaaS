'use client'

import { useState } from 'react'
import { Coins, TrendingDown, Calculator, Award, Info } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function CarbonCreditsPage() {
  const [showCalculator, setShowCalculator] = useState(false)

  // Mock data
  const creditData = {
    totalEmissions: 1.08, // tonnes
    offsetPotential: 0.54, // tonnes (50% offset)
    estimatedCost: 13.5, // USD (assuming $25/tonne)
    creditsNeeded: 0.54
  }

  const offsetProjects = [
    {
      id: 1,
      name: 'UAE Solar Energy Project',
      type: 'Renewable Energy',
      location: 'Dubai, UAE',
      price: 25,
      available: 1000,
      certification: 'Gold Standard'
    },
    {
      id: 2,
      name: 'Mangrove Restoration',
      type: 'Nature-based',
      location: 'Abu Dhabi, UAE',
      price: 30,
      available: 500,
      certification: 'Verified Carbon Standard'
    },
    {
      id: 3,
      name: 'Wind Energy Farm',
      type: 'Renewable Energy',
      location: 'Oman',
      price: 22,
      available: 2000,
      certification: 'Gold Standard'
    }
  ]

  const monthlyData = [
    { month: 'Jun', emissions: 0, offset: 0 },
    { month: 'Jul', emissions: 0, offset: 0 },
    { month: 'Aug', emissions: 0, offset: 0 },
    { month: 'Sep', emissions: 0, offset: 0 },
    { month: 'Oct', emissions: 0, offset: 0 },
    { month: 'Nov', emissions: 1.08, offset: 0 }
  ]

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Carbon Credits</h1>
        <p className="mt-2 text-gray-600">Offset your carbon footprint with verified carbon credits</p>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <Coins className="h-8 w-8 text-green-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">{creditData.totalEmissions}t</p>
          <p className="text-sm text-gray-600 mt-1">Total Emissions</p>
        </div>

        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <TrendingDown className="h-8 w-8 text-blue-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">{creditData.offsetPotential}t</p>
          <p className="text-sm text-gray-600 mt-1">Offset Potential</p>
        </div>

        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <Calculator className="h-8 w-8 text-orange-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">{creditData.creditsNeeded}</p>
          <p className="text-sm text-gray-600 mt-1">Credits Needed</p>
        </div>

        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <Award className="h-8 w-8 text-purple-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">${creditData.estimatedCost}</p>
          <p className="text-sm text-gray-600 mt-1">Estimated Cost</p>
        </div>
      </div>

      {/* Emissions vs Offset Chart */}
      <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Emissions & Offset Trend</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={monthlyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="emissions" stroke="#EF4444" name="Emissions (tonnes)" />
            <Line type="monotone" dataKey="offset" stroke="#10B981" name="Offset (tonnes)" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Offset Projects */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Available Offset Projects</h2>
          <button
            onClick={() => setShowCalculator(true)}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-2 text-white font-semibold hover:bg-blue-700 transition-colors"
          >
            <Calculator className="h-5 w-5" />
            Calculate Offset
          </button>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {offsetProjects.map((project) => (
            <div
              key={project.id}
              className="rounded-lg bg-white border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100">
                  <Coins className="h-6 w-6 text-green-600" />
                </div>
                <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-blue-100 text-blue-800">
                  {project.certification}
                </span>
              </div>

              <h3 className="text-lg font-semibold text-gray-900 mb-2">{project.name}</h3>

              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <div className="flex justify-between">
                  <span>Type:</span>
                  <span className="font-medium text-gray-900">{project.type}</span>
                </div>
                <div className="flex justify-between">
                  <span>Location:</span>
                  <span className="font-medium text-gray-900">{project.location}</span>
                </div>
                <div className="flex justify-between">
                  <span>Price:</span>
                  <span className="font-medium text-gray-900">${project.price}/tonne</span>
                </div>
                <div className="flex justify-between">
                  <span>Available:</span>
                  <span className="font-medium text-gray-900">{project.available} tonnes</span>
                </div>
              </div>

              <button className="w-full rounded-lg bg-green-600 px-4 py-2 text-white font-medium hover:bg-green-700 transition-colors">
                Purchase Credits
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Info Box */}
      <div className="rounded-lg bg-green-50 border border-green-200 p-6">
        <div className="flex gap-4">
          <Info className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-green-900 mb-2">About Carbon Credits</h4>
            <p className="text-sm text-green-800 mb-3">
              Carbon credits represent one tonne of CO₂ equivalent that has been prevented from entering
              or removed from the atmosphere. By purchasing verified carbon credits, you can offset your
              organization's carbon footprint and support sustainable projects worldwide.
            </p>
            <p className="text-sm text-green-800">
              All projects listed are certified by internationally recognized standards (Gold Standard, VCS)
              ensuring transparency and real environmental impact.
            </p>
          </div>
        </div>
      </div>

      {/* Calculator Modal */}
      {showCalculator && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Carbon Offset Calculator</h2>

            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Total Emissions
                </label>
                <input
                  type="text"
                  value={`${creditData.totalEmissions} tonnes CO₂e`}
                  disabled
                  className="w-full rounded-lg border border-gray-300 px-4 py-2 bg-gray-50"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Offset Percentage
                </label>
                <select className="w-full rounded-lg border border-gray-300 px-4 py-2">
                  <option>50% - Carbon Neutral Goal</option>
                  <option>75% - High Impact</option>
                  <option>100% - Net Zero</option>
                </select>
              </div>

              <div className="rounded-lg bg-blue-50 p-4 border border-blue-200">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-blue-800">Credits Needed:</span>
                  <span className="font-semibold text-blue-900">{creditData.creditsNeeded} tonnes</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-blue-800">Estimated Cost:</span>
                  <span className="font-semibold text-blue-900">${creditData.estimatedCost} USD</span>
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowCalculator(false)}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-gray-700 font-medium hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  alert('Purchase flow coming soon!')
                  setShowCalculator(false)
                }}
                className="flex-1 rounded-lg bg-green-600 px-4 py-2 text-white font-medium hover:bg-green-700 transition-colors"
              >
                Proceed to Purchase
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
