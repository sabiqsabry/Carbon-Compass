import { useState } from 'react'
import { ChevronDown, ChevronUp, FileText, Loader2, Sparkles, AlertCircle } from 'lucide-react'

type SummaryData = {
  executive_summary: string
  section_summaries: Array<{
    section_name: string
    summary: string
  }>
  commitments: string[]
}

type ReportSummaryProps = {
  summary: SummaryData
  isLoading?: boolean
  needsGeneration?: boolean
  onGenerate?: () => void
  error?: string
}

function ProgressBar() {
  return (
    <div className="space-y-4 py-6">
      <div className="flex items-center gap-3">
        <Loader2 className="h-5 w-5 text-emerald-400 animate-spin flex-shrink-0" />
        <div className="flex-1">
          <p className="text-sm font-medium text-slate-200">Generating report summary...</p>
          <p className="text-xs text-slate-500 mt-0.5">
            The AI model is analysing each section. This may take a minute on first run.
          </p>
        </div>
      </div>
      <div className="relative h-2 w-full rounded-full bg-slate-800 overflow-hidden">
        <div className="absolute inset-0 h-full w-1/2 rounded-full bg-gradient-to-r from-emerald-600 to-emerald-400 animate-[shimmer_2s_ease-in-out_infinite]" />
      </div>
      <style>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
      `}</style>
    </div>
  )
}

export function ReportSummary({ summary, isLoading, needsGeneration, onGenerate, error }: ReportSummaryProps) {
  const [expandedSections, setExpandedSections] = useState<Set<number>>(new Set([0]))

  const toggleSection = (idx: number) => {
    const newSet = new Set(expandedSections)
    if (newSet.has(idx)) {
      newSet.delete(idx)
    } else {
      newSet.add(idx)
    }
    setExpandedSections(newSet)
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <h2 className="text-lg font-semibold text-slate-50 mb-4">Report Summary</h2>

      {isLoading ? (
        <ProgressBar />
      ) : needsGeneration ? (
        <div className="flex flex-col items-center gap-4 py-8">
          <div className="p-3 rounded-full bg-emerald-500/10">
            <Sparkles className="h-6 w-6 text-emerald-400" />
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-slate-200">
              AI-powered summaries are available
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Generate section-by-section summaries and an executive overview using our BART model
            </p>
          </div>
          <button
            onClick={onGenerate}
            className="flex items-center gap-2 rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-500 transition-colors"
          >
            <Sparkles className="h-4 w-4" />
            Generate Summary
          </button>
          {error && (
            <div className="flex items-center gap-2 text-xs text-red-400 mt-1">
              <AlertCircle className="h-3.5 w-3.5" />
              {error}
            </div>
          )}
        </div>
      ) : (
        <>
          {summary.executive_summary && (
            <div className="mb-6 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
              <h3 className="text-sm font-semibold text-emerald-300 mb-2">Executive Summary</h3>
              <p className="text-sm text-slate-300 leading-relaxed">{summary.executive_summary}</p>
            </div>
          )}

          <div className="space-y-2">
            {summary.section_summaries.length === 0 ? (
              <p className="text-sm text-slate-500 text-center py-8">No section summaries available</p>
            ) : (
              summary.section_summaries.map((section, idx) => {
                const isExpanded = expandedSections.has(idx)
                return (
                  <div
                    key={idx}
                    className="rounded-lg border border-slate-800 bg-slate-900/40 overflow-hidden"
                  >
                    <button
                      onClick={() => toggleSection(idx)}
                      className="w-full flex items-center justify-between p-4 hover:bg-slate-900/60 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <FileText className="h-4 w-4 text-slate-400" />
                        <span className="text-sm font-medium text-slate-200">{section.section_name}</span>
                      </div>
                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4 text-slate-400" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-slate-400" />
                      )}
                    </button>
                    {isExpanded && (
                      <div className="px-4 pb-4">
                        <p className="text-sm text-slate-300 leading-relaxed">{section.summary}</p>
                      </div>
                    )}
                  </div>
                )
              })
            )}
          </div>
        </>
      )}
    </div>
  )
}
