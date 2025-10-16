'use client'

import { useState, useEffect } from 'react'
import LoginPage from '@/components/LoginPage'
import IdentificationModule from '@/components/IdentificationModule'
import RegistrationModule from '@/components/RegistrationModule'
import StudentsModule from '@/components/StudentsModule'
import StatsModule from '@/components/StatsModule'

export default function Home() {
  const [activeTab, setActiveTab] = useState('identify')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [username, setUsername] = useState('')

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token')
    const storedUsername = localStorage.getItem('username')
    if (token) {
      setIsAuthenticated(true)
      setUsername(storedUsername || 'User')
    }
  }, [])

  const handleLoginSuccess = () => {
    setIsAuthenticated(true)
    setUsername(localStorage.getItem('username') || 'User')
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    setIsAuthenticated(false)
    setUsername('')
  }

  if (!isAuthenticated) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />
  }

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Student Identification System
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                AI-Powered Face Recognition with GFPGAN + AdaFace + FAISS
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, <span className="font-medium">{username}</span>
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'identify', label: 'Identify Student', icon: '🔍' },
              { id: 'register', label: 'Register Student', icon: '➕' },
              { id: 'students', label: 'Student Database', icon: '👥' },
              { id: 'stats', label: 'Statistics', icon: '📊' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'identify' && <IdentificationModule />}
        {activeTab === 'register' && <RegistrationModule />}
        {activeTab === 'students' && <StudentsModule />}
        {activeTab === 'stats' && <StatsModule />}
      </div>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            © 2025 Student Identification System. Powered by GFPGAN v1.4, AdaFace, and FAISS.
          </p>
        </div>
      </footer>
    </main>
  )
}
