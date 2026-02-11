'use client'

import { useState, useEffect } from 'react'
import { FileText, CheckCircle, Clock, AlertCircle, Download } from 'lucide-react'
import Link from 'next/link'
import { apiClient, Bill } from '@/lib/api'

export default function BillsPage() {
  const [selectedType, setSelectedType] = useState<string>('all')
  const [bills, setBills] = useState<Bill[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchBills()
  }, [])

  const fetchBills = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.listBills()
      setBills(data)
    } catch (err) {
      setError('Failed to load bills. Please try again.')
      console.error('Error fetching bills:', err)
    } finally {
      setLoading(false)
    }
  }

  const filteredBills = selectedType === 'all'
    ? bills
    : bills.filter(bill => bill.bill_type === selectedType)

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'validated':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'processing':
        return <Clock className="h-5 w-5 text-yellow-600" />
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-600" />
      default:
        return <FileText className="h-5 w-5 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'validated':
        return 'bg-green-100 text-green-800'
      case 'processing':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getBillTypeColor = (type: string) => {
    switch (type) {
      case 'electricity':
        return 'bg-yellow-100 text-yellow-800'
      case 'water':
        return 'bg-blue-100 text-blue-800'
      case 'gas':
        return 'bg-orange-100 text-orange-800'
      case 'fuel':
        return 'bg-red-100 text-red-800'
      case 'waste':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Bills</h1>
          <p className="mt-2 text-gray-600">Manage and review your uploaded utility bills</p>
        </div>
        <Link
          href="/dashboard/bills/upload"
          className="rounded-lg bg-blue-600 px-6 py-3 text-white font-semibold hover:bg-blue-700 transition-colors"
        >
          Upload New Bill
        </Link>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <p className="text-red-800">{error}</p>
          </div>
          <button
            onClick={fetchBills}
            className="mt-2 text-sm text-red-600 hover:text-red-700 underline"
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <Clock className="mx-auto h-12 w-12 text-gray-400 animate-spin" />
            <p className="mt-4 text-gray-600">Loading bills...</p>
          </div>
        </div>
      )}

      {/* Filters */}
      {!loading && (
      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setSelectedType('all')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            selectedType === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All Bills
        </button>
        <button
          onClick={() => setSelectedType('electricity')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            selectedType === 'electricity'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Electricity
        </button>
        <button
          onClick={() => setSelectedType('water')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            selectedType === 'water'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Water
        </button>
        <button
          onClick={() => setSelectedType('gas')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            selectedType === 'gas'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Gas
        </button>
      </div>
      )}

      {/* Bills Grid */}
      {!loading && (
      <div className="grid gap-4">
        {filteredBills.map((bill) => (
          <div
            key={bill.id}
            className="rounded-lg bg-white border border-gray-200 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4 flex-1">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
                  <FileText className="h-6 w-6 text-blue-600" />
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {bill.file_name}
                    </h3>
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getBillTypeColor(bill.bill_type)}`}>
                      {bill.bill_type}
                    </span>
                    <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusColor(bill.status)}`}>
                      {getStatusIcon(bill.status)}
                      {bill.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                    <div>
                      <span className="font-medium">Uploaded:</span>{' '}
                      {new Date(bill.created_at).toLocaleDateString()}
                    </div>
                    {bill.ocr_confidence && (
                      <div>
                        <span className="font-medium">OCR Confidence:</span>{' '}
                        {(bill.ocr_confidence * 100).toFixed(0)}%
                      </div>
                    )}
                  </div>

                  {bill.extracted_data && (
                    <div className="mt-3 rounded-lg bg-gray-50 p-3">
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <div className="font-medium text-gray-700">Consumption</div>
                          <div className="mt-1 text-gray-900">
                            {bill.extracted_data.consumption_amount} {bill.extracted_data.consumption_unit}
                          </div>
                        </div>
                        <div>
                          <div className="font-medium text-gray-700">Provider</div>
                          <div className="mt-1 text-gray-900">
                            {bill.extracted_data.provider_name}
                          </div>
                        </div>
                        <div>
                          <div className="font-medium text-gray-700">Amount</div>
                          <div className="mt-1 text-gray-900">
                            AED {bill.extracted_data.total_amount}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => apiClient.downloadBill(bill.id, bill.file_name)}
                  className="rounded-lg p-2 text-gray-600 hover:bg-gray-100 transition-colors"
                  title="Download bill"
                >
                  <Download className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
      )}

      {!loading && filteredBills.length === 0 && (
        <div className="rounded-lg bg-gray-50 border border-gray-200 p-12 text-center">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No bills found</h3>
          <p className="mt-2 text-gray-600">
            Upload your first bill to get started with carbon tracking
          </p>
          <Link
            href="/dashboard/bills/upload"
            className="mt-6 inline-block rounded-lg bg-blue-600 px-6 py-2 text-white font-semibold hover:bg-blue-700 transition-colors"
          >
            Upload Bill
          </Link>
        </div>
      )}
    </div>
  )
}
