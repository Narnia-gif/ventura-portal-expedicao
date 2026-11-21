"""Status do pedido (RF09) e conferência com coletor (RF05).

Ventura Biomédica – Portal Comercial e Expedição.
Integrantes: Luis Felipe Rodrigues Galan, Leandro Inacio, Felipe dos Reis.

Versão em memória (sem banco), usada nos testes unitários.
"""
from portal.validacoes import validar_ean13

LIBERADO = "Liberado"
EM_CONFERENCIA = "Em conferência"
CONFERIDO = "Conferido"
ENVIADO = "Enviado"

# Única ordem permitida: Liberado → Em conferência → Conferido → Enviado
TRANSICOES = {
    LIBERADO: EM_CONFERENCIA,
    EM_CONFERENCIA: CONFERIDO,
    CONFERIDO: ENVIADO,
}


def mudar_status(origem: str, destino: str) -> str:
    if TRANSICOES.get(origem) != destino:
        raise ValueError("Transição de status não permitida.")
    return destino


class Conferencia:
    """Conferência de um pedido: itens = {ean: quantidade pedida}."""

    def __init__(self, itens: dict):
        self.pedido = dict(itens)
        self.conferido = {ean: 0 for ean in itens}

    def registrar_leitura(self, ean: str) -> int:
        validar_ean13(ean)
        if ean not in self.pedido:
            raise ValueError("Produto não pertence a este pedido.")
        if self.conferido[ean] >= self.pedido[ean]:
            raise ValueError(f"Quantidade excede o pedido ({self.pedido[ean]}).")
        self.conferido[ean] += 1
        return self.conferido[ean]

    def faltam(self) -> int:
        return sum(self.pedido[e] - self.conferido[e] for e in self.pedido)

    def finalizar(self) -> str:
        if self.faltam() > 0:
            raise ValueError(f"Conferência incompleta: faltam {self.faltam()} unidade(s).")
        return CONFERIDO
