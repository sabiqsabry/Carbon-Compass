import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { CloudUpload, FileText, Loader2, XCircle } from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'

type UploadedReport = {
  filename: string
  size_bytes?: number
}

type UploadResponse = {
  file_id: string
  filename: string
}

type AnalyseResponse = {
  status: string
}

export function UploadZone() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const { data: recentReports } = useQuery<UploadedReport[]>({
    queryKey: ['reports'],
    queryFn: async () => {
      const res = await api.get('/reports')
      return res.data ?? []
    },
  })

  const uploadMutation = useMutation<UploadResponse, Error, File>({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const res = await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: () => {},
      })
      return res.data
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['reports'] })
    },
  })

  const analyseMutation = useMutation<AnalyseResponse, Error, string>({
    mutationFn: async (filename: string) => {
      const res = await api.post(`/analyse/${encodeURIComponent(filename)}`)
      return res.data
    },
    onSuccess: (_data, filename) => {
      navigate(`/reports/${encodeURIComponent(filename)}`)
    },
  })

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: 50 * 1024 * 1024,
    multiple: false,
    onDropRejected: (fileRejections) => {
      const first = fileRejections[0]
      if (!first) return
      if (first.errors.some((e) => e.code === 'file-too-large')) {
        setError('File is too large. Maximum size is 50MB.')
      } else {
        setError('Only PDF files are allowed.')
      }
    },
    onDrop: (acceptedFiles) => {
      setError(null)
      const file = acceptedFiles[0]
      if (!file) return
      setSelectedFile(file)
      uploadMutation.mutate(file)
    },
  })

  const hasSelection = Boolean(selectedFile)
  const isUploading = uploadMutation.isPending
  const isAnalysing = analyseMutation.isPending

  return (
    <div className="space-y-6">
      <div
        {...getRootProps()}
        className={[
          'relative flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-12 transition-colors',
          isDragActive ? 'border-emerald-400 bg-emerald-500/5' : 'border-slate-700 bg-slate-900/60 hover:border-emerald-500',
        ].join(' ')}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400">
            <CloudUpload className="h-7 w-7" />
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium text-slate-50">
              Drag &amp; drop your sustainability report here
            </p>
            <p className="text-xs text-slate-400">or click to browse a PDF (max 50MB)</p>
          </div>
          <p className="text-[11px] uppercase tracking-wide text-slate-500">
            ESG, sustainability, CSR, climate, or integrated reports
          </p>
        </div>
        {isUploading && (
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center rounded-2xl bg-slate-950/70">
            <div className="flex items-center gap-2 text-xs text-slate-200">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Uploading report…</span>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-md border border-red-700/60 bg-red-950/40 px-3 py-2 text-xs text-red-200">
          <XCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      {hasSelection && selectedFile && (
        <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-3 text-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400">
              <FileText className="h-4 w-4" />
            </div>
            <div>
              <p className="font-medium text-slate-100">{selectedFile.name}</p>
              <p className="text-xs text-slate-500">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={isUploading || isAnalysing}
              onClick={() => {
                if (!selectedFile) return
                analyseMutation.mutate(selectedFile.name)
              }}
              className="inline-flex items-center gap-2 rounded-full bg-emerald-500 px-4 py-2 text-xs font-semibold text-emerald-950 shadow-sm transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:bg-emerald-700/70"
            >
              {isAnalysing ? (
                <>
                  <Loader2 className="h-3 w-3 animate-spin" />
                  <span>Analysing…</span>
                </>
              ) : (
                <span>Analyse now</span>
              )}
            </button>
            <button
              type="button"
              disabled={isUploading || isAnalysing}
              onClick={() => {
                setSelectedFile(null)
                setError(null)
              }}
              className="rounded-full border border-slate-700 px-3 py-2 text-xs font-medium text-slate-200 hover:border-slate-500 disabled:cursor-not-allowed disabled:border-slate-800 disabled:text-slate-600"
            >
              Upload another
            </button>
          </div>
        </div>
      )}

      <section className="space-y-2">
        <h2 className="text-sm font-semibold text-slate-100">Recent reports</h2>
        <div className="space-y-2 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
          {recentReports && recentReports.length > 0 ? (
            <ul className="space-y-1 text-xs text-slate-300">
              {recentReports.slice(0, 5).map((report) => (
                <li key={report.filename} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-slate-800 text-[10px] font-semibold uppercase text-slate-200">
                      PDF
                    </span>
                    <span className="truncate">{report.filename}</span>
                  </div>
                  {typeof report.size_bytes === 'number' && (
                    <span className="text-[11px] text-slate-500">
                      {(report.size_bytes / (1024 * 1024)).toFixed(2)} MB
                    </span>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-slate-500">
              No uploads yet. Start by dragging a sustainability report into the drop zone above.
            </p>
          )}
        </div>
      </section>
    </div>
  )
}

