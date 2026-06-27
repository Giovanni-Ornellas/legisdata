import os
from typing import Any

import mysql.connector
import pandas as pd


def _load_env_file() -> None:
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_config_from_env() -> dict[str, Any]:
    _load_env_file()
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3307")),
        "database": os.getenv("MYSQL_DATABASE", "trabalho_final"),
        "user": os.getenv("MYSQL_USER", "bdi"),
        "password": os.getenv("MYSQL_PASSWORD", "bdi"),
    }


def connect_mysql(config: dict[str, Any]):
    return mysql.connector.connect(
        host=config["host"],
        port=int(config["port"]),
        database=config["database"],
        user=config["user"],
        password=config["password"],
        autocommit=True,
    )


def run_select_query(connection, query: str) -> pd.DataFrame:
    normalized = query.strip().lower()
    if not normalized.startswith("select") and not normalized.startswith("with"):
        raise ValueError("A aplicacao executa apenas consultas SELECT.")

    connection.ping(reconnect=True, attempts=2, delay=1)
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return pd.DataFrame(rows)
    finally:
        cursor.close()
