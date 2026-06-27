import os
from typing import Any

import mysql.connector
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def _parse_bool(value: Any, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "sim", "s", "yes", "y"}:
        return True
    if normalized in {"0", "false", "nao", "não", "n", "no"}:
        return False
    return default


def _load_env_file() -> None:
    env_path = os.path.join(BASE_DIR, ".env")
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
        "ssl_mode": os.getenv("MYSQL_SSL_MODE", ""),
        "ssl_ca": os.getenv("MYSQL_SSL_CA", ""),
        "ssl_verify_cert": os.getenv("MYSQL_SSL_VERIFY_CERT", ""),
        "ssl_verify_identity": os.getenv("MYSQL_SSL_VERIFY_IDENTITY", ""),
    }


def build_connection_kwargs(config: dict[str, Any], autocommit: bool = True) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "host": config["host"],
        "port": int(config["port"]),
        "database": config["database"],
        "user": config["user"],
        "password": config["password"],
        "autocommit": autocommit,
    }

    ssl_mode = str(config.get("ssl_mode", "") or "").upper()
    ssl_ca = str(config.get("ssl_ca", "") or "").strip()

    if ssl_mode == "DISABLED":
        kwargs["ssl_disabled"] = True
        return kwargs

    if ssl_mode or ssl_ca:
        kwargs["ssl_disabled"] = False

    if ssl_ca:
        if not os.path.isabs(ssl_ca):
            ssl_ca = os.path.join(BASE_DIR, ssl_ca)
        kwargs["ssl_ca"] = ssl_ca

    if ssl_mode in {"VERIFY_CA", "VERIFY_IDENTITY"}:
        kwargs["ssl_verify_cert"] = True
    elif "ssl_verify_cert" in config and str(config.get("ssl_verify_cert", "")) != "":
        kwargs["ssl_verify_cert"] = _parse_bool(config.get("ssl_verify_cert"))

    if ssl_mode == "VERIFY_IDENTITY":
        kwargs["ssl_verify_identity"] = True
    elif "ssl_verify_identity" in config and str(config.get("ssl_verify_identity", "")) != "":
        kwargs["ssl_verify_identity"] = _parse_bool(config.get("ssl_verify_identity"))

    return kwargs


def connect_mysql(config: dict[str, Any], autocommit: bool = True):
    return mysql.connector.connect(**build_connection_kwargs(config, autocommit=autocommit))


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
