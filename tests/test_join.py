import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from build import join_vendas_lojas  # noqa: E402


def test_join_row_count_and_no_loja_999():
    cols, rows = join_vendas_lojas()
    assert len(rows) == 420
    assert all(r["id_loja"] != "999" for r in rows)
    assert cols[-4:] == ["nome_loja", "regiao", "uf", "gerente"]
