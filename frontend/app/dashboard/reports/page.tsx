'use client'

import { useState, useEffect } from 'react'
import { FileText, Download, Clock, CheckCircle, Plus, AlertCircle } from 'lucide-react'
import apiClient from '@/lib/api'

interface Report {
  id: number
  organization_id: number
  report_type: string
  title: string
  period_start: string
  period_end: string
  status: string
  file_path?: string
  created_at: string
}

export default function ReportsPage() {
  const [showGenerateModal, setShowGenerateModal] = useState(false)
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form state for report generation
  const [reportType, setReportType] = useState('GRI-305')
  const [periodStart, setPeriodStart] = useState('2024-05-01')
  const [periodEnd, setPeriodEnd] = useState('2024-06-30')

  useEffect(() => {
    fetchReports()
  }, [])

  const fetchReports = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.listReports()
      setReports(data)
    } catch (err) {
      console.error('Failed to load reports:', err)
      setError('Failed to load reports. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateReport = async () => {
    try {
      setGenerating(true)
      setError(null)

      const data = {
        report_type: reportType,
        period_start: `${periodStart}T00:00:00`,
        period_end: `${periodEnd}T23:59:59`,
        title: `${reportType.toUpperCase()} Report - ${periodStart} to ${periodEnd}`,
        description: `Auto-generated ${reportType.toUpperCase()} compliance report`,
      }

      await apiClient.generateReport(data)

      // Refresh reports list
      await fetchReports()

      // Close modal
      setShowGenerateModal(false)

      // Reset form
      setReportType('GRI-305')
      setPeriodStart('2024-05-01')
      setPeriodEnd('2024-06-30')

      alert('Report generated successfully!')
    } catch (err: any) {
      console.error('Failed to generate report:', err)
      setError(err.message || 'Failed to generate report. Please try again.')
      alert(`Error: ${err.message || 'Failed to generate report'}`)
    } finally {
      setGenerating(false)
    }
  }

  const handleDownloadReport = async (reportId: number, title: string) => {
    try {
      const blob = await apiClient.downloadReport(reportId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${title}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Failed to download report:', err)
      alert('Failed to download report. Please try again.')
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
          <p className="mt-2 text-gray-600">Generate and manage GRI compliance reports</p>
        </div>
        <button
          onClick={() => setShowGenerateModal(true)}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-white font-semibold hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-5 w-5" />
          Generate Report
        </button>
      </div>

      {error && (
        <div className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4 flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Report Types Grid */}
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">GRI 305</h3>
          <p className="mt-2 text-sm text-gray-600">Emissions reporting standard</p>
          <a
            href="https://www.globalreporting.org/standards/standards-development/topic-standard-project-for-ghg-emissions/"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-block text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Learn more →
          </a>
        </div>

        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">GRI 302</h3>
          <p className="mt-2 text-sm text-gray-600">Energy reporting standard</p>
          <a
            href="https://www.globalreporting.org/standards/"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-block text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Learn more →
          </a>
        </div>

        <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">CDP</h3>
          <p className="mt-2 text-sm text-gray-600">Carbon Disclosure Project</p>
          <a
            href="https://www.cdp.net/"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-block text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Learn more →
          </a>
        </div>
      </div>

      {/* Reports List */}
      <div className="rounded-lg bg-white shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Generated Reports</h3>
        </div>

        {loading ? (
          <div className="p-12 text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
            <p className="mt-4 text-gray-600">Loading reports...</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {reports.length > 0 ? (
              reports.map((report) => (
              <div key={report.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-start gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
                      <FileText className="h-6 w-6 text-blue-600" />
                    </div>

                    <div>
                      <h4 className="text-lg font-semibold text-gray-900">{report.title}</h4>
                      <div className="mt-1 flex items-center gap-4 text-sm text-gray-600">
                        <span>Type: {report.report_type.toUpperCase()}</span>
                        <span>•</span>
                        <span>Created: {new Date(report.created_at).toLocaleDateString()}</span>
                        <span>•</span>
                        <div className="flex items-center gap-1">
                          {report.status === 'completed' ? (
                            <>
                              <CheckCircle className="h-4 w-4 text-green-600" />
                              <span className="text-green-600">Completed</span>
                            </>
                          ) : report.status === 'processing' ? (
                            <>
                              <Clock className="h-4 w-4 text-yellow-600" />
                              <span className="text-yellow-600">Processing</span>
                            </>
                          ) : (
                            <>
                              <AlertCircle className="h-4 w-4 text-red-600" />
                              <span className="text-red-600">{report.status}</span>
                            </>
                          )}
                        </div>
                      </div>
                      <div className="mt-1 text-sm text-gray-500">
                        Period: {new Date(report.period_start).toLocaleDateString()} - {new Date(report.period_end).toLocaleDateString()}
                      </div>
                    </div>
                  </div>

                  {report.status === 'completed' && (
                    <button
                      onClick={() => handleDownloadReport(report.id, report.title)}
                      className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
                    >
                      <Download className="h-4 w-4" />
                      Download PDF
                    </button>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="p-12 text-center">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">No reports yet</h3>
              <p className="mt-2 text-gray-600">Generate your first report to get started</p>
              <button
                onClick={() => setShowGenerateModal(true)}
                className="mt-6 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-2 text-white font-semibold hover:bg-blue-700 transition-colors"
              >
                <Plus className="h-5 w-5" />
                Generate Report
              </button>
            </div>
          )}
        </div>
        )}
      </div>

      {/* Generate Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Generate Report</h2>
            <p className="text-gray-600 mb-6">
              Generate a GRI compliance report based on your emissions data.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Report Type
                </label>
                <select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-2"
                >
                  <option value="GRI-305">GRI 305 - Emissions</option>
                  <option value="GRI-302">GRI 302 - Energy</option>
                  <option value="CDP">CDP - Carbon Disclosure</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Period Start
                </label>
                <input
                  type="date"
                  value={periodStart}
                  onChange={(e) => setPeriodStart(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Period End
                </label>
                <input
                  type="date"
                  value={periodEnd}
                  onChange={(e) => setPeriodEnd(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-2"
                />
              </div>
            </div>

            <div className="mt-6 flex gap-3">
              <button
                onClick={() => setShowGenerateModal(false)}
                disabled={generating}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-gray-700 font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleGenerateReport}
                disabled={generating}
                className="flex-1 rounded-lg bg-blue-600 px-4 py-2 text-white font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generating ? 'Generating...' : 'Generate'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
