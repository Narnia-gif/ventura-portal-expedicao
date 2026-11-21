"""Servidor web simples do Portal Comercial e Expedição (Ventura Biomédica).

Integrantes: Luis Felipe Rodrigues Galan, Leandro Inacio, Felipe dos Reis.

Usa só a biblioteca padrão do Python. Os dados abaixo são FICTÍCIOS e
substituem, nesta demonstração, as tabelas do Protheus.

Para rodar:  python -m portal.servidor   e abrir http://localhost:8000
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from portal.pedido import Conferencia
from portal.validacoes import validar_codigo_cliente, validar_cep, validar_peso, validar_volumes

# ----- dados fictícios (no sistema real vêm do Protheus) -----
CLIENTES = {
    "000123": {"nome": "Laboratório Exemplo Ltda", "cidade": "São José do Rio Preto/SP", "cep": "15015-000", "bloqueado": False},
    "000201": {"nome": "Hospital Bem-Estar", "cidade": "São Paulo/SP", "cep": "01310-100", "bloqueado": False},
    "000202": {"nome": "Hospital Horizonte", "cidade": "Ribeirão Preto/SP", "cep": "14010-000", "bloqueado": False},
    "000203": {"nome": "Clínica Vitalis", "cidade": "Bauru/SP", "cep": "17010-000", "bloqueado": False},
    "000777": {"nome": "Hospital Fictício S/A", "cidade": "Campinas/SP", "cep": "13010-000", "bloqueado": True},
}
PRODUTOS = {
    "7891000000014": "Luva nitrílica cx 100",
    "7891000000021": "Seringa 10 ml cx 50",
    "7891000000038": "Máscara cirúrgica cx 50",
    "7891000000045": "Kit coleta de sangue",
    "7891000000052": "Gaze estéril pct 10",
}
PEDIDO = {"numero": "045210", "itens": {"7891000000014": 2, "7891000000021": 1}}
TRANSPORTADORAS = [  # nome, valor fixo, valor por kg, prazo em dias
    ("Transportadora Alfa", 25.0, 1.8, 3),
    ("Beta Cargas", 18.0, 2.4, 5),
    ("Gama Express", 40.0, 1.2, 2),
]

conferencia = Conferencia(PEDIDO["itens"])


def consultar_cliente(codigo):
    codigo = validar_codigo_cliente(codigo)
    cliente = CLIENTES.get(codigo)
    if cliente is None:
        raise LookupError("Cliente não encontrado.")
    if cliente["bloqueado"]:
        raise ValueError("Cliente bloqueado no Protheus. Procure o Comercial.")
    return {"codigo": codigo, **cliente}


def situacao_conferencia():
    itens = [{"ean": e, "produto": PRODUTOS[e], "pedido": q, "conferido": conferencia.conferido[e]}
             for e, q in conferencia.pedido.items()]
    return {"numero": PEDIDO["numero"], "itens": itens, "faltam": conferencia.faltam()}


# Quanto mais longe da fábrica (Rio Preto, CEP 15xxx), mais caro e demorado o frete
FATOR_REGIAO = {"15": (1.0, 0), "14": (1.15, 1), "17": (1.2, 1), "13": (1.3, 1), "01": (1.4, 2)}


def cotar_frete(cep, peso):
    cep = validar_cep(cep)
    peso = float(validar_peso(peso))
    fator, dias_extra = FATOR_REGIAO.get(cep[:2], (1.6, 3))
    cotacoes = [{"transportadora": n, "valor": round((fixo + kg * peso) * fator, 2), "prazo": p + dias_extra}
                for n, fixo, kg, p in TRANSPORTADORAS]
    return sorted(cotacoes, key=lambda c: c["valor"])


def cadastros():
    """Clientes e produtos cadastrados, para as listas da tela."""
    clientes = [{"codigo": c, **d} for c, d in CLIENTES.items()]
    produtos = [{"ean": e, "nome": n, "no_pedido": e in PEDIDO["itens"]} for e, n in PRODUTOS.items()]
    return {"clientes": clientes, "produtos": produtos}


def tratar(rota, dados):
    """Recebe a rota e os dados do formulário e devolve (status HTTP, resposta)."""
    global conferencia
    try:
        if rota == "/api/cadastros":
            return 200, cadastros()
        if rota == "/api/cliente":
            return 200, consultar_cliente(dados.get("codigo", ""))
        if rota == "/api/conferencia":
            return 200, situacao_conferencia()
        if rota == "/api/leitura":
            conferencia.registrar_leitura(dados.get("ean", "").strip())
            return 200, situacao_conferencia()
        if rota == "/api/finalizar":
            volumes = validar_volumes(dados.get("volumes", ""))
            peso = validar_peso(dados.get("peso", ""))
            status = conferencia.finalizar()
            return 200, {"mensagem": f"Pedido {PEDIDO['numero']} {status}: {volumes} volume(s), {str(peso).replace('.', ',')} kg."}
        if rota == "/api/reiniciar":
            conferencia = Conferencia(PEDIDO["itens"])
            return 200, situacao_conferencia()
        if rota == "/api/frete":
            return 200, {"cotacoes": cotar_frete(dados.get("cep", ""), dados.get("peso", ""))}
        return 404, {"erro": "Rota não encontrada."}
    except LookupError as e:
        return 404, {"erro": str(e)}
    except ValueError as e:
        return 400, {"erro": str(e)}


class Handler(BaseHTTPRequestHandler):
    def _responder(self, status, corpo, tipo="application/json; charset=utf-8"):
        dados = corpo if isinstance(corpo, bytes) else json.dumps(corpo, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            html = (Path(__file__).parent / "static" / "index.html").read_bytes()
            return self._responder(200, html, "text/html; charset=utf-8")
        self._responder(*tratar(self.path, {}))

    def do_POST(self):
        tamanho = int(self.headers.get("Content-Length") or 0)
        try:
            dados = json.loads(self.rfile.read(tamanho) or b"{}")
        except json.JSONDecodeError:
            dados = {}
        self._responder(*tratar(self.path, dados))

    def log_message(self, *args):
        pass  # não poluir o terminal


def criar_servidor(porta=8000):
    return ThreadingHTTPServer(("127.0.0.1", porta), Handler)


if __name__ == "__main__":
    print("Portal rodando em http://localhost:8000  (Ctrl+C para parar)", flush=True)
    try:
        criar_servidor().serve_forever()
    except KeyboardInterrupt:
        pass
