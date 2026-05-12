"""
Configuration centralisée pour le service Retrieve.
Toutes les variables d'environnement et constantes sont définies ici.
"""

import os
from pathlib import Path


# Chemins 
DATA_DIR = Path(os.getenv("RETRIEVE_DATA_DIR", "/data"))

# Limites de fichiers 
MAX_FILE_SIZE_MB = int(os.getenv("RETRIEVE_MAX_FILE_SIZE_MB", "100"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

