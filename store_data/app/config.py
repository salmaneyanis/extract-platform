import os

DATABASE_URL = os.getenv("DATABASE_URL","postgresql+asyncpg://user:pass@store_db:5432/mydb")