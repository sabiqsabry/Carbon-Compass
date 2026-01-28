import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Search, FileText } from 'lucide-react'
import { api } from '../services/api'
import { ReportCard } from '../components/ReportCard'

type Report = {
  filename: string
  size_bytes?: number
}

type SortBy = 'name-asc' | 'name-desc' | 'recent'

export function ReportsPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<SortBy>('name-asc')

  const { data: reports = [], isLoading } = useQuery<Report[]>({
    queryKey: ['reports'],
    queryFn: async () => {
      const res = await api.get('/reports')
      return res.data ?? []
    },
  })

  const filteredReports = reports
    .filter((report) => report.filename.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) => {
      if (sortBy === 'name-asc') return a.filename.localeCompare(b.filename)
      if (sortBy === 'name-desc') return b.filename.localeCompare(a.filename)
      return 0 // recent - would need analysis date, keeping simple for now
    })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-slate-400">Loading reports...</div>
      </div>
    )
  }

  return (
    <section className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-50">Reports</h1>
          <p className="text-sm text-slate-400 mt-1">
            {reports.length} {reports.length === 1 ? 'report' : 'reports'} available
          </p>
        </div>
      </header>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search reports..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-700 bg-slate-900/60 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
          />
        </div>
        <select
          value={sortBy}
          onChange={(e) => {
            const value = e.target.value
            if (value === 'name-asc' || value === 'name-desc' || value === 'recent') {
              setSortBy(value)
            }
          }}
          className="px-4 py-2 rounded-lg border border-slate-700 bg-slate-900/60 text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
        >
          <option value="name-asc">Name A-Z</option>
          <option value="name-desc">Name Z-A</option>
          <option value="recent">Recently Added</option>
        </select>
      </div>

      {filteredReports.length === 0 ? (
        <div className="text-center py-12 rounded-xl border border-slate-800 bg-slate-900/60">
          <FileText className="h-12 w-12 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400 mb-2">
            {searchQuery ? 'No reports match your search.' : 'No reports yet.'}
          </p>
          <p className="text-sm text-slate-500">
            {searchQuery ? (
              'Try a different search term.'
            ) : (
              <>
                Upload your first sustainability report{' '}
                <button
                  onClick={() => navigate('/upload')}
                  className="text-emerald-400 hover:text-emerald-300 underline"
                >
                  here
                </button>
                .
              </>
            )}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredReports.map((report) => (
            <ReportCard key={report.filename} report={report} />
          ))}
        </div>
      )}
    </section>
  )
}
