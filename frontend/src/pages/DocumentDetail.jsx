import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { documentService } from '../services/api';

export default function DocumentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [document, setDocument] = useState(null);
  const [parses, setParses] = useState([]); 
  const [extractLoading, setExtractLoading] = useState(false);
  const [extractError, setExtractError] = useState(null);

  // États pour la configuration d'une nouvelle extraction
  const [profile, setProfile] = useState('balanced');
  const [device, setDevice] = useState('cpu');

  const loadDocumentData = async () => {
    try {
      const docData = await documentService.getDocument(id);
      setDocument(docData);

      // Récupération de l'historique des analyses (parses)
      const parsesResponse = await documentService.getDocumentParses ? 
        await documentService.getDocumentParses(id) : 
        await fetch(`http://localhost:8000/documents/${id}/parse`).then(res => res.json());
      
      if (parsesResponse && parsesResponse.parses) {
        setParses(parsesResponse.parses);
      } else if (Array.isArray(parsesResponse)) {
        setParses(parsesResponse);
      }
    } catch (err) {
      setExtractError("Erreur lors de la récupération des données du document.");
    }
  };

  // Gestion du rechargement automatique toutes les 5 secondes
  useEffect(() => {
    // 1. Charger les données immédiatement au montage de la page
    loadDocumentData();

    // 2. Mettre en place le compteur si le document n'est pas encore terminé
    const intervalId = setInterval(() => {
      // On rafraîchit uniquement si le document est en cours ou en attente
      if (document && (document.status === 'pending' || document.status === 'processing')) {
        console.log("Polling actif : Rafraîchissement de la fiche document...");
        loadDocumentData();
      }
    }, 5000); // 5000 millisecondes = 5 secondes

    // 3. NETTOYAGE : Coupe le compteur dès qu'on change de page
    return () => clearInterval(intervalId);
  }, [id, document?.status]); // Re-déclenche si l'ID ou le statut change

  // Déclenchement d'une nouvelle extraction
  const handleLaunchExtract = async (e) => {
    e.preventDefault();
    setExtractLoading(true);
    setExtractError(null);
    try {
      await documentService.extractOnly(id, {
        profile: profile,
        device: device,
        output_format: 'both'
      });
      // Rechargement des données pour voir la nouvelle ligne apparaître dans l'historique
      await loadDocumentData(); 
    } catch (err) {
      setExtractError(err.response?.data?.detail || "L'extraction a échoué au niveau du moteur Docling.");
    } finally {
      setExtractLoading(false);
    }
  };

  // Fonction utilitaire pour déclencher le téléchargement d'un fichier texte
  const triggerDownload = (content, filename, contentType) => {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const link = window.document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (!document) return <div className="loader">Analyse de la persistance en cours...</div>;

  const displayId = document.doc_id || document.id;
  const displayFileName = document.file_name || document.name;
  const displayStatus = (document.status || '').toLowerCase();
  
  const formattedDate = document.created_at 
    ? new Date(document.created_at).toLocaleString('fr-FR', { dateStyle: 'long', timeStyle: 'short' })
    : 'Inconnue';

  const baseName = displayFileName ? displayFileName.replace(/\.[^/.]+$/, "") : `document_${displayId}`;

  return (
    <div className="detail-container" style={{ padding: '20px', maxWidth: '1000px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      
      {/* En-tête de navigation */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, color: '#1a202c' }}>Fiche Document : {displayFileName}</h2>
        <button 
          onClick={() => navigate('/')} 
          style={{ padding: '8px 16px', background: '#4a5568', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: '500' }}
        >
          ← Retour au tableau de suivi
        </button>
      </div>

      {extractError && (
        <div style={{ color: '#721c24', background: '#f8d7da', border: '1px solid #f5c6cb', padding: '12px', borderRadius: '4px', marginBottom: '20px', fontWeight: '500' }}>
          ⚠️ {extractError}
        </div>
      )}
      
      {/* SECTION 1 : Métadonnées Globales */}
      <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '25px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
        <h3 style={{ marginTop: 0, borderBottom: '2px solid #edf2f7', paddingBottom: '8px', color: '#2d3748' }}>📋 Informations Générales</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '15px' }}>
          <p style={{ margin: 0 }}><strong>Identifiant système :</strong> {displayId}</p>
          <p style={{ margin: 0 }}><strong>Statut actuel :</strong> <span className={`status-badge badge-${displayStatus}`} style={{ fontWeight: 'bold', textTransform: 'uppercase' }}>{document.status}</span></p>
          <p style={{ margin: 0 }}><strong>Date d'importation :</strong> {formattedDate}</p>
          <p style={{ margin: 0 }}><strong>Type MIME :</strong> {document.content_type || 'application/pdf'}</p>
          <p style={{ margin: 0 }}><strong>Taille du fichier :</strong> {document.file_size ? `${(document.file_size / 1024 / 1024).toFixed(2)} Mo` : 'N/A'}</p>
          <p style={{ margin: 0 }}><strong>Dossier cible :</strong> {document.category || 'originals'}</p>
        </div>
      </div>

      {/* SECTION 2 : Formulaire pour REFAIRE une extraction */}
      <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '25px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
        <h3 style={{ marginTop: 0, borderBottom: '2px solid #edf2f7', paddingBottom: '8px', color: '#2d3748' }}>🔄 Exécuter une nouvelle extraction</h3>
        <p style={{ color: '#4a5568', fontSize: '14px', marginTop: '8px' }}>
          Vous pouvez soumettre à nouveau ce document au moteur de traitement Docling en modifiant le profil de précision ou l'architecture matérielle.
        </p>
        <form onSubmit={handleLaunchExtract} style={{ display: 'flex', gap: '20px', alignItems: 'center', marginTop: '15px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <label style={{ fontSize: '13px', fontWeight: 'bold', color: '#4a5568' }}>Profil :</label>
            <select value={profile} onChange={(e) => setProfile(e.target.value)} style={{ padding: '6px 12px', borderRadius: '4px', border: '1px solid #cbd5e0' }}>
              <option value="fast">FAST (Léger / OCR rapide)</option>
              <option value="balanced">BALANCED (Recommandé / Équilibré)</option>
              <option value="accurate">ACCURATE (Lourd / Analyse poussée)</option>
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <label style={{ fontSize: '13px', fontWeight: 'bold', color: '#4a5568' }}>Matériel :</label>
            <select value={device} onChange={(e) => setDevice(e.target.value)} style={{ padding: '6px 12px', borderRadius: '4px', border: '1px solid #cbd5e0' }}>
              <option value="cpu">CPU (Processeur hôte)</option>
              <option value="cuda">CUDA (Accélération Carte Graphique)</option>
            </select>
          </div>

          <button 
            type="submit" 
            disabled={extractLoading} 
            style={{ 
              padding: '8px 20px', 
              background: extractLoading ? '#a0aec0' : '#3182ce', 
              color: '#fff', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: extractLoading ? 'not-allowed' : 'pointer',
              fontWeight: 'bold',
              alignSelf: 'flex-end',
              height: '36px'
            }}
          >
            {extractLoading ? 'Moteur Docling actif...' : 'Lancer le traitement'}
          </button>
        </form>
      </div>

      {/* SECTION 3 : Historique des extractions et Téléchargements */}
      <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
        <h3 style={{ marginTop: 0, borderBottom: '2px solid #edf2f7', paddingBottom: '8px', color: '#2d3748' }}>📦 Documents structurés disponibles</h3>
        
        {parses.length === 0 ? (
          <p style={{ color: '#718096', fontStyle: 'italic', marginTop: '15px', fontSize: '14px' }}>
            Aucun historique d'extraction trouvé. Utilisez le formulaire ci-dessus pour lancer un premier parsing.
          </p>
        ) : (
          <div style={{ overflowX: 'auto', marginTop: '15px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ background: '#f7fafc', borderBottom: '2px solid #e2e8f0' }}>
                  <th style={{ padding: '12px', color: '#4a5568', fontSize: '14px' }}>ID</th>
                  <th style={{ padding: '12px', color: '#4a5568', fontSize: '14px' }}>Date du calcul</th>
                  <th style={{ padding: '12px', color: '#4a5568', fontSize: '14px' }}>Format</th>
                  <th style={{ padding: '12px', color: '#4a5568', fontSize: '14px' }}>Actions de téléchargement</th>
                </tr>
              </thead>
              <tbody>
                {parses.map((parse, index) => {
                  const parseId = parse.parse_id || parse.id || index;
                  const parseDate = parse.created_at 
                    ? new Date(parse.created_at).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' })
                    : 'N/A';
                  
                  const representation = parse.representation_type || 'both';

                  return (
                    <tr key={parseId} style={{ borderBottom: '1px solid #edf2f7' }}>
                      <td style={{ padding: '12px', fontWeight: 'bold', color: '#4a5568' }}>#{parseId}</td>
                      <td style={{ padding: '12px', color: '#2d3748', fontSize: '14px' }}>{parseDate}</td>
                      <td style={{ padding: '12px' }}>
                        <span style={{ background: '#edf2f7', color: '#4a5568', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: '600' }}>
                          {representation.toUpperCase()}
                        </span>
                      </td>
                      <td style={{ padding: '12px' }}>
                        <div style={{ display: 'flex', gap: '10px' }}>
                          
                          {/* Téléchargement MD */}
                          <button
                            onClick={() => triggerDownload(parse.content_text, `${baseName}_run_${parseId}.md`, 'text/markdown')}
                            disabled={!parse.content_text}
                            style={{ 
                              padding: '6px 14px', 
                              background: parse.content_text ? '#3182ce' : '#cbd5e0', 
                              color: '#fff', 
                              border: 'none', 
                              borderRadius: '4px', 
                              cursor: parse.content_text ? 'pointer' : 'not-allowed',
                              fontSize: '13px',
                              fontWeight: '500'
                            }}
                          >
                            Télécharger .MD
                          </button>

                          {/* Téléchargement JSON */}
                          <button
                            onClick={() => triggerDownload(
                              typeof parse.content_json === 'string' ? parse.content_json : JSON.stringify(parse.content_json, null, 2), 
                              `${baseName}_run_${parseId}.json`, 
                              'application/json'
                            )}
                            disabled={!parse.content_json}
                            style={{ 
                              padding: '6px 14px', 
                              background: parse.content_json ? '#38a169' : '#cbd5e0', 
                              color: '#fff', 
                              border: 'none', 
                              borderRadius: '4px', 
                              cursor: parse.content_json ? 'pointer' : 'not-allowed',
                              fontSize: '13px',
                              fontWeight: '500'
                            }}
                          >
                            Télécharger .JSON
                          </button>

                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}