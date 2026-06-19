import React, { useState, useRef } from 'react'
import { documentApi } from '../services/api'
import '../styles/DocumentUpload.css'

export default function DocumentUpload({ onDocumentProcessed, onRefresh }) {
  const [file, setFile] = useState(null)
  const [profile, setProfile] = useState('balanced')
  const [device, setDevice] = useState('auto')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [uploadMode, setUploadMode] = useState('process') // 'process' or 'uploadOnly'
  const fileInputRef = useRef(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError(null)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Sélectionnez un fichier')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      let result
      if (uploadMode === 'process') {
        result = await documentApi.processDocument(file, profile, device)
      } else {
        result = await documentApi.uploadDocument(file)
      }

      setSuccess(
        uploadMode === 'process'
          ? `Document traité! Job ID: ${result.job_id}, Doc ID: ${result.doc_id}`
          : `Document uploadé! Doc ID: ${result.doc_id}`
      )

      setFile(null)
      fileInputRef.current.value = ''

      if (onDocumentProcessed) {
        onDocumentProcessed(result)
      }
      if (onRefresh) {
        setTimeout(onRefresh, 1500)
      }
    } catch (err) {
      setError('Erreur: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h2>Nouveau Document</h2>

      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label>Mode:</label>
          <div className="radio-group">
            <label>
              <input
                type="radio"
                value="process"
                checked={uploadMode === 'process'}
                onChange={(e) => setUploadMode(e.target.value)}
              />
              Upload + Extraction
            </label>
            <label>
              <input
                type="radio"
                value="uploadOnly"
                checked={uploadMode === 'uploadOnly'}
                onChange={(e) => setUploadMode(e.target.value)}
              />
              Upload seulement
            </label>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="file">Fichier PDF:</label>
          <input
            id="file"
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            ref={fileInputRef}
            required
          />
          {file && <p className="file-info">✓ {file.name}</p>}
        </div>

        {uploadMode === 'process' && (
          <>
            <div className="form-group">
              <label htmlFor="profile">Profil extraction:</label>
              <select
                id="profile"
                value={profile}
                onChange={(e) => setProfile(e.target.value)}
              >
                <option value="fast">Fast (5s, simple)</option>
                <option value="balanced">Balanced (7s, défaut)</option>
                <option value="accurate">Accurate (20-30s, précis)</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="device">Device:</label>
              <select
                id="device"
                value={device}
                onChange={(e) => setDevice(e.target.value)}
              >
                <option value="auto">Auto</option>
                <option value="cpu">CPU</option>
                <option value="cuda">CUDA (GPU)</option>
              </select>
            </div>
          </>
        )}

        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}

        <button
          type="submit"
          disabled={loading || !file}
          className="btn-primary btn-large"
        >
          {loading ? 'Traitement...' : 'Envoyer'}
        </button>
      </form>
    </div>
  )
}
