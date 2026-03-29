import { Routes, Route } from 'react-router-dom'
import { UseCaseProvider } from './context/UseCaseContext'
import { ToastProvider } from './context/ToastContext'
import { WorkflowProvider } from './context/WorkflowContext'
import { HopexProvider } from './context/HopexContext'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Editor from './pages/Editor'
import NotFound from './pages/NotFound'

function App() {
  return (
    <ToastProvider>
      <UseCaseProvider>
        <WorkflowProvider>
          <HopexProvider>
            <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/usecase/:id" element={<Editor />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
            </Layout>
          </HopexProvider>
        </WorkflowProvider>
      </UseCaseProvider>
    </ToastProvider>
  )
}

export default App
