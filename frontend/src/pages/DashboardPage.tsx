import { useQuery } from '@tanstack/react-query'
import { FileText, BarChart3, AlertTriangle, TrendingUp } from 'lucide-react'
import { api } from '../services/api'
import { StatCard } from '../components/StatCard'
import { RecentAnalyses } from '../components/RecentAnalyses'
import { QuickActions } from '../components/QuickActions'

export function DashboardPage(): JSX.Element {
  const { data: reports = [] } = useQuery({
    queryKey: ['reports'],
    queryFn: async () => {
      const res = await api.get('/reports')
      return res.data ?? []
    },
  })

  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-slate-50">Welcome to Carbon Compass</h1>
        <p className="text-sm text-slate-400">AI-powered sustainability report analysis</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={FileText}
          label="Total Reports"
          value={reports.length.toString()}
          color="emerald"
        />
        <StatCard
          icon={BarChart3}
          label="Analysed"
          value={reports.length.toString()}
          color="blue"
          subtitle="All reports"
        />
        <StatCard
          icon={AlertTriangle}
          label="Greenwashing Flags"
          value="0"
          color="amber"
          subtitle="Across all reports"
        />
        <StatCard
          icon={TrendingUp}
          label="Avg Risk Score"
          value="—"
          color="slate"
          subtitle="Calculate after analysis"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <QuickActions />
        <RecentAnalyses />
      </div>
    </section>
  )
}
