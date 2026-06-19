import React, { useState, useEffect } from 'react'
import { documentApi } from '../services/api'
import '../styles/DocumentList.css'

export default function DocumentList({ onSelectDocument, refreshTrigger }) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadDocuments()
  }, [refreshTrigger])

  const loadDocuments = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await documentApi.listDocuments(0, 100)
      setDocuments(data || [])
    } catch (err) {
      setError('Erreur chargement documents: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (docId) => {
    if (!window.confirm('Supprimer ce document?')) return
    try {
      await documentApi.deleteDocument(docId)
      setDocuments(documents.filter(d => d.doc_id !== docId))
    } catch (err) {
      setError('Erreur suppression: ' + err.message)
    }
  }

  const handleDownload = async (docId, filename) => {
    try {
      const blob = await documentApi.downloadFile(docId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError('Erreur téléchargement: ' + err.message)
    }
  }

  if (loading) return <div className="container"><p>Chargement...</p></div>
  if (error) return <div className="container error">{error}</div>

  return (
    <div className="container">
      <h2>Documents</h2>
      <button onClick={loadDocuments} className="btn-secondary">
        Actualiser
      </button>

      {documents.length === 0 ? (
        <p className="empty">Aucun document. Uploadez-en un.</p>
      ) : (
        <table className="documents-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Filename</th>
              <th>Status</th>
              <th>Créé</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map(doc => (
              <tr key={doc.doc_id}>
                <td>{doc.doc_id}</td>
                <td>{doc.filename}</td>
                <td>
                  <span className={`status status-${doc.status?.toLowerCase()}`}>
                    {doc.status || 'UNKNOWN'}
                  </span>
                </td>
                <td>{new Date(doc.created_at).toLocaleString()}</td>
                <td className="actions">
                  <button
                    onClick={() => onSelectDocument(doc)}
                    className="btn-small btn-primary"
                  >
                    Voir
                  </button>
                  <button
                    onClick={() => handleDownload(doc.doc_id, doc.filename)}
                    className="btn-small btn-secondary"
                  >
                    Télécharger
                  </button>
                  <button
                    onClick={() => handleDelete(doc.doc_id)}
                    className="btn-small btn-danger"
                  >
                    Supprimer
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
