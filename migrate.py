import asyncio
from database import engine, metadata

async def migrate():
    print("Création des tables (si inexistantes)...")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    print("✅ Migration terminée !")

if __name__ == "__main__":
    asyncio.run(migrate())
