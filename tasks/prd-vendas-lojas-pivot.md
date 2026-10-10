# PRD: Join vendas × lojas, pivot de receita e gráfico

## Introduction

Hoje `vendas.csv` (423 vendas, jan–jun/2026) e `lojas.csv` (8 lojas) estão separados. Precisamos cruzá-los por `id_loja`, resumir a receita por região × mês e exibir o resultado em uma página HTML com gráfico. Tudo gerado por um script Python e validado por pytest.

## Goals

- Gerar `vendas_lojas.csv` com o join por `id_loja`.
- Gerar `pivot_receita.csv` com receita somada por região (linhas) × mês (colunas).
- Gerar `index.html` com gráfico de barras empilhadas por mês, uma série por região.
- Suíte pytest inteira verde, com pelo menos 4 casos.

## User Stories

### US-001: Join vendas × lojas
**Description:** Como analista, quero cada venda enriquecida com os dados da loja para filtrar por região.

**Acceptance Criteria:**
- [ ] Script `build.py` lê `vendas.csv` e `lojas.csv` e grava `vendas_lojas.csv`
- [ ] Inner join por `id_loja`: 420 linhas (as 3 vendas da loja 999 ficam de fora)
- [ ] Colunas: as de vendas + `nome_loja`, `regiao`, `uf`, `gerente`
- [ ] `vendas.csv` e `lojas.csv` não são modificados
- [ ] Teste pytest: número de linhas do join (420) e ausência de `id_loja` 999
- [ ] Testes passam

### US-002: Receita total consistente
**Description:** Como analista, quero ter certeza de que nenhuma receita foi perdida ou duplicada no join.

**Acceptance Criteria:**
- [ ] `receita_brl` lida como número (float), nunca como texto
- [ ] Soma de `receita_brl` em `vendas_lojas.csv` = soma de `vendas.csv` − soma das vendas da loja 999 (939394,06 − 8120,00 = 931274,06)
- [ ] Teste pytest compara a receita total calculada a partir dos CSVs de origem, com tolerância de centavos
- [ ] Testes passam

### US-003: Pivot região × mês
**Description:** Como analista, quero a receita por região e mês para comparar o desempenho.

**Acceptance Criteria:**
- [ ] `pivot_receita.csv`: linhas = `regiao`, colunas = mês `YYYY-MM` (2026-01 a 2026-06), valores = soma de `receita_brl`
- [ ] 4 regiões × 6 meses; combinação sem vendas = 0
- [ ] Soma de todas as células = receita total do join
- [ ] Teste pytest: forma (4, 6) e soma das células
- [ ] Testes passam

### US-004: Página com gráfico
**Description:** Como usuário, quero abrir `index.html` e ver a receita por região e mês.

**Acceptance Criteria:**
- [ ] `index.html` autônomo (sem CDN): SVG ou canvas com JS inline, dados do pivot embutidos como JSON
- [ ] Barras empilhadas: eixo X = mês, uma série por região, legenda, eixos rotulados e título em português
- [ ] Teste pytest: o HTML contém o elemento do gráfico, uma série por região e os valores do pivot
- [ ] Testes passam
- [ ] Verificar no navegador com a skill dev-browser

## Functional Requirements

- FR-1: `build.py` é o único ponto de entrada e gera os 3 artefatos na raiz do projeto.
- FR-2: O join é inner por `id_loja`; lê os ids como texto para casar corretamente.
- FR-3: `receita_brl` é convertida para número; valor não numérico deve causar erro explícito, não ser descartado nem inventado.
- FR-4: O mês é derivado da coluna `data` (`YYYY-MM`).
- FR-5: Pivot com `sum`, preenchendo combinações ausentes com 0.
- FR-6: `pytest` na raiz executa toda a suíte (≥ 4 casos) sem falhas.

## Non-Goals

- Não alterar nem apagar linhas de `vendas.csv` e `lojas.csv`.
- Não inventar nem imputar dados (a loja 999 não ganha região fictícia).
- Sem servidor, framework web ou bibliotecas de gráfico externas.
- Sem filtros ou interatividade além de tooltip opcional.

## Technical Considerations

- Python com pandas e pytest; testes em `tests/`.
- A exclusão das 3 vendas órfãs é consequência do inner join e deve ser documentada em comentário no script e no README. Os valores esperados dos testes devem ser calculados a partir dos CSVs de origem, não fixos no código.

## Success Metrics

- `pytest` retorna 0 falhas.
- `vendas_lojas.csv` com 420 linhas; soma do pivot = R$ 931.274,06.
- `index.html` abre offline e mostra as 6 barras mensais empilhadas por 4 regiões.

## Open Questions

- As 3 vendas órfãs (R$ 8.120, loja 999, dias 15 de fev/mar/abr) devem ser reportadas à origem dos dados?
