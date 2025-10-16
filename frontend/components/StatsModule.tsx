'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function StatsModule() {
  const [stats, setStats] = useState<any>(null)
  const [logs, setLogs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
    fetchLogs()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/stats`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const fetchLogs = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/logs?limit=50`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      setLogs(response.data)
    } catch (error) {
      console.error('Failed to fetch logs:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white shadow rounded-lg p-6">
            <div className="text-sm text-gray-600 mb-1">Total Students</div>
            <div className="text-3xl font-bold text-primary-600">{stats.total_students}</div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <div className="text-sm text-gray-600 mb-1">Total Identifications</div>
            <div className="text-3xl font-bold text-primary-600">{stats.total_identifications}</div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <div className="text-sm text-gray-600 mb-1">Success Rate (24h)</div>
            <div className="text-3xl font-bold text-green-600">{stats.success_rate.toFixed(1)}%</div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <div className="text-sm text-gray-600 mb-1">Avg Latency</div>
            <div className="text-3xl font-bold text-blue-600">{stats.average_latency.total.toFixed(2)}s</div>
          </div>
        </div>
      )}

      {/* Performance Metrics */}
      {stats && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-xl font-bold mb-4">Performance Metrics (Last 24h)</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-600">Preprocessing</div>
              <div className="text-lg font-semibold">{(stats.average_latency.preprocessing * 1000).toFixed(0)}ms</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Embedding</div>
              <div className="text-lg font-semibold">{(stats.average_latency.embedding * 1000).toFixed(0)}ms</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Search</div>
              <div className="text-lg font-semibold">{(stats.average_latency.search * 1000).toFixed(0)}ms</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Total</div>
              <div className="text-lg font-semibold">{(stats.average_latency.total * 1000).toFixed(0)}ms</div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Identification Logs */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-xl font-bold mb-4">Recent Identifications</h3>
        
        {loading ? (
          <div className="text-center py-8">
            <p className="text-gray-500">Loading logs...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">No logs found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Student ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Similarity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Time
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {log.student_id || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.similarity_score ? `${(log.similarity_score * 100).toFixed(1)}%` : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded ${log.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                        {log.success ? '✓ Success' : '✗ Failed'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.total_time.toFixed(2)}s
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
