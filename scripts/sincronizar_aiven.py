import os
import sys
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from src.database import connect_mysql, get_config_from_env  # noqa: E402


TABLES = {
    "Partido": ["ID", "sigla", "nome"],
    "Orgao": ["ID", "sigla", "nome", "tipo_orgao"],
    "Tema": ["Cod", "nome", "descricao"],
    "Proposicao": [
        "ID",
        "Sigla_tipo",
        "Cod_tipo",
        "numero",
        "ano",
        "ementa",
        "data_apresentacao",
        "descricao_tipo",
    ],
    "Deputado": ["ID", "nome", "sigla_uf", "url_foto", "email", "fk_Partido_ID"],
    "Tramitacao": [
        "sequencia",
        "data_hora",
        "descricao_tramitacao",
        "descricao_situacao",
        "despacho",
        "apreciacao",
        "fk_Proposicao_ID",
        "fk_Orgao_ID",
    ],
    "Participa": [
        "fk_Deputado_ID",
        "fk_Proposicao_ID",
        "ordem_assinatura",
        "proponente",
    ],
    "Classificacao": ["fk_Proposicao_ID", "fk_Tema_Cod"],
}


def load_env_file() -> None:
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return

    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_streamlit_mysql_secrets() -> dict[str, Any]:
    path = BASE_DIR / ".streamlit" / "secrets.toml"
    if not path.exists():
        raise FileNotFoundError(
            "Arquivo .streamlit/secrets.toml nao encontrado. "
            "Configure os dados do Aiven antes de sincronizar."
        )

    config: dict[str, Any] = {}
    in_mysql = False
    multiline_key: str | None = None
    multiline_value: list[str] = []

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if multiline_key:
            if line == '"""':
                config[multiline_key] = "\n".join(multiline_value)
                multiline_key = None
                multiline_value = []
            else:
                multiline_value.append(raw)
            continue

        if line.startswith("["):
            in_mysql = line == "[mysql]"
            continue

        if not in_mysql or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value == '"""':
            multiline_key = key
            continue
        if value.lower() in {"true", "false"}:
            config[key] = value.lower() == "true"
        elif value.startswith('"') and value.endswith('"'):
            config[key] = value[1:-1]
        else:
            try:
                config[key] = int(value)
            except ValueError:
                config[key] = value

    required = {"host", "port", "database", "user", "password"}
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"Secrets incompletos para MySQL: {', '.join(missing)}")
    return config


def build_upsert_sql(table: str, columns: list[str]) -> str:
    column_list = ", ".join(f"`{column}`" for column in columns)
    placeholders = ", ".join(["%s"] * len(columns))
    updates = ", ".join(
        f"`{column}` = VALUES(`{column}`)" for column in columns
    )
    return (
        f"INSERT INTO `{table}` ({column_list}) "
        f"VALUES ({placeholders}) "
        f"ON DUPLICATE KEY UPDATE {updates}"
    )


def copy_table(source_conn, target_conn, table: str, columns: list[str]) -> int:
    select_sql = f"SELECT {', '.join(f'`{column}`' for column in columns)} FROM `{table}`"
    upsert_sql = build_upsert_sql(table, columns)
    total = 0

    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()
    try:
        source_cursor.execute(select_sql)
        while True:
            rows = source_cursor.fetchmany(500)
            if not rows:
                break
            target_cursor.executemany(upsert_sql, rows)
            target_conn.commit()
            total += len(rows)
    finally:
        source_cursor.close()
        target_cursor.close()

    return total


def count_rows(conn, table: str) -> int:
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
        return int(cursor.fetchone()[0])
    finally:
        cursor.close()


def main() -> int:
    load_env_file()
    local_config = get_config_from_env()
    aiven_config = load_streamlit_mysql_secrets()

    source = connect_mysql(local_config, autocommit=False)
    target = connect_mysql(aiven_config, autocommit=False)

    try:
        print("Sincronizando dados locais para o MySQL configurado em .streamlit/secrets.toml.")
        print("Operacao incremental: nao apaga dados e usa ON DUPLICATE KEY UPDATE.\n")

        for table, columns in TABLES.items():
            copied = copy_table(source, target, table, columns)
            target_count = count_rows(target, table)
            print(f"[OK] {table:14s} enviados={copied:6d} total_destino={target_count}")
    finally:
        source.close()
        target.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
