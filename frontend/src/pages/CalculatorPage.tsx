import { useState } from 'react'
import { Calculator, Upload } from 'lucide-react'
import { ActivityForm } from '../components/calculator/ActivityForm'
import { BulkUploadTab } from '../components/calculator/BulkUploadTab'
import { EmissionsResult } from '../components/calculator/EmissionsResult'
import { ScopeBreakdown } from '../components/calculator/ScopeBreakdown'

type TabId = 'manual' | 'upload'

type EmissionsData = {
  total_kg_co2e: number
  total_tonnes_co2e: number
  by_scope: Record<string, number>
  by_category: Record<string, number>
  breakdown: Array<{
    activity_type: string
    activity_amount: number
    activity_unit: string
    emissions_kg_co2e: number
    emissions_tonnes_co2e: number
    scope: number
    factor_used: number
    factor_source: string
    calculation_details: string
  }>
  activity_count: number
  warnings: string[]
}

export function CalculatorPage(): JSX.Element {
  const [activeTab, setActiveTab] = useState<TabId>('manual')
  const [results, setResults] = useState<EmissionsData | null>(null)

  const tabs: { id: TabId; label: string; icon: typeof Calculator }[] = [
    { id: 'manual', label: 'Manual Entry', icon: Calculator },
    { id: 'upload', label: 'Bulk Upload', icon: Upload },
  ]

  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-slate-50">Emissions Calculator</h1>
        <p className="text-sm text-slate-400">
          Calculate your carbon footprint from activity data using official DEFRA 2024 conversion factors
        </p>
      </header>

      {/* Tab Switcher */}
      <div className="flex gap-1 rounded-lg bg-slate-900/60 border border-slate-800 p-1 w-fit">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={[
                'flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors',
                activeTab === tab.id
                  ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20'
                  : 'text-slate-400 hover:text-slate-200 border border-transparent',
              ].join(' ')}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          {activeTab === 'manual' ? (
            <ActivityForm onResults={setResults} />
          ) : (
            <BulkUploadTab onResults={setResults} />
          )}
        </div>

        <div className="space-y-6">
          {results && (
            <>
              <ScopeBreakdown data={results} />
            </>
          )}
        </div>
      </div>

      {results && <EmissionsResult data={results} />}
    </section>
  )
}
