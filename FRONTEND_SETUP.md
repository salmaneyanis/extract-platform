# Frontend Setup

React UI pour plateforme extraction documents TALIUM.

## Installation Rapide

### Dev local

```bash
cd frontend
npm install
npm run dev
```

Ouvre http://localhost:3000. Proxy automatique API vers http://localhost:8000.

Backend services doivent tourner (FastAPI). Lance dans terminal séparé:
```bash
docker-compose up
```

### Production (Docker)

```bash
docker-compose build
docker-compose up
```

Frontend servi sur http://localhost. API sur http://localhost:8000.

## Structure

```
frontend/
├── src/
│   ├── pages/              # Pages principales
│   ├── services/           # API client
│   ├── styles/             # CSS pages
│   ├── App.jsx             # Routing
│   └── main.jsx
├── index.html
├── vite.config.js
├── Dockerfile              # Pour production
├── package.json
└── README.md
```

## Pages

- **DocumentList** — Liste tous docs, delete, download
- **DocumentUpload** — Upload PDF, choisir profil extraction
- **DocumentDetail** — Voir extraction résultats, relancer extraction

## API Endpoints utilisés

- `POST /documents` — upload + extract
- `POST /documents/upload` — upload only
- `GET /documents` — list docs
- `GET /documents/{doc_id}` — single doc
- `GET /documents/{doc_id}/parse` — parses
- `DELETE /documents/{doc_id}` — delete
- `GET /documents/{doc_id}/file` — download

## Variables d'env

- `VITE_API_URL` — base URL API (défaut: http://localhost:8000)

## Tech Stack

- React 18
- Vite (build tool)
- Axios (HTTP client)
- CSS3 vanilla

## Dev Notes

- Pas de routes library (React Router simple nav en state)
- Pas de state management (useState suffisant)
- CSS vanilla (pas Tailwind, pas styled-components)
- Responsive design basique
