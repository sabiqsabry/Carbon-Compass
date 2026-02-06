import { useState } from 'react'
import { Plus, Trash2, ShieldCheck, Loader2 } from 'lucide-react'
import { api } from '../../services/api'

type Activity = {
  id: string
  category: string
  sub_category: string
  amount: string
  unit: string
  country: string
}

type VerificationInputProps = {
  reportFilename: string
  onResult: (data: Record<string, unknown>) => void
}

const CATEGORIES = [
  { value: 'electricity', label: 'Electricity' },
  { value: 'fuel', label: 'Fuel' },
  { value: 'transport', label: 'Transport' },
  { value: 'flight', label: 'Flights' },
  { value: 'waste', label: 'Waste' },
  { value: 'water', label: 'Water' },
]

let idCounter = 0

export function VerificationInput({ reportFilename, onResult }: VerificationInputProps) {
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [category, setCategory] = useState('')
  const [subCategory, setSubCategory] = useState('')
  const [amount, setAmount] = useState('')
  const [unit, setUnit] = useState('')
  const [country, setCountry] = useState('')

  const addActivity = () => {
    if (!category || !amount) return
    setActivities([
      ...activities,
      {
        id: `v-${++idCounter}`,
        category,
        sub_category: subCategory,
        amount,
        unit: unit || 'kWh',
        country,
      },
    ])
    setCategory('')
    setSubCategory('')
    setAmount('')
    setUnit('')
    setCountry('')
  }

  const removeActivity = (id: string) => {
    setActivities(activities.filter((a) => a.id !== id))
  }

  const runVerification = async () => {
    if (activities.length === 0) return
    setLoading(true)
    setError(null)

    try {
      const payload = {
        activities: activities.map((a) => ({
          category: a.category,
          sub_category: a.sub_category || undefined,
          amount: parseFloat(a.amount),
          unit: a.unit || undefined,
          country: a.country || undefined,
        })),
      }
      const res = await api.post(`/verify/${encodeURIComponent(reportFilename)}`, payload)
      onResult(res.data)
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      setError(axiosErr?.response?.data?.detail || 'Verification failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
      <h2 className="text-lg font-semibold text-slate-50">Enter Activity Data</h2>
      <p className="text-xs text-slate-400">
        Enter the actual activity data to compare against what {reportFilename} reports
      </p>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Category</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-50 focus:ring-2 focus:ring-emerald-500/50"
          >
            <option value="">Select...</option>
            {CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Sub-category</label>
          <input
            type="text"
            value={subCategory}
            onChange={(e) => setSubCategory(e.target.value)}
            placeholder="e.g. diesel"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-50 focus:ring-2 focus:ring-emerald-500/50"
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Amount</label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-50 focus:ring-2 focus:ring-emerald-500/50"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Unit</label>
          <input
            type="text"
            value={unit}
            onChange={(e) => setUnit(e.target.value)}
            placeholder="kWh, litres..."
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-50 focus:ring-2 focus:ring-emerald-500/50"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Country</label>
          <input
            type="text"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            placeholder="optional"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-50 focus:ring-2 focus:ring-emerald-500/50"
          />
        </div>
      </div>

      <button
        onClick={addActivity}
        disabled={!category || !amount}
        className="flex items-center gap-2 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-xs font-medium text-emerald-300 hover:bg-emerald-500/20 transition-colors disabled:opacity-40"
      >
        <Plus className="h-3.5 w-3.5" />
        Add Activity
      </button>

      {activities.length > 0 && (
        <>
          <div className="space-y-1.5 border-t border-slate-800 pt-3">
            {activities.map((act) => (
              <div key={act.id} className="flex items-center justify-between rounded-md bg-slate-800/50 px-3 py-2 text-xs">
                <span className="text-slate-300">
                  <span className="text-emerald-400 capitalize">{act.category}</span>
                  {act.sub_category && <span className="text-slate-500"> / {act.sub_category}</span>}
                  {' — '}
                  {parseFloat(act.amount).toLocaleString()} {act.unit}
                </span>
                <button onClick={() => removeActivity(act.id)} className="text-slate-600 hover:text-red-400">
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            ))}
          </div>

          <button
            onClick={runVerification}
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-500 transition-colors disabled:opacity-60"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ShieldCheck className="h-4 w-4" />}
            {loading ? 'Verifying...' : 'Verify Against Report'}
          </button>

          {error && <p className="text-xs text-red-400">{error}</p>}
        </>
      )}
    </div>
  )
}
