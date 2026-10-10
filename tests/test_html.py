import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from build import join_vendas_lojas, pivot_receita, render_html  # noqa: E402


def _html_e_pivot():
    _, rows = join_vendas_lojas()
    meses, table = pivot_receita(rows)
    return render_html(meses, table), meses, table


def test_html_autonomo_com_elemento_do_grafico():
    html, _, _ = _html_e_pivot()
    assert '<svg id="grafico"' in html
    assert "http://" not in html.replace("http://www.w3.org/2000/svg", "")
    assert "https://" not in html and "<script src" not in html


def test_html_uma_serie_por_regiao_e_valores_do_pivot():
    html, meses, table = _html_e_pivot()
    m = re.search(r'<script id="dados" type="application/json">(.*?)</script>', html, re.S)
    dados = json.loads(m.group(1))
    assert dados["meses"] == meses
    assert [s["regiao"] for s in dados["series"]] == list(table)
    assert len(dados["series"]) == 4
    for s in dados["series"]:
        for mes in meses:
            assert s["valores"][mes] == pytest.approx(table[s["regiao"]][mes], abs=0.005)


def test_html_rotulos_em_portugues():
    html, _, _ = _html_e_pivot()
    assert "Receita por região e mês" in html
    assert '"Mês"' in html and '"Receita (R$)"' in html
