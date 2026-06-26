"""
Configuration du service Extract (moteur Docling : classic + vlm).

Toutes les valeurs sont surchargeables par variables d'environnement.
"""

import os

# === Moteur par défaut ===
# "classic" = pipeline OCR Docling (profils) ; "vlm" = VLM Nanonets via Docling.
DEFAULT_ENGINE = os.getenv("EXTRACT_DEFAULT_ENGINE", "vlm")

# === Modèle VLM (mode engine=vlm) ===
# Nanonets-OCR2-3B : VLM ~4B basé sur Qwen2.5-VL, spécialisé documents financiers
# (factures, rapports financiers, formulaires), sortie markdown structuré.
VLM_MODEL_ID = os.getenv("VLM_MODEL_ID", "nanonets/Nanonets-OCR2-3B")

VLM_PROMPT = os.getenv(
    "VLM_PROMPT",
    "Convert this page to markdown. Do not miss any text and only output the bare markdown.",
)

VLM_MAX_NEW_TOKENS = int(os.getenv("VLM_MAX_NEW_TOKENS", "4096"))

# === Workers ===
# 1 par défaut : l'inférence GPU est sérialisée (un seul modèle en VRAM).
EXTRACT_WORKERS = int(os.getenv("EXTRACT_WORKERS", "1"))

# === Device par défaut ===
DEFAULT_DEVICE = os.getenv("EXTRACT_DEFAULT_DEVICE", "auto")

# === Limites ===
MAX_FILE_SIZE_MB = int(os.getenv("EXTRACT_MAX_FILE_SIZE_MB", "100"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# === Timeout (secondes) ===
PARSE_TIMEOUT_SECONDS = int(os.getenv("EXTRACT_TIMEOUT_SECONDS", "1200"))
