import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from build import join_vendas_lojas, parse_receita, pivot_receita  # noqa: E402


def test_pivot_forma_e_soma():
    _, rows = join_vendas_lojas()
    meses, table = pivot_receita(rows)
    assert (len(table), len(meses)) == (4, 6)
    assert meses[0] == "2026-01" and meses[-1] == "2026-06"
    total = sum(v for vals in table.values() for v in vals.values())
    esperado = sum(parse_receita(r) for r in rows)
    assert total == pytest.approx(esperado, abs=0.005)
