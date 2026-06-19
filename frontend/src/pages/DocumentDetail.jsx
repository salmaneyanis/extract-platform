import React, { useState, useEffect } from 'react'
import { documentApi } from '../services/api'
import '../styles/DocumentDetail.css'

export default function DocumentDetail({ document, onBack }) {
  const [parses, setParses] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('info')
  const [extracting, setExtracting] = useState(false)
  const [profile, setProfile] = useState('balanced')

  useEffect(() => {
    if (document) {
      loadParses()
    }
  }, [document])

  const loadParses = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await documentApi.getDocumentParses(document.doc_id)
      setParses(data)
    } catch (err) {
      setError('Erreur chargement extractions: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleExtract = async () => {
    setExtracting(true)
    setError(null)
    try {
      const result = await documentApi.extractDocument(document.doc_id, profile)
      loadParses()
    } catch (err) {
      setError('Erreur extraction: ' + err.message)
    } finally {
      setExtracting(false)
    }
  }

  if (!document) return null

  return (
    <div className="detail-container">
      <button onClick={onBack} className="btn-secondary btn-back">
        ← Retour
      </button>

      <h2>{document.filename}</h2>

      <div className="document-meta">
        <div className="meta-item">
          <strong>ID:</strong> {document.doc_id}
        </div>
        <div className="meta-item">
          <strong>Status:</strong>
          <span className={`status status-${document.status?.toLowerCase()}`}>
            {document.status}
          </span>
        </div>
        <div className="meta-item">
          <strong>Créé:</strong> {new Date(document.created_at).toLocaleString()}
        </div>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'info' ? 'active' : ''}`}
          onClick={() => setActiveTab('info')}
        >
          Infos
        </button>
        <button
          className={`tab ${activeTab === 'parses' ? 'active' : ''}`}
          onClick={() => setActiveTab('parses')}
        >
          Extractions
        </button>
      </div>

      {activeTab === 'info' && (
        <div className="tab-content">
          <div className="extract-section">
            <h3>Extraction</h3>
            <div className="extract-controls">
              <select
                value={profile}
                onChange={(e) => setProfile(e.target.value)}
                disabled={extracting}
              >
                <option value="fast">Fast</option>
                <option value="balanced">Balanced</option>
                <option value="accurate">Accurate</option>
              </select>
              <button
                onClick={handleExtract}
                disabled={extracting}
                className="btn-primary"
              >
                {extracting ? 'Extraction...' : 'Extraire'}
              </button>
            </div>
            {error && <div className="error">{error}</div>}
          </div>
        </div>
      )}

      {activeTab === 'parses' && (
        <div className="tab-content">
          {loading ? (
            <p>Chargement extractions...</p>
          ) : error ? (
            <div className="error">{error}</div>
          ) : parses?.parses && parses.parses.length > 0 ? (
            <div className="parses-list">
              {parses.parses.map((parse, idx) => (
                <div key={parse.parse_id} className="parse-item">
                  <h4>Extraction {idx + 1}</h4>
                  <p className="parse-meta">ID: {parse.parse_id}</p>

                  {parse.content_text && (
                    <div className="parse-section">
                      <h5>Texte extrait</h5>
                      <div className="text-preview">
                        {parse.content_text.substring(0, 500)}...
                      </div>
                    </div>
                  )}

                  {parse.content_json && (
                    <div className="parse-section">
                      <h5>Structure JSON</h5>
                      <details>
                        <summary>Voir JSON complet</summary>
                        <pre className="json-preview">
                          {JSON.stringify(parse.content_json, null, 2).substring(0, 1000)}...
                        </pre>
                      </details>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="empty">Aucune extraction. Cliquez "Extraire" pour commencer.</p>
          )}
        </div>
      )}
    </div>
  )
}
