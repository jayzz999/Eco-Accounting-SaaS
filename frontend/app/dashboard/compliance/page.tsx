'use client'

import { useState } from 'react'
import { Shield, CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react'

export default function CompliancePage() {
  const [selectedRegulation, setSelectedRegulation] = useState('all')

  // Mock compliance data
  const complianceStatus = {
    overall: 'compliant',
    totalRules: 12,
    compliant: 10,
    warnings: 2,
    nonCompliant: 0
  }

  const regulations = [
    {
      id: 1,
      name: 'GRI Standards',
      category: 'Reporting',
      status: 'compliant',
      lastChecked: '2024-11-26',
      description: 'Global Reporting Initiative standards for emissions reporting'
    },
    {
      id: 2,
      name: 'ISO 14064',
      category: 'Carbon Accounting',
      status: 'compliant',
      lastChecked: '2024-11-26',
      description: 'Greenhouse gas accounting and verification standard'
    },
    {
      id: 3,
      name: 'CDP Requirements',
      category: 'Disclosure',
      status: 'warning',
      lastChecked: '2024-11-20',
      description: 'Carbon Disclosure Project requirements - Scope 3 data incomplete'
    },
    {
      id: 4,
      name: 'UAE Carbon Regulations',
      category: 'Regional',
      status: 'compliant',
      lastChecked: '2024-11-26',
      description: 'UAE environmental and carbon emission regulations'
    },
    {
      id: 5,
      name: 'Paris Agreement Alignment',
      category: 'International',
      status: 'warning',
      lastChecked: '2024-11-15',
      description: 'Alignment with Paris Agreement targets - verification needed'
    }
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant':
        return <CheckCircle className="h-6 w-6 text-green-600" />
      case 'warning':
        return <AlertTriangle className="h-6 w-6 text-yellow-600" />
      case 'non-compliant':
        return <XCircle className="h-6 w-6 text-red-600" />
      default:
        return <Info className="h-6 w-6 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'non-compliant':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const filteredRegulations = selectedRegulation === 'all'
    ? regulations
    : regulations.filter(r => r.status === selectedRegulation)

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Compliance</h1>
        <p className="mt-2 text-gray-600">Monitor regulatory compliance and reporting requirements</p>
      </div>

      {/* Overview Cards */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <Shield className="h-8 w-8 text-blue-600" />
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(complianceStatus.overall)}`}>
              {complianceStatus.overall}
            </span>
          </div>
          <p className="text-sm text-gray-600">Overall Status</p>
        </div>

        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <p className="text-3xl font-bold text-green-600">{complianceStatus.compliant}</p>
          <p className="text-sm text-gray-600 mt-1">Compliant</p>
        </div>

        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <p className="text-3xl font-bold text-yellow-600">{complianceStatus.warnings}</p>
          <p className="text-sm text-gray-600 mt-1">Warnings</p>
        </div>

        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <p className="text-3xl font-bold text-red-600">{complianceStatus.nonCompliant}</p>
          <p className="text-sm text-gray-600 mt-1">Non-Compliant</p>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setSelectedRegulation('all')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            selectedRegulation === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All Regulations
        </button>
        <button
          onClick={() => setSelectedRegulation('compliant')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            selectedRegulation === 'compliant'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Compliant
        </button>
        <button
          onClick={() => setSelectedRegulation('warning')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            selectedRegulation === 'warning'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Warnings
        </button>
        <button
          onClick={() => setSelectedRegulation('non-compliant')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            selectedRegulation === 'non-compliant'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Non-Compliant
        </button>
      </div>

      {/* Regulations List */}
      <div className="grid gap-4">
        {filteredRegulations.map((regulation) => (
          <div
            key={regulation.id}
            className="rounded-lg bg-white border border-gray-200 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4 flex-1">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
                  {getStatusIcon(regulation.status)}
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{regulation.name}</h3>
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusColor(regulation.status)} border`}>
                      {regulation.status}
                    </span>
                    <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-gray-100 text-gray-700">
                      {regulation.category}
                    </span>
                  </div>

                  <p className="text-sm text-gray-600 mb-3">{regulation.description}</p>

                  <div className="text-sm text-gray-500">
                    Last checked: {new Date(regulation.lastChecked).toLocaleDateString()}
                  </div>
                </div>
              </div>

              <button className="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors">
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredRegulations.length === 0 && (
        <div className="rounded-lg bg-gray-50 border border-gray-200 p-12 text-center">
          <Shield className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No regulations found</h3>
          <p className="mt-2 text-gray-600">Try adjusting your filters</p>
        </div>
      )}

      {/* Info Box */}
      <div className="mt-8 rounded-lg bg-blue-50 border border-blue-200 p-6">
        <div className="flex gap-4">
          <Info className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-blue-900 mb-2">Compliance Monitoring</h4>
            <p className="text-sm text-blue-800">
              This platform automatically monitors your compliance status based on uploaded bills and calculated emissions.
              Compliance checks are updated in real-time as new data is processed. For detailed compliance reports and
              audit trails, use the Reports section to generate official GRI documentation.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
