import { useState } from 'react'
import { Plus, Trash2, Calculator, Loader2 } from 'lucide-react'
import { api } from '../../services/api'

type Activity = {
  id: string
  category: string
  sub_category: string
  amount: string
  unit: string
  country: string
}

type ActivityFormProps = {
  onResults: (data: Record<string, unknown>) => void
}

const CATEGORIES = [
  { value: 'electricity', label: 'Electricity' },
  { value: 'fuel', label: 'Fuel' },
  { value: 'transport', label: 'Transport' },
  { value: 'flight', label: 'Flights' },
  { value: 'waste', label: 'Waste' },
  { value: 'water', label: 'Water' },
]

const SUB_CATEGORIES: Record<string, { value: string; label: string }[]> = {
  electricity: [],
  fuel: [
    { value: 'petrol', label: 'Petrol (Gasoline)' },
    { value: 'diesel', label: 'Diesel' },
    { value: 'natural_gas', label: 'Natural Gas' },
    { value: 'lpg', label: 'LPG' },
    { value: 'coal_industrial', label: 'Coal (Industrial)' },
    { value: 'heating_oil', label: 'Heating Oil' },
  ],
  transport: [
    { value: 'small_petrol_car', label: 'Small Petrol Car' },
    { value: 'medium_petrol_car', label: 'Medium Petrol Car' },
    { value: 'large_petrol_car', label: 'Large Petrol Car' },
    { value: 'small_diesel_car', label: 'Small Diesel Car' },
    { value: 'medium_diesel_car', label: 'Medium Diesel Car' },
    { value: 'electric_car', label: 'Electric Car' },
    { value: 'hybrid_car', label: 'Hybrid Car' },
    { value: 'motorcycle', label: 'Motorcycle' },
    { value: 'van', label: 'Van' },
    { value: 'bus', label: 'Bus' },
    { value: 'taxi', label: 'Taxi' },
  ],
  flight: [
    { value: 'domestic', label: 'Domestic' },
    { value: 'short_haul', label: 'Short-Haul International' },
    { value: 'long_haul', label: 'Long-Haul International' },
  ],
  waste: [
    { value: 'landfill_mixed', label: 'Landfill (Mixed)' },
    { value: 'landfill_food', label: 'Landfill (Food)' },
    { value: 'incineration', label: 'Incineration' },
    { value: 'recycling_average', label: 'Recycling (Average)' },
    { value: 'composting', label: 'Composting' },
    { value: 'anaerobic_digestion', label: 'Anaerobic Digestion' },
  ],
  water: [
    { value: 'supply_and_treatment', label: 'Supply + Treatment' },
    { value: 'supply', label: 'Supply Only' },
  ],
}

const UNITS: Record<string, { value: string; label: string }[]> = {
  electricity: [{ value: 'kWh', label: 'kWh' }],
  fuel: [
    { value: 'litres', label: 'Litres' },
    { value: 'gallons', label: 'Gallons' },
    { value: 'kg', label: 'kg' },
    { value: 'kwh', label: 'kWh' },
    { value: 'cubic_metres', label: 'm³' },
    { value: 'therms', label: 'Therms' },
  ],
  transport: [
    { value: 'km', label: 'km' },
    { value: 'miles', label: 'Miles' },
  ],
  flight: [
    { value: 'trips', label: 'Trips' },
    { value: 'km', label: 'km' },
  ],
  waste: [{ value: 'tonnes', label: 'Tonnes' }],
  water: [{ value: 'cubic_metres', label: 'Cubic Metres (m³)' }],
}

const COUNTRIES = [
  { value: 'sri_lanka', label: 'Sri Lanka' },
  { value: 'united_kingdom', label: 'United Kingdom' },
  { value: 'united_states', label: 'United States' },
  { value: 'uae', label: 'UAE' },
  { value: 'saudi_arabia', label: 'Saudi Arabia' },
  { value: 'india', label: 'India' },
  { value: 'china', label: 'China' },
  { value: 'germany', label: 'Germany' },
  { value: 'france', label: 'France' },
  { value: 'australia', label: 'Australia' },
  { value: 'singapore', label: 'Singapore' },
  { value: 'japan', label: 'Japan' },
  { value: 'south_korea', label: 'South Korea' },
  { value: 'canada', label: 'Canada' },
  { value: 'brazil', label: 'Brazil' },
  { value: 'world_average', label: 'World Average' },
]

