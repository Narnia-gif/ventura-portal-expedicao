"""Testes unitários das validações – Ventura Biomédica, Portal Comercial e Expedição.
Integrantes: Luis Felipe Rodrigues Galan, Leandro Inacio, Felipe dos Reis.

Técnicas: particionamento de equivalência (EP) e análise de valor limite (BVA).
Cada teste traz no nome o caso de teste (CT) do plano.
"""
from datetime import date
from decimal import Decimal

import pytest

from portal.validacoes import (
    validar_senha, validar_codigo_cliente, validar_ean13,
    validar_volumes, validar_peso, validar_periodo, validar_cep,
)


# ---------- CT003 – RF01: senha de 8 a 20 caracteres (BVA: 7, 8, 20, 21) ----------
@pytest.mark.parametrize("senha", ["Abc@1234", "Abc@1234567890123456"], ids=["8_chars", "20_chars"])
def test_ct003_senha_no_limite_e_aceita(senha):
    assert validar_senha(senha) == senha


@pytest.mark.parametrize("senha", ["Abc@123", "Abc@12345678901234567"], ids=["7_chars", "21_chars"])
def test_ct003_senha_fora_do_limite_e_recusada(senha):
    with pytest.raises(ValueError, match="de 8 a 20 caracteres"):
        validar_senha(senha)


def test_ct003_senha_vazia_e_recusada():
    with pytest.raises(ValueError, match="Senha obrigatória"):
        validar_senha("")


# ---------- CT007/CT008 – RF02: código do cliente (EP + BVA: 5, 6, 7 dígitos) ----------
def test_ct008_codigo_com_6_digitos_e_aceito():
    assert validar_codigo_cliente("000123") == "000123"


@pytest.mark.parametrize("codigo", ["00012", "0001234"], ids=["5_digitos", "7_digitos"])
def test_ct008_codigo_com_tamanho_errado_e_recusado(codigo):
    with pytest.raises(ValueError, match="6 dígitos"):
        validar_codigo_cliente(codigo)


def test_ct007_codigo_nao_numerico_e_recusado():
    with pytest.raises(ValueError, match="apenas números"):
        validar_codigo_cliente("12A45B")


def test_ct007_codigo_vazio_e_recusado():
    with pytest.raises(ValueError, match="Informe o código do cliente"):
        validar_codigo_cliente("")


# ---------- CT015 – RF05: EAN-13 (BVA: 12, 13, 14 dígitos; EP: DV certo/errado, letras) ----------
def test_ct015_ean_valido_e_aceito():
    assert validar_ean13("7891000000014") == "7891000000014"


@pytest.mark.parametrize("ean", [
    "789100000001",     # 12 dígitos
    "78910000000140",   # 14 dígitos
    "7891000000015",    # 13 dígitos, dígito verificador errado
    "78910000A0014",    # contém letra
], ids=["12_digitos", "14_digitos", "dv_errado", "com_letra"])
def test_ct015_ean_invalido_e_recusado(ean):
    with pytest.raises(ValueError, match="Código de barras inválido"):
        validar_ean13(ean)


# ---------- CT017 – RF06: volumes de 1 a 99 (BVA: 0, 1, 99, 100) ----------
@pytest.mark.parametrize("valor, esperado", [(1, 1), (99, 99)], ids=["1", "99"])
def test_ct017_volumes_no_limite_sao_aceitos(valor, esperado):
    assert validar_volumes(valor) == esperado


@pytest.mark.parametrize("valor", [0, 100, -1], ids=["0", "100", "negativo"])
def test_ct017_volumes_fora_da_faixa_sao_recusados(valor):
    with pytest.raises(ValueError, match="de 1 a 99 volumes"):
        validar_volumes(valor)


@pytest.mark.parametrize("valor", ["2,5", "dois"], ids=["decimal", "texto"])
def test_ct017_volumes_nao_inteiros_sao_recusados(valor):
    with pytest.raises(ValueError, match="deve ser inteiro"):
        validar_volumes(valor)


# ---------- CT018 – RF06/RF08: peso de 0,01 a 999,99 kg (BVA: 0,00 · 0,01 · 999,99 · 1000,00) ----------
@pytest.mark.parametrize("valor, esperado", [("0,01", Decimal("0.01")), ("999,99", Decimal("999.99"))], ids=["0,01", "999,99"])
def test_ct018_peso_no_limite_e_aceito(valor, esperado):
    assert validar_peso(valor) == esperado


@pytest.mark.parametrize("valor", ["0,00", "1000,00", "-5,00"], ids=["0,00", "1000,00", "negativo"])
def test_ct018_peso_fora_da_faixa_e_recusado(valor):
    with pytest.raises(ValueError, match="entre 0,01 e 999,99 kg"):
        validar_peso(valor)


@pytest.mark.parametrize("valor", ["12,555", "doze"], ids=["3_casas", "texto"])
def test_ct018_peso_mal_formatado_e_recusado(valor):
    with pytest.raises(ValueError, match="até 2 casas decimais"):
        validar_peso(valor)


# ---------- CT020 – RF07: período até 90 dias (BVA: 0, 89, 90, 91) ----------
@pytest.mark.parametrize("inicio, fim, dias", [
    (date(2026, 11, 5), date(2026, 11, 5), 0),
    (date(2026, 8, 7), date(2026, 11, 4), 89),
    (date(2026, 8, 7), date(2026, 11, 5), 90),
], ids=["0_dias", "89_dias", "90_dias"])
def test_ct020_periodo_valido_e_aceito(inicio, fim, dias):
    assert validar_periodo(inicio, fim) == dias


def test_ct020_periodo_de_91_dias_e_recusado():
    with pytest.raises(ValueError, match="máximo é de 90 dias"):
        validar_periodo(date(2026, 8, 7), date(2026, 11, 6))


def test_ct020_data_inicial_maior_que_final_e_recusada():
    with pytest.raises(ValueError, match="data inicial deve ser anterior"):
        validar_periodo(date(2026, 11, 10), date(2026, 11, 5))


# ---------- CT022 – RF08: CEP com 8 dígitos (BVA: 7, 8, 9) ----------
@pytest.mark.parametrize("cep", ["15015000", "15015-000"], ids=["sem_hifen", "com_hifen"])
def test_ct022_cep_valido_e_normalizado(cep):
    assert validar_cep(cep) == "15015000"


@pytest.mark.parametrize("cep", ["1501500", "150150000", "15A15000"], ids=["7_digitos", "9_digitos", "com_letra"])
def test_ct022_cep_invalido_e_recusado(cep):
    with pytest.raises(ValueError, match="CEP inválido"):
        validar_cep(cep)
