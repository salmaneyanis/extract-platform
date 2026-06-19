import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const documentApi = {
  // Upload + extract
  processDocument: async (file, profile = 'balanced', device = 'auto') => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('profile', profile)
    formData.append('device', device)
    formData.append('output_format', 'markdown')

    const response = await api.post('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  // Upload only
  uploadDocument: async (file) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  // Extract uploaded doc
  extractDocument: async (docId, profile = 'balanced', device = 'auto') => {
    const formData = new FormData()
    formData.append('profile', profile)
    formData.append('device', device)
    formData.append('output_format', 'markdown')

    const response = await api.post(`/documents/${docId}/extract`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  // List documents
  listDocuments: async (skip = 0, limit = 100) => {
    const response = await api.get('/documents', {
      params: { skip, limit }
    })
    return response.data
  },

  // Get single document
  getDocument: async (docId) => {
    const response = await api.get(`/documents/${docId}`)
    return response.data
  },

  // Get document parses
  getDocumentParses: async (docId) => {
    const response = await api.get(`/documents/${docId}/parse`)
    return response.data
  },

  // Download file
  downloadFile: async (docId) => {
    const response = await api.get(`/documents/${docId}/file`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Delete document
  deleteDocument: async (docId) => {
    await api.delete(`/documents/${docId}`)
  },

  // Update document
  updateDocument: async (docId, data) => {
    const response = await api.patch(`/documents/${docId}`, data)
    return response.data
  }
}

export default api
