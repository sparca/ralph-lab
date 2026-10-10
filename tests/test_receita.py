import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from build import join_vendas_lojas, parse_receita, read_csv  # noqa: E402


def test_receita_total_preservada():
    _, vendas = read_csv(ROOT / "vendas.csv")
    _, lojas = read_csv(ROOT / "lojas.csv")
    ids = {l["id_loja"] for l in lojas}
    esperado = sum(parse_receita(v) for v in vendas if v["id_loja"] in ids)
    _, rows = join_vendas_lojas()
    assert sum(parse_receita(r) for r in rows) == pytest.approx(esperado, abs=0.005)


def test_receita_nao_numerica_gera_erro(tmp_path):
    for name in ("vendas.csv", "lojas.csv"):
        shutil.copy(ROOT / name, tmp_path / name)
    text = (tmp_path / "vendas.csv").read_text(encoding="utf-8").splitlines()
    header = text[0].split(",")
    i = header.index("receita_brl")
    cells = text[1].split(",")
    cells[i] = "abc"
    text[1] = ",".join(cells)
    (tmp_path / "vendas.csv").write_text("\n".join(text), encoding="utf-8")
    with pytest.raises(ValueError, match="receita_brl"):
        join_vendas_lojas(tmp_path)
