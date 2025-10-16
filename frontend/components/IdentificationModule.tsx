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
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Identify Student</h2>
        
        {/* Upload or Webcam Toggle */}
        <div className="mb-4 flex space-x-4">
          <button
            onClick={() => setUseWebcam(false)}
            className={`px-4 py-2 rounded ${!useWebcam ? 'bg-primary-600 text-white' : 'bg-gray-200'}`}
          >
            📤 Upload Photo
          </button>
          <button
            onClick={() => setUseWebcam(true)}
            className={`px-4 py-2 rounded ${useWebcam ? 'bg-primary-600 text-white' : 'bg-gray-200'}`}
          >
            📷 Use Webcam
          </button>
        </div>

        {/* Image Input */}
        {!useWebcam ? (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Image
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded file:border-0
                file:text-sm file:font-semibold
                file:bg-primary-50 file:text-primary-700
                hover:file:bg-primary-100"
            />
          </div>
        ) : (
          <div className="mb-4">
            <Webcam
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              className="w-full rounded border"
            />
            <button
              onClick={captureFromWebcam}
              className="mt-2 w-full bg-primary-600 text-white py-2 rounded hover:bg-primary-700"
            >
              📸 Capture Photo
            </button>
          </div>
        )}

        {/* Preview */}
        {preview && (
          <div className="mb-4">
            <img
              src={preview}
              alt="Preview"
              className="max-w-md mx-auto rounded border"
            />
          </div>
        )}

        {/* Identify Button */}
        <button
          onClick={identifyStudent}
          disabled={!selectedFile || loading}
          className={`w-full py-3 rounded font-semibold text-white
            ${!selectedFile || loading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-primary-600 hover:bg-primary-700'
            }`}
        >
          {loading ? '🔄 Identifying...' : '🔍 Identify Student'}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className={`bg-white shadow rounded-lg p-6 ${result.success ? 'border-l-4 border-green-500' : 'border-l-4 border-red-500'}`}>
          <h3 className="text-xl font-bold mb-4">
            {result.success ? '✓ Student Identified' : '✗ No Match Found'}
          </h3>

          {result.success && result.student && (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Student ID</p>
                  <p className="font-semibold">{result.student?.student_id || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Name</p>
                  <p className="font-semibold">{result.student?.name || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Department</p>
                  <p className="font-semibold">{result.student?.department || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Roll Number</p>
                  <p className="font-semibold">{result.student?.roll_number || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Similarity Score</p>
                  <p className="font-semibold">{result.similarity ? (result.similarity * 100).toFixed(2) + '%' : 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Processing Time</p>
                  <p className="font-semibold">{result.processing_time ? result.processing_time.toFixed(3) + 's' : 'N/A'}</p>
                </div>
              </div>

              {/* Metrics */}
              {result.metrics && (
                <div className="mt-4 pt-4 border-t">
                  <p className="text-sm font-semibold text-gray-700 mb-2">Processing Metrics</p>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>Face Detected: {result.metrics.face_detected ? '✓' : '✗'}</div>
                    <div>
                      Quality: {
                        result.metrics.enhanced_quality && result.metrics.quality_improvement ? (
                          <>
                            {(result.metrics.image_quality! * 100).toFixed(0)}% → {(result.metrics.enhanced_quality * 100).toFixed(0)}%
                            <span className="text-green-600 font-semibold"> ({result.metrics.quality_improvement > 0 ? '+' : ''}{(result.metrics.quality_improvement * 100).toFixed(0)}%)</span>
                          </>
                        ) : (
                          result.metrics.image_quality ? (result.metrics.image_quality * 100).toFixed(0) + '%' : 'N/A'
                        )
                      }
                    </div>
                    <div>Enhancement Needed: {result.metrics.enhancement_needed ? '⚡ Yes' : '✨ No (Good Quality)'}</div>
                    <div>Enhanced: {result.metrics.enhanced ? '🔧 GFPGAN Applied' : '✗'}</div>
                    {result.metrics.super_resolved && (
                      <div className="col-span-2">Super Resolution: 🚀 Applied</div>
                    )}
                    <div>Face Confidence: {result.metrics.face_confidence ? (result.metrics.face_confidence * 100).toFixed(0) + '%' : 'N/A'}</div>
                  </div>
                  {result.metrics.enhancement_needed === false && (
                    <div className="mt-2 text-xs text-green-600 bg-green-50 p-2 rounded">
                      💡 Enhancement skipped - image quality is already good!
                    </div>
                  )}
                  {result.metrics.enhanced && (
                    <div className="mt-2 text-xs text-blue-600 bg-blue-50 p-2 rounded">
                      🔧 Image was enhanced using GFPGAN to improve recognition accuracy
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {!result.success && (
            <div>
              <p className="text-red-600 mb-4">
                {result.error || 'No match found - student not in database or similarity below threshold'}
              </p>
              
              {/* Show metrics even for failed matches */}
              {result.metrics && (
                <div className="mt-4 pt-4 border-t">
                  <p className="text-sm font-semibold text-gray-700 mb-2">Processing Metrics</p>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>Face Detected: {result.metrics.face_detected ? '✓' : '✗'}</div>
                    <div>
                      Quality: {
                        result.metrics.enhanced_quality && result.metrics.quality_improvement ? (
                          <>
                            {(result.metrics.image_quality! * 100).toFixed(0)}% → {(result.metrics.enhanced_quality * 100).toFixed(0)}%
                            <span className="text-green-600 font-semibold"> ({result.metrics.quality_improvement > 0 ? '+' : ''}{(result.metrics.quality_improvement * 100).toFixed(0)}%)</span>
                          </>
                        ) : (
                          result.metrics.image_quality ? (result.metrics.image_quality * 100).toFixed(0) + '%' : 'N/A'
                        )
                      }
                    </div>
                    <div>Enhancement Needed: {result.metrics.enhancement_needed ? '⚡ Yes' : '✨ No (Good Quality)'}</div>
                    <div>Enhanced: {result.metrics.enhanced ? '🔧 GFPGAN Applied' : '✗'}</div>
                    {result.metrics.super_resolved && (
                      <div className="col-span-2">Super Resolution: 🚀 Applied</div>
                    )}
                    <div>Face Confidence: {result.metrics.face_confidence ? (result.metrics.face_confidence * 100).toFixed(0) + '%' : 'N/A'}</div>
                  </div>
                  
                  {result.metrics.face_detected && (
                    <div className="mt-2 text-xs text-blue-600 bg-blue-50 p-2 rounded">
                      ✓ Face was detected and processed successfully, but no matching student found in database
                    </div>
                  )}
                  {!result.metrics.face_detected && (
                    <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded">
                      ✗ No face detected in the image. Please ensure the image contains a clear, visible face
                    </div>
                  )}
                  {result.metrics.enhancement_needed === false && (
                    <div className="mt-2 text-xs text-green-600 bg-green-50 p-2 rounded">
                      💡 Enhancement skipped - image quality is already good!
                    </div>
                  )}
                  {result.metrics.enhanced && (
                    <div className="mt-2 text-xs text-blue-600 bg-blue-50 p-2 rounded">
                      🔧 Image was enhanced using GFPGAN to improve recognition accuracy
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
