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

  const handleDeleteLog = async (logId: number) => {
    if (!confirm('Are you sure you want to delete this log?')) {
      return
    }

    try {
      await axios.delete(`${API_URL}/api/logs/${logId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      fetchLogs()
      fetchStats()
    } catch (error) {
      console.error('Failed to delete log:', error)
      alert('Failed to delete log')
    }
  }

  const handleDeleteAllLogs = async () => {
    if (!confirm('Are you sure you want to delete ALL logs? This action cannot be undone!')) {
      return
    }

    try {
      await axios.delete(`${API_URL}/api/logs`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      fetchLogs()
      fetchStats()
    } catch (error) {
      console.error('Failed to delete all logs:', error)
      alert('Failed to delete all logs')
    }
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 float-animation">
          <div className="glass-card-strong rounded-2xl p-6 border border-white/20 hover:scale-105 transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-gray-400 font-medium">Total Students</div>
              <div className="text-3xl">👥</div>
            </div>
            <div className="text-4xl font-bold text-gradient">{stats.total_students}</div>
          </div>

          <div className="glass-card-strong rounded-2xl p-6 border border-white/20 hover:scale-105 transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-gray-400 font-medium">Total Identifications</div>
              <div className="text-3xl">🔍</div>
            </div>
            <div className="text-4xl font-bold text-blue-300">{stats.total_identifications}</div>
          </div>

          <div className="glass-card-strong rounded-2xl p-6 border border-white/20 hover:scale-105 transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-gray-400 font-medium">Avg Latency</div>
              <div className="text-3xl">⚡</div>
            </div>
            <div className="text-4xl font-bold text-cyan-300">{stats.average_latency.total.toFixed(2)}s</div>
          </div>
        </div>
      )}

      {/* Performance Metrics */}
      {stats && (
        <div className="glass-card rounded-2xl p-8 border border-white/20">
          <div className="flex items-center gap-3 mb-6">
            <div className="text-3xl">📊</div>
            <h3 className="text-2xl font-bold text-gradient">Performance Metrics (Last 24h)</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
            <div className="glass-card rounded-xl p-4 border border-white/10 hover:border-blue-400/30 transition-all duration-300">
              <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                <span className="text-lg">🔄</span>
                Preprocessing
              </div>
              <div className="text-2xl font-bold text-blue-300">{(stats.average_latency.preprocessing * 1000).toFixed(0)}ms</div>
            </div>
            <div className="glass-card rounded-xl p-4 border border-white/10 hover:border-purple-400/30 transition-all duration-300">
              <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                <span className="text-lg">🧠</span>
                Embedding
              </div>
              <div className="text-2xl font-bold text-purple-300">{(stats.average_latency.embedding * 1000).toFixed(0)}ms</div>
            </div>
            <div className="glass-card rounded-xl p-4 border border-white/10 hover:border-green-400/30 transition-all duration-300">
              <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                <span className="text-lg">🔍</span>
                Search
              </div>
              <div className="text-2xl font-bold text-green-300">{(stats.average_latency.search * 1000).toFixed(0)}ms</div>
            </div>
            <div className="glass-card rounded-xl p-4 border border-white/10 hover:border-cyan-400/30 transition-all duration-300">
              <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                <span className="text-lg">⚡</span>
                Total
              </div>
              <div className="text-2xl font-bold text-cyan-300">{(stats.average_latency.total * 1000).toFixed(0)}ms</div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Identification Logs */}
      <div className="glass-card rounded-2xl p-8 border border-white/20">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="text-3xl">📜</div>
            <h3 className="text-2xl font-bold text-gradient">Recent Identifications</h3>
          </div>
          {logs.length > 0 && (
            <button
              onClick={handleDeleteAllLogs}
              className="px-4 py-2 glass-card border border-red-400/30 text-red-300 rounded-lg 
                        hover:bg-red-500/20 transition-all duration-300 font-medium"
            >
              🗑️ Delete All Logs
            </button>
          )}
        </div>
        
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block w-12 h-12 border-4 border-blue-400/30 border-t-blue-400 rounded-full animate-spin mb-4"></div>
            <p className="text-gray-300">Loading logs...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-12 glass-card-strong rounded-xl border border-white/10">
            <div className="text-6xl mb-4">📋</div>
            <p className="text-gray-300 text-lg">No logs found</p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl">
            <table className="min-w-full">
              <thead>
                <tr className="glass-card-strong border-b border-white/10">
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Student ID
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Similarity
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Time
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {logs.map((log, index) => (
                  <tr 
                    key={log.id}
                    className="glass-card hover:glass-card-strong transition-all duration-300"
                    style={{ animationDelay: `${index * 30}ms` }}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-blue-300">
                      {log.student_id || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-purple-300">
                      {log.similarity_score ? `${(log.similarity_score * 100).toFixed(1)}%` : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1.5 text-xs font-semibold rounded-lg glass-card border ${
                        log.success 
                          ? 'border-green-400/30 text-green-300 bg-green-500/10' 
                          : 'border-red-400/30 text-red-300 bg-red-500/10'
                      }`}>
                        {log.success ? '✓ Success' : '✗ Failed'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-cyan-300 font-medium">
                      {log.total_time.toFixed(2)}s
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => handleDeleteLog(log.id)}
                        className="px-3 py-1.5 glass-card border border-red-400/30 text-red-300 rounded-lg 
                                  hover:bg-red-500/20 transition-all duration-300"
                      >
                        🗑️ Delete
                      </button>
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
