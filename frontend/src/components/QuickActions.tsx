import { Link } from 'react-router-dom'
import { UploadCloud, Files, LineChart } from 'lucide-react'

const actions = [
  {
    icon: UploadCloud,
    title: 'Upload Report',
    description: 'Add a new sustainability report for analysis',
    to: '/upload',
    color: 'emerald',
  },
  {
    icon: Files,
    title: 'View Reports',
    description: 'Browse all uploaded reports',
    to: '/reports',
    color: 'blue',
  },
  {
    icon: LineChart,
    title: 'Compare Companies',
    description: 'Side-by-side comparison of multiple reports',
    to: '/compare',
    color: 'amber',
  },
]

export function QuickActions() {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <h2 className="text-lg font-semibold text-slate-50 mb-4">Quick Actions</h2>
      <div className="grid grid-cols-1 gap-3">
        {actions.map((action) => {
          const Icon = action.icon
          const colorClasses = {
            emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20',
            blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20 hover:bg-blue-500/20',
            amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20 hover:bg-amber-500/20',
          }

          return (
            <Link
              key={action.to}
              to={action.to}
              className={`flex items-center gap-4 p-4 rounded-lg border transition-colors ${colorClasses[action.color as keyof typeof colorClasses]}`}
            >
              <div className="p-2 rounded-lg bg-current/10">
                <Icon className="h-5 w-5" />
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-slate-50 mb-0.5">{action.title}</h3>
                <p className="text-xs text-slate-400">{action.description}</p>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
