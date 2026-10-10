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


def join_vendas_lojas(root: Path = ROOT) -> tuple[list[str], list[dict[str, str]]]:
    vendas_cols, vendas = read_csv(root / "vendas.csv")
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


def main() -> None:
    cols, rows = join_vendas_lojas()
    with (ROOT / "vendas_lojas.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
