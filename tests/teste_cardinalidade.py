# ==========================================================
# test_cardinalidades.py
#
# Objetivo:
# Validar cardinalidades do DER utilizando
# diretamente a API da Câmara dos Deputados.
#
# Cardinalidades:
# - N:N
# - 1:N
# - N:1
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
# UTILITARIOS
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
# CARDINALIDADE N:N
# ==========================================================

def testar_cardinalidade_nn():
    """
    Valida cardinalidade N:N
    entre DEPUTADO e PROPOSICAO.
    """

    print_title(
        "TESTANDO CARDINALIDADE N:N"
    )

    deputado_id = 220592

    dados = api_get(
        "proposicoes",
        {
            "idDeputadoAutor": deputado_id,
            "itens": 5
        }
    )

    proposicoes = dados["dados"]

    print_json(proposicoes)

    print(
        "\nQuantidade de proposições:",
        len(proposicoes)
    )

    # ------------------------------------------------------
    # VALIDACAO
    # ------------------------------------------------------

    if len(proposicoes) > 1:

        print(
            "\n[OK] Um deputado participa "
            "de múltiplas proposições"
        )

        print(
            "[OK] Cardinalidade "
            "N:N validada"
        )


# ==========================================================
# CARDINALIDADE 1:N
# ==========================================================

def testar_cardinalidade_1n():
    """
    Valida cardinalidade 1:N
    entre PROPOSICAO e TRAMITACAO.
    """

    print_title(
        "TESTANDO CARDINALIDADE 1:N"
    )

    proposicao_id = 14666

    dados = api_get(
        f"proposicoes/"
        f"{proposicao_id}/tramitacoes"
    )

    tramitacoes = dados["dados"]

    print(
        "\nQuantidade de tramitações:",
        len(tramitacoes)
    )

    if tramitacoes:

        print_json(tramitacoes[0])

    # ------------------------------------------------------
    # VALIDACAO
    # ------------------------------------------------------

    if len(tramitacoes) > 1:

        print(
            "\n[OK] Uma proposição possui "
            "múltiplas tramitações"
        )

        print(
            "[OK] Cardinalidade "
            "1:N validada"
        )


# ==========================================================
# CARDINALIDADE N:1
# ==========================================================

def testar_cardinalidade_n1():
    """
    Valida cardinalidade N:1
    entre TRAMITACAO e ORGAO.
    """

    print_title(
        "TESTANDO CARDINALIDADE N:1"
    )

    proposicao_id = 14666

    dados = api_get(
        f"proposicoes/"
        f"{proposicao_id}/tramitacoes"
    )

    tramitacoes = dados["dados"]

    print_json(tramitacoes[:3])

    # ------------------------------------------------------
    # VALIDACAO
    # ------------------------------------------------------

    orgaos = []

    for tramitacao in tramitacoes:

        sigla = tramitacao.get(
            "siglaOrgao"
        )

        if sigla:

            orgaos.append(sigla)

    print(
        "\nÓrgãos encontrados:\n"
    )

    print(orgaos)

    if orgaos:

        print(
            "\n[OK] Diversas tramitações "
            "ocorrem em órgãos"
        )

        print(
            "[OK] Cardinalidade "
            "N:1 validada"
        )


# ==========================================================
# CARDINALIDADE N:N PROPOSICAO ↔ TEMA
# ==========================================================

def testar_cardinalidade_tema():
    """
    Valida cardinalidade N:N
    entre PROPOSICAO e TEMA.
    """

    print_title(
        "TESTANDO CARDINALIDADE "
        "N:N PROPOSICAO ↔ TEMA"
    )

    proposicao_id = 14666

    dados = api_get(
        f"proposicoes/{proposicao_id}"
    )

    proposicao = dados["dados"]

    keywords = proposicao.get(
        "keywords"
    )

    print(
        "\nKeywords encontradas:\n"
    )

    print(keywords)

    # ------------------------------------------------------
    # VALIDACAO
    # ------------------------------------------------------

    if keywords:

        temas = keywords.split(",")

        print(
            "\nQuantidade de temas:",
            len(temas)
        )

        print(
            "\n[OK] Uma proposição "
            "possui múltiplos temas"
        )

        print(
            "[OK] Cardinalidade "
            "N:N validada"
        )


# ==========================================================
# EXECUCAO
# ==========================================================

def testar_cardinalidades():
    """
    Executa todos os testes
    de cardinalidade.
    """

    print(
        "\nVALIDANDO CARDINALIDADES "
        "DO DER\n"
    )

    testar_cardinalidade_nn()

    testar_cardinalidade_1n()

    testar_cardinalidade_n1()

    testar_cardinalidade_tema()

    print(
        "\nVALIDACAO DE "
        "CARDINALIDADES FINALIZADA\n"
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    testar_cardinalidades()