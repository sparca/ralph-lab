# Dados do exercício ia-3.1

Dois CSVs **sintéticos** e **determinísticos**, gerados por
[`../scripts/gen_dados_ia31.py`](../scripts/gen_dados_ia31.py).

```bash
python scripts/gen_dados_ia31.py
```

O script usa `random.seed(7)` e uma ordem fixa de sorteios: rodar de novo, em
qualquer máquina, reescreve os mesmos arquivos **byte a byte**. Não edite os CSVs
na mão — se precisar recriá-los, rode o script.

Nada aqui vem de dados reais: lojas, gerentes e valores são inventados.

---

## `lojas.csv` — dimensão (8 linhas)

Uma linha por loja. Chave: `id_loja`.

| Coluna | Tipo | Descrição | Exemplo |
|---|---|---|---|
| `id_loja` | inteiro | Identificador da loja (101–108). Chave primária. | `103` |
| `nome_loja` | texto | Nome do ponto de venda. | `Moema` |
| `regiao` | texto | Região do IBGE: `Centro-Oeste`, `Nordeste`, `Sudeste`, `Sul`. | `Sudeste` |
| `uf` | texto | Sigla da unidade federativa (2 letras). | `SP` |
| `gerente` | texto | Nome do gerente responsável. | `Carla Nunes` |

## `vendas.csv` — fato (423 linhas)

Uma linha por venda agregada de loja × categoria. Chave: `id_venda`.

| Coluna | Tipo | Descrição | Domínio observado |
|---|---|---|---|
| `id_venda` | texto | Identificador sequencial `V00001`…`V00423`. Chave primária. | `V00001`–`V00423` |
| `data` | texto (`YYYY-MM-DD`) | Data da venda. Extraia `YYYY-MM` para agrupar por mês. | `2026-01-02` a `2026-06-28` |
| `id_loja` | inteiro | Chave estrangeira para `lojas.csv`. | 101–107 e **999** |
| `categoria` | texto | `Bebidas`, `Higiene`, `Limpeza`, `Mercearia`, `Padaria`. | 5 valores |
| `unidades` | inteiro | Quantidade vendida. | 20–180 |
| `receita_brl` | decimal | Receita em reais, ponto como separador decimal, 2 casas. | 299.61 – 7531.92 |

> Formatação: `receita_brl` sai com no máximo 2 casas, mas sem zeros à direita —
> você vai ver `349.5` e `1200` além de `4406.88`. Leia como número, não como texto.

---

## Armadilhas pedagógicas (propositais)

Os dois "defeitos" abaixo **não são bugs**. Eles existem para você ter que decidir
— e **documentar** — qual tipo de join usar.

1. **A loja 108 (Batel/PR) não tem nenhuma venda.** Ela existe em `lojas.csv` e
   nunca aparece em `vendas.csv`.
   - Com `inner join`, a loja 108 **some** do relatório.
   - Com `left join` a partir de `lojas.csv`, ela aparece com receita nula/zero —
   o que é a informação mais útil para um gestor ("essa loja vendeu zero"),
   desde que você trate o nulo antes de somar.

2. **Três vendas órfãs com `id_loja = 999`.** Esse id não existe em `lojas.csv`
   (são as linhas `V00421`, `V00422` e `V00423`, somando R$ 8.120,00).
   - Com `inner join`, essas 3 vendas são **descartadas em silêncio**: a receita
   total cai de 939.394,06 para 931.274,06.
   - Com `left join` a partir de `vendas.csv`, elas ficam, mas sem região/UF —
   e vão parar num grupo nulo no pivot.

### O que se espera de você

- Escolher **um** tipo de join, aplicar de forma consistente e **escrever no
  README da sua entrega** qual escolheu e por quê.
- Reportar quantas linhas entraram, quantas saíram e quanta receita foi perdida
  ou preservada na decisão.
- Não "consertar" os dados apagando as linhas problemáticas sem registrar isso.

### Números de referência (para conferir seu pipeline)

| Métrica | Valor |
|---|---|
| Linhas em `vendas.csv` | 423 |
| Linhas em `lojas.csv` | 8 |
| Linhas após `inner join` por `id_loja` | 420 |
| Soma de `receita_brl` no inner join | 931274.06 |
| Soma de `receita_brl` em `vendas.csv` (tudo) | 939394.06 |
| Shape do pivot `regiao` × `mês` (inner join) | 4 × 6 |
| Região de maior receita | Sudeste — 265077.49 |
