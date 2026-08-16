from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv(Path(".env"))
url = os.getenv("DATABASE_URL")
if not url:
    raise SystemExit("DATABASE_URL environment variable is not set")

engine = create_async_engine(url, echo=False)

async def main():
    sql = Path("fix_schema.sql").read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]
    async with engine.begin() as conn:
        for stmt in statements:
            await conn.exec_driver_sql(stmt)
    print("SQL fix executed successfully")

import asyncio
asyncio.run(main())
