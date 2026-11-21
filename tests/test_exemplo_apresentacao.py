"""EXEMPLO PARA A APRESENTAÇÃO – poucos testes, bem explicados.

Ventura Biomédica – Portal Comercial e Expedição
Integrantes: Luis Felipe Rodrigues Galan, Leandro Inacio, Felipe dos Reis

Rodar só este arquivo:   pytest -v tests/test_exemplo_apresentacao.py
"""
import pytest

from portal.validacoes import validar_codigo_cliente, validar_volumes


# 1) CENÁRIO DE SUCESSO – CT006 / RF02
#    Um código de cliente válido (6 dígitos) é aceito.
def test_1_sucesso_codigo_de_cliente_valido():
    assert validar_codigo_cliente("000123") == "000123"


# 2) ENTRADA INVÁLIDA – CT007 / RF02 (particionamento de equivalência)
#    Um código com letras pertence à classe inválida e é recusado com mensagem.
def test_2_entrada_invalida_codigo_com_letras():
    with pytest.raises(ValueError, match="apenas números"):
        validar_codigo_cliente("12A45B")


# 3) VALOR LIMITE – CT017 / RF06 (análise de valor limite)
#    A regra é "de 1 a 99 volumes". Testamos os limites e um valor de cada lado.
@pytest.mark.parametrize("volumes, aceito", [
    (0, False),    # logo abaixo do limite inferior
    (1, True),     # limite inferior
    (99, True),    # limite superior
    (100, False),  # logo acima do limite superior
])
def test_3_valor_limite_volumes(volumes, aceito):
    if aceito:
        assert validar_volumes(volumes) == volumes
    else:
        with pytest.raises(ValueError, match="de 1 a 99 volumes"):
            validar_volumes(volumes)
