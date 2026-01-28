type ComparisonData = {
  companies: string[]
  risk: Record<string, unknown>
  greenwashing: Record<string, { risk_score?: number; flags_count?: number } | undefined>
}

type ComparisonTableProps = {
  data: ComparisonData
}

export function ComparisonTable({ data }: ComparisonTableProps) {
  const getNestedNumber = (obj: unknown, path: string): number | undefined => {
    const keys = path.split('.')
    let value: unknown = obj

    for (const key of keys) {
      if (value == null || typeof value !== 'object') return undefined
      value = (value as Record<string, unknown>)[key]
    }

    return typeof value === 'number' ? value : undefined
  }

  const formatName = (filename: string) => {
    return filename.replace(/\.pdf$/i, '').replace(/[_-]/g, ' ')
  }

  const getBestWorst = (values: number[]) => {
    const max = Math.max(...values)
    const min = Math.min(...values)
    return { best: max, worst: min }
  }

  const riskRows = [
    { label: 'Overall Risk Score', key: 'overall_score' },
    { label: 'Transparency', key: 'components.transparency' },
    { label: 'Commitment', key: 'components.commitment' },
    { label: 'Credibility', key: 'components.credibility' },
    { label: 'Data Quality', key: 'components.data_quality' },
    { label: 'Verification', key: 'components.verification' },
  ]

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-800">
              <th className="px-4 py-3 text-left text-sm font-semibold text-slate-300">Metric</th>
              {data.companies.map((company) => (
                <th key={company} className="px-4 py-3 text-center text-sm font-semibold text-slate-300">
                  {formatName(company)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {riskRows.map((row) => {
              const values = data.companies.map((company) => {
                const value = getNestedNumber(data.risk[company], row.key)
                return value ?? 0
              })
              const { best, worst } = getBestWorst(values)

              return (
                <tr key={row.key} className="border-b border-slate-800/50 hover:bg-slate-900/40">
                  <td className="px-4 py-3 text-sm text-slate-300">{row.label}</td>
                  {data.companies.map((company) => {
                    const value = getNestedNumber(data.risk[company], row.key)
                    const numValue = value ?? 0
                    const isBest = numValue === best && best !== worst
                    const isWorst = numValue === worst && best !== worst

                    return (
                      <td
                        key={company}
                        className={`px-4 py-3 text-center text-sm ${
                          isBest
                            ? 'bg-emerald-500/20 text-emerald-300'
                            : isWorst
                            ? 'bg-red-500/20 text-red-300'
                            : 'text-slate-200'
                        }`}
                      >
                        {typeof value === 'number' ? value.toFixed(1) : '—'}
                      </td>
                    )
                  })}
                </tr>
              )
            })}
            <tr className="border-b border-slate-800">
              <td className="px-4 py-3 text-sm text-slate-300">Greenwashing Risk</td>
              {data.companies.map((company) => (
                <td key={company} className="px-4 py-3 text-center text-sm text-slate-200">
                  {data.greenwashing[company]?.risk_score?.toFixed(1) || '—'}
                </td>
              ))}
            </tr>
            <tr>
              <td className="px-4 py-3 text-sm text-slate-300">Greenwashing Flags</td>
              {data.companies.map((company) => (
                <td key={company} className="px-4 py-3 text-center text-sm text-slate-200">
                  {data.greenwashing[company]?.flags_count || 0}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
