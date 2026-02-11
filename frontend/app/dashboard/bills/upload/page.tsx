'use client'

import { useState, useCallback } from 'react'
import { Upload, FileText, CheckCircle, AlertCircle, Loader } from 'lucide-react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api'

type BillType = 'electricity' | 'water' | 'gas' | 'fuel' | 'waste' | ''

export default function UploadBillPage() {
  const router = useRouter()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [billType, setBillType] = useState<BillType>('')
  const [uploading, setUploading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const [uploadResult, setUploadResult] = useState<any>(null)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0])
      setError(null)
      setSuccess(false)
    }
  }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
      setError(null)
      setSuccess(false)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload')
      return
    }

    setUploading(true)
    setError(null)
    setSuccess(false)

    try {
      const result = await apiClient.uploadBill(selectedFile, billType || undefined)
      setSuccess(true)
      setUploadResult(result)
      setSelectedFile(null)
      setBillType('')

      // Redirect to bills list after 3 seconds
      setTimeout(() => {
        router.push('/dashboard/bills')
      }, 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Upload Bill</h1>
        <p className="mt-2 text-gray-600">
          Upload your utility bills for AI-powered processing and carbon footprint calculation
        </p>
      </div>

      <div className="max-w-3xl">
        {/* Bill Type Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Bill Type (Optional - AI will auto-detect)
          </label>
          <select
            value={billType}
            onChange={(e) => setBillType(e.target.value as BillType)}
            className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">Auto-detect</option>
            <option value="electricity">Electricity</option>
            <option value="water">Water</option>
            <option value="gas">Gas</option>
            <option value="fuel">Fuel</option>
            <option value="waste">Waste</option>
          </select>
        </div>

        {/* File Upload Area */}
        <div
          className={`relative rounded-lg border-2 border-dashed p-12 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 bg-white hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={handleFileChange}
          />

          {!selectedFile ? (
            <div className="space-y-4">
              <div className="flex justify-center">
                <Upload className="h-12 w-12 text-gray-400" />
              </div>
              <div>
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer text-blue-600 hover:text-blue-700 font-medium"
                >
                  Click to upload
                </label>
                <span className="text-gray-600"> or drag and drop</span>
              </div>
              <p className="text-sm text-gray-500">PDF, PNG, JPG up to 10MB</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex justify-center">
                <FileText className="h-12 w-12 text-blue-600" />
              </div>
              <div>
                <p className="font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <button
                onClick={() => setSelectedFile(null)}
                className="text-sm text-red-600 hover:text-red-700"
              >
                Remove
              </button>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-4 rounded-lg bg-red-50 border border-red-200 p-4 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-red-800">{error}</div>
          </div>
        )}

        {/* Success Message */}
        {success && uploadResult && (
          <div className="mt-4 rounded-lg bg-green-50 border border-green-200 p-6">
            <div className="flex items-start gap-3 mb-4">
              <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-lg font-semibold text-green-900 mb-1">
                  Bill uploaded and processed successfully!
                </h3>
                <p className="text-sm text-green-800">
                  Redirecting to bills list in 3 seconds...
                </p>
              </div>
            </div>
            {uploadResult.data && (
              <div className="ml-9 space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-green-700">Status:</span>
                  <span className="font-medium text-green-900">{uploadResult.data.status}</span>
                </div>
                {uploadResult.data.extracted_data && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-green-700">Provider:</span>
                      <span className="font-medium text-green-900">
                        {uploadResult.data.extracted_data.provider_name}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-green-700">Consumption:</span>
                      <span className="font-medium text-green-900">
                        {uploadResult.data.extracted_data.consumption_amount} {uploadResult.data.extracted_data.consumption_unit}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-green-700">Amount:</span>
                      <span className="font-medium text-green-900">
                        {uploadResult.data.extracted_data.currency} {uploadResult.data.extracted_data.total_amount}
                      </span>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        )}

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={!selectedFile || uploading}
          className="mt-6 w-full rounded-lg bg-blue-600 px-6 py-3 text-white font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {uploading ? (
            <>
              <Loader className="h-5 w-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Upload className="h-5 w-5" />
              Upload and Process
            </>
          )}
        </button>

        {/* Info Section */}
        <div className="mt-8 rounded-lg bg-blue-50 border border-blue-200 p-6">
          <h3 className="font-semibold text-blue-900 mb-2">How it works</h3>
          <ol className="space-y-2 text-sm text-blue-800">
            <li className="flex gap-2">
              <span className="font-semibold">1.</span>
              <span>Upload your bill (PDF, image, or scan)</span>
            </li>
            <li className="flex gap-2">
              <span className="font-semibold">2.</span>
              <span>AWS Textract extracts text using OCR</span>
            </li>
            <li className="flex gap-2">
              <span className="font-semibold">3.</span>
              <span>Claude AI identifies and structures the data</span>
            </li>
            <li className="flex gap-2">
              <span className="font-semibold">4.</span>
              <span>Review and confirm the extracted information</span>
            </li>
            <li className="flex gap-2">
              <span className="font-semibold">5.</span>
              <span>Carbon emissions are calculated automatically</span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  )
}
