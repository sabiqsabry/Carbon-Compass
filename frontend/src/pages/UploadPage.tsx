import { UploadZone } from '../components/UploadZone'

export function UploadPage(): JSX.Element {
  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-slate-50">Upload sustainability report</h1>
        <p className="text-sm text-slate-400">
          Drag &amp; drop a PDF report to start an AI-powered environmental analysis.
        </p>
      </header>
      <UploadZone />
    </section>
  )
}

