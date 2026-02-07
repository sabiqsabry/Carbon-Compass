import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileSpreadsheet, Loader2, Download } from 'lucide-react'
import { api } from '../../services/api'

type FilePreview = {
  columns: string[]
  rows: Record<string, unknown>[]
  total_columns: number
  detected_mapping: Record<string, string | null>
}

type FileUploaderProps = {
  onFileUploaded: (file: File, preview: FilePreview) => void
}

export function FileUploader({ onFileUploaded }: FileUploaderProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return
    const file = acceptedFiles[0]
    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await api.post('/calculate/upload/preview', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      onFileUploaded(file, res.data)
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      setError(axiosErr?.response?.data?.detail || 'Failed to preview file')
    } finally {
      setLoading(false)
    }
  }, [onFileUploaded])

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
        <h2 className="text-lg font-semibold text-slate-50">Step 1: Upload File</h2>
        <button
          onClick={downloadTemplate}
          className="flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 transition-colors"
        >
          <Download className="h-3.5 w-3.5" />
          Download Template
        </button>
      </div>

      <div
        {...getRootProps()}
        className={[
          'border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors',
          isDragActive
            ? 'border-emerald-500 bg-emerald-500/5'
            : 'border-slate-700 hover:border-slate-600',
        ].join(' ')}
      >
        <input {...getInputProps()} />
        {loading ? (
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-12 w-12 text-emerald-400 animate-spin" />
            <p className="text-sm text-slate-300">Reading file...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            {isDragActive ? (
              <FileSpreadsheet className="h-12 w-12 text-emerald-400" />
            ) : (
              <Upload className="h-12 w-12 text-slate-500" />
            )}
            <div>
              <p className="text-sm font-medium text-slate-200">
                {isDragActive ? 'Drop your file here' : 'Drag & drop your CSV or Excel file'}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Supports .csv, .xlsx, .xls — Max 10MB
              </p>
            </div>
          </div>
        )}
      </div>

      {error && (
        <p className="text-sm text-red-400">{error}</p>
      )}
    </div>
  )
}
