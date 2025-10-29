'use client'

import { useState, useRef } from 'react'
import Webcam from 'react-webcam'
import axios from 'axios'
import { extractErrorMessage } from '@/utils/errorUtils'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Student {
  student_id: string
  name: string
  department: string
  roll_number: string
}

interface Metrics {
  face_detected: boolean
  enhanced: boolean
  super_resolved?: boolean
  enhancement_needed?: boolean
  image_quality: number
  enhanced_quality?: number
  quality_improvement?: number
  face_confidence: number
  failure_reason?: string
  failure_advice?: string
  failure_status?: string
}

interface IdentificationResult {
  success: boolean
  student?: Student
  similarity?: number
  processing_time?: number
  metrics?: Metrics
  error?: string
}

export default function IdentificationModule() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [result, setResult] = useState<IdentificationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [useWebcam, setUseWebcam] = useState(false)
  const webcamRef = useRef<any>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setPreview(URL.createObjectURL(file))
      setResult(null)
    }
  }

  const captureFromWebcam = () => {
    const imageSrc = webcamRef.current?.getScreenshot()
    if (imageSrc) {
      fetch(imageSrc)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], 'webcam.jpg', { type: 'image/jpeg' })
          setSelectedFile(file)
          setPreview(imageSrc)
          setUseWebcam(false)
          setResult(null)
        })
    }
  }

  const identifyStudent = async () => {
    if (!selectedFile) return

    setLoading(true)
    setResult(null)

    const formData = new FormData()
    formData.append('photo', selectedFile)
    formData.append('enhance', 'true')
    formData.append('top_k', '3')

    try {
      const response = await axios.post(
        `${API_URL}/api/students/identify`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      )
      setResult(response.data)
    } catch (error: any) {
      const errorMessage = extractErrorMessage(error.response?.data || error)
      setResult({
        success: false,
        error: errorMessage
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 float-animation">
      <div className="glass-card rounded-2xl p-8 border border-white/20">
        <div className="flex items-center gap-3 mb-6">
          <div className="text-4xl">🔍</div>
          <h2 className="text-3xl font-bold text-gradient">Identify Student</h2>
        </div>
        
        {/* Upload or Webcam Toggle */}
        <div className="mb-6 flex space-x-3">
          <button
            onClick={() => setUseWebcam(false)}
            className={`flex-1 py-3 px-6 rounded-xl font-medium transition-all duration-300 ${
              !useWebcam 
                ? 'glow-button bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/50 scale-105' 
                : 'glass-card text-gray-300 hover:text-white hover:scale-105'
            }`}
          >
            <span className="flex items-center justify-center gap-2">
              📤 Upload Photo
            </span>
          </button>
          <button
            onClick={() => setUseWebcam(true)}
            className={`flex-1 py-3 px-6 rounded-xl font-medium transition-all duration-300 ${
              useWebcam 
                ? 'glow-button bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/50 scale-105' 
                : 'glass-card text-gray-300 hover:text-white hover:scale-105'
            }`}
          >
            <span className="flex items-center justify-center gap-2">
              📷 Use Webcam
            </span>
          </button>
        </div>

        {/* Image Input */}
        {!useWebcam ? (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Select Image
            </label>
            <div className="glass-card rounded-xl p-4 border border-white/10">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="block w-full text-sm text-gray-300
                  file:mr-4 file:py-2.5 file:px-5
                  file:rounded-lg file:border-0
                  file:text-sm file:font-semibold
                  file:bg-gradient-to-r file:from-blue-500 file:to-cyan-500 file:text-white
                  hover:file:shadow-lg hover:file:shadow-blue-500/50
                  file:transition-all file:duration-300 file:cursor-pointer"
              />
            </div>
          </div>
        ) : (
          <div className="mb-6">
            <div className="glass-card rounded-xl overflow-hidden border border-white/20 mb-3">
              <Webcam
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                className="w-full"
              />
            </div>
            <button
              onClick={captureFromWebcam}
              className="glow-button w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 rounded-xl 
                        font-medium shadow-lg hover:shadow-purple-500/50 transition-all duration-300"
            >
              📸 Capture Photo
            </button>
          </div>
        )}

        {/* Preview */}
        {preview && (
          <div className="mb-6">
            <div className="glass-card-strong rounded-xl p-4 border border-white/20">
              <img
                src={preview}
                alt="Preview"
                className="max-w-md mx-auto rounded-lg shadow-2xl"
              />
            </div>
          </div>
        )}

        {/* Identify Button */}
        <button
          onClick={identifyStudent}
          disabled={!selectedFile || loading}
          className={`w-full py-4 rounded-xl font-bold text-lg transition-all duration-300
            ${!selectedFile || loading
              ? 'glass-card text-gray-500 cursor-not-allowed'
              : 'glow-button bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg hover:shadow-green-500/50 hover:scale-105'
            }`}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="inline-block w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              Identifying...
            </span>
          ) : (
            '🔍 Identify Student'
          )}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className={`glass-card-strong rounded-2xl p-8 border-l-4 transform transition-all duration-500 ${
          result.success 
            ? 'border-green-400 shadow-lg shadow-green-500/20' 
            : 'border-red-400 shadow-lg shadow-red-500/20'
        }`}>
          <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
            {result.success ? (
              <>
                <span className="text-3xl">✓</span>
                <span className="text-gradient">Student Identified</span>
              </>
            ) : (
              <>
                <span className="text-3xl">✗</span>
                <span className="text-red-400">No Match Found</span>
              </>
            )}
          </h3>

          {result.success && result.student && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="glass-card rounded-xl p-4 border border-white/10">
                  <p className="text-sm text-gray-400 mb-1">Student ID</p>
                  <p className="font-bold text-lg text-blue-300">{result.student?.student_id || 'N/A'}</p>
                </div>
                <div className="glass-card rounded-xl p-4 border border-white/10">
                  <p className="text-sm text-gray-400 mb-1">Name</p>
                  <p className="font-bold text-lg">{result.student?.name || 'N/A'}</p>
                </div>
                <div className="glass-card rounded-xl p-4 border border-white/10">
                  <p className="text-sm text-gray-400 mb-1">Department</p>
                  <p className="font-bold text-lg text-purple-300">{result.student?.department || 'N/A'}</p>
                </div>
                <div className="glass-card rounded-xl p-4 border border-white/10">
                  <p className="text-sm text-gray-400 mb-1">Roll Number</p>
                  <p className="font-bold text-lg">{result.student?.roll_number || 'N/A'}</p>
                </div>
                <div className="glass-card rounded-xl p-4 border border-white/10">
                  <p className="text-sm text-gray-400 mb-1">Similarity Score</p>
                  <p className="font-bold text-lg text-green-300">
                    {result.similarity ? (result.similarity * 100).toFixed(2) + '%' : 'N/A'}
                  </p>
                </div>
                <div className="glass-card rounded-xl p-4 border border-white/10">
                  <p className="text-sm text-gray-400 mb-1">Processing Time</p>
                  <p className="font-bold text-lg text-cyan-300">
                    {result.processing_time ? result.processing_time.toFixed(3) + 's' : 'N/A'}
                  </p>
                </div>
              </div>

              {/* Metrics */}
              {result.metrics && (
                <div className="mt-6 pt-6 border-t border-white/10">
                  <p className="text-sm font-bold text-gray-300 mb-4 flex items-center gap-2">
                    <span className="text-xl">📊</span>
                    Processing Metrics
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div className="glass-card rounded-lg p-3">
                      <span className="text-gray-400">Face Detected:</span>{' '}
                      <span className={result.metrics.face_detected ? 'text-green-400 font-semibold' : 'text-red-400'}>
                        {result.metrics.face_detected ? '✓ Yes' : '✗ No'}
                      </span>
                    </div>
                    <div className="glass-card rounded-lg p-3">
                      <span className="text-gray-400">Quality:</span>{' '}
                      {result.metrics.enhanced_quality && result.metrics.quality_improvement ? (
                        <>
                          <span className="text-orange-400">{(result.metrics.image_quality! * 100).toFixed(0)}%</span>
                          {' → '}
                          <span className="text-green-400 font-semibold">{(result.metrics.enhanced_quality * 100).toFixed(0)}%</span>
                          <span className="text-green-300 text-xs ml-1">
                            ({result.metrics.quality_improvement > 0 ? '+' : ''}{(result.metrics.quality_improvement * 100).toFixed(0)}%)
                          </span>
                        </>
                      ) : (
                        <span className="text-blue-300 font-semibold">
                          {result.metrics.image_quality ? (result.metrics.image_quality * 100).toFixed(0) + '%' : 'N/A'}
                        </span>
                      )}
                    </div>
                    <div className="glass-card rounded-lg p-3">
                      <span className="text-gray-400">Enhancement Needed:</span>{' '}
                      <span className={result.metrics.enhancement_needed ? 'text-yellow-400' : 'text-green-400 font-semibold'}>
                        {result.metrics.enhancement_needed ? '⚡ Yes' : '✨ No (Good Quality)'}
                      </span>
                    </div>
                    <div className="glass-card rounded-lg p-3">
                      <span className="text-gray-400">Enhanced:</span>{' '}
                      <span className={result.metrics.enhanced ? 'text-blue-400 font-semibold' : 'text-gray-500'}>
                        {result.metrics.enhanced ? '🔧 GFPGAN Applied' : '✗ Not Applied'}
                      </span>
                    </div>
                    {result.metrics.super_resolved && (
                      <div className="glass-card rounded-lg p-3 md:col-span-2">
                        <span className="text-gray-400">Super Resolution:</span>{' '}
                        <span className="text-purple-400 font-semibold">🚀 Applied</span>
                      </div>
                    )}
                    <div className="glass-card rounded-lg p-3 md:col-span-2">
                      <span className="text-gray-400">Face Confidence:</span>{' '}
                      <span className="text-cyan-400 font-semibold">
                        {result.metrics.face_confidence ? (result.metrics.face_confidence * 100).toFixed(0) + '%' : 'N/A'}
                      </span>
                    </div>
                  </div>
                  {result.metrics.enhancement_needed === false && (
                    <div className="mt-4 glass-card border border-green-400/30 rounded-xl p-4 bg-green-500/10">
                      <p className="text-sm text-green-300 flex items-center gap-2">
                        <span className="text-xl">💡</span>
                        Enhancement skipped - image quality is already good!
                      </p>
                    </div>
                  )}
                  {result.metrics.enhanced && (
                    <div className="mt-4 glass-card border border-blue-400/30 rounded-xl p-4 bg-blue-500/10">
                      <p className="text-sm text-blue-300 flex items-center gap-2">
                        <span className="text-xl">🔧</span>
                        Image was enhanced using GFPGAN to improve recognition accuracy
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {!result.success && (
            <div>
              <div className="glass-card border border-red-400/30 rounded-xl p-4 bg-red-500/10 mb-4">
                <p className="text-red-300 flex items-center gap-2">
                  <span className="text-xl">⚠️</span>
                  {result.error || 'No match found - student not in database or similarity below threshold'}
                </p>
              </div>
              
              {/* Show failure reason and advice if available */}
              {result.metrics?.failure_reason && (
                <div className="mb-4 glass-card-strong border border-yellow-400/30 rounded-xl p-5 bg-yellow-500/10">
                  <div className="flex items-start gap-3">
                    <span className="text-3xl">⚠️</span>
                    <div className="flex-1">
                      <p className="font-bold text-yellow-300 mb-2 text-lg">
                        Failure Reason: {result.metrics.failure_reason.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                      </p>
                      {result.metrics.failure_advice && (
                        <p className="text-sm text-yellow-200 flex items-start gap-2">
                          <span>💡</span>
                          <span>{result.metrics.failure_advice}</span>
                        </p>
                      )}
                      {result.metrics.failure_status && (
                        <div className="mt-3 inline-block glass-card px-3 py-1.5 rounded-lg border border-yellow-400/30">
                          <span className="text-xs text-yellow-300 font-medium">
                            Status: {result.metrics.failure_status}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
              
              {/* Show metrics even for failed matches */}
              {result.metrics && (
                <div className="mt-6 pt-6 border-t border-white/10">
                  <p className="text-sm font-bold text-gray-300 mb-4 flex items-center gap-2">
                    <span className="text-xl">📊</span>
                    Processing Metrics
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div className="glass-card rounded-lg p-3">
                      <span className="text-gray-400">Face Detected:</span>{' '}
                      <span className={result.metrics.face_detected ? 'text-green-400 font-semibold' : 'text-red-400 font-semibold'}>
                        {result.metrics.face_detected ? '✓ Yes' : '✗ No'}
                      </span>
                    </div>
                    <div className="glass-card rounded-lg p-3">
                      <span className="text-gray-400">Quality:</span>{' '}
                      {result.metrics.enhanced_quality && result.metrics.quality_improvement ? (
                        <>
                          <span className="text-orange-400">{(result.metrics.image_quality! * 100).toFixed(0)}%</span>
                          {' → '}
                          <span className="text-green-400 font-semibold">{(result.metrics.enhanced_quality * 100).toFixed(0)}%</span>
                          <span className="text-green-300 text-xs ml-1">
                            ({result.metrics.quality_improvement > 0 ? '+' : ''}{(result.metrics.quality_improvement * 100).toFixed(0)}%)
                          </span>
                        </>
                      ) : (
                        <span className="text-blue-300 font-semibold">
                          {result.metrics.image_quality ? (result.metrics.image_quality * 100).toFixed(0) + '%' : 'N/A'}
                        </span>
                      )}
                    </div>
                    <div className="glass-card rounded-lg p-3">
                      <span className="text-gray-400">Enhancement Needed:</span>{' '}
                      <span className={result.metrics.enhancement_needed ? 'text-yellow-400' : 'text-green-400 font-semibold'}>
                        {result.metrics.enhancement_needed ? '⚡ Yes' : '✨ No (Good Quality)'}
                      </span>
                    </div>
                    <div className="glass-card rounded-lg p-3">
                      <span className="text-gray-400">Enhanced:</span>{' '}
                      <span className={result.metrics.enhanced ? 'text-blue-400 font-semibold' : 'text-gray-500'}>
                        {result.metrics.enhanced ? '🔧 GFPGAN Applied' : '✗ Not Applied'}
                      </span>
                    </div>
                    {result.metrics.super_resolved && (
                      <div className="glass-card rounded-lg p-3 md:col-span-2">
                        <span className="text-gray-400">Super Resolution:</span>{' '}
                        <span className="text-purple-400 font-semibold">🚀 Applied</span>
                      </div>
                    )}
                    <div className="glass-card rounded-lg p-3 md:col-span-2">
                      <span className="text-gray-400">Face Confidence:</span>{' '}
                      <span className="text-cyan-400 font-semibold">
                        {result.metrics.face_confidence ? (result.metrics.face_confidence * 100).toFixed(0) + '%' : 'N/A'}
                      </span>
                    </div>
                  </div>
                  
                  {result.metrics.face_detected && !result.metrics.failure_reason && (
                    <div className="mt-4 glass-card border border-blue-400/30 rounded-xl p-4 bg-blue-500/10">
                      <p className="text-sm text-blue-300 flex items-center gap-2">
                        <span className="text-xl">✓</span>
                        Face was detected and processed successfully, but no matching student found in database
                      </p>
                    </div>
                  )}
                  {!result.metrics.face_detected && (
                    <div className="mt-4 glass-card border border-red-400/30 rounded-xl p-4 bg-red-500/10">
                      <p className="text-sm text-red-300 flex items-center gap-2">
                        <span className="text-xl">✗</span>
                        No face detected in the image. Please ensure the image contains a clear, visible face
                      </p>
                    </div>
                  )}
                  {result.metrics.enhancement_needed === false && (
                    <div className="mt-4 glass-card border border-green-400/30 rounded-xl p-4 bg-green-500/10">
                      <p className="text-sm text-green-300 flex items-center gap-2">
                        <span className="text-xl">💡</span>
                        Enhancement skipped - image quality is already good!
                      </p>
                    </div>
                  )}
                  {result.metrics.enhanced && (
                    <div className="mt-4 glass-card border border-blue-400/30 rounded-xl p-4 bg-blue-500/10">
                      <p className="text-sm text-blue-300 flex items-center gap-2">
                        <span className="text-xl">🔧</span>
                        Image was enhanced using GFPGAN to improve recognition accuracy
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
