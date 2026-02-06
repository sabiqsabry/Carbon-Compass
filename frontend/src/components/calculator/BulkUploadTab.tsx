import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileSpreadsheet, Loader2, AlertCircle } from 'lucide-react'
import { api } from '../../services/api'

type BulkUploadTabProps = {
  onResults: (data: Record<string, unknown>) => void
}

export function BulkUploadTab({ onResults }: BulkUploadTabProps) {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [parseInfo, setParseInfo] = useState<{ valid_rows: number; total_rows: number; invalid_rows: number } | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0])
      setError(null)
      setParseInfo(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  })

  const handleCalculate = async () => {
    if (!file) return
    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await api.post('/calculate/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setParseInfo(res.data.parsing)
      onResults(res.data)
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string | { message?: string } } } }
      const detail = axiosErr?.response?.data?.detail
      setError(typeof detail === 'string' ? detail : (detail as { message?: string })?.message || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const downloadTemplate = () => {
    const csv = `Category,Sub-category,Amount,Unit,Country
Electricity,Grid,50000,kWh,Sri Lanka
Fuel,Diesel,5000,litres,
Transport,Medium Petrol Car,25000,km,
Flight,Short-Haul International,10,trips,
Waste,Landfill (Mixed),50,tonnes,
Water,Supply + Treatment,1000,cubic metres,`
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'carbon_compass_template.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-5">
      <div className="flex items-start justify-between">
        <h2 className="text-lg font-semibold text-slate-50">Upload Activity Data</h2>
        <button
          onClick={downloadTemplate}
          className="text-xs text-emerald-400 hover:text-emerald-300 transition-colors"
        >
          Download template CSV
        </button>
      </div>

      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={[
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          isDragActive
            ? 'border-emerald-500 bg-emerald-500/5'
            : file
              ? 'border-emerald-500/30 bg-emerald-500/5'
              : 'border-slate-700 hover:border-slate-600',
        ].join(' ')}
      >
        <input {...getInputProps()} />
        {file ? (
          <div className="flex flex-col items-center gap-2">
            <FileSpreadsheet className="h-10 w-10 text-emerald-400" />
            <p className="text-sm font-medium text-slate-200">{file.name}</p>
            <p className="text-xs text-slate-400">{(file.size / 1024).toFixed(1)} KB</p>
            <p className="text-xs text-emerald-400">Click or drop to replace</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload className="h-10 w-10 text-slate-500" />
            <p className="text-sm text-slate-300">
              {isDragActive ? 'Drop your file here' : 'Drag & drop CSV or Excel file'}
            </p>
            <p className="text-xs text-slate-500">Supports .csv, .xlsx, .xls (max 10MB)</p>
          </div>
        )}
      </div>

      {/* Calculate Button */}
      {file && (
        <button
          onClick={handleCalculate}
          disabled={loading}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-500 transition-colors disabled:opacity-60"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <FileSpreadsheet className="h-4 w-4" />
          )}
          {loading ? 'Processing...' : 'Calculate from File'}
        </button>
      )}

      {/* Parse Info */}
      {parseInfo && (
        <div className="rounded-lg bg-slate-800/50 border border-slate-700 p-4 text-sm">
          <p className="text-slate-300">
            Processed <span className="text-emerald-400 font-medium">{parseInfo.valid_rows}</span> of {parseInfo.total_rows} rows
            {parseInfo.invalid_rows > 0 && (
              <span className="text-amber-400"> ({parseInfo.invalid_rows} skipped)</span>
            )}
          </p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 rounded-lg bg-red-500/10 border border-red-500/20 p-4">
          <AlertCircle className="h-4 w-4 text-red-400 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-red-300">{error}</p>
        </div>
      )}
    </div>
  )
}
