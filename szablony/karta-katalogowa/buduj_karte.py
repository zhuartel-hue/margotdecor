#!/usr/bin/env python3
"""Margot Decor – generator karty katalogowej (szablon v1, 2026-11-02).

Użycie:  python3 buduj_karte.py dane-lampy.json  [--final]
Wynik:   <plik>.html (podgląd / artefakt) i <plik>.pdf (A4, 2 strony, do druku i wysyłki)

Dane w JSON (wzór: sophia-gleam-50-40.json). Wartość null w danych technicznych
= brak danych. W wersji TEST pokazuje się jako "do uzupełnienia"; z --final
generator przerywa pracę, bo karta dla klienta nie może mieć braków.
"""
import base64, html, json, re, sys, pathlib, io

ROOT = pathlib.Path(__file__).resolve().parent
FS = ROOT / "fonts"  # zamrożone kopie @fontsource (cormorant-garamond 5.x, jost 5.x) – nie pobieramy z internetu


def b64(path):
    return base64.b64encode(pathlib.Path(path).read_bytes()).decode()


def fonts_css():
    out = []
    for fam, files in [("cormorant-garamond", ["400", "500", "400-italic"]), ("jost", ["300", "400", "500"])]:
        for f in files:
            css = (FS / fam / f"{f}.css").read_text()
            for block in re.findall(r"@font-face\s*{[^}]+}", css):
                if "cyrillic" in block or "vietnamese" in block:
                    continue
                m = re.search(r"url\(\./files/([^)]+?\.woff2)\)", block)
                data = b64(FS / fam / "files" / m.group(1))
                block = re.sub(r"src:[^;]+;", f"src:url(data:font/woff2;base64,{data}) format('woff2');", block)
                out.append(block)
    return "\n".join(out)


def img(path):
    return f"data:image/jpeg;base64,{b64(ROOT / path)}"


def qr_svg(url):
    import qrcode, qrcode.image.svg as s
    buf = io.BytesIO()
    qrcode.make(url, image_factory=s.SvgPathImage, box_size=10, border=0,
                error_correction=qrcode.constants.ERROR_CORRECT_M).save(buf)
    svg = buf.getvalue().decode()
    svg = re.sub(r"<\?xml[^>]*>", "", svg)
    svg = re.sub(r'width="[^"]*mm" height="[^"]*mm"', "", svg, count=1)
    return svg.replace("<path ", '<path fill="currentColor" ')


def logo_svg():
    svg = (ROOT / "logo.svg").read_text()
    return svg.replace("<svg ", '<svg class="logo" role="img" aria-label="Margot Decor" ', 1)


def e(s):
    return html.escape(s, quote=True)


