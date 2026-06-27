import logging
import os
import re
import time
from datetime import datetime
from typing import Any

import mysql.connector
import requests
from mysql.connector import Error as MySQLError


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

DEFAULT_API_BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
DEFAULT_TIMEOUT = 30
DEFAULT_ITEMS_PER_PAGE = 100


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


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
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning("Valor invalido para %s=%r. Usando %s.", name, value, default)
        return default


def clean_text(value: Any, max_length: int | None = None) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    if value == "":
        return None
    if max_length is not None:
        return value[:max_length]
    return value


def parse_date(value: Any) -> str | None:
    value = clean_text(value)
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        logger.debug("Data invalida ignorada: %r", value)
        return None


def parse_datetime(value: Any) -> str | None:
    value = clean_text(value)
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(value[:19], "%Y-%m-%dT%H:%M:%S").strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            logger.debug("Data/hora invalida ignorada: %r", value)
            return None


def as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def as_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "sim", "s", "yes"}:
        return True
    if normalized in {"0", "false", "nao", "não", "n", "no"}:
        return False
    return None


def id_from_uri(uri: Any, resource: str) -> int | None:
    uri = clean_text(uri)
    if not uri:
        return None
    match = re.search(rf"/{re.escape(resource)}/(\d+)(?:\D*$|$)", uri)
    if match:
        return int(match.group(1))
    return None


def is_deputado_author(author: dict[str, Any]) -> bool:
    tipo = clean_text(author.get("tipo")) or clean_text(author.get("tipoAutor"))
    uri = clean_text(author.get("uri")) or clean_text(author.get("uriAutor"))
    if tipo and "deputad" in tipo.lower():
        return True
    return bool(uri and "/deputados/" in uri)


class CamaraAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        for attempt in range(1, 4):
            try:
                response = self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT)
                if response.status_code == 404:
                    logger.debug("Endpoint nao encontrado: %s", response.url)
                    return None
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                wait_seconds = attempt * 2
                if attempt == 3:
                    logger.warning("Falha definitiva na API: %s params=%s erro=%s", url, params, exc)
                    return None
                logger.warning(
                    "Falha temporaria na API: %s params=%s tentativa=%s. Retentando em %ss.",
                    url,
                    params,
                    attempt,
                    wait_seconds,
                )
                time.sleep(wait_seconds)
        return None

    def iter_paginated(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        max_items: int | None = None,
    ):
        params = dict(params or {})
        params.setdefault("itens", DEFAULT_ITEMS_PER_PAGE)
        page = as_int(params.get("pagina")) or 1
        total = 0

        while True:
            params["pagina"] = page
            payload = self.get(endpoint, params)
            if not payload:
                return

            rows = payload.get("dados") or []
            if not rows:
                return

            for row in rows:
                yield row
                total += 1
                if max_items is not None and total >= max_items:
                    return

            links = payload.get("links") or []
            has_next = any(link.get("rel") == "next" for link in links if isinstance(link, dict))
            if not has_next:
                return
            page += 1


class Banco:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            port=env_int("MYSQL_PORT", 3307),
            database=os.getenv("MYSQL_DATABASE", "trabalho_final"),
            user=os.getenv("MYSQL_USER", "bdi"),
            password=os.getenv("MYSQL_PASSWORD", "bdi"),
            autocommit=False,
        )

    def close(self) -> None:
        self.conn.close()

    def execute(self, sql: str, params: tuple[Any, ...]) -> None:
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, params)
        finally:
            cursor.close()

    def commit(self) -> None:
        self.conn.commit()

    def rollback(self) -> None:
        self.conn.rollback()


