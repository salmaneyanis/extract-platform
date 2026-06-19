import React, { useState } from 'react'
import DocumentList from './pages/DocumentList'
import DocumentUpload from './pages/DocumentUpload'
import DocumentDetail from './pages/DocumentDetail'
import './App.css'

export default function App() {
  const [currentView, setCurrentView] = useState('list') // 'list', 'upload', 'detail'
  const [selectedDocument, setSelectedDocument] = useState(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleSelectDocument = (doc) => {
    setSelectedDocument(doc)
    setCurrentView('detail')
  }

  const handleDocumentProcessed = (result) => {
    setRefreshTrigger(prev => prev + 1)
    setCurrentView('list')
  }

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  const handleBack = () => {
    setCurrentView('list')
    setSelectedDocument(null)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>📄 Plateforme d'Extraction Docling</h1>
        <nav className="nav">
          <button
            onClick={() => setCurrentView('list')}
            className={`nav-btn ${currentView === 'list' ? 'active' : ''}`}
          >
            Liste
          </button>
          <button
            onClick={() => setCurrentView('upload')}
            className={`nav-btn ${currentView === 'upload' ? 'active' : ''}`}
          >
            Nouveau
          </button>
        </nav>
      </header>

      <main className="main">
        {currentView === 'list' && (
          <DocumentList
            onSelectDocument={handleSelectDocument}
            refreshTrigger={refreshTrigger}
          />
        )}

        {currentView === 'upload' && (
          <DocumentUpload
            onDocumentProcessed={handleDocumentProcessed}
            onRefresh={handleRefresh}
          />
        )}

        {currentView === 'detail' && selectedDocument && (
          <DocumentDetail
            document={selectedDocument}
            onBack={handleBack}
          />
        )}
      </main>

      <footer className="footer">
        <p>TALIUM - Extraction Intelligente de Documents Financiers</p>
        <p className="version">v0.1.0</p>
      </footer>
    </div>
  )
}
