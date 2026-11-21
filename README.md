# Ventura Biomédica – Portal Comercial e Expedição · Testes automatizados

**Integrantes:** Luis Felipe Rodrigues Galan · Leandro Inacio · Felipe dos Reis
**Disciplina:** Teste e Qualidade de Software – Atividade 1
**Repositório:** https://github.com/[usuario]/ventura-portal-expedicao  *(preencher)*

Testes unitários das regras do portal, escritos com **pytest**, seguindo os casos de teste do Plano de Testes. Aplicam **particionamento de equivalência** e **análise de valor limite**.

## Jeito mais fácil (Windows)

- **`iniciar_portal.bat`** – clique duas vezes: abre a tela em http://localhost:8000.
- **`rodar_testes.bat`** – clique duas vezes: roda todos os testes.

- **F5 no VS Code** – na aba "Executar e Depurar", escolha *Abrir portal* ou *Rodar testes* e aperte F5 (precisa do `.venv` já criado).

Na primeira vez, eles criam o ambiente `.venv` e instalam o pytest sozinhos (precisa de internet). Nas próximas, abrem direto.

## Como rodar os testes

```bash
pip install -r requirements.txt
pytest -v
```

Resultado esperado: `70 passed`.

## Como abrir a tela (front-end)

```bash
python -m portal.servidor
```

Abra **http://localhost:8000** no navegador. Para parar, aperte `Ctrl+C` no terminal.
A tela tem três quadros: consultar cliente (RF02), conferência do pedido com coletor (RF05/RF06) e cotação de frete (RF08). Os dados são fictícios e ficam no próprio `servidor.py`, no lugar do banco do Protheus.

## Estrutura

| Arquivo | Finalidade |
|---|---|
| `portal/validacoes.py` | Regras de validação: senha, código do cliente, EAN-13, volumes, peso, período e CEP |
| `portal/pedido.py` | Status do pedido (máquina de estados) e conferência com coletor |
| `portal/servidor.py` | Servidor web simples (só biblioteca padrão do Python) e dados fictícios |
| `portal/static/index.html` | Tela do portal (HTML, CSS e JavaScript) |
| `tests/test_exemplo_apresentacao.py` | Exemplo curto para apresentar: sucesso, entrada inválida e valor limite |
| `tests/test_servidor.py` | Testes da API e da página (CT006, CT007, CT009, CT013, CT014, CT017, CT021, CT022) |
| `tests/test_validacoes.py` | Testes das validações (CT003, CT007, CT008, CT015, CT017, CT018, CT020, CT022) |
| `tests/test_pedido.py` | Testes de status e conferência (CT013, CT014, CT016, CT023, CT024) |
| `.github/workflows/testes.yml` | Executa os testes a cada push no GitHub (regressão) |
| `evidencias/resultado_pytest.txt` | Saída da última execução |

## Casos de teste cobertos

| Caso | Requisito | Técnica | Valores testados |
|---|---|---|---|
| CT003 | RF01 Senha | Valor limite | 7, 8, 20, 21 caracteres e vazia |
| CT007/CT008 | RF02 Código do cliente | EP + valor limite | 5, 6, 7 dígitos; letras; vazio |
| CT013/CT014 | RF05 Conferência | EP | Pedido completo; produto fora do pedido |
| CT015 | RF05 EAN-13 | EP + valor limite | 12, 13, 14 dígitos; DV errado; letra |
| CT016 | RF05 Quantidade | Valor limite | 9, 10, 11 leituras (pedido de 10) |
| CT017 | RF06 Volumes | Valor limite | 0, 1, 99, 100; negativo; decimal; texto |
| CT018 | RF06 Peso | Valor limite | 0,00; 0,01; 999,99; 1000,00; 3 casas; texto |
| CT020 | RF07 Período | Valor limite | 0, 89, 90, 91 dias; inicial > final |
| CT022 | RF08 CEP | Valor limite | 7, 8, 9 dígitos; com hífen; letra |
| CT023/CT024 | RF09 Status | Transição de estados | Fluxo válido; 4 transições inválidas |

## Demonstração: o teste pega o erro

Troque, em `portal/validacoes.py`, o limite da senha de `20` para `21` e rode `pytest`. O teste `test_ct003_senha_fora_do_limite_e_recusada[21_chars]` falha, mostrando que a análise de valor limite detecta o defeito. Volte para `20` e tudo passa de novo.

> Observação: esta é uma versão em memória (sem banco do Protheus), para os testes unitários. Os testes de integração e de interface estão descritos no Plano de Testes.
