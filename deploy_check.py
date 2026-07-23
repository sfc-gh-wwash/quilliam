#!/usr/bin/env python3
"""
Quilliam version check and deploy.
Uses the same .env and key-pair auth as the backend.
Run from project root: python3 deploy_check.py [--force]
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import snowflake.connector

PROJECT_DIR = Path(__file__).parent
BACKEND_DIR = PROJECT_DIR / "backend"
DB_DIR = PROJECT_DIR / "database"
VERSION_FILE = PROJECT_DIR / "VERSION"

# SQL files to run in order
SQL_FILES = [
    ("DDL", "meeting_notes_ddl.sql"),
    ("Search Services", "cortex_search_service.sql"),
    ("Semantic View", "semantic_view.sql"),
    ("Agent", "cortex_agent.sql"),
    ("MCP Connectors", "mcp_connectors.sql"),
]


def get_connection():
    load_dotenv(dotenv_path=BACKEND_DIR / ".env")
    load_dotenv(dotenv_path=PROJECT_DIR / ".env")

    key_path = os.getenv('SNOWFLAKE_PRIVATE_KEY_PATH', str(BACKEND_DIR / 'rsa_key.p8'))
    if not os.path.isabs(key_path):
        key_path = str(BACKEND_DIR / key_path)
    with open(key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    return snowflake.connector.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        user=os.getenv('SNOWFLAKE_USER'),
        private_key=private_key_bytes,
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'QUILLIAM_WH'),
        database=os.getenv('SNOWFLAKE_DATABASE', 'QUILLIAM'),
        schema=os.getenv('SNOWFLAKE_SCHEMA', 'STG'),
        role=os.getenv('SNOWFLAKE_ROLE', 'QUILLIAM_ADMIN_RL'),
    )


def get_app_version():
    return VERSION_FILE.read_text().strip()


def get_deployed_version(conn):
    try:
        cur = conn.cursor()
        cur.execute("SELECT MAX(VERSION) FROM QUILLIAM.STG.APP_VERSION")
        row = cur.fetchone()
        return row[0] if row and row[0] else None
    except Exception:
        return None


def run_sql_file(conn, filepath):
    sql = filepath.read_text()
    cur = conn.cursor()
    for statement in sql.split(';'):
        stmt = statement.strip()
        if not stmt or stmt.startswith('--'):
            continue
        try:
            cur.execute(stmt)
        except Exception as e:
            err = str(e)
            # Skip role/permission errors silently (DDL has USE ROLE ACCOUNTADMIN
            # but we may be running as QUILLIAM_ADMIN_RL which already owns objects)
            if any(x in err.lower() for x in ['insufficient privileges', 'not authorized', 'cannot be granted']):
                pass
            else:
                print(f"    WARNING: {err[:120]}")


def stamp_version(conn, version):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO QUILLIAM.STG.APP_VERSION (VERSION) VALUES (%s)",
        (version,)
    )


def deploy(conn, app_version):
    print(f"Deploying Quilliam v{app_version}...")
    print()

    for desc, filename in SQL_FILES:
        filepath = DB_DIR / filename
        if not filepath.exists():
            print(f"  [{desc}] SKIP (file not found: {filename})")
            continue
        print(f"  [{desc}] {filename}...")
        run_sql_file(conn, filepath)

    stamp_version(conn, app_version)
    print()
    print(f"Deployed v{app_version} successfully.")


def main():
    force = '--force' in sys.argv
    app_version = get_app_version()

    print(f"Quilliam deploy check (app v{app_version})")
    print()

    conn = get_connection()
    deployed_version = get_deployed_version(conn)

    if deployed_version == app_version and not force:
        print(f"  Already at v{app_version}. No deployment needed.")
        print(f"  Use --force to redeploy anyway.")
        conn.close()
        return False

    if deployed_version:
        print(f"  Upgrading: v{deployed_version} → v{app_version}")
    else:
        print(f"  Initial deployment: v{app_version}")
    print()

    deploy(conn, app_version)
    conn.close()
    return True


if __name__ == '__main__':
    deployed = main()
    sys.exit(0 if not deployed else 0)
