import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '../services/api'
import { CompanySelector } from '../components/CompanySelector'
import { ComparisonTable } from '../components/ComparisonTable'
import { ComparisonCharts } from '../components/ComparisonCharts'

type Report = {
  filename: string
}

export function ComparePage(): JSX.Element {
  const [selectedReports, setSelectedReports] = useState<string[]>([])
  const [activeTab, setActiveTab] = useState<'table' | 'charts'>('table')

  const { data: reports = [] } = useQuery<Report[]>({
    queryKey: ['reports'],
    queryFn: async () => {
      const res = await api.get<Report[]>('/reports')
      return res.data ?? []
    },
  })

  const compareMutation = useMutation({
    mutationFn: async (filenames: string[]) => {
      const res = await api.post('/compare', { filenames })
      return res.data
    },
  })

  const handleCompare = () => {
    if (selectedReports.length >= 2) {
      compareMutation.mutate(selectedReports)
    }
  }

  return (
    <section className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-50">Compare Companies</h1>
        <p className="text-sm text-slate-400 mt-1">
          Select 2-4 reports to compare side-by-side
        </p>
      </header>

      <CompanySelector
        reports={reports.map((r) => r.filename)}
        selected={selectedReports}
        onChange={setSelectedReports}
        onCompare={handleCompare}
        isLoading={compareMutation.isPending}
      />

      {compareMutation.data && (
        <div className="space-y-4">
          <div className="flex gap-2 border-b border-slate-800">
            <button
              onClick={() => setActiveTab('table')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'table'
                  ? 'border-emerald-500 text-emerald-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Table View
            </button>
            <button
              onClick={() => setActiveTab('charts')}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'charts'
                  ? 'border-emerald-500 text-emerald-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Charts View
            </button>
          </div>

          {activeTab === 'table' ? (
            <ComparisonTable data={compareMutation.data} />
          ) : (
            <ComparisonCharts data={compareMutation.data} />
          )}
        </div>
      )}

      {compareMutation.isError && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4 text-red-300 text-sm">
          Failed to compare reports. Please try again.
        </div>
      )}
    </section>
  )
}
