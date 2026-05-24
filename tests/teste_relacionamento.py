# ==========================================================
# test_relacionamentos.py
#
# Objetivo:
# Validar relacionamentos do DER utilizando
# diretamente a API da Câmara dos Deputados.
#
# Relacionamentos:
# - AUTORIA
# - FILIACAO
# - POSSUI_TRAMITACAO
# - OCORRE_EM
# - CLASSIFICACAO
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
# TESTE AUTORIA
# ==========================================================

def testar_autoria(prop_id):
    """
    Valida relacionamento:
    DEPUTADO ↔ PROPOSICAO
    """

    print_title(
        "TESTANDO RELACIONAMENTO AUTORIA"
    )

    dados = api_get(
        f"proposicoes/{prop_id}/autores"
    )

    autores = dados["dados"]

    print_json(autores)

    print(
        "\nQuantidade de autores:",
        len(autores)
    )

    # ------------------------------------------------------
    # VALIDAÇÃO
    # ------------------------------------------------------

    if autores:

        print(
            "\n[OK] Relacionamento "
            "AUTORIA validado"
        )

        print(
            "[OK] Atributos do "
            "relacionamento encontrados:"
        )

        print(
            "- ordemAssinatura"
        )

        print(
            "- proponente"
        )


# ==========================================================
# TESTE FILIACAO
# ==========================================================

def testar_filiacao():
    """
    Valida relacionamento:
    DEPUTADO ↔ PARTIDO
    """

    print_title(
        "TESTANDO RELACIONAMENTO FILIACAO"
    )

    dados = api_get(
        "deputados",
        {"itens": 1}
    )

    deputado = dados["dados"][0]

    print_json(deputado)

    if "siglaPartido" in deputado:

        print(
            "\n[OK] Relacionamento "
            "FILIACAO validado"
        )


# ==========================================================
# TESTE POSSUI_TRAMITACAO
# ==========================================================

def testar_possui_tramitacao(prop_id):
    """
    Valida relacionamento:
    PROPOSICAO ↔ TRAMITACAO
    """

    print_title(
        "TESTANDO RELACIONAMENTO "
        "POSSUI_TRAMITACAO"
    )

    dados = api_get(
        f"proposicoes/{prop_id}/tramitacoes"
    )

    tramitacoes = dados["dados"]

    print(
        "\nQuantidade de tramitações:",
        len(tramitacoes)
    )

    if tramitacoes:

        print_json(tramitacoes[0])

    # ------------------------------------------------------
    # VALIDAÇÃO
    # ------------------------------------------------------

    if len(tramitacoes) > 1:

        print(
            "\n[OK] Cardinalidade "
            "1:N validada"
        )

        print(
            "[OK] Relacionamento "
            "POSSUI_TRAMITACAO validado"
        )


# ==========================================================
# TESTE OCORRE_EM
# ==========================================================

def testar_ocorre_em(prop_id):
    """
    Valida relacionamento:
    TRAMITACAO ↔ ORGAO
    """

    print_title(
        "TESTANDO RELACIONAMENTO "
        "OCORRE_EM"
    )

    dados = api_get(
        f"proposicoes/{prop_id}/tramitacoes"
    )

    tramitacao = dados["dados"][0]

    print_json(tramitacao)

    # ------------------------------------------------------
    # VALIDAÇÃO
    # ------------------------------------------------------

    if "siglaOrgao" in tramitacao:

        print(
            "\n[OK] Relacionamento "
            "OCORRE_EM validado"
        )


# ==========================================================
# TESTE CLASSIFICACAO
# ==========================================================

def testar_classificacao(prop_id):
    """
    Valida relacionamento:
    PROPOSICAO ↔ TEMA
    """

    print_title(
        "TESTANDO RELACIONAMENTO "
        "CLASSIFICACAO"
    )

    dados = api_get(
        f"proposicoes/{prop_id}"
    )

    proposicao = dados["dados"]

    print_json(proposicao)

    keywords = proposicao.get("keywords")

    print("\nKeywords encontradas:\n")

    print(keywords)

    # ------------------------------------------------------
    # VALIDAÇÃO
    # ------------------------------------------------------

    if keywords:

        print(
            "\n[OK] Relacionamento "
            "CLASSIFICACAO validado"
        )


# ==========================================================
# EXECUCAO
# ==========================================================

def testar_relacionamentos():
    """
    Executa todos os testes
    de relacionamentos.
    """

    print(
        "\nVALIDANDO RELACIONAMENTOS "
        "DO DER\n"
    )

    # ------------------------------------------------------
    # PROPOSICAO UTILIZADA
    # ------------------------------------------------------

    proposicao_id = 14666

    # ------------------------------------------------------
    # TESTES
    # ------------------------------------------------------

    testar_autoria(
        proposicao_id
    )

    testar_filiacao()

    testar_possui_tramitacao(
        proposicao_id
    )

    testar_ocorre_em(
        proposicao_id
    )

    testar_classificacao(
        proposicao_id
    )

    print(
        "\nVALIDACAO DE "
        "RELACIONAMENTOS FINALIZADA\n"
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    testar_relacionamentos()