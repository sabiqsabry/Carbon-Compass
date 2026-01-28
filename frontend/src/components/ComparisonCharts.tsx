import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'

type RiskComponentKey = 'transparency' | 'commitment' | 'credibility' | 'data_quality' | 'verification'

type RiskComponents = Partial<Record<RiskComponentKey, number>>

type RiskData = {
  overall_score?: number
  components?: RiskComponents
}

type GreenwashingData = {
  risk_score?: number
}

type ComparisonData = {
  companies: string[]
  risk: Record<string, RiskData | undefined>
  greenwashing: Record<string, GreenwashingData | undefined>
}

type ComparisonChartsProps = {
  data: ComparisonData
}

export function ComparisonCharts({ data }: ComparisonChartsProps) {
  const formatName = (filename: string) => {
    return filename.replace(/\.pdf$/i, '').replace(/[_-]/g, ' ').substring(0, 20)
  }

  const barData = data.companies.map((company) => ({
    name: formatName(company),
    'Risk Score': data.risk[company]?.overall_score || 0,
    'Greenwashing Risk': data.greenwashing[company]?.risk_score || 0,
  }))

  const radarData = data.companies.map((company) => {
    const components = data.risk[company]?.components || {}
    return {
      company: formatName(company),
      Transparency: components.transparency || 0,
      Commitment: components.commitment || 0,
      Credibility: components.credibility || 0,
      'Data Quality': components.data_quality || 0,
      Verification: components.verification || 0,
    }
  })

  const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-lg font-semibold text-slate-50 mb-4">Risk Scores Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '8px',
                color: '#e2e8f0',
              }}
            />
            <Legend />
            <Bar dataKey="Risk Score" fill="#10b981" />
            <Bar dataKey="Greenwashing Risk" fill="#f59e0b" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-lg font-semibold text-slate-50 mb-4">Component Scores</h3>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={radarData[0] ? [radarData[0]] : []}>
            <PolarGrid stroke="#334155" />
            <PolarAngleAxis dataKey="company" stroke="#94a3b8" />
            <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#94a3b8" />
            {radarData.map((item, idx) => (
              <Radar
                key={idx}
                name={item.company}
                dataKey="Transparency"
                stroke={colors[idx % colors.length]}
                fill={colors[idx % colors.length]}
                fillOpacity={0.6}
              />
            ))}
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '8px',
                color: '#e2e8f0',
              }}
            />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
