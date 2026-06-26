import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import DocumentList from './pages/DocumentList';
import DocumentUpload from './pages/DocumentUpload';
import DocumentDetail from './pages/DocumentDetail';
import './App.css';

export default function App() {
  return (
    <Router>
      <div className="app-wrapper">
        <header className="app-header">
          <div className="logo-area">
            <h1>TALIUM</h1>
            <span>Plateforme d'Extraction Intelligente de Documents</span>
          </div>
          <nav className="main-nav">
            <Link to="/">Tableau de suivi</Link>
            <Link to="/upload" className="nav-accent">Extraire un PDF</Link>
          </nav>
        </header>

        <main className="app-main-content">
          <Routes>
            <Route path="/" element={<DocumentList />} />
            <Route path="/upload" element={<DocumentUpload />} />
            <Route path="/document/:id" element={<DocumentDetail />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>© 2026 TALIUM R&D - Solution locale de parsing de documents financiers conforme RGPD[cite: 31, 39, 50].</p>
        </footer>
      </div>
    </Router>
  );
}