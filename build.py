"""Gera vendas_lojas.csv a partir de vendas.csv e lojas.csv."""
import csv
import json
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


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Receita por região e mês</title>
<style>
body { font-family: sans-serif; margin: 2rem; }
.legenda span { display: inline-block; margin-right: 1rem; }
.legenda i { display: inline-block; width: 12px; height: 12px; margin-right: 4px; }
</style>
</head>
<body>
<h1>Receita por região e mês (R$)</h1>
<svg id="grafico" width="760" height="420" role="img" aria-label="Receita por região e mês"></svg>
<div id="legenda" class="legenda"></div>
<script id="dados" type="application/json">__DATA__</script>
<script>
const d = JSON.parse(document.getElementById("dados").textContent);
const cores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"];
const svg = document.getElementById("grafico"), NS = "http://www.w3.org/2000/svg";
const L = 80, B = 50, T = 20, W = 760 - L - 20, H = 420 - B - T;
const totais = d.meses.map(m => d.series.reduce((s, r) => s + r.valores[m], 0));
const max = Math.max(...totais), passo = Math.pow(10, Math.floor(Math.log10(max)));
const topo = Math.ceil(max / passo) * passo;
function el(n, a, t) { const e = document.createElementNS(NS, n);
  for (const k in a) e.setAttribute(k, a[k]); if (t !== undefined) e.textContent = t;
  svg.appendChild(e); return e; }
for (let i = 0; i <= 5; i++) { const v = topo * i / 5, y = T + H - H * i / 5;
  el("line", {x1: L, x2: L + W, y1: y, y2: y, stroke: "#ddd"});
  el("text", {x: L - 6, y: y + 4, "text-anchor": "end", "font-size": 11}, Math.round(v).toLocaleString("pt-BR")); }
const bw = W / d.meses.length;
d.meses.forEach((m, i) => { let acc = 0;
  d.series.forEach((s, j) => { const h = H * s.valores[m] / topo;
    const r = el("rect", {x: L + i * bw + bw * 0.15, y: T + H - (acc + h), width: bw * 0.7, height: h, fill: cores[j % cores.length]});
    r.appendChild(Object.assign(document.createElementNS(NS, "title"), {textContent: s.regiao + " " + m + ": R$ " + s.valores[m].toFixed(2)}));
    acc += h; });
  el("text", {x: L + i * bw + bw / 2, y: T + H + 18, "text-anchor": "middle", "font-size": 12}, m); });
el("text", {x: L + W / 2, y: 415, "text-anchor": "middle", "font-size": 13}, "Mês");
el("text", {x: 15, y: T + H / 2, "text-anchor": "middle", "font-size": 13, transform: "rotate(-90 15 " + (T + H / 2) + ")"}, "Receita (R$)");
document.getElementById("legenda").innerHTML = d.series.map((s, j) =>
  '<span><i style="background:' + cores[j % cores.length] + '"></i>' + s.regiao + "</span>").join("");
</script>
</body>
</html>
"""


def render_html(meses: list[str], table: dict[str, dict[str, float]]) -> str:
    # Página autônoma (sem CDN): dados do pivot embutidos como JSON.
    data = {
        "meses": meses,
        "series": [
            {"regiao": reg, "valores": {m: round(vals[m], 2) for m in meses}}
            for reg, vals in table.items()
        ],
    }
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return HTML_TEMPLATE.replace("__DATA__", payload)


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
    (ROOT / "index.html").write_text(render_html(meses, table), encoding="utf-8")


if __name__ == "__main__":
    main()
