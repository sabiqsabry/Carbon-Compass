import { useQuery } from '@tanstack/react-query'
import { FileText, BarChart3, AlertTriangle, TrendingUp, Calculator, ShieldCheck } from 'lucide-react'
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

      {/* How It Works */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-lg font-semibold text-slate-50 mb-4">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-lg border border-slate-700 p-4">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="h-5 w-5 text-blue-400" />
              <h3 className="text-sm font-medium text-slate-200">1. Analyse Reports</h3>
            </div>
            <p className="text-xs text-slate-400">Upload sustainability PDFs — AI extracts metrics, detects greenwashing, and scores risk</p>
          </div>
          <div className="rounded-lg border border-slate-700 p-4">
            <div className="flex items-center gap-2 mb-2">
              <Calculator className="h-5 w-5 text-emerald-400" />
              <h3 className="text-sm font-medium text-slate-200">2. Calculate Emissions</h3>
            </div>
            <p className="text-xs text-slate-400">Input activity data (energy, fuel, travel, waste) and compute emissions using DEFRA factors</p>
          </div>
          <div className="rounded-lg border border-slate-700 p-4">
            <div className="flex items-center gap-2 mb-2">
              <ShieldCheck className="h-5 w-5 text-amber-400" />
              <h3 className="text-sm font-medium text-slate-200">3. Verify Claims</h3>
            </div>
            <p className="text-xs text-slate-400">Compare what reports claim vs what the numbers show — find discrepancies automatically</p>
          </div>
        </div>
      </div>
    </section>
  )
}
