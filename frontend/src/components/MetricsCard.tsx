import { useState } from 'react'
import { Factory, Zap, Droplets, Trash2, Leaf, Target, type LucideIcon } from 'lucide-react'

type Metric = {
  metric_type: string
  value: number
  unit: string
  year?: number
  scope?: string
  context: string
}

type MetricsCardProps = {
  metrics: Metric[]
}

const metricIcons: Record<string, LucideIcon> = {
  carbon_emissions: Factory,
  energy: Zap,
  water: Droplets,
  waste: Trash2,
  renewable_percentage: Leaf,
  reduction_target: Target,
}

const metricLabels: Record<string, string> = {
  carbon_emissions: 'Emissions',
  energy: 'Energy',
  water: 'Water',
  waste: 'Waste',
  renewable_percentage: 'Renewables',
  reduction_target: 'Targets',
}

export function MetricsCard({ metrics }: MetricsCardProps) {
  const [activeTab, setActiveTab] = useState<string>('all')

  const groupedMetrics = metrics.reduce((acc, metric) => {
    const type = metric.metric_type
    if (!acc[type]) acc[type] = []
    acc[type].push(metric)
    return acc
  }, {} as Record<string, Metric[]>)

  const tabs = [
    { id: 'all', label: 'All', count: metrics.length },
    ...Object.entries(groupedMetrics).map(([type, items]) => ({
      id: type,
      label: metricLabels[type] || type,
      count: items.length,
    })),
  ]

  const displayMetrics =
    activeTab === 'all' ? metrics : groupedMetrics[activeTab] || []

  const formatValue = (value: number, unit: string) => {
    if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(2)}B ${unit}`
    if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M ${unit}`
    if (value >= 1_000) return `${(value / 1_000).toFixed(2)}K ${unit}`
    return `${value.toFixed(2)} ${unit}`
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <h2 className="text-lg font-semibold text-slate-50 mb-4">Extracted Metrics</h2>

      <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              activeTab === tab.id
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            {tab.label} ({tab.count})
          </button>
        ))}
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {displayMetrics.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-8">No metrics found</p>
        ) : (
          displayMetrics.map((metric, idx) => {
            const Icon = metricIcons[metric.metric_type] || Factory
            return (
              <div
                key={idx}
                className="p-3 rounded-lg border border-slate-800 bg-slate-900/40 hover:bg-slate-900/60 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0">
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-slate-200">
                        {formatValue(metric.value, metric.unit)}
                      </span>
                      {metric.scope && (
                        <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                          {metric.scope}
                        </span>
                      )}
                      {metric.year && (
                        <span className="text-xs text-slate-500">{metric.year}</span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 line-clamp-2">{metric.context}</p>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
