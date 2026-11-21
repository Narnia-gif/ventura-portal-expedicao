"""Testes do servidor web (integração das regras com a API) – Ventura Biomédica.
Integrantes: Luis Felipe Rodrigues Galan, Leandro Inacio, Felipe dos Reis.
"""
import json
import threading
import urllib.request

import pytest

from portal import servidor
from portal.servidor import tratar


@pytest.fixture(autouse=True)
def conferencia_limpa():
    tratar("/api/reiniciar", {})


# RF02 – consulta de cliente (CT006, CT007, CT009)
def test_ct006_cliente_ativo_e_encontrado():
    status, corpo = tratar("/api/cliente", {"codigo": "000123"})
    assert status == 200 and corpo["nome"] == "Laboratório Exemplo Ltda"


@pytest.mark.parametrize("codigo, status_esperado, mensagem", [
    ("999999", 404, "Cliente não encontrado"),
    ("12A45B", 400, "apenas números"),
    ("000777", 400, "Cliente bloqueado"),
], ids=["inexistente", "nao_numerico", "bloqueado"])
def test_ct007_ct009_cliente_invalido(codigo, status_esperado, mensagem):
    status, corpo = tratar("/api/cliente", {"codigo": codigo})
    assert status == status_esperado and mensagem in corpo["erro"]


# RF05/RF06 – conferência pela API (CT013, CT014)
def test_ct013_conferencia_completa_pela_api():
    for ean in ("7891000000014", "7891000000014", "7891000000021"):
        assert tratar("/api/leitura", {"ean": ean})[0] == 200
    status, corpo = tratar("/api/finalizar", {"volumes": "3", "peso": "12,50"})
    assert status == 200 and "Conferido" in corpo["mensagem"]


def test_ct014_produto_fora_do_pedido_pela_api():
    status, corpo = tratar("/api/leitura", {"ean": "7891000000038"})
    assert status == 400 and "não pertence" in corpo["erro"]


def test_ct017_finalizar_com_volumes_invalidos():
    status, corpo = tratar("/api/finalizar", {"volumes": "0", "peso": "12,50"})
    assert status == 400 and "de 1 a 99 volumes" in corpo["erro"]


# RF08 – frete (CT021, CT022)
def test_ct021_frete_ordenado_pelo_menor_valor():
    status, corpo = tratar("/api/frete", {"cep": "15015-000", "peso": "12,50"})
    valores = [c["valor"] for c in corpo["cotacoes"]]
    assert status == 200 and len(valores) == 3 and valores == sorted(valores)


def test_ct022_frete_com_cep_invalido():
    status, corpo = tratar("/api/frete", {"cep": "1501500", "peso": "12,50"})
    assert status == 400 and "CEP inválido" in corpo["erro"]


# Servidor HTTP de verdade: a página abre e a API responde
def test_pagina_e_api_respondem_por_http():
    srv = servidor.criar_servidor(porta=0)  # porta livre qualquer
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        html = urllib.request.urlopen(base + "/").read().decode()
        assert "Portal Comercial e Expedição" in html
        req = urllib.request.Request(base + "/api/cliente", data=json.dumps({"codigo": "000123"}).encode(),
                                     headers={"Content-Type": "application/json"})
        assert json.loads(urllib.request.urlopen(req).read())["codigo"] == "000123"
    finally:
        srv.shutdown()


# Cadastros usados nas listas da tela
def test_cadastros_tem_clientes_e_produtos():
    status, corpo = tratar("/api/cadastros", {})
    assert status == 200
    assert len(corpo["clientes"]) >= 4 and len(corpo["produtos"]) >= 4
    no_pedido = {p["ean"] for p in corpo["produtos"] if p["no_pedido"]}
    assert no_pedido == {"7891000000014", "7891000000021"}


@pytest.mark.parametrize("codigo", ["000201", "000202", "000203"])
def test_ct006_hospitais_cadastrados_sao_encontrados(codigo):
    status, corpo = tratar("/api/cliente", {"codigo": codigo})
    assert status == 200 and corpo["codigo"] == codigo


def test_ct021_frete_mais_caro_para_mais_longe():
    perto = tratar("/api/frete", {"cep": "15015-000", "peso": "12,50"})[1]["cotacoes"][0]["valor"]
    longe = tratar("/api/frete", {"cep": "01310-100", "peso": "12,50"})[1]["cotacoes"][0]["valor"]
    assert longe > perto
