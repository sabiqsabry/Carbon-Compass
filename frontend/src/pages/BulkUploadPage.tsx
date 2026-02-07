import { useState } from 'react'
import { FileSpreadsheet } from 'lucide-react'
import { FileUploader } from '../components/calculator/FileUploader'
import { ColumnMapper } from '../components/calculator/ColumnMapper'
import { ValidationErrors } from '../components/calculator/ValidationErrors'
import { EmissionsResult } from '../components/calculator/EmissionsResult'
import { ScopeBreakdown } from '../components/calculator/ScopeBreakdown'
import { api } from '../services/api'

type Step = 1 | 2 | 3 | 4

type FilePreview = {
  columns: string[]
  rows: Record<string, unknown>[]
  total_columns: number
  detected_mapping: Record<string, string | null>
}

type ParsedResult = {
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
  parsing?: {
    total_rows: number
    valid_rows: number
    invalid_rows: number
    errors: string[]
    warnings: string[]
  }
}

const STEP_LABELS = ['Upload File', 'Map Columns', 'Review', 'Results']

export function BulkUploadPage(): JSX.Element {
  const [step, setStep] = useState<Step>(1)
  const [fileContent, setFileContent] = useState<File | null>(null)
  const [preview, setPreview] = useState<FilePreview | null>(null)
  const [columnMapping, setColumnMapping] = useState<Record<string, string | null>>({})
  const [results, setResults] = useState<ParsedResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileUploaded = (file: File, previewData: FilePreview) => {
    setFileContent(file)
    setPreview(previewData)
    setColumnMapping(previewData.detected_mapping)
    setError(null)
    setStep(2)
  }

  const handleMappingConfirmed = () => {
    setStep(3)
  }

  const handleCalculate = async () => {
    if (!fileContent) return
    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', fileContent)
      const res = await api.post('/calculate/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResults(res.data)
      setStep(4)
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string | { message?: string } } } }
      const detail = axiosErr?.response?.data?.detail
      setError(typeof detail === 'string' ? detail : (detail as { message?: string })?.message || 'Calculation failed')
    } finally {
      setLoading(false)
    }
  }

  const resetWizard = () => {
    setStep(1)
    setFileContent(null)
    setPreview(null)
    setColumnMapping({})
    setResults(null)
    setError(null)
  }

  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <div className="flex items-center gap-3">
          <FileSpreadsheet className="h-7 w-7 text-emerald-400" />
          <h1 className="text-2xl font-semibold text-slate-50">Bulk Emissions Calculator</h1>
        </div>
        <p className="text-sm text-slate-400">
          Upload your activity data as CSV or Excel and calculate emissions in bulk
        </p>
      </header>

      {/* Step Indicator */}
      <div className="flex items-center gap-2">
        {STEP_LABELS.map((label, idx) => {
          const stepNum = (idx + 1) as Step
          const isActive = step === stepNum
          const isComplete = step > stepNum
          return (
            <div key={label} className="flex items-center gap-2">
              {idx > 0 && (
                <div className={`h-px w-8 ${isComplete ? 'bg-emerald-500' : 'bg-slate-700'}`} />
              )}
              <div className="flex items-center gap-2">
                <div
                  className={[
                    'flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold',
                    isActive
                      ? 'bg-emerald-500 text-white'
                      : isComplete
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : 'bg-slate-800 text-slate-500',
                  ].join(' ')}
                >
                  {isComplete ? '✓' : stepNum}
                </div>
                <span
                  className={`text-xs font-medium ${isActive ? 'text-emerald-300' : isComplete ? 'text-slate-400' : 'text-slate-600'}`}
                >
                  {label}
                </span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Step Content */}
      {step === 1 && <FileUploader onFileUploaded={handleFileUploaded} />}

      {step === 2 && preview && (
        <ColumnMapper
          columns={preview.columns}
          rows={preview.rows}
          mapping={columnMapping}
          onMappingChange={setColumnMapping}
          onConfirm={handleMappingConfirmed}
          onBack={() => setStep(1)}
        />
      )}

      {step === 3 && preview && (
        <ValidationErrors
          preview={preview}
          mapping={columnMapping}
          loading={loading}
          error={error}
          onCalculate={handleCalculate}
          onBack={() => setStep(2)}
        />
      )}

      {step === 4 && results && (
        <div className="space-y-6">
          {results.parsing && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
              <h2 className="text-lg font-semibold text-slate-50 mb-3">Processing Summary</h2>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-3">
                  <p className="text-2xl font-bold text-emerald-400">{results.parsing.valid_rows}</p>
                  <p className="text-xs text-slate-400">Valid Rows</p>
                </div>
                <div className="rounded-lg bg-slate-800/50 border border-slate-700 p-3">
                  <p className="text-2xl font-bold text-slate-300">{results.parsing.total_rows}</p>
                  <p className="text-xs text-slate-400">Total Rows</p>
                </div>
                {results.parsing.invalid_rows > 0 && (
                  <div className="rounded-lg bg-amber-500/10 border border-amber-500/20 p-3">
                    <p className="text-2xl font-bold text-amber-400">{results.parsing.invalid_rows}</p>
                    <p className="text-xs text-slate-400">Skipped</p>
                  </div>
                )}
              </div>
              {results.parsing.errors.length > 0 && (
                <div className="mt-3 space-y-1">
                  {results.parsing.errors.map((e, i) => (
                    <p key={i} className="text-xs text-amber-300">{e}</p>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ScopeBreakdown data={results} />
            <div />
          </div>

          <EmissionsResult data={results} />

          <button
            onClick={resetWizard}
            className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors"
          >
            Upload Another File
          </button>
        </div>
      )}
    </section>
  )
}