let idCounter = 0

export function ActivityForm({ onResults }: ActivityFormProps) {
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Current form state
  const [category, setCategory] = useState('')
  const [subCategory, setSubCategory] = useState('')
  const [amount, setAmount] = useState('')
  const [unit, setUnit] = useState('')
  const [country, setCountry] = useState('')

  const resetForm = () => {
    setCategory('')
    setSubCategory('')
    setAmount('')
    setUnit('')
    setCountry('')
  }

  const addActivity = () => {
    if (!category || !amount) return
    const newActivity: Activity = {
      id: `act-${++idCounter}`,
      category,
      sub_category: subCategory,
      amount,
      unit: unit || (UNITS[category]?.[0]?.value ?? ''),
      country,
    }
    setActivities([...activities, newActivity])
    resetForm()
  }

  const removeActivity = (id: string) => {
    setActivities(activities.filter((a) => a.id !== id))
  }

  const calculateTotal = async () => {
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
      const res = await api.post('/calculate/bulk', payload)
      onResults(res.data)
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      setError(axiosErr?.response?.data?.detail || 'Calculation failed')
    } finally {
      setLoading(false)
    }
  }

  const showSubCategory = category && SUB_CATEGORIES[category]?.length > 0
  const showCountry = category === 'electricity'

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-5">
      <h2 className="text-lg font-semibold text-slate-50">Add Activities</h2>

      <div className="space-y-4">
        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">Category</label>
          <select
            value={category}
            onChange={(e) => {
              setCategory(e.target.value)
              setSubCategory('')
              setUnit(UNITS[e.target.value]?.[0]?.value ?? '')
            }}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-50 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500"
          >
            <option value="">Select category...</option>
            {CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
        </div>

        {/* Sub-category */}
        {showSubCategory && (
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              {category === 'flight' ? 'Flight Type' : 'Sub-category'}
            </label>
            <select
              value={subCategory}
              onChange={(e) => setSubCategory(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-50 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500"
            >
              <option value="">Select...</option>
              {SUB_CATEGORIES[category]?.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>
        )}

        {/* Country (electricity only) */}
        {showCountry && (
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Country</label>
            <select
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-50 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500"
            >
              <option value="">Select country...</option>
              {COUNTRIES.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>
        )}

        {/* Amount + Unit */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Amount</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0"
              min="0"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-50 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Unit</label>
            <select
              value={unit}
              onChange={(e) => setUnit(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-50 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500"
            >
              {(UNITS[category] ?? []).map((u) => (
                <option key={u.value} value={u.value}>{u.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Add Button */}
        <button
          onClick={addActivity}
          disabled={!category || !amount}
          className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Plus className="h-4 w-4" />
          Add Activity
        </button>
      </div>

      {/* Activity List */}
      {activities.length > 0 && (
        <div className="border-t border-slate-800 pt-4 space-y-2">
          <h3 className="text-sm font-medium text-slate-300 mb-2">
            Activities ({activities.length})
          </h3>
          {activities.map((act) => (
            <div
              key={act.id}
              className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-2.5"
            >
              <div className="text-sm">
                <span className="text-emerald-400 font-medium capitalize">{act.category}</span>
                {act.sub_category && (
                  <span className="text-slate-400"> / {act.sub_category.replace(/_/g, ' ')}</span>
                )}
                <span className="text-slate-50 ml-2">
                  {parseFloat(act.amount).toLocaleString()} {act.unit}
                </span>
                {act.country && (
                  <span className="text-slate-500 ml-1">({act.country.replace(/_/g, ' ')})</span>
                )}
              </div>
              <button
                onClick={() => removeActivity(act.id)}
                className="text-slate-500 hover:text-red-400 transition-colors"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}

          {/* Calculate Button */}
          <button
            onClick={calculateTotal}
            disabled={loading}
            className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-500 transition-colors disabled:opacity-60"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Calculator className="h-4 w-4" />
            )}
            {loading ? 'Calculating...' : 'Calculate Total Emissions'}
          </button>

          {error && (
            <p className="text-sm text-red-400 mt-2">{error}</p>
          )}
        </div>
      )}
    </div>
  )
}