def build(data, final=False):
    missing = []
    groups = []
    for gname, rows in data["dane"]:
        trs = []
        for label, val in rows:
            if val is None:
                missing.append(label)
                val_html = '<span class="brak">do uzupełnienia</span>'
            else:
                val_html = e(val)
            trs.append(f"<tr><th scope=\"row\">{e(label)}</th><td>{val_html}</td></tr>")
        groups.append(f'<div class="spec-group"><h3>{e(gname)}</h3><table>{"".join(trs)}</table></div>')
    if final and missing:
        sys.exit("BRAKI w danych (karta FINAL wstrzymana): " + ", ".join(missing))

    full = f'{data["nazwa"]} {data["wymiar"]}'
    keys = "".join(f'<div class="fact"><span class="fact-l">{e(l)}</span><span class="fact-v">{e(v)}</span></div>'
                   for l, v in data["kluczowe"])
    about = "".join(f"<p>{e(p)}</p>" for p in data["o_modelu"])
    details = "".join(f'<figure><img src="{img(p)}" alt="{e(full)} – {e(c)}"><figcaption>{e(c)}</figcaption></figure>'
                      for p, c in data["zdjecia"]["detale"])
    bulbs = "".join(f"<li><span>{e(n)}</span><span class=\"dots\"></span><span>{e(c)}</span></li>" for n, c in data["zarowki"])
    montaz = f"Do montażu potrzebne są {e(data['montaz_osoby'])}. " if data.get("montaz_osoby") else ""
    test_badge = '<span class="test">Wersja testowa</span>' if data.get("wersja") == "TEST" else ""

    head = f"""
    <header class="top">
      {logo_svg()}
      <div class="top-r"><span class="eyebrow">Karta katalogowa</span>{test_badge}<span class="top-model">{e(full)}</span></div>
    </header>"""
    foot = f"""
    <footer class="foot">
      <div><strong>Margot Decor</strong> · margotdecor.com · info@margotdecor.com · +48 792 333 322</div>
      <div>Ari Erdmann Worlds Sp. z o.o. · ul. Prochowa 5, 89-600 Chojnice · Stan danych: {e(data["data_karty"])}</div>
    </footer>"""

    return f"""<title>Karta katalogowa {e(full)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
{fonts_css()}
/* Układ: dwie kartki A4. Str. 1 = okładka (zdjęcie, nazwa, 4 kluczowe dane, cena, QR). Str. 2 = opis, detale, dane techniczne, informacje. */
:root {{
  --paper: #ffffff;
  --ink: #1f1c18;
  --stone: #6f685d;
  --gold: #9c7a33;
  --line: #e4ddd0;
  --veil: #f6f2ea;
  --amber: #b45309;
  --desk: #d9d3c7;
  --display: 'Cormorant Garamond', 'Cormorant', Georgia, serif;
  --body: 'Jost', 'Futura', 'Helvetica Neue', Arial, sans-serif;
}}
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ background: var(--desk); color: var(--ink); }}
body {{ margin: 0; font-family: var(--body); font-weight: 300; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.stack {{ display: grid; justify-items: center; gap: 24px; padding-block: 24px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }}
.fit {{ width: 100%; max-width: 210mm; aspect-ratio: 210 / 297; position: relative; overflow: hidden; box-shadow: 0 1px 2px rgba(40,30,10,.12), 0 8px 28px rgba(40,30,10,.12); background: var(--paper); }}
.page {{ width: 210mm; height: 297mm; padding: 13mm 14mm 11mm; background: var(--paper); position: absolute; top: 0; left: 0; transform-origin: 0 0; transform: scale(var(--s, 1)); display: flex; flex-direction: column; gap: 6mm; overflow: hidden; }}
@media print {{
  html, body {{ background: var(--paper); }}
  .stack {{ display: block; padding: 0; }}
  .fit {{ max-width: none; width: 210mm; height: 297mm; aspect-ratio: auto; box-shadow: none; break-after: page; }}
  .fit:last-child {{ break-after: auto; }}
  .page {{ transform: none; }}
}}
.top {{ display: flex; justify-content: space-between; align-items: center; padding-bottom: 4mm; border-bottom: 0.3mm solid var(--line); }}
.logo {{ width: 36mm; height: auto; fill: var(--ink); display: block; }}
.top-r {{ display: flex; align-items: baseline; gap: 4mm; }}
.eyebrow {{ font-size: 7.5pt; letter-spacing: .22em; text-transform: uppercase; color: var(--gold); font-weight: 500; }}
.top-model {{ font-family: var(--display); font-size: 12pt; font-style: italic; color: var(--stone); }}
.test {{ font-size: 7pt; letter-spacing: .12em; text-transform: uppercase; color: var(--amber); border: 0.3mm solid var(--amber); padding: .6mm 2mm; border-radius: 1mm; }}

/* Str. 1 */
.hero {{ margin: 0; height: 148mm; overflow: hidden; }}
.hero img {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 30%; display: block; }}
.title {{ display: grid; grid-template-columns: 1fr auto; gap: 8mm; align-items: end; }}
.kind {{ font-size: 8pt; letter-spacing: .2em; text-transform: uppercase; color: var(--stone); margin: 0 0 1mm; }}
h1 {{ font-family: var(--display); font-weight: 400; font-size: 44pt; line-height: .95; margin: 0; letter-spacing: -.01em; text-wrap: balance; }}
h1 .dim {{ color: var(--gold); font-style: italic; font-size: 30pt; margin-left: 2mm; }}
.intro {{ font-family: var(--display); font-style: italic; font-size: 14pt; color: var(--stone); margin: 2mm 0 0; max-width: 110mm; }}
.facts {{ display: grid; grid-template-columns: repeat(4, 1fr); border-top: 0.3mm solid var(--ink); border-bottom: 0.3mm solid var(--line); }}
.fact {{ display: flex; flex-direction: column; gap: 1mm; padding: 3.2mm 0 3.2mm 4mm; border-left: 0.3mm solid var(--line); }}
.fact:first-child {{ border-left: 0; padding-left: 0; }}
.fact-l {{ font-size: 7pt; letter-spacing: .16em; text-transform: uppercase; color: var(--stone); }}
.fact-v {{ font-family: var(--display); font-size: 19pt; font-weight: 500; font-variant-numeric: lining-nums; }}
.buy {{ margin-top: auto; display: grid; grid-template-columns: 1fr auto; gap: 8mm; align-items: center; background: var(--veil); padding: 5mm 6mm; }}
.price {{ font-family: var(--display); font-size: 30pt; font-weight: 500; line-height: 1; }}
.price small {{ font-family: var(--body); font-size: 8pt; font-weight: 400; letter-spacing: .14em; text-transform: uppercase; color: var(--stone); margin-left: 2mm; }}
.terms {{ margin: 2.5mm 0 0; font-size: 8.5pt; line-height: 1.55; color: var(--ink); }}
.terms b {{ font-weight: 500; }}
.qr {{ display: grid; grid-template-columns: 24mm auto; gap: 3mm; align-items: center; color: var(--ink); }}
.qr svg {{ width: 24mm; height: 24mm; display: block; }}
.qr p {{ margin: 0; font-size: 7.5pt; line-height: 1.5; color: var(--stone); max-width: 30mm; }}
.qr p b {{ display: block; color: var(--ink); font-weight: 500; font-size: 8pt; letter-spacing: .08em; text-transform: uppercase; }}

/* Str. 2 */
h2 {{ font-family: var(--display); font-weight: 400; font-size: 20pt; margin: 0 0 3mm; display: flex; align-items: baseline; gap: 3mm; }}
h2::after {{ content: ""; flex: 1; border-bottom: 0.3mm solid var(--line); transform: translateY(-1.5mm); }}
.about {{ display: grid; grid-template-columns: 1fr 86mm; gap: 8mm; }}
.about-text p {{ font-size: 9.5pt; line-height: 1.65; margin: 0 0 3mm; max-width: 95mm; }}
.details {{ display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }}
.details figure {{ margin: 0; }}
.details img {{ width: 100%; aspect-ratio: 1; object-fit: cover; display: block; }}
.details figcaption {{ font-size: 7pt; letter-spacing: .06em; color: var(--stone); margin-top: 1.5mm; }}
.specs {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0 8mm; }}
.spec-col {{ display: flex; flex-direction: column; gap: 4mm; }}
.spec-group h3 {{ font-size: 7.5pt; letter-spacing: .18em; text-transform: uppercase; color: var(--gold); font-weight: 500; margin: 0 0 1mm; }}
table {{ width: 100%; border-collapse: collapse; font-size: 8.8pt; }}
th, td {{ text-align: left; padding: 1.55mm 0; border-bottom: 0.25mm solid var(--line); vertical-align: top; }}
th {{ font-weight: 300; color: var(--stone); width: 55%; padding-right: 3mm; }}
td {{ font-weight: 400; font-variant-numeric: tabular-nums; }}
.brak {{ color: var(--amber); font-weight: 500; font-size: 7.5pt; letter-spacing: .06em; text-transform: uppercase; }}
.info {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8mm; background: var(--veil); padding: 5mm 6mm; margin-top: auto; }}
.info h3 {{ font-size: 7.5pt; letter-spacing: .18em; text-transform: uppercase; color: var(--gold); font-weight: 500; margin: 0 0 2mm; }}
.info p {{ margin: 0 0 1.5mm; font-size: 8.5pt; line-height: 1.55; }}
.info ul {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 1.5mm; font-size: 8.5pt; }}
.info li {{ display: flex; gap: 2mm; align-items: baseline; }}
.info li .dots {{ flex: 1; border-bottom: 0.3mm dotted var(--stone); transform: translateY(-1mm); }}
.foot {{ border-top: 0.3mm solid var(--line); padding-top: 3mm; display: grid; gap: .8mm; font-size: 7pt; color: var(--stone); letter-spacing: .02em; }}
.foot strong {{ color: var(--ink); font-weight: 500; }}
.note {{ font-size: 6.8pt; color: var(--stone); margin: 0; }}
</style>

<main class="stack">
  <div class="fit"><section class="page" aria-label="Strona 1">
    {head}
    <figure class="hero"><img src="{img(data["zdjecia"]["glowne"])}" alt="{e(data["zdjecia"]["glowne_podpis"])}"></figure>
    <div class="title">
      <div>
        <p class="kind">{e(data["typ"])} · kolekcja {e(data["kolekcja"])}</p>
        <h1>{e(data["nazwa"])}<span class="dim">{e(data["wymiar"])}</span></h1>
        <p class="intro">{e(data["intro"])}</p>
      </div>
    </div>
    <div class="facts">{keys}</div>
    <div class="buy">
      <div>
        <div class="price">{e(data["cena"])}<small>cena brutto</small></div>
        <p class="terms"><b>Wykonywana na zamówienie</b> · realizacja 1–3 miesiące · 100% przedpłaty<br>Żarówki nie są w zestawie.</p>
      </div>
      <div class="qr">{qr_svg(data["url"])}<p><b>Zobacz w sklepie</b>{e(data["url_krotki"])}</p></div>
    </div>
  </section></div>

  <div class="fit"><section class="page" aria-label="Strona 2">
    {head}
    <div class="about">
      <div class="about-text"><h2>O modelu</h2>{about}</div>
      <div class="details">{details}</div>
    </div>
    <div>
      <h2>Dane techniczne</h2>
      <div class="specs">
        <div class="spec-col">{groups[0]}{groups[1] if len(groups) > 1 else ""}</div>
        <div class="spec-col">{"".join(groups[2:])}</div>
      </div>
    </div>
    <div class="info">
      <div>
        <h3>Zamówienie i montaż</h3>
        <p>Każda lampa jest wykonywana na zamówienie. Realizacja trwa 1–3 miesiące, płatność 100% z góry.</p>
        <p>{montaz}Podłączenie powinien wykonać elektryk z uprawnieniami.</p>
      </div>
      <div>
        <h3>Pasujące żarówki (sprzedawane osobno)</h3>
        <ul>{bulbs}</ul>
        <p class="note" style="margin-top:2mm">Można też użyć dowolnych żarówek E14, LED lub tradycyjnych.</p>
      </div>
    </div>
    <p class="note">Zdjęcia aranżacji mają charakter poglądowy.</p>
    {foot}
  </section></div>
</main>

<script>
(function () {{
  function fit() {{
    document.querySelectorAll('.fit').forEach(function (w) {{
      var px = w.getBoundingClientRect().width;
      var mm = 210 * 96 / 25.4;
      w.querySelector('.page').style.setProperty('--s', (px / mm).toFixed(4));
    }});
  }}
  if (!window.matchMedia('print').matches) {{ fit(); window.addEventListener('resize', fit); }}
}})();
</script>
""", missing


def main():
    src = pathlib.Path(sys.argv[1])
    final = "--final" in sys.argv
    data = json.loads(src.read_text())
    page, missing = build(data, final)
    out_html = src.with_suffix(".html")
    out_html.write_text(page)
    import subprocess
    subprocess.run(["node", str(ROOT / "render.js"), str(out_html), str(src.with_suffix(".pdf")), str(src.with_suffix(".png"))], check=True)
    print("OK", out_html, "braki:", missing)


if __name__ == "__main__":
    main()
