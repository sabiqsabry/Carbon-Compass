import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { MoreVertical, Play } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { api } from '../services/api'

type Report = {
  filename: string
  size_bytes?: number
}

type ReportCardProps = {
  report: Report
}

export function ReportCard({ report }: ReportCardProps) {
  const navigate = useNavigate()
  const [showMenu, setShowMenu] = useState(false)

  const analyseMutation = useMutation({
    mutationFn: async (filename: string) => {
      const res = await api.post(`/analyse/${encodeURIComponent(filename)}`)
      return res.data
    },
    onSuccess: (_data, filename) => {
      navigate(`/reports/${encodeURIComponent(filename)}`)
    },
  })

  const formatFilename = (filename: string) => {
    return filename.replace(/\.pdf$/i, '').replace(/[_-]/g, ' ').trim()
  }

  const formatSize = (bytes?: number) => {
    if (!bytes) return 'Unknown size'
    const mb = bytes / (1024 * 1024)
    return `${mb.toFixed(2)} MB`
  }

  const getInitials = (filename: string) => {
    const name = formatFilename(filename)
    const words = name.split(' ')
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase()
    }
    return name.substring(0, 2).toUpperCase()
  }

  return (
    <div
      className="group relative rounded-xl border border-slate-800 bg-slate-900/60 p-4 hover:border-emerald-500/50 hover:bg-slate-900/80 transition-all cursor-pointer"
      onClick={() => navigate(`/reports/${encodeURIComponent(report.filename)}`)}
    >
      <div className="flex items-start gap-3">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400 font-semibold text-sm">
          {getInitials(report.filename)}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-slate-100 truncate">{formatFilename(report.filename)}</h3>
          <p className="text-xs text-slate-500 mt-1">{formatSize(report.size_bytes)}</p>
        </div>
        <div className="relative">
          <button
            onClick={(e) => {
              e.stopPropagation()
              setShowMenu(!showMenu)
            }}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200"
          >
            <MoreVertical className="h-4 w-4" />
          </button>
          {showMenu && (
            <div
              className="absolute right-0 top-8 z-10 w-48 rounded-lg border border-slate-700 bg-slate-900 shadow-lg py-1"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  analyseMutation.mutate(report.filename)
                  setShowMenu(false)
                }}
                className="w-full px-4 py-2 text-left text-sm text-slate-200 hover:bg-slate-800 flex items-center gap-2"
              >
                <Play className="h-4 w-4" />
                Analyse
              </button>
              <a
                href={`/api/v1/reports/${encodeURIComponent(report.filename)}`}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => {
                  e.stopPropagation()
                  setShowMenu(false)
                }}
                className="w-full px-4 py-2 text-left text-sm text-slate-200 hover:bg-slate-800 flex items-center gap-2"
              >
                Download PDF
              </a>
            </div>
          )}
        </div>
      </div>
      <div className="mt-3 flex gap-2">
        <button
          onClick={(e) => {
            e.stopPropagation()
            analyseMutation.mutate(report.filename)
          }}
          disabled={analyseMutation.isPending}
          className="flex-1 rounded-lg bg-emerald-500/10 px-3 py-1.5 text-xs font-medium text-emerald-400 hover:bg-emerald-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-1"
        >
          {analyseMutation.isPending ? (
            <>Processing...</>
          ) : (
            <>
              <Play className="h-3 w-3" />
              Analyse
            </>
          )}
        </button>
      </div>
    </div>
  )
}
