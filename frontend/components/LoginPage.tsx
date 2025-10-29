'use client'

import { useState } from 'react'
import axios from 'axios'
import { extractErrorMessage } from '@/utils/errorUtils'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface LoginPageProps {
  onLoginSuccess: () => void
}

export default function LoginPage({ onLoginSuccess }: LoginPageProps) {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      console.log('Attempting login with:', { username, password: '***' })
      console.log('API URL:', `${API_URL}/api/auth/login`)
      
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        username,
        password
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      })

      console.log('Login successful:', response.data)
      localStorage.setItem('token', response.data.access_token)
      localStorage.setItem('username', username)
      onLoginSuccess()
    } catch (err: any) {
      console.error('Login error details:', {
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        config: err.config
      })
      const errorMessage = extractErrorMessage(err.response?.data || err)
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden flex items-center justify-center p-4">
      {/* Animated background elements */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-10 left-10 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-10 right-10 w-[500px] h-[500px] bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-pink-500/10 rounded-full blur-3xl animate-pulse delay-2000"></div>
      </div>

      <div className="max-w-md w-full relative z-10">
        {/* Logo and Title */}
        <div className="text-center mb-8 float-animation">
          <div className="inline-block glass-card-strong p-6 rounded-full shadow-2xl mb-6 border border-white/20">
            <svg className="w-16 h-16 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <h1 className="text-4xl font-bold text-gradient mb-3">
            Student Identification System
          </h1>
          <p className="text-gray-300 text-lg">
            AI-Powered Face Recognition
          </p>
        </div>

        {/* Login Card */}
        <div className="glass-card-strong rounded-2xl p-8 shadow-2xl border border-white/20">
          <h2 className="text-3xl font-bold text-white mb-8 text-center flex items-center justify-center gap-3">
            <span className="text-3xl">🔐</span>
            Sign In
          </h2>

          <form onSubmit={handleLogin} className="space-y-6">
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-2">
                Username
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                          text-white placeholder-gray-400 focus:outline-none 
                          focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20 
                          transition-all duration-300"
                placeholder="Enter username"
                required
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                          text-white placeholder-gray-400 focus:outline-none 
                          focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20 
                          transition-all duration-300"
                placeholder="Enter password"
                required
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="glass-card border border-red-400/30 bg-red-500/10 rounded-xl p-4">
                <p className="text-red-300 flex items-center gap-2">
                  <span className="text-xl">⚠️</span>
                  {typeof error === 'string' ? error : 'Login failed. Please check your credentials.'}
                </p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-4 rounded-xl font-bold text-lg transition-all duration-300
                ${loading
                  ? 'glass-card text-gray-500 cursor-not-allowed'
                  : 'glow-button bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg hover:shadow-blue-500/50 hover:scale-105'
                }`}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="inline-block w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  Signing in...
                </span>
              ) : (
                '🔓 Sign In'
              )}
            </button>
          </form>

          {/* Default Credentials Info */}
          <div className="mt-6 glass-card border border-blue-400/30 bg-blue-500/10 rounded-xl p-5">
            <p className="text-sm text-blue-300 font-bold mb-2 flex items-center gap-2">
              <span className="text-lg">ℹ️</span>
              Default Credentials:
            </p>
            <p className="text-sm text-blue-200">
              Username: <code className="font-mono glass-card px-3 py-1 rounded-lg border border-blue-400/20 text-blue-300">admin</code><br />
              Password: <code className="font-mono glass-card px-3 py-1 rounded-lg border border-blue-400/20 text-blue-300 mt-1 inline-block">admin123</code>
            </p>
            <p className="text-xs text-blue-300 mt-3 flex items-center gap-2">
              <span>⚠️</span>
              Please change the password after first login
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-400">
          <p className="glass-card inline-block px-6 py-3 rounded-full border border-white/10">
            Powered by{' '}
            <span className="text-blue-400 font-semibold">GFPGAN v1.4</span>,{' '}
            <span className="text-purple-400 font-semibold">AdaFace</span>, and{' '}
            <span className="text-pink-400 font-semibold">FAISS</span>
          </p>
        </div>
      </div>
    </div>
  )
}
