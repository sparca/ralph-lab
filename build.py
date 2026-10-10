"""Gera vendas_lojas.csv a partir de vendas.csv e lojas.csv."""
import csv
from pathlib import Path

ROOT = Path(__file__).parent
LOJA_COLS = ["nome_loja", "regiao", "uf", "gerente"]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    # csv.DictReader mantém todos os valores como texto (id_loja incluso)
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def parse_receita(row: dict[str, str]) -> float:
    # Erro explícito: nunca descartar nem inventar valores não numéricos.
    raw = row.get("receita_brl")
    try:
        return float(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise ValueError(f"receita_brl não numérica: {raw!r} (linha: {row})") from None


def join_vendas_lojas(root: Path = ROOT) -> tuple[list[str], list[dict[str, str]]]:
    vendas_cols, vendas = read_csv(root / "vendas.csv")
    for v in vendas:
        parse_receita(v)
    _, lojas = read_csv(root / "lojas.csv")
    lojas_by_id = {l["id_loja"]: l for l in lojas}
    # Inner join por id_loja: vendas cujo id_loja não existe em lojas.csv
    # (ex.: as 3 vendas da loja 999) ficam de fora do resultado.
    rows = [
        {**v, **{c: lojas_by_id[v["id_loja"]][c] for c in LOJA_COLS}}
        for v in vendas
        if v["id_loja"] in lojas_by_id
    ]
    return vendas_cols + LOJA_COLS, rows


def pivot_receita(
    rows: list[dict[str, str]],
) -> tuple[list[str], dict[str, dict[str, float]]]:
    # Mês = primeiros 7 caracteres de data (YYYY-MM); células sem vendas = 0.
    meses = sorted({r["data"][:7] for r in rows})
    regioes = sorted({r["regiao"] for r in rows})
    table = {reg: {m: 0.0 for m in meses} for reg in regioes}
    for r in rows:
        table[r["regiao"]][r["data"][:7]] += parse_receita(r)
    return meses, table


def main() -> None:
    cols, rows = join_vendas_lojas()
    with (ROOT / "vendas_lojas.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    meses, table = pivot_receita(rows)
    with (ROOT / "pivot_receita.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["regiao", *meses])
        for reg, vals in table.items():
            w.writerow([reg, *(f"{vals[m]:.2f}" for m in meses)])


if __name__ == "__main__":
    main()
