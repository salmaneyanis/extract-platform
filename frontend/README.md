# Frontend - Plateforme d'Extraction Docling

React UI simple pour la plateforme extraction documents financiers TALIUM.

## Stack

- **React 18** — UI framework
- **Vite** — build tool (fast HMR)
- **Axios** — HTTP client
- **CSS3** — vanilla styling

## Installation

```bash
cd frontend
npm install
```

## Développement

```bash
npm run dev
```

Lance dev server sur http://localhost:3000. Proxy API vers http://localhost:8000.

## Build

```bash
npm run build
```

Crée `dist/` optimisé pour production.

## Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── DocumentList.jsx      # Liste documents, delete, download
│   │   ├── DocumentUpload.jsx     # Upload + extraction
│   │   └── DocumentDetail.jsx     # Voir détails extraction
│   ├── services/
│   │   └── api.js                # Appels API FastAPI
│   ├── styles/
│   │   ├── DocumentList.css
│   │   ├── DocumentUpload.css
│   │   └── DocumentDetail.css
│   ├── App.jsx                   # Navigation principal
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── index.html
├── vite.config.js
└── package.json
```

## Features

- **Liste documents** — voir tous documents uploadés, status, actions (voir, télécharger, supprimer)
- **Upload + Extraction** — upload PDF direct, choisir profil extraction (fast/balanced/accurate)
- **Upload only** — upload sans extraction directe, extraire plus tard
- **Détails document** — voir metadata, extractions, contenu texte/JSON
- **Extraction on-demand** — relancer extraction avec profil différent
- **Download** — télécharger fichier original

## Variables environnement

- `REACT_APP_API_URL` — base URL API FastAPI (défaut: http://localhost:8000)

## Déploiement

Voir `docker-compose.yaml` racine pour intégration avec services FastAPI.

Frontend servi sur port 3000 en dev, port 80 en production.
