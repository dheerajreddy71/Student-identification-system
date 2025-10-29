'use client'

import { useState } from 'react'
import axios from 'axios'
import { extractErrorMessage } from '@/utils/errorUtils'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface RegistrationFormData {
  student_id: string
  name: string
  department: string
  year: string
  roll_number: string
  email: string
  phone: string
  address: string
}

interface RegistrationResult {
  success: boolean
  message: string
}

export default function RegistrationModule() {
  const [formData, setFormData] = useState<RegistrationFormData>({
    student_id: '',
    name: '',
    department: '',
    year: '1',
    roll_number: '',
    email: '',
    phone: '',
    address: ''
  })
  const [photos, setPhotos] = useState<File[]>([])
  const [previews, setPreviews] = useState<string[]>([])
  const [result, setResult] = useState<RegistrationResult | null>(null)
  const [loading, setLoading] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handlePhotoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      const fileArray = Array.from(files)
      setPhotos(fileArray)
      
      // Create previews for all selected files
      const previewUrls = fileArray.map(file => URL.createObjectURL(file))
      setPreviews(previewUrls)
    }
  }

  const removePhoto = (index: number) => {
    const newPhotos = photos.filter((_, i) => i !== index)
    const newPreviews = previews.filter((_, i) => i !== index)
    
    // Revoke the URL to free memory
    URL.revokeObjectURL(previews[index])
    
    setPhotos(newPhotos)
    setPreviews(newPreviews)
  }

  const registerStudent = async (e: React.FormEvent) => {
    e.preventDefault()
    if (photos.length === 0) {
      alert('Please select at least one photo')
      return
    }

    setLoading(true)
    setResult(null)

    const formDataToSend = new FormData()
    Object.entries(formData).forEach(([key, value]) => {
      formDataToSend.append(key, value.toString())
    })
    
    // Append all photos with explicit filenames
    photos.forEach((photo, index) => {
      formDataToSend.append('photos', photo, photo.name || `photo_${index + 1}.jpg`)
    })
    
    console.log('Sending registration with', photos.length, 'photos')

    try {
      const response = await axios.post(
        `${API_URL}/api/students/register`,
        formDataToSend,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      )
      setResult(response.data)
      
      if (response.data.success) {
        // Reset form
        setFormData({
          student_id: '',
          name: '',
          department: '',
          year: '1',
          roll_number: '',
          email: '',
          phone: '',
          address: ''
        })
        
        // Clean up previews
        previews.forEach(url => URL.revokeObjectURL(url))
        setPhotos([])
        setPreviews([])
      }
    } catch (error: any) {
      console.error('Registration error:', error.response?.data || error)
      const errorMessage = extractErrorMessage(error.response?.data || error)
      setResult({
        success: false,
        message: errorMessage
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="glass-card rounded-2xl p-8 border border-white/20 float-animation">
      <div className="flex items-center gap-3 mb-6">
        <div className="text-4xl">➕</div>
        <h2 className="text-3xl font-bold text-gradient">Register New Student</h2>
      </div>

      <form onSubmit={registerStudent} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Student ID *
            </label>
            <input
              type="text"
              name="student_id"
              value={formData.student_id}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                        text-white placeholder-gray-400 focus:outline-none 
                        focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20 
                        transition-all duration-300"
              placeholder="e.g., STU2024001"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Full Name *
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                        text-white placeholder-gray-400 focus:outline-none 
                        focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20 
                        transition-all duration-300"
              placeholder="Enter full name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Department *
            </label>
            <input
              type="text"
              name="department"
              value={formData.department}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                        text-white placeholder-gray-400 focus:outline-none 
                        focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20 
                        transition-all duration-300"
              placeholder="e.g., CSE, ECE"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Year *
            </label>
            <select
              name="year"
              value={formData.year}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                        text-white focus:outline-none focus:border-blue-400/50 
                        focus:ring-2 focus:ring-blue-400/20 transition-all duration-300 
                        bg-slate-800/50 cursor-pointer"
            >
              {[1, 2, 3, 4].map(year => (
                <option key={year} value={year} className="bg-slate-800">Year {year}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Roll Number *
            </label>
            <input
              type="text"
              name="roll_number"
              value={formData.roll_number}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                        text-white placeholder-gray-400 focus:outline-none 
                        focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20 
                        transition-all duration-300"
              placeholder="e.g., 21BCS001"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                        text-white placeholder-gray-400 focus:outline-none 
                        focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20 
                        transition-all duration-300"
              placeholder="student@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Phone
            </label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleInputChange}
              className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                        text-white placeholder-gray-400 focus:outline-none 
                        focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20 
                        transition-all duration-300"
              placeholder="+91 XXXXXXXXXX"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Address
          </label>
          <textarea
            name="address"
            value={formData.address}
            onChange={handleInputChange}
            rows={3}
            className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                      text-white placeholder-gray-400 focus:outline-none 
                      focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20 
                      transition-all duration-300 resize-none"
            placeholder="Enter complete address"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
            <span className="text-xl">📸</span>
            Photos (Multiple photos for better accuracy) *
          </label>
          <div className="glass-card rounded-xl p-4 border border-white/10">
            <input
              type="file"
              accept="image/*"
              multiple
              onChange={handlePhotoSelect}
              required
              className="block w-full text-sm text-gray-300
                file:mr-4 file:py-2.5 file:px-5
                file:rounded-lg file:border-0
                file:text-sm file:font-semibold
                file:bg-gradient-to-r file:from-purple-500 file:to-pink-500 file:text-white
                hover:file:shadow-lg hover:file:shadow-purple-500/50
                file:transition-all file:duration-300 file:cursor-pointer"
            />
          </div>
          {previews.length > 0 && (
            <div className="mt-5">
              <p className="text-sm text-gray-300 mb-3 flex items-center gap-2">
                <span className="inline-block w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                Selected {previews.length} photo{previews.length > 1 ? 's' : ''}
              </p>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {previews.map((preview, index) => (
                  <div key={index} className="relative group">
                    <div className="glass-card-strong rounded-xl overflow-hidden border border-white/20 p-2 
                                  transition-all duration-300 hover:scale-105 hover:border-purple-400/50">
                      <img
                        src={preview}
                        alt={`Preview ${index + 1}`}
                        className="w-full h-32 object-cover rounded-lg"
                      />
                    </div>
                    <button
                      type="button"
                      onClick={() => removePhoto(index)}
                      className="absolute -top-2 -right-2 bg-gradient-to-r from-red-500 to-pink-600 
                                text-white rounded-full w-8 h-8 flex items-center justify-center 
                                shadow-lg hover:shadow-red-500/50 transition-all duration-300 
                                hover:scale-110 opacity-0 group-hover:opacity-100"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={loading}
          className={`w-full py-4 rounded-xl font-bold text-lg transition-all duration-300
            ${loading
              ? 'glass-card text-gray-500 cursor-not-allowed'
              : 'glow-button bg-gradient-to-r from-purple-500 to-pink-600 text-white shadow-lg hover:shadow-purple-500/50 hover:scale-105'
            }`}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="inline-block w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              Registering...
            </span>
          ) : (
            '➕ Register Student'
          )}
        </button>
      </form>

      {/* Result */}
      {result && (
        <div className={`mt-6 glass-card-strong rounded-xl p-5 border-l-4 transform transition-all duration-500 ${
          result.success 
            ? 'border-green-400 bg-green-500/10' 
            : 'border-red-400 bg-red-500/10'
        }`}>
          <p className={`font-bold flex items-center gap-3 ${
            result.success ? 'text-green-300' : 'text-red-300'
          }`}>
            <span className="text-2xl">{result.success ? '✓' : '✗'}</span>
            {result.message}
          </p>
        </div>
      )}
    </div>
  )
}
