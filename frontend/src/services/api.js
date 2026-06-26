import axios from 'axios';

// Le main_service est l'unique porte d'entrée externe sur le port 8000
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// IL EST CRUCIAL D'AVOIR LE MOT "export" ICI :
export const documentService = {
  // Récupérer la liste paginée de tous les documents 
  getAllDocuments: async (skip = 0, limit = 100) => {
    const response = await api.get(`/documents?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  // Récupérer les détails d'un document spécifique 
  getDocument: async (id) => {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },

  // WORKFLOW 1 : Traitement complet (Envoi + Extraction directe)
  processComplete: async (file, options) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('engine', options.engine);
    formData.append('profile', options.profile);
    formData.append('device', options.device);
    formData.append('output_format', options.output_format);
    
    const response = await api.post('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // WORKFLOW 2 : Envoi seul (Dépôt en attente)
  uploadOnly: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // WORKFLOW 3 : Extraction seule "à la carte" 
  extractOnly: async (docId, options) => {
    const formData = new FormData();
    formData.append('profile', options.profile);
    formData.append('device', options.device);
    formData.append('output_format', options.output_format);

    const response = await api.post(`/documents/${docId}/extract`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // Supprimer un document 
  deleteDocument: async (id) => {
    const response = await api.delete(`/documents/${id}`);
    return response.data;
  }
};