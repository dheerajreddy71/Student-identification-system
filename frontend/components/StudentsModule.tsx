'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Student {
  id: number
  student_id: string
  name: string
  department: string
  year: number
  roll_number: string
  email?: string
  phone?: string
  address?: string
  is_active: boolean
}

interface PaginatedResponse {
  students: Student[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export default function StudentsModule() {
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [limit] = useState(10)
  const [editingStudent, setEditingStudent] = useState<Student | null>(null)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)

  useEffect(() => {
    fetchStudents()
  }, [page, searchTerm])

  const fetchStudents = async () => {
    setLoading(true)
    try {
      const params: any = { page, limit }
      if (searchTerm) {
        params.search = searchTerm
      }
      
      const response = await axios.get<PaginatedResponse>(`${API_URL}/api/students`, {
        params,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      setStudents(response.data.students)
      setTotal(response.data.total)
      setTotalPages(response.data.total_pages)
    } catch (error) {
      console.error('Failed to fetch students:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (value: string) => {
    setSearchTerm(value)
    setPage(1) // Reset to first page on search
  }

  const handleEdit = (student: Student) => {
    setEditingStudent(student)
    setIsEditModalOpen(true)
  }

  const handleDelete = async (student: Student) => {
    if (!confirm(`Are you sure you want to delete ${student.name}?`)) {
      return
    }

    try {
      await axios.delete(`${API_URL}/api/students/${student.student_id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      fetchStudents()
    } catch (error) {
      console.error('Failed to delete student:', error)
      alert('Failed to delete student')
    }
  }

  const handleUpdateStudent = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingStudent) return

    try {
      await axios.put(
        `${API_URL}/api/students/${editingStudent.student_id}`,
        {
          name: editingStudent.name,
          email: editingStudent.email,
          phone: editingStudent.phone,
          address: editingStudent.address
        },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      )
      setIsEditModalOpen(false)
      setEditingStudent(null)
      fetchStudents()
    } catch (error) {
      console.error('Failed to update student:', error)
      alert('Failed to update student')
    }
  }

  return (
    <div className="glass-card rounded-2xl p-8 border border-white/20 float-animation">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <div className="text-4xl">👥</div>
          <h2 className="text-3xl font-bold text-gradient">Student Database</h2>
        </div>
        <div className="glass-card px-4 py-2 rounded-full border border-white/10">
          <span className="text-sm text-gray-300">Total: </span>
          <span className="font-bold text-blue-300">{total}</span>
          <span className="text-sm text-gray-300"> students</span>
        </div>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <input
            type="text"
            placeholder="🔍 Search by name, ID, roll number, or department..."
            value={searchTerm}
            onChange={(e) => handleSearch(e.target.value)}
            className="w-full px-5 py-4 pl-12 glass-card rounded-xl border border-white/10 
                      text-white placeholder-gray-400 focus:outline-none 
                      focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20 
                      transition-all duration-300"
          />
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-2xl">🔍</span>
        </div>
      </div>

      {/* Students Table/Cards */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block w-12 h-12 border-4 border-blue-400/30 border-t-blue-400 rounded-full animate-spin mb-4"></div>
          <p className="text-gray-300">Loading students...</p>
        </div>
      ) : students.length === 0 ? (
        <div className="text-center py-12 glass-card-strong rounded-xl border border-white/10">
          <div className="text-6xl mb-4">🔍</div>
          <p className="text-gray-300 text-lg">No students found</p>
          <p className="text-gray-400 text-sm mt-2">Try adjusting your search criteria</p>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto rounded-xl mb-6">
            <table className="min-w-full">
              <thead>
                <tr className="glass-card-strong border-b border-white/10">
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Student ID
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Department
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Year
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Roll Number
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {students.map((student, index) => (
                  <tr 
                    key={student.id} 
                    className="glass-card hover:glass-card-strong transition-all duration-300 hover:scale-[1.02] group"
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-blue-300">
                      {student.student_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                      {student.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className="px-3 py-1 rounded-lg glass-card border border-purple-400/30 text-purple-300">
                        {student.department}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      Year {student.year}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-cyan-300">
                      {student.roll_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {student.email || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleEdit(student)}
                          className="px-3 py-1.5 glass-card border border-blue-400/30 text-blue-300 rounded-lg 
                                    hover:bg-blue-500/20 transition-all duration-300"
                        >
                          ✏️ Edit
                        </button>
                        <button
                          onClick={() => handleDelete(student)}
                          className="px-3 py-1.5 glass-card border border-red-400/30 text-red-300 rounded-lg 
                                    hover:bg-red-500/20 transition-all duration-300"
                        >
                          🗑️ Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between glass-card-strong rounded-xl p-4 border border-white/10">
            <div className="text-sm text-gray-300">
              Showing {students.length} of {total} students (Page {page} of {totalPages})
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                  page === 1
                    ? 'glass-card text-gray-500 cursor-not-allowed'
                    : 'glass-card border border-blue-400/30 text-blue-300 hover:bg-blue-500/20'
                }`}
              >
                ← Previous
              </button>
              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum
                  if (totalPages <= 5) {
                    pageNum = i + 1
                  } else if (page <= 3) {
                    pageNum = i + 1
                  } else if (page >= totalPages - 2) {
                    pageNum = totalPages - 4 + i
                  } else {
                    pageNum = page - 2 + i
                  }
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setPage(pageNum)}
                      className={`w-10 h-10 rounded-lg font-medium transition-all duration-300 ${
                        page === pageNum
                          ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
                          : 'glass-card border border-white/10 text-gray-300 hover:border-blue-400/30'
                      }`}
                    >
                      {pageNum}
                    </button>
                  )
                })}
              </div>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                  page === totalPages
                    ? 'glass-card text-gray-500 cursor-not-allowed'
                    : 'glass-card border border-blue-400/30 text-blue-300 hover:bg-blue-500/20'
                }`}
              >
                Next →
              </button>
            </div>
          </div>
        </>
      )}

      {/* Edit Modal */}
      {isEditModalOpen && editingStudent && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass-card-strong rounded-2xl p-8 border border-white/20 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h3 className="text-2xl font-bold text-gradient mb-6">Edit Student</h3>
            <form onSubmit={handleUpdateStudent} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Name</label>
                <input
                  type="text"
                  value={editingStudent.name}
                  onChange={(e) => setEditingStudent({ ...editingStudent, name: e.target.value })}
                  className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                            text-white placeholder-gray-400 focus:outline-none 
                            focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                <input
                  type="email"
                  value={editingStudent.email || ''}
                  onChange={(e) => setEditingStudent({ ...editingStudent, email: e.target.value })}
                  className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                            text-white placeholder-gray-400 focus:outline-none 
                            focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Phone</label>
                <input
                  type="tel"
                  value={editingStudent.phone || ''}
                  onChange={(e) => setEditingStudent({ ...editingStudent, phone: e.target.value })}
                  className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                            text-white placeholder-gray-400 focus:outline-none 
                            focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Address</label>
                <textarea
                  value={editingStudent.address || ''}
                  onChange={(e) => setEditingStudent({ ...editingStudent, address: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-3 glass-card rounded-xl border border-white/10 
                            text-white placeholder-gray-400 focus:outline-none 
                            focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20 resize-none"
                />
              </div>
              <div className="flex gap-3 mt-6">
                <button
                  type="submit"
                  className="flex-1 py-3 rounded-xl font-bold bg-gradient-to-r from-blue-500 to-cyan-500 
                            text-white shadow-lg hover:shadow-blue-500/50 transition-all duration-300"
                >
                  💾 Save Changes
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setIsEditModalOpen(false)
                    setEditingStudent(null)
                  }}
                  className="flex-1 py-3 rounded-xl font-bold glass-card border border-white/10 
                            text-gray-300 hover:bg-white/5 transition-all duration-300"
                >
                  ✖️ Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
