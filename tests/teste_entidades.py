# ==========================================================
# test_entidades.py
#
# Objetivo:
# Validar entidades do DER utilizando diretamente
# a API da Câmara dos Deputados.
#
# ==========================================================

import requests
import json

BASE_URL = (
    "https://dadosabertos.camara.leg.br/api/v2"
)


# ==========================================================
# CLIENT API
# ==========================================================

def api_get(endpoint, params=None):
    """
    Realiza requisição GET na API.
    """

    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        params=params
    )

    response.raise_for_status()

    return response.json()


# ==========================================================
# UTILITÁRIOS
# ==========================================================

def print_title(title):
    """
    Imprime título formatado.
    """

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_json(data):
    """
    Imprime JSON formatado.
    """

    print(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        )
    )


# ==========================================================
# API PROPOSICOES
# ==========================================================

def listar_proposicoes():
    """
    Lista proposições.
    """

    return api_get(
        "proposicoes",
        {"itens": 1}
    )


def detalhes_proposicao(prop_id):
    """
    Busca detalhes da proposição.
    """

    return api_get(
        f"proposicoes/{prop_id}"
    )


def tramitacoes_proposicao(prop_id):
    """
    Busca tramitações.
    """

    return api_get(
        f"proposicoes/{prop_id}/tramitacoes"
    )


# ==========================================================
# API DEPUTADOS
# ==========================================================

def listar_deputados():
    """
    Lista deputados.
    """

    return api_get(
        "deputados",
        {"itens": 1}
    )


# ==========================================================
# API PARTIDOS
# ==========================================================

def listar_partidos():
    """
    Lista partidos.
    """

    return api_get(
        "partidos",
        {"itens": 1}
    )


# ==========================================================
# API ORGAOS
# ==========================================================

def detalhes_orgao(orgao_id):
    """
    Busca órgão.
    """

    return api_get(
        f"orgaos/{orgao_id}"
    )


# ==========================================================
# API TEMAS
# ==========================================================

def listar_temas():
    """
    Lista temas.
    """

    return api_get(
        "referencias/proposicoes/codTema"
    )


# ==========================================================
# TESTE PROPOSICAO
# ==========================================================

def testar_proposicao():
    """
    Valida entidade PROPOSICAO.
    """

    print_title(
        "TESTANDO ENTIDADE PROPOSICAO"
    )

    dados = listar_proposicoes()

    proposicao = dados["dados"][0]

    print_json(proposicao)

    print(
        "\n[OK] Entidade "
        "PROPOSICAO validada"
    )

    return proposicao["id"]


# ==========================================================
# TESTE DETALHES PROPOSICAO
# ==========================================================

def testar_detalhes_proposicao(prop_id):
    """
    Valida atributos completos
    da proposicao.
    """

    print_title(
        "TESTANDO DETALHES "
        "DA PROPOSICAO"
    )

    dados = detalhes_proposicao(prop_id)

    print_json(dados["dados"])

    print(
        "\n[OK] Atributos da "
        "PROPOSICAO validados"
    )


# ==========================================================
# TESTE DEPUTADO
# ==========================================================

def testar_deputado():
    """
    Valida entidade DEPUTADO.
    """

    print_title(
        "TESTANDO ENTIDADE DEPUTADO"
    )

    dados = listar_deputados()

    deputado = dados["dados"][0]

    print_json(deputado)

    print(
        "\n[OK] Entidade "
        "DEPUTADO validada"
    )


# ==========================================================
# TESTE PARTIDO
# ==========================================================

def testar_partido():
    """
    Valida entidade PARTIDO.
    """

    print_title(
        "TESTANDO ENTIDADE PARTIDO"
    )

    dados = listar_partidos()

    partido = dados["dados"][0]

    print_json(partido)

    print(
        "\n[OK] Entidade "
        "PARTIDO validada"
    )


# ==========================================================
# TESTE TRAMITACAO
# ==========================================================

def testar_tramitacao(prop_id):
    """
    Valida entidade TRAMITACAO.
    """

    print_title(
        "TESTANDO ENTIDADE TRAMITACAO"
    )

    dados = tramitacoes_proposicao(
        prop_id
    )

    tramitacao = dados["dados"][0]

    print_json(tramitacao)

    print(
        "\n[OK] Entidade "
        "TRAMITACAO validada"
    )


# ==========================================================
# TESTE ORGAO
# ==========================================================

def testar_orgao():
    """
    Valida entidade ORGAO.
    """

    print_title(
        "TESTANDO ENTIDADE ORGAO"
    )

    dados = detalhes_orgao(180)

    print_json(dados["dados"])

    print(
        "\n[OK] Entidade "
        "ORGAO validada"
    )


# ==========================================================
# TESTE TEMA
# ==========================================================

def testar_tema():
    """
    Valida entidade TEMA.
    """

    print_title(
        "TESTANDO ENTIDADE TEMA"
    )

    dados = listar_temas()

    tema = dados["dados"][0]

    print_json(tema)

    print(
        "\n[OK] Entidade "
        "TEMA validada"
    )


# ==========================================================
# EXECUCAO
# ==========================================================

def testar_entidades():
    """
    Executa todos os testes.
    """

    print(
        "\nVALIDANDO ENTIDADES "
        "DO DER\n"
    )

    proposicao_id = testar_proposicao()

    testar_detalhes_proposicao(
        proposicao_id
    )

    testar_deputado()

    testar_partido()

    testar_tramitacao(
        proposicao_id
    )

    testar_orgao()

    testar_tema()

    print(
        "\nVALIDACAO DE "
        "ENTIDADES FINALIZADA\n"
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    testar_entidades()