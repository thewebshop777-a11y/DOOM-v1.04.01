"""
DOOM AI — Database (breaks circular imports)
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

engine = create_engine(settings.database_url or "sqlite:///./doom.db", pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def is_postgres():
    return "postgres" in str(engine.url).lower() or "neon" in str(engine.url).lower()

def init_schema():
    pk = "SERIAL PRIMARY KEY" if is_postgres() else "INTEGER PRIMARY KEY AUTOINCREMENT"
    with engine.connect() as conn:
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS users (
                id {pk},
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'owner',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS workspaces (
                id {pk},
                name TEXT NOT NULL,
                owner_id INTEGER,
                plan TEXT DEFAULT 'pro',
                seats INTEGER DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS connected_accounts (
                id {pk},
                workspace_id TEXT NOT NULL DEFAULT 'web-shop',
                connector_id TEXT NOT NULL,
                connector_name TEXT NOT NULL,
                status TEXT DEFAULT 'connected',
                connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                composio_connection_id TEXT,
                meta TEXT,
                UNIQUE(workspace_id, connector_id)
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                function TEXT,
                connectors TEXT,
                workflow TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS approvals (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                detail TEXT,
                risk TEXT DEFAULT 'low',
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                decided_at TIMESTAMP,
                note TEXT
            );
        """))
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS usage_log (
                id {pk},
                workspace_id TEXT DEFAULT 'web-shop',
                plan TEXT,
                power TEXT,
                model_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS settings (
                id {pk},
                workspace_id TEXT NOT NULL DEFAULT 'web-shop',
                key TEXT NOT NULL,
                value TEXT,
                UNIQUE(workspace_id, key)
            );
        """))
        conn.commit()
    print("Schema ready —", "Postgres/Neon" if is_postgres() else "SQLite")
