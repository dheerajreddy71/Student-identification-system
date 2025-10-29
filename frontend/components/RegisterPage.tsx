'use client'

import { useState } from 'react'
import axios from 'axios'
import { extractErrorMessage } from '@/utils/errorUtils'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface RegisterPageProps {
  onRegisterSuccess: () => void
  onBackToLogin: () => void
}

export default function RegisterPage({ onRegisterSuccess, onBackToLogin }: RegisterPageProps) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters')
      setLoading(false)
      return
    }

    if (!formData.username || !formData.email || !formData.password) {
      setError('Please fill in all required fields')
      setLoading(false)
      return
    }

    try {
      console.log('Attempting registration with:', { 
        username: formData.username, 
        email: formData.email,
        full_name: formData.fullName
      })
      
      const response = await axios.post(`${API_URL}/api/auth/register`, {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.fullName || null,
        role: 'user' // Default role
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      })

      console.log('Registration successful:', response.data)
      
      // Store token and username
      localStorage.setItem('token', response.data.access_token)
      localStorage.setItem('username', formData.username)
      
      setSuccess('Registration successful! Redirecting...')
      
      // Redirect after 1.5 seconds
      setTimeout(() => {
        onRegisterSuccess()
      }, 1500)
      
    } catch (err: any) {
      console.error('Registration error details:', {
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
        <div className="absolute top-10 left-10 w-96 h-96 bg-green-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-10 right-10 w-[500px] h-[500px] bg-teal-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-2000"></div>
      </div>

      <div className="max-w-md w-full relative z-10">
        {/* Logo and Title */}
        <div className="text-center mb-8 float-animation">
          <div className="inline-block glass-card-strong p-6 rounded-full shadow-2xl mb-6 border border-white/20">
            <svg className="w-16 h-16 text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h1 className="text-4xl font-bold text-gradient mb-3">
            Create Account
          </h1>
          <p className="text-gray-300 text-lg">
            Join the Student Identification System
          </p>
        </div>

        {/* Register Card */}
        <div className="glass-card-strong rounded-2xl p-8 shadow-2xl border border-white/20">
          <h2 className="text-3xl font-bold text-white mb-8 text-center flex items-center justify-center gap-3">
            <span className="text-3xl">✨</span>
            Sign Up
          </h2>

          <form onSubmit={handleRegister} className="space-y-5">
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-2">
                Username <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                          text-white placeholder-gray-400 focus:outline-none 
                          focus:border-green-400/50 focus:ring-2 focus:ring-green-400/20 
                          transition-all duration-200"
                placeholder="Choose a username"
              />
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                Email Address <span className="text-red-400">*</span>
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                          text-white placeholder-gray-400 focus:outline-none 
                          focus:border-green-400/50 focus:ring-2 focus:ring-green-400/20 
                          transition-all duration-200"
                placeholder="your.email@example.com"
              />
            </div>

            {/* Full Name */}
            <div>
              <label htmlFor="fullName" className="block text-sm font-medium text-gray-300 mb-2">
                Full Name (Optional)
              </label>
              <input
                type="text"
                id="fullName"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                          text-white placeholder-gray-400 focus:outline-none 
                          focus:border-green-400/50 focus:ring-2 focus:ring-green-400/20 
                          transition-all duration-200"
                placeholder="Your full name"
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Password <span className="text-red-400">*</span>
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={6}
                className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                          text-white placeholder-gray-400 focus:outline-none 
                          focus:border-green-400/50 focus:ring-2 focus:ring-green-400/20 
                          transition-all duration-200"
                placeholder="At least 6 characters"
              />
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300 mb-2">
                Confirm Password <span className="text-red-400">*</span>
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                          text-white placeholder-gray-400 focus:outline-none 
                          focus:border-green-400/50 focus:ring-2 focus:ring-green-400/20 
                          transition-all duration-200"
                placeholder="Re-enter password"
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="glass-card p-4 rounded-xl border border-red-400/30 bg-red-500/10">
                <div className="flex items-center gap-2 text-red-300">
                  <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm">{error}</span>
                </div>
              </div>
            )}

            {/* Success Message */}
            {success && (
              <div className="glass-card p-4 rounded-xl border border-green-400/30 bg-green-500/10">
                <div className="flex items-center gap-2 text-green-300">
                  <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm">{success}</span>
                </div>
              </div>
            )}

            {/* Register Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full gradient-button text-white font-semibold py-3 px-6 rounded-xl 
                       shadow-lg transition-all duration-200 disabled:opacity-50 
                       disabled:cursor-not-allowed flex items-center justify-center gap-2 
                       hover:shadow-xl hover:scale-105"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-t-2 border-white rounded-full animate-spin"></div>
                  <span>Creating Account...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                  </svg>
                  <span>Create Account</span>
                </>
              )}
            </button>

            {/* Back to Login */}
            <div className="text-center mt-6">
              <button
                type="button"
                onClick={onBackToLogin}
                className="text-gray-300 hover:text-white transition-colors duration-200 
                         flex items-center justify-center gap-2 mx-auto group"
              >
                <svg className="w-4 h-4 group-hover:-translate-x-1 transition-transform duration-200" 
                     fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                <span>Already have an account? Sign In</span>
              </button>
            </div>
          </form>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-400 text-sm">
          <p>By registering, you agree to the system's terms of use</p>
        </div>
      </div>
    </div>
  )
}
