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
    <main className="min-h-screen relative overflow-hidden">
      {/* Animated background elements */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-pink-500/10 rounded-full blur-3xl animate-pulse delay-2000"></div>
      </div>

      {/* Header */}
      <header className="relative glass-card-strong border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="float-animation">
              <h1 className="text-4xl font-bold text-gradient mb-2">
                Student Identification System
              </h1>
              <p className="text-sm text-gray-300 flex items-center gap-2">
                <span className="inline-block w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                AI-Powered Face Recognition with GFPGAN + AdaFace + FAISS
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="glass-card px-4 py-2 rounded-full">
                <span className="text-sm text-gray-300">Welcome, </span>
                <span className="font-semibold text-blue-300">{username}</span>
              </div>
              <button
                onClick={handleLogout}
                className="glow-button px-6 py-2.5 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-full 
                          font-medium shadow-lg hover:shadow-red-500/50 transition-all duration-300"
              >
                <span className="relative z-10 flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Logout
                </span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
        <div className="glass-card rounded-2xl p-2">
          <nav className="flex space-x-2">
            {[
              { id: 'identify', label: 'Identify Student', icon: '🔍', gradient: 'from-blue-500 to-cyan-500' },
              { id: 'register', label: 'Register Student', icon: '➕', gradient: 'from-purple-500 to-pink-500' },
              { id: 'students', label: 'Student Database', icon: '👥', gradient: 'from-green-500 to-emerald-500' },
              { id: 'stats', label: 'Statistics', icon: '📊', gradient: 'from-orange-500 to-red-500' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex-1 group relative overflow-hidden rounded-xl py-4 px-4 font-medium text-sm
                  transition-all duration-300 transform
                  ${activeTab === tab.id
                    ? `bg-gradient-to-r ${tab.gradient} text-white shadow-lg scale-105`
                    : 'text-gray-300 hover:text-white hover:bg-white/5'
                  }
                `}
              >
                <span className="relative z-10 flex items-center justify-center gap-2">
                  <span className="text-2xl">{tab.icon}</span>
                  <span className="hidden sm:inline">{tab.label}</span>
                </span>
                {activeTab !== tab.id && (
                  <div className={`absolute inset-0 bg-gradient-to-r ${tab.gradient} opacity-0 
                                  group-hover:opacity-10 transition-opacity duration-300`}></div>
                )}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        <div className="transform transition-all duration-500">
          {activeTab === 'identify' && <IdentificationModule />}
          {activeTab === 'register' && <RegistrationModule />}
          {activeTab === 'students' && <StudentsModule />}
          {activeTab === 'stats' && <StatsModule />}
        </div>
      </div>

      {/* Footer */}
      <footer className="relative glass-card-strong border-t border-white/10 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-400">
            © 2025 Student Identification System. Powered by{' '}
            <span className="text-blue-400 font-semibold">GFPGAN v1.4</span>,{' '}
            <span className="text-purple-400 font-semibold">AdaFace</span>, and{' '}
            <span className="text-pink-400 font-semibold">FAISS</span>.
          </p>
        </div>
      </footer>
    </main>
  )
}
