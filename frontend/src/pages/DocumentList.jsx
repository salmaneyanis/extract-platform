import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { documentService } from '../services/api';

export default function DocumentList() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDocuments = async () => {
    try {
      const data = await documentService.getAllDocuments();
      setDocuments(data.items || data);
    } catch (err) {
      setError("Impossible de charger l'historique des documents.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
    // Système de rafraîchissement automatique toutes les 5 secondes pour suivre le statut PROCESSING
    const interval = setInterval(fetchDocuments, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleDelete = async (id) => {
    if (window.confirm("Êtes-vous sûr de vouloir supprimer ce document ? (Suppression en cascade)")) {
      try {
        await documentService.deleteDocument(id);
        // On s'assure de filtrer sur la bonne clé (doc_id)
        setDocuments(documents.filter(doc => (doc.doc_id || doc.id) !== id));
      } catch (err) {
        alert("Erreur lors de la suppression du fichier.");
      }
    }
  };

  if (loading) return <div className="loader">Chargement de la plateforme d'extraction...</div>;
  if (error) return <div className="error-banner">{error}</div>;

  return (
    <div className="list-container">
      <div className="header-actions">
        <h2>Suivi de l'activité d'extraction (Base PostgreSQL)</h2>
        <Link to="/upload" className="btn-primary">Nouveau traitement</Link>
      </div>

      <table className="documents-table">
        <thead>
          <tr>
            <th>Nom du fichier</th>
            <th>Taille</th>
            <th>Statut du cycle de vie</th>
            <th>Actions applicatives</th>
          </tr>
        </thead>
        <tbody>
          {documents.length === 0 ? (
            <tr><td colSpan="4" style={{ textAlign: 'center' }}>Aucun document sur le serveur.</td></tr>
          ) : (
            documents.map((doc) => {
              // Récupération sécurisée du bon identifiant venant de l'API
              const currentId = doc.doc_id || doc.id;

              return (
                <tr key={currentId}>
                  <td><strong>{doc.file_name || doc.name}</strong></td>
                  <td>{doc.file_size ? (doc.file_size / 1024 / 1024).toFixed(2) : 'N/A'} Mo</td>
                  <td>
                    {/* Gestion visuelle basée sur les status en minuscules (pending, processing, done, failed) */}
                    <span className={`status-badge badge-${doc.status.toLowerCase()}`}>
                      {doc.status}
                    </span>
                  </td>
                  <td>
                    <div className="actions-cell">
                      <Link to={`/document/${currentId}`} className="btn-view">
                        {/* Le statut final de l'API est "done" et non plus "COMPLETED" */}
                        {doc.status === 'done' ? 'Consulter le résultat' : 'Gérer l\'extraction'}
                      </Link>
                      <button onClick={() => handleDelete(currentId)} className="btn-delete">
                        Supprimer
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}