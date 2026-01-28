import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Clock, ArrowRight } from 'lucide-react'
import { api } from '../services/api'

type Report = {
  filename: string
}

export function RecentAnalyses() {
  const { data: reports = [] } = useQuery<Report[]>({
    queryKey: ['reports'],
    queryFn: async () => {
      const res = await api.get<Report[]>('/reports')
      return res.data ?? []
    },
  })

  const recentReports = reports.slice(0, 5)

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-50">Recent Reports</h2>
        <Link
          to="/reports"
          className="text-sm text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
        >
          View All
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      <div className="space-y-2">
        {recentReports.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-8">No reports yet</p>
        ) : (
          recentReports.map((report) => (
            <Link
              key={report.filename}
              to={`/reports/${encodeURIComponent(report.filename)}`}
              className="flex items-center justify-between p-3 rounded-lg border border-slate-800 bg-slate-900/40 hover:bg-slate-900/60 transition-colors group"
            >
              <div className="flex items-center gap-3 min-w-0 flex-1">
                <div className="h-8 w-8 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-xs font-semibold shrink-0">
                  {report.filename.substring(0, 2).toUpperCase()}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-slate-200 truncate">
                    {report.filename.replace(/\.pdf$/i, '').replace(/[_-]/g, ' ')}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <Clock className="h-3 w-3 text-slate-500" />
                    <span className="text-xs text-slate-500">Ready to analyse</span>
                  </div>
                </div>
              </div>
              <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-emerald-400 transition-colors shrink-0" />
            </Link>
          ))
        )}
      </div>
    </div>
  )
}
