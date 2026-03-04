import { Routes, Route, NavLink } from 'react-router-dom'
import { FileText, MessageSquare, Database } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Models from './pages/Models'

function App() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-xl font-bold">Solution Architecture</h1>
          <p className="text-sm text-gray-400">Co-Pilot</p>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-800'
              }`
            }
          >
            <FileText className="w-5 h-5" />
            Dashboard
          </NavLink>

          <NavLink
            to="/chat"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-800'
              }`
            }
          >
            <MessageSquare className="w-5 h-5" />
            Architecture Chat
          </NavLink>

          <NavLink
            to="/models"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-800'
              }`
            }
          >
            <Database className="w-5 h-5" />
            Reference Models
          </NavLink>
        </nav>

        <div className="p-4 border-t border-gray-800 text-xs text-gray-500">
          SACP Unified v0.1.0
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/models" element={<Models />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