class PopularBanco:
    def __init__(self, banco: Banco, api: CamaraAPI):
        self.banco = banco
        self.api = api
        self.partidos_por_sigla: dict[str, int] = {}
        self.temas_por_nome: dict[str, int] = {}
        self.orgaos_conhecidos: set[int] = set()
        self.deputados_conhecidos: set[int] = set()
        self.stats = {
            "Partido": 0,
            "Orgao": 0,
            "Tema": 0,
            "Proposicao": 0,
            "Deputado": 0,
            "Tramitacao": 0,
            "Participa": 0,
            "Classificacao": 0,
            "autores_sem_deputado": 0,
            "tramitacoes_sem_orgao": 0,
        }
        self.deputado_ids: list[int] = []

    def upsert_partido(self, partido: dict[str, Any]) -> int | None:
        partido_id = as_int(partido.get("id")) or id_from_uri(partido.get("uri"), "partidos")
        if partido_id is None:
            return None

        sigla = clean_text(partido.get("sigla"), 15)
        nome = clean_text(partido.get("nome"), 255)
        self.banco.execute(
            """
            INSERT INTO Partido (ID, sigla, nome)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                sigla = VALUES(sigla),
                nome = VALUES(nome)
            """,
            (partido_id, sigla, nome),
        )
        if sigla:
            self.partidos_por_sigla[sigla] = partido_id
        self.stats["Partido"] += 1
        return partido_id

    def ensure_partido_from_uri_or_sigla(self, uri: Any, sigla: Any) -> int | None:
        partido_id = id_from_uri(uri, "partidos")
        sigla_limpa = clean_text(sigla, 15)

        if partido_id is not None:
            payload = self.api.get(f"partidos/{partido_id}")
            dados = payload.get("dados") if payload else None
            if isinstance(dados, dict):
                return self.upsert_partido(dados)
            self.banco.execute(
                """
                INSERT INTO Partido (ID, sigla, nome)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    sigla = COALESCE(VALUES(sigla), sigla),
                    nome = COALESCE(VALUES(nome), nome)
                """,
                (partido_id, sigla_limpa, sigla_limpa),
            )
            if sigla_limpa:
                self.partidos_por_sigla[sigla_limpa] = partido_id
            return partido_id

        if sigla_limpa and sigla_limpa in self.partidos_por_sigla:
            return self.partidos_por_sigla[sigla_limpa]
        return None

    def upsert_orgao(self, orgao: dict[str, Any]) -> int | None:
        orgao_id = (
            as_int(orgao.get("id"))
            or as_int(orgao.get("codOrgao"))
            or id_from_uri(orgao.get("uri"), "orgaos")
            or id_from_uri(orgao.get("uriOrgao"), "orgaos")
        )
        if orgao_id is None:
            return None

        tipo_orgao = (
            clean_text(orgao.get("tipoOrgao"), 100)
            or clean_text(orgao.get("tipo"), 100)
            or clean_text(orgao.get("descricaoTipo"), 100)
        )
        self.banco.execute(
            """
            INSERT INTO Orgao (ID, sigla, nome, tipo_orgao)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                sigla = COALESCE(VALUES(sigla), sigla),
                nome = COALESCE(VALUES(nome), nome),
                tipo_orgao = COALESCE(VALUES(tipo_orgao), tipo_orgao)
            """,
            (
                orgao_id,
                clean_text(orgao.get("sigla") or orgao.get("siglaOrgao"), 20),
                clean_text(orgao.get("nome") or orgao.get("nomeOrgao"), 255),
                tipo_orgao,
            ),
        )
        self.orgaos_conhecidos.add(orgao_id)
        self.stats["Orgao"] += 1
        return orgao_id

    def ensure_orgao(self, tramitacao: dict[str, Any]) -> int | None:
        orgao_id = (
            as_int(tramitacao.get("codOrgao"))
            or as_int(tramitacao.get("idOrgao"))
            or id_from_uri(tramitacao.get("uriOrgao"), "orgaos")
            or id_from_uri(tramitacao.get("uri"), "orgaos")
        )
        if orgao_id is None:
            self.stats["tramitacoes_sem_orgao"] += 1
            return None

        if orgao_id in self.orgaos_conhecidos:
            return orgao_id

        payload = self.api.get(f"orgaos/{orgao_id}")
        dados = payload.get("dados") if payload else None
        if isinstance(dados, dict):
            return self.upsert_orgao(dados)

        return self.upsert_orgao(
            {
                "id": orgao_id,
                "sigla": tramitacao.get("siglaOrgao"),
                "nome": tramitacao.get("nomeOrgao"),
                "tipoOrgao": tramitacao.get("tipoOrgao"),
            }
        )

    def upsert_tema(self, tema: dict[str, Any]) -> int | None:
        tema_cod = (
            as_int(tema.get("cod"))
            or as_int(tema.get("Cod"))
            or as_int(tema.get("codTema"))
            or as_int(tema.get("codigo"))
            or as_int(tema.get("id"))
        )
        if tema_cod is None:
            return None

        nome = clean_text(tema.get("nome") or tema.get("tema") or tema.get("descricao"), 255)
        descricao = clean_text(tema.get("descricao") or tema.get("nome") or tema.get("tema"))
        self.banco.execute(
            """
            INSERT INTO Tema (Cod, nome, descricao)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                nome = COALESCE(VALUES(nome), nome),
                descricao = COALESCE(VALUES(descricao), descricao)
            """,
            (tema_cod, nome, descricao),
        )
        if nome:
            self.temas_por_nome[nome.lower()] = tema_cod
        self.stats["Tema"] += 1
        return tema_cod

    def upsert_proposicao(self, proposicao: dict[str, Any]) -> int | None:
        prop_id = as_int(proposicao.get("id")) or id_from_uri(proposicao.get("uri"), "proposicoes")
        if prop_id is None:
            return None

        self.banco.execute(
            """
            INSERT INTO Proposicao (
                ID,
                Sigla_tipo,
                Cod_tipo,
                numero,
                ano,
                ementa,
                data_apresentacao,
                descricao_tipo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                Sigla_tipo = COALESCE(VALUES(Sigla_tipo), Sigla_tipo),
                Cod_tipo = COALESCE(VALUES(Cod_tipo), Cod_tipo),
                numero = COALESCE(VALUES(numero), numero),
                ano = COALESCE(VALUES(ano), ano),
                ementa = COALESCE(VALUES(ementa), ementa),
                data_apresentacao = COALESCE(VALUES(data_apresentacao), data_apresentacao),
                descricao_tipo = COALESCE(VALUES(descricao_tipo), descricao_tipo)
            """,
            (
                prop_id,
                clean_text(proposicao.get("siglaTipo"), 10),
                clean_text(proposicao.get("codTipo"), 20),
                as_int(proposicao.get("numero")),
                as_int(proposicao.get("ano")),
                clean_text(proposicao.get("ementa")),
                parse_date(proposicao.get("dataApresentacao")),
                clean_text(proposicao.get("descricaoTipo"), 255),
            ),
        )
        self.stats["Proposicao"] += 1
        return prop_id

    def upsert_deputado(self, deputado: dict[str, Any]) -> int | None:
        dep_id = (
            as_int(deputado.get("id"))
            or as_int(deputado.get("idCadastro"))
            or id_from_uri(deputado.get("uri"), "deputados")
            or id_from_uri(deputado.get("uriAutor"), "deputados")
        )
        if dep_id is None:
            return None

        ultimo_status = deputado.get("ultimoStatus") if isinstance(deputado.get("ultimoStatus"), dict) else {}
        sigla_partido = deputado.get("siglaPartido") or ultimo_status.get("siglaPartido")
        uri_partido = deputado.get("uriPartido") or ultimo_status.get("uriPartido")
        partido_id = self.ensure_partido_from_uri_or_sigla(uri_partido, sigla_partido)

        self.banco.execute(
            """
            INSERT INTO Deputado (ID, nome, sigla_uf, url_foto, email, fk_Partido_ID)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                nome = COALESCE(VALUES(nome), nome),
                sigla_uf = COALESCE(VALUES(sigla_uf), sigla_uf),
                url_foto = COALESCE(VALUES(url_foto), url_foto),
                email = COALESCE(VALUES(email), email),
                fk_Partido_ID = COALESCE(VALUES(fk_Partido_ID), fk_Partido_ID)
            """,
            (
                dep_id,
                clean_text(deputado.get("nome") or ultimo_status.get("nome"), 255),
                clean_text(deputado.get("siglaUf") or ultimo_status.get("siglaUf"), 2),
                clean_text(deputado.get("urlFoto") or ultimo_status.get("urlFoto"), 500),
                clean_text(deputado.get("email") or ultimo_status.get("email"), 255),
                partido_id,
            ),
        )
        self.deputados_conhecidos.add(dep_id)
        self.stats["Deputado"] += 1
        return dep_id

    def ensure_deputado(self, author: dict[str, Any]) -> int | None:
        dep_id = (
            as_int(author.get("id"))
            or as_int(author.get("idCadastro"))
            or id_from_uri(author.get("uri"), "deputados")
            or id_from_uri(author.get("uriAutor"), "deputados")
        )
        if dep_id is None:
            self.stats["autores_sem_deputado"] += 1
            return None

        if dep_id in self.deputados_conhecidos:
            return dep_id

        payload = self.api.get(f"deputados/{dep_id}")
        dados = payload.get("dados") if payload else None
        if isinstance(dados, dict):
            return self.upsert_deputado(dados)

        return self.upsert_deputado(
            {
                "id": dep_id,
                "nome": author.get("nome"),
                "uri": author.get("uri") or author.get("uriAutor"),
            }
        )

    def upsert_participa(self, dep_id: int, prop_id: int, author: dict[str, Any]) -> None:
        self.banco.execute(
            """
            INSERT INTO Participa (
                fk_Deputado_ID,
                fk_Proposicao_ID,
                ordem_assinatura,
                proponente
            )
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                ordem_assinatura = COALESCE(VALUES(ordem_assinatura), ordem_assinatura),
                proponente = COALESCE(VALUES(proponente), proponente)
            """,
            (
                dep_id,
                prop_id,
                as_int(author.get("ordemAssinatura")),
                as_bool(author.get("proponente")),
            ),
        )
        self.stats["Participa"] += 1

    def upsert_classificacao(self, prop_id: int, tema_cod: int) -> None:
        self.banco.execute(
            """
            INSERT INTO Classificacao (fk_Proposicao_ID, fk_Tema_Cod)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                fk_Tema_Cod = VALUES(fk_Tema_Cod)
            """,
            (prop_id, tema_cod),
        )
        self.stats["Classificacao"] += 1

    def upsert_tramitacao(self, prop_id: int, tramitacao: dict[str, Any]) -> None:
        sequencia = as_int(tramitacao.get("sequencia"))
        if sequencia is None:
            logger.debug("Tramitacao sem sequencia ignorada para proposicao %s.", prop_id)
            return

        orgao_id = self.ensure_orgao(tramitacao)
        self.banco.execute(
            """
            INSERT INTO Tramitacao (
                sequencia,
                data_hora,
                descricao_tramitacao,
                descricao_situacao,
                despacho,
                apreciacao,
                fk_Proposicao_ID,
                fk_Orgao_ID
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                data_hora = COALESCE(VALUES(data_hora), data_hora),
                descricao_tramitacao = COALESCE(VALUES(descricao_tramitacao), descricao_tramitacao),
                descricao_situacao = COALESCE(VALUES(descricao_situacao), descricao_situacao),
                despacho = COALESCE(VALUES(despacho), despacho),
                apreciacao = COALESCE(VALUES(apreciacao), apreciacao),
                fk_Orgao_ID = COALESCE(VALUES(fk_Orgao_ID), fk_Orgao_ID)
            """,
            (
                sequencia,
                parse_datetime(tramitacao.get("dataHora")),
                clean_text(tramitacao.get("descricaoTramitacao")),
                clean_text(tramitacao.get("descricaoSituacao"), 255),
                clean_text(tramitacao.get("despacho")),
                clean_text(tramitacao.get("apreciacao"), 255),
                prop_id,
                orgao_id,
            ),
        )
        self.stats["Tramitacao"] += 1

    def popular_partidos(self) -> None:
        logger.info("Populando Partido...")
        for partido in self.api.iter_paginated("partidos"):
            self.upsert_partido(partido)
        self.banco.commit()
        logger.info("Partido processado: %s registros.", self.stats["Partido"])

    def popular_orgaos(self) -> None:
        logger.info("Populando Orgao...")
        for orgao in self.api.iter_paginated("orgaos"):
            self.upsert_orgao(orgao)
        self.banco.commit()
        logger.info("Orgao processado: %s registros.", self.stats["Orgao"])

    def popular_temas(self) -> None:
        logger.info("Populando Tema...")
        payload = self.api.get("referencias/proposicoes/codTema")
        for tema in (payload or {}).get("dados") or []:
            if isinstance(tema, dict):
                self.upsert_tema(tema)
        self.banco.commit()
        logger.info("Tema processado: %s registros.", self.stats["Tema"])

    def popular_deputados(self) -> None:
        logger.info("Populando Deputado...")
        for deputado in self.api.iter_paginated("deputados"):
            dep_id = self.upsert_deputado(deputado)
            if dep_id is not None:
                self.deputado_ids.append(dep_id)
        self.banco.commit()
        logger.info("Deputado processado: %s registros.", self.stats["Deputado"])

    def buscar_detalhes_proposicao(self, prop_id: int) -> dict[str, Any] | None:
        payload = self.api.get(f"proposicoes/{prop_id}")
        dados = payload.get("dados") if payload else None
        return dados if isinstance(dados, dict) else None

    def buscar_temas_proposicao(self, prop_id: int, detalhes: dict[str, Any]) -> list[int]:
        tema_codes: list[int] = []

        payload = self.api.get(f"proposicoes/{prop_id}/temas")
        for tema in (payload or {}).get("dados") or []:
            if isinstance(tema, dict):
                tema_cod = self.upsert_tema(tema)
                if tema_cod is not None:
                    tema_codes.append(tema_cod)

        possible_values = [
            detalhes.get("codTema"),
            detalhes.get("codTemas"),
            detalhes.get("tema"),
            detalhes.get("temas"),
        ]
        for value in possible_values:
            if value is None:
                continue
            values = value if isinstance(value, list) else [value]
            for item in values:
                if isinstance(item, dict):
                    tema_cod = self.upsert_tema(item)
                else:
                    tema_cod = as_int(item)
                if tema_cod is not None:
                    tema_codes.append(tema_cod)

        unique_codes = sorted(set(tema_codes))
        return unique_codes

    def coletar_ids_proposicoes_com_autoria_de_deputados(
        self,
        ano: int,
        max_proposicoes: int,
    ) -> list[int]:
        proposicao_ids: list[int] = []
        seen: set[int] = set()

        logger.info("Buscando proposicoes por idDeputadoAutor para priorizar Participa...")
        for dep_index, dep_id in enumerate(self.deputado_ids, start=1):
            params = {
                "ano": ano,
                "idDeputadoAutor": dep_id,
                "ordem": "DESC",
                "ordenarPor": "id",
                "itens": DEFAULT_ITEMS_PER_PAGE,
            }
            for proposicao in self.api.iter_paginated("proposicoes", params=params):
                prop_id = as_int(proposicao.get("id"))
                if prop_id is None or prop_id in seen:
                    continue
                seen.add(prop_id)
                proposicao_ids.append(prop_id)
                if len(proposicao_ids) >= max_proposicoes:
                    logger.info(
                        "Selecionadas %s proposicoes com autoria de deputados.",
                        len(proposicao_ids),
                    )
                    return proposicao_ids

            if dep_index % 50 == 0:
                logger.info(
                    "%s deputados consultados; %s proposicoes selecionadas ate agora.",
                    dep_index,
                    len(proposicao_ids),
                )

        logger.info(
            "Selecionadas %s proposicoes com autoria de deputados apos consultar deputados disponiveis.",
            len(proposicao_ids),
        )
        return proposicao_ids

    def coletar_ids_proposicoes_gerais(
        self,
        ano: int,
        max_proposicoes: int,
        ids_existentes: set[int],
    ) -> list[int]:
        proposicao_ids: list[int] = []
        params = {
            "ano": ano,
            "ordem": "DESC",
            "ordenarPor": "id",
        }
        for proposicao in self.api.iter_paginated("proposicoes", params=params):
            prop_id = as_int(proposicao.get("id"))
            if prop_id is None or prop_id in ids_existentes:
                continue
            proposicao_ids.append(prop_id)
            ids_existentes.add(prop_id)
            if len(proposicao_ids) >= max_proposicoes:
                return proposicao_ids
        return proposicao_ids

    def popular_proposicoes(self, ano: int, max_proposicoes: int) -> None:
        logger.info("Populando Proposicao e relacionamentos: ano=%s limite=%s.", ano, max_proposicoes)
        proposicao_ids = self.coletar_ids_proposicoes_com_autoria_de_deputados(
            ano,
            max_proposicoes,
        )
        if len(proposicao_ids) < max_proposicoes:
            faltantes = max_proposicoes - len(proposicao_ids)
            logger.info(
                "Completando carga com ate %s proposicoes gerais do ano %s.",
                faltantes,
                ano,
            )
            proposicao_ids.extend(
                self.coletar_ids_proposicoes_gerais(
                    ano,
                    faltantes,
                    set(proposicao_ids),
                )
            )

        for index, prop_id in enumerate(proposicao_ids, start=1):
            try:
                detalhes = self.buscar_detalhes_proposicao(prop_id)
                if not detalhes:
                    continue
                prop_id = self.upsert_proposicao(detalhes)
                if prop_id is None:
                    continue

                self.popular_autores(prop_id)
                self.popular_classificacao(prop_id, detalhes)
                self.popular_tramitacoes(prop_id)

                if index % 25 == 0:
                    self.banco.commit()
                    logger.info("%s proposicoes processadas...", index)
            except MySQLError as exc:
                self.banco.rollback()
                logger.warning("Erro MySQL ao processar proposicao %s: %s", prop_id, exc)
            except Exception as exc:
                self.banco.rollback()
                logger.warning("Erro inesperado ao processar proposicao %s: %s", prop_id, exc)

        self.banco.commit()
        logger.info("Proposicoes processadas: %s.", self.stats["Proposicao"])

    def popular_autores(self, prop_id: int) -> None:
        payload = self.api.get(f"proposicoes/{prop_id}/autores")
        autores = (payload or {}).get("dados") or []
        for author in autores:
            if not isinstance(author, dict):
                continue
            if not is_deputado_author(author):
                self.stats["autores_sem_deputado"] += 1
                continue
            dep_id = self.ensure_deputado(author)
            if dep_id is None:
                logger.debug("Autor sem identificador de deputado ignorado: %s", author)
                continue
            self.upsert_participa(dep_id, prop_id, author)

    def popular_classificacao(self, prop_id: int, detalhes: dict[str, Any]) -> None:
        for tema_cod in self.buscar_temas_proposicao(prop_id, detalhes):
            self.upsert_classificacao(prop_id, tema_cod)

    def popular_tramitacoes(self, prop_id: int) -> None:
        payload = self.api.get(f"proposicoes/{prop_id}/tramitacoes")
        for tramitacao in (payload or {}).get("dados") or []:
            if isinstance(tramitacao, dict):
                self.upsert_tramitacao(prop_id, tramitacao)

    def print_stats(self) -> None:
        logger.info("Resumo da carga:")
        for table in [
            "Partido",
            "Orgao",
            "Tema",
            "Proposicao",
            "Deputado",
            "Tramitacao",
            "Participa",
            "Classificacao",
        ]:
            logger.info("  %-14s %s", table, self.stats[table])
        logger.info("  %-14s %s", "autores_sem_deputado", self.stats["autores_sem_deputado"])
        logger.info("  %-14s %s", "tramitacoes_sem_orgao", self.stats["tramitacoes_sem_orgao"])


def main() -> int:
    load_env_file()

    api_base_url = os.getenv("CAMARA_API_BASE_URL", DEFAULT_API_BASE_URL)
    ano = env_int("ANO_PROPOSICOES", 2025)
    max_proposicoes = env_int("MAX_PROPOSICOES", 500)

    logger.info(
        "Conectando ao MySQL em %s:%s/%s.",
        os.getenv("MYSQL_HOST", "127.0.0.1"),
        os.getenv("MYSQL_PORT", "3307"),
        os.getenv("MYSQL_DATABASE", "trabalho_final"),
    )

    banco = Banco()
    try:
        popular = PopularBanco(banco, CamaraAPI(api_base_url))
        popular.popular_partidos()
        popular.popular_orgaos()
        popular.popular_temas()
        popular.popular_deputados()
        popular.popular_proposicoes(ano=ano, max_proposicoes=max_proposicoes)
        popular.print_stats()
    finally:
        banco.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
