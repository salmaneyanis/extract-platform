# Guide de deploiement GPU (serveur CUDA 13 / driver 580)

Plateforme d'extraction de documents financiers basee sur **Docling**, avec
**deux moteurs au choix**, deployee en microservices Docker sur GPU NVIDIA L4.

## Les deux moteurs

| Moteur (`engine`) | Pipeline | Usage |
|-------------------|----------|-------|
| `classic`         | OCR (EasyOCR) + analyse de layout + TableFormer | Rapide, leger. Documents deja textuels. Les profils fast/balanced/accurate s'appliquent. |
| `vlm`             | VlmPipeline + Nanonets-OCR2-3B (VLM ~4B) | Plus puissant sur scans et documents complexes. Specialise documents financiers. |

Le modele VLM `nanonets/Nanonets-OCR2-3B` est base sur Qwen2.5-VL, fine-tune sur
des rapports financiers, factures et formulaires. Il genere du markdown structure.

## Architecture

| Service       | Role                                            | Port (hote) |
|---------------|-------------------------------------------------|-------------|
| frontend      | Interface React                                 | 80          |
| main_service  | Orchestrateur (porte d'entree)                  | 8000        |
| extract       | Extraction Docling (classic / vlm)              | 3001        |
| retrieve      | Stockage des fichiers                            | 3002        |
| store_data    | Persistance PostgreSQL + migrations Alembic     | 3003        |
| store_db      | Base PostgreSQL 16                               | 3013        |

## Prerequis (serveur GPU)

- Docker + Docker Compose
- Pilote NVIDIA (driver 580, CUDA 13.0)
- **NVIDIA Container Toolkit**

```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:13.0.0-runtime-ubuntu24.04 nvidia-smi
```

## Installation

```bash
cp .env.example .env
docker compose build
docker compose up -d
docker compose logs -f extract   # attendre "Converter pret"
```

Au premier demarrage :
- store_data applique les migrations Alembic (creation des tables).
- extract cree le converter Docling. Le modele VLM (~8 Go) se telecharge dans
  le volume hf_cache a la PREMIERE extraction en mode vlm.

## Verification

```bash
curl http://localhost:8000/health
curl http://localhost:3001/health   # extract Docling
watch -n 1 nvidia-smi               # pendant une extraction
```

## Utilisation de l'API

### Mode VLM (defaut)

```bash
curl -X POST http://localhost:8000/documents \
  -F "file=@document.pdf" \
  -F "engine=vlm" \
  -F "device=auto" \
  -F "output_format=markdown"
```

### Mode classique (OCR + profil)

```bash
curl -X POST http://localhost:8000/documents \
  -F "file=@document.pdf" \
  -F "engine=classic" \
  -F "profile=accurate" \
  -F "device=auto"
```

Reponse immediate (mode asynchrone) :
```json
{"doc_id": 1, "status": "processing", "message": "Extraction demarree en arriere-plan"}
```

Suivi :
```bash
curl http://localhost:8000/documents/1          # status: processing -> done
curl http://localhost:8000/documents/1/parse    # le markdown quand termine
```

## Parametres

- `engine` : `classic` ou `vlm` (defaut)
- `profile` : `fast` / `balanced` / `accurate` (mode classic uniquement)
- `device` : `auto` / `gpu` / `cpu`

## Notes techniques

- Architecture asynchrone : POST /documents repond immediatement (202), extraction
  en tache de fond (BackgroundTasks), suivi par polling du frontend.
- Les converters Docling sont crees en lazy loading (a la premiere utilisation).
- L'inference GPU est serialisee (un seul modele en VRAM a la fois).
- Le cache HuggingFace est persistant (volume hf_cache).
