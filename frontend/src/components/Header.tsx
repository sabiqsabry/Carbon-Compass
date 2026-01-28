import { Compass } from 'lucide-react'
import { Link } from 'react-router-dom'

type HeaderProps = {
  onToggleTheme?: () => void
}

export function Header({ onToggleTheme }: HeaderProps) {
  return (
    <header className="flex items-center justify-between border-b border-slate-800 bg-slate-950/80 px-6 py-4 backdrop-blur">
      <Link to="/" className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400">
          <Compass className="h-5 w-5" />
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-semibold tracking-wide text-slate-50">Carbon Compass</span>
          <span className="text-xs text-slate-400">AI sustainability insights</span>
        </div>
      </Link>

      <div className="flex items-center gap-3 text-xs text-slate-400">
        <span className="hidden md:inline">Sustainability report analysis</span>
        {onToggleTheme && (
          <button
            type="button"
            onClick={onToggleTheme}
            className="rounded-full border border-slate-700 px-3 py-1 text-xs font-medium text-slate-200 hover:border-emerald-500 hover:text-emerald-300"
          >
            Toggle theme
          </button>
        )}
      </div>
    </header>
  )
}

