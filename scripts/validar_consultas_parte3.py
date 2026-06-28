import os
import sys
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from src.database import connect_mysql, get_config_from_env  # noqa: E402
from src.queries import (  # noqa: E402
    RANKING_DEPUTADOS_QUERY,
    RANKING_PARTIDOS_QUERY,
    TEMAS_ACIMA_MEDIA_QUERY,
    TRAMITACOES_ACIMA_MEDIA_QUERY,
)


CONSULTAS = [
    ("Consulta 1 - Ranking de partidos por proposições com autoria", RANKING_PARTIDOS_QUERY),
    ("Consulta 2 - Deputados com maior número de proposições assinadas", RANKING_DEPUTADOS_QUERY),
    (
        "Consulta 3 - Proposições e seus temas, mantendo proposições sem tema",
        """
        SELECT
            pr.ID AS proposicao_id,
            pr.Sigla_tipo,
            pr.numero,
            pr.ano,
            pr.ementa,
            COALESCE(GROUP_CONCAT(DISTINCT t.nome ORDER BY t.nome SEPARATOR ', '), 'Sem tema associado') AS temas
        FROM Proposicao pr
        LEFT JOIN Classificacao c
            ON c.fk_Proposicao_ID = pr.ID
        LEFT JOIN Tema t
            ON t.Cod = c.fk_Tema_Cod
        GROUP BY
            pr.ID,
            pr.Sigla_tipo,
            pr.numero,
            pr.ano,
            pr.ementa
        ORDER BY
            pr.ano DESC,
            pr.numero DESC,
            pr.ID DESC
        """,
    ),
    (
        "Consulta 4 - Última tramitação conhecida de cada proposição",
        """
        SELECT
            pr.ID AS proposicao_id,
            pr.Sigla_tipo,
            pr.numero,
            pr.ano,
            pr.ementa,
            tr.sequencia,
            tr.data_hora,
            tr.descricao_situacao,
            tr.descricao_tramitacao,
            o.sigla AS sigla_orgao,
            o.nome AS nome_orgao
        FROM Proposicao pr
        JOIN Tramitacao tr
            ON tr.fk_Proposicao_ID = pr.ID
            AND tr.sequencia = (
                SELECT MAX(tr2.sequencia)
                FROM Tramitacao tr2
                WHERE tr2.fk_Proposicao_ID = pr.ID
            )
        LEFT JOIN Orgao o
            ON o.ID = tr.fk_Orgao_ID
        ORDER BY
            tr.data_hora DESC,
            pr.ID DESC
        """,
    ),
    ("Consulta 5 - Temas com quantidade de proposições acima da média", TEMAS_ACIMA_MEDIA_QUERY),
    ("Consulta 6 - Proposições com número de tramitações acima da média", TRAMITACOES_ACIMA_MEDIA_QUERY),
]


def _load_streamlit_secrets() -> dict[str, Any]:
    path = BASE_DIR / ".streamlit" / "secrets.toml"
    if not path.exists():
        return {}

    config: dict[str, Any] = {}
    in_mysql = False
    multiline_key = None
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
    return config


def get_config() -> dict[str, Any]:
    env_config = get_config_from_env()
    if os.path.exists(BASE_DIR / ".env") or os.getenv("MYSQL_HOST"):
        return env_config
    secrets_config = _load_streamlit_secrets()
    return secrets_config or env_config


def is_select_query(query: str) -> bool:
    normalized = query.strip().lower()
    return normalized.startswith("select") or normalized.startswith("with")


def main() -> int:
    conn = connect_mysql(get_config())
    cursor = conn.cursor()
    has_error = False

    try:
        for nome, query in CONSULTAS:
            if not is_select_query(query):
                print(f"[ERRO] {nome}: consulta bloqueada por não ser SELECT/WITH")
                has_error = True
                continue
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
                print(f"[OK] {nome}: {len(rows)} linhas retornadas")
            except Exception as exc:
                print(f"[ERRO] {nome}: {exc}")
                has_error = True
    finally:
        cursor.close()
        conn.close()

    return 1 if has_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
