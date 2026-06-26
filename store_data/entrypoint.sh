#!/bin/sh
set -e

# Attendre que PostgreSQL soit prêt, puis appliquer les migrations Alembic,
# puis démarrer l'API. Garantit que les tables existent au 1er lancement.

echo "[store_data] Attente de PostgreSQL..."
# Petite boucle d'attente simple (pg n'est pas forcément prêt au démarrage)
RETRIES=30
until python -c "
import asyncio, asyncpg, os, sys
url = os.environ['DATABASE_URL'].replace('postgresql+asyncpg://','postgresql://')
async def check():
    try:
        conn = await asyncpg.connect(url)
        await conn.close()
    except Exception as e:
        sys.exit(1)
asyncio.run(check())
" 2>/dev/null || [ $RETRIES -eq 0 ]; do
    RETRIES=$((RETRIES-1))
    echo "[store_data] PostgreSQL pas encore prêt, nouvelle tentative ($RETRIES)..."
    sleep 2
done

echo "[store_data] Application des migrations Alembic..."
alembic upgrade head

echo "[store_data] Démarrage de l'API..."
exec uvicorn app.store_main:app --host 0.0.0.0 --port 8003
