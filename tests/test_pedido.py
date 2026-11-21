"""Testes unitários de status e conferência – Ventura Biomédica, Portal Comercial e Expedição.
Integrantes: Luis Felipe Rodrigues Galan, Leandro Inacio, Felipe dos Reis.
"""
import pytest

from portal.pedido import (
    Conferencia, mudar_status, LIBERADO, EM_CONFERENCIA, CONFERIDO, ENVIADO,
)

EAN_A = "7891000000014"
EAN_B = "7891000000021"
EAN_FORA = "7891000000038"
EAN_10 = "7891000000045"


# ---------- CT023/CT024 – RF09: transição de estados ----------
def test_ct023_fluxo_valido_ate_enviado():
    status = LIBERADO
    for proximo in (EM_CONFERENCIA, CONFERIDO, ENVIADO):
        status = mudar_status(status, proximo)
    assert status == ENVIADO


@pytest.mark.parametrize("origem, destino", [
    (LIBERADO, ENVIADO),
    (LIBERADO, CONFERIDO),
    (ENVIADO, EM_CONFERENCIA),
    (CONFERIDO, LIBERADO),
], ids=["pula_para_enviado", "pula_conferencia", "volta_de_enviado", "volta_para_liberado"])
def test_ct024_transicao_invalida_e_bloqueada(origem, destino):
    with pytest.raises(ValueError, match="Transição de status não permitida"):
        mudar_status(origem, destino)


# ---------- CT013/CT014 – RF05: conferência com coletor ----------
def test_ct013_conferencia_completa_e_finalizada():
    conf = Conferencia({EAN_A: 2, EAN_B: 1})
    for ean in (EAN_A, EAN_A, EAN_B):
        conf.registrar_leitura(ean)
    assert conf.finalizar() == CONFERIDO


def test_ct014_produto_fora_do_pedido_e_recusado():
    conf = Conferencia({EAN_A: 2, EAN_B: 1})
    with pytest.raises(ValueError, match="não pertence a este pedido"):
        conf.registrar_leitura(EAN_FORA)
    assert conf.faltam() == 3  # nenhuma quantidade foi somada


# ---------- CT016 – RF05: quantidade conferida (BVA: 9, 10, 11 para pedido de 10) ----------
def test_ct016_com_9_leituras_nao_finaliza():
    conf = Conferencia({EAN_10: 10})
    for _ in range(9):
        conf.registrar_leitura(EAN_10)
    with pytest.raises(ValueError, match="faltam 1 unidade"):
        conf.finalizar()


def test_ct016_com_10_leituras_finaliza():
    conf = Conferencia({EAN_10: 10})
    for _ in range(10):
        conf.registrar_leitura(EAN_10)
    assert conf.finalizar() == CONFERIDO


def test_ct016_11a_leitura_excede_e_e_recusada():
    conf = Conferencia({EAN_10: 10})
    for _ in range(10):
        conf.registrar_leitura(EAN_10)
    with pytest.raises(ValueError, match=r"excede o pedido \(10\)"):
        conf.registrar_leitura(EAN_10)
    assert conf.conferido[EAN_10] == 10
