import os
from typing import Any

import mysql.connector


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

TABLES = [
    "Partido",
    "Orgao",
    "Tema",
    "Proposicao",
    "Deputado",
    "Tramitacao",
    "Participa",
    "Classificacao",
]


def load_env_file(path: str = ENV_PATH) -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def connect():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=env_int("MYSQL_PORT", 3307),
        database=os.getenv("MYSQL_DATABASE", "trabalho_final"),
        user=os.getenv("MYSQL_USER", "bdi"),
        password=os.getenv("MYSQL_PASSWORD", "bdi"),
    )


def print_rows(columns: list[str], rows: list[tuple[Any, ...]]) -> None:
    print("\t".join(columns))
    for row in rows:
        print("\t".join("" if value is None else str(value) for value in row))


def main() -> int:
    load_env_file()
    conn = connect()
    cursor = conn.cursor()

    try:
        print("\n=== CONTAGENS ===")
        for table in TABLES:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:14s} {count}")

        for table in TABLES:
            print(f"\n=== {table} LIMIT 10 ===")
            cursor.execute(f"SELECT * FROM {table} LIMIT 10")
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            if rows:
                print_rows(columns, rows)
            else:
                print("(sem registros)")
    finally:
        cursor.close()
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
