import { BarChart3, Files, LineChart, UploadCloud } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Dashboard', icon: BarChart3 },
  { to: '/upload', label: 'Upload', icon: UploadCloud },
  { to: '/reports', label: 'Reports', icon: Files },
  { to: '/compare', label: 'Compare', icon: LineChart },
]

export function Sidebar() {
  return (
    <aside className="hidden w-56 flex-col border-r border-slate-800 bg-slate-950/80 px-4 py-6 text-sm text-slate-300 md:flex">
      <nav className="space-y-1">
        {navItems.map((item) => {
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

