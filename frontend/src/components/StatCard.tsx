import type { LucideIcon } from 'lucide-react'

type StatCardProps = {
  icon: LucideIcon
  label: string
  value: string
  color?: 'emerald' | 'blue' | 'amber' | 'slate'
  subtitle?: string
}

export function StatCard({ icon: Icon, label, value, color = 'emerald', subtitle }: StatCardProps) {
  const colorClasses = {
    emerald: 'bg-emerald-500/10 text-emerald-400',
    blue: 'bg-blue-500/10 text-blue-400',
    amber: 'bg-amber-500/10 text-amber-400',
    slate: 'bg-slate-700/50 text-slate-400',
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <div>
        <p className="text-2xl font-bold text-slate-50 mb-1">{value}</p>
        <p className="text-sm font-medium text-slate-300">{label}</p>
        {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
      </div>
    </div>
  )
}
