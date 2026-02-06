import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { UploadPage } from './pages/UploadPage'
import { ReportsPage } from './pages/ReportsPage'
import { AnalysisPage } from './pages/AnalysisPage'
import { DashboardPage } from './pages/DashboardPage'
import { ComparePage } from './pages/ComparePage'
import { CalculatorPage } from './pages/CalculatorPage'
import { VerificationPage } from './pages/VerificationPage'

const queryClient = new QueryClient()

function App(): JSX.Element {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/reports/:filename" element={<AnalysisPage />} />
            <Route path="/compare" element={<ComparePage />} />
            <Route path="/calculator" element={<CalculatorPage />} />
            <Route path="/verify" element={<VerificationPage />} />
            <Route path="/verify/:filename" element={<VerificationPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
