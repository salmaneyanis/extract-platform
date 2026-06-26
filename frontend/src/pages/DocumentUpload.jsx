import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { documentService } from '../services/api';

export default function DocumentUpload() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [workflow, setWorkflow] = useState('1');
  const [engine, setEngine] = useState('vlm');
  const [profile, setProfile] = useState('balanced');
  const [device, setDevice] = useState('auto');
  const [format, setFormat] = useState('both');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Veuillez sélectionner un fichier PDF avant de valider.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (workflow === '1') {
        // CORRECTION 1 : Appel du vrai nom de la fonction 'processComplete'
        // CORRECTION 2 : Envoi du fichier brut et de l'objet d'options séparés
        await documentService.processComplete(file, {
          engine: engine,
          profile: profile,
          device: device,
          output_format: format
        });
        navigate('/');
      } else {
        // WORKFLOW 2 : Appel de 'uploadOnly' avec le fichier binaire brut
        await documentService.uploadOnly(file);
        navigate('/');
      }
    } catch (err) {
      // Lecture intelligente de l'erreur brute
      const backendError = err.response?.data?.detail;
      
      if (Array.isArray(backendError)) {
        const msg = backendError[0]?.msg || '';
        const loc = backendError[0]?.loc?.join('.') || '';
        setError(`Erreur de validation API [paramètre: ${loc}] : ${msg}`);
      } else if (typeof backendError === 'string') {
        setError(backendError);
      } else {
        setError("Une erreur est survenue lors de l'envoi du document. Vérifiez la connexion ou le format.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '750px', margin: '40px auto', padding: '0 20px', fontFamily: 'sans-serif' }}>
      
      <div style={{ background: '#fff', padding: '30px', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)', border: '1px solid #e2e8f0' }}>
        
        <h2 style={{ margin: '0 0 10px 0', color: '#1a202c', fontSize: '24px', fontWeight: '700' }}>
          📤 Déposer un document financier
        </h2>
        <p style={{ margin: '0 0 25px 0', color: '#4a5568', fontSize: '14px' }}>
          Sélectionnez un état de compte, un bilan ou un rapport au format PDF pour l'analyse intelligente.
        </p>

        {error && (
          <div style={{ color: '#721c24', background: '#f8d7da', border: '1px solid #f5c6cb', padding: '12px', borderRadius: '6px', marginBottom: '20px', fontSize: '14px', fontWeight: '500' }}>
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Zone Fichier */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '14px', fontWeight: '600', color: '#4a5568' }}>Fichier PDF (Max 50 Mo) :</label>
            <input 
              type="file" 
              accept=".pdf" 
              onChange={handleFileChange}
              style={{ padding: '10px', background: '#f7fafc', borderRadius: '6px', border: '1px solid #cbd5e0', fontSize: '14px', cursor: 'pointer' }}
            />
          </div>

          {/* Type de parcours */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '14px', fontWeight: '600', color: '#4a5568' }}>Type de parcours utilisateur :</label>
            <select 
              value={workflow} 
              onChange={(e) => setWorkflow(e.target.value)}
              style={{ padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e0', background: '#fff', fontSize: '14px', width: '100%' }}
            >
              <option value="1">Workflow 1 : Traitement complet (Instantané)</option>
              <option value="2">Workflow 2 : Envoi seul (Planification / Batch)</option>
            </select>
          </div>

          {/* Options Docling conditionnelles */}
          {workflow === '1' && (
            <div style={{ background: '#f7fafc', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <h4 style={{ margin: '0 0 5px 0', color: '#2d3748', fontSize: '15px', fontWeight: '600', borderBottom: '1px solid #e2e8f0', paddingBottom: '5px' }}>
                ⚙️ Options d'extraction Docling
              </h4>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                <label style={{ fontSize: '13px', fontWeight: '600', color: '#4a5568' }}>Moteur d'extraction :</label>
                <select value={engine} onChange={(e) => setEngine(e.target.value)} style={{ padding: '8px', borderRadius: '6px', border: '1px solid #cbd5e0', background: '#fff', fontSize: '13px' }}>
                  <option value="vlm">VLM (Nanonets-OCR2-3B — IA vision, documents complexes)</option>
                  <option value="classic">Classique (OCR + tables — rapide, documents textuels)</option>
                </select>
                <span style={{ fontSize: '11px', color: '#718096' }}>
                  Le profil ci-dessous s'applique uniquement au moteur classique.
                </span>
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                  <label style={{ fontSize: '13px', fontWeight: '600', color: '#4a5568' }}>Profil d'extraction :</label>
                  <select value={profile} onChange={(e) => setProfile(e.target.value)} style={{ padding: '8px', borderRadius: '6px', border: '1px solid #cbd5e0', background: '#fff', fontSize: '13px' }}>
                    <option value="fast">FAST (Économique / OCR rapide)</option>
                    <option value="balanced">BALANCED (Équilibré / Recommandé)</option>
                    <option value="accurate">ACCURATE (Précision maximale)</option>
                  </select>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                  <label style={{ fontSize: '13px', fontWeight: '600', color: '#4a5568' }}>Matériel cible (Device) :</label>
                  <select value={device} onChange={(e) => setDevice(e.target.value)} style={{ padding: '8px', borderRadius: '6px', border: '1px solid #cbd5e0', background: '#fff', fontSize: '13px' }}>
                    <option value="auto">Auto (Bascule GPU/CPU automatique)</option>
                    <option value="cpu">CPU (Processeur local)</option>
                    <option value="gpu">GPU (Carte Graphique Nvidia)</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                <label style={{ fontSize: '13px', fontWeight: '600', color: '#4a5568' }}>Format de sortie attendu :</label>
                <select value={format} onChange={(e) => setFormat(e.target.value)} style={{ padding: '8px', borderRadius: '6px', border: '1px solid #cbd5e0', background: '#fff', fontSize: '13px' }}>
                  <option value="both">Tous (Markdown + JSON)</option>
                  <option value="markdown">Markdown uniquement (.md)</option>
                  <option value="json">Structure JSON uniquement (.json)</option>
                </select>
              </div>
            </div>
          )}

          {/* Bouton de validation */}
          <button 
            type="submit" 
            disabled={loading}
            style={{ 
              marginTop: '10px',
              padding: '12px', 
              background: loading ? '#a0aec0' : '#3182ce', 
              color: '#fff', 
              border: 'none', 
              borderRadius: '6px', 
              cursor: loading ? 'not-allowed' : 'pointer', 
              fontSize: '15px', 
              fontWeight: '600',
              boxShadow: '0 2px 4px rgba(49, 130, 206, 0.2)',
              transition: 'background 0.2s'
            }}
          >
            {loading ? 'Moteur d\'analyse en cours...' : '🚀 Valider le parcours et lancer'}
          </button>

        </form>
      </div>
    </div>
  );
}