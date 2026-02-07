import { BarChart3, Calculator, FileSpreadsheet, Files, LineChart, ShieldCheck, UploadCloud } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const reportItems = [
  { to: '/', label: 'Dashboard', icon: BarChart3 },
  { to: '/upload', label: 'Upload', icon: UploadCloud },
  { to: '/reports', label: 'Reports', icon: Files },
  { to: '/compare', label: 'Compare', icon: LineChart },
]

const calculateItems = [
  { to: '/calculator', label: 'Calculator', icon: Calculator },
  { to: '/calculator/bulk', label: 'Bulk Upload', icon: FileSpreadsheet },
  { to: '/verify', label: 'Verify Report', icon: ShieldCheck },
]

export function Sidebar() {
  return (
    <aside className="hidden w-56 flex-col border-r border-slate-800 bg-slate-950/80 px-4 py-6 text-sm text-slate-300 md:flex">
      <nav className="space-y-1">
        <p className="px-3 pb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Report Analysis</p>
        {reportItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                [
                  'flex items-center gap-2 rounded-md px-3 py-2 transition-colors',
                  isActive
                    ? 'bg-emerald-500/10 text-emerald-300'
                    : 'text-slate-300 hover:bg-slate-800/70 hover:text-slate-100',
                ].join(' ')
              }
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      <div className="my-4 border-t border-slate-800" />

      <nav className="space-y-1">
        <p className="px-3 pb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Calculate</p>
        {calculateItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                [
                  'flex items-center gap-2 rounded-md px-3 py-2 transition-colors',
                  isActive
                    ? 'bg-emerald-500/10 text-emerald-300'
                    : 'text-slate-300 hover:bg-slate-800/70 hover:text-slate-100',
                ].join(' ')
              }
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>
    </aside>
  )
}

