"""Regras de validação do Portal Comercial e Expedição (Ventura Biomédica).

Integrantes: Luis Felipe Rodrigues Galan, Leandro Inacio, Felipe dos Reis.

Cada função recebe o valor digitado e devolve o valor já tratado.
Se o valor for inválido, lança ValueError com a mensagem mostrada ao usuário.
"""
import re
from datetime import date
from decimal import Decimal, InvalidOperation


# RF01 – senha de 8 a 20 caracteres
def validar_senha(senha: str) -> str:
    if not senha:
        raise ValueError("Senha obrigatória.")
    if not 8 <= len(senha) <= 20:
        raise ValueError("A senha deve ter de 8 a 20 caracteres.")
    return senha


# RF02 – código do cliente do Protheus (6 dígitos numéricos)
def validar_codigo_cliente(codigo: str) -> str:
    codigo = (codigo or "").strip()
    if not codigo:
        raise ValueError("Informe o código do cliente.")
    if not codigo.isdigit():
        raise ValueError("O código deve conter apenas números.")
    if len(codigo) != 6:
        raise ValueError("O código deve ter 6 dígitos.")
    return codigo


# RF05 – código de barras EAN-13 com dígito verificador
def digito_verificador_ean13(doze_digitos: str) -> int:
    soma = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(doze_digitos))
    return (10 - soma % 10) % 10


def validar_ean13(codigo: str) -> str:
    if not re.fullmatch(r"\d{13}", codigo or ""):
        raise ValueError("Código de barras inválido. Leia novamente.")
    if digito_verificador_ean13(codigo[:12]) != int(codigo[12]):
        raise ValueError("Código de barras inválido. Leia novamente.")
    return codigo


# RF06 – volumes: inteiro de 1 a 99
def validar_volumes(valor) -> int:
    texto = str(valor).strip()
    if not re.fullmatch(r"-?\d+", texto):
        raise ValueError("O número de volumes deve ser inteiro.")
    volumes = int(texto)
    if not 1 <= volumes <= 99:
        raise ValueError("Informe de 1 a 99 volumes.")
    return volumes


# RF06 / RF08 – peso bruto de 0,01 a 999,99 kg, até 2 casas decimais
def validar_peso(valor) -> Decimal:
    texto = str(valor).strip().replace(",", ".")
    if not re.fullmatch(r"-?\d+(\.\d{1,2})?", texto):
        raise ValueError("Informe o peso com até 2 casas decimais.")
    try:
        peso = Decimal(texto)
    except InvalidOperation:
        raise ValueError("Informe o peso com até 2 casas decimais.")
    if not Decimal("0.01") <= peso <= Decimal("999.99"):
        raise ValueError("Peso deve estar entre 0,01 e 999,99 kg.")
    return peso


# RF07 – período do painel: inicial <= final e no máximo 90 dias
def validar_periodo(inicio: date, fim: date) -> int:
    if inicio > fim:
        raise ValueError("A data inicial deve ser anterior ou igual à final.")
    dias = (fim - inicio).days
    if dias > 90:
        raise ValueError("O período máximo é de 90 dias.")
    return dias


# RF08 – CEP com 8 dígitos (hífen opcional)
def validar_cep(cep: str) -> str:
    if not re.fullmatch(r"\d{5}-?\d{3}", (cep or "").strip()):
        raise ValueError("CEP inválido. Informe 8 dígitos.")
    return cep.replace("-", "").strip()
