#!/usr/bin/env python3
"""Margot Decor – etykieta na karton (DYMO LabelWriter XL, etykieta 102 × 210 mm, nr 2166659).

Użycie:  python3 buduj_etykiete.py dane-lampy.json [katalog_wyjściowy]
Wynik:   <plik>.html, <plik>.pdf (1:1, 102×210 mm), <plik>-300dpi.png (1205×2480 px, 1-bit)
         i <plik>-300dpi-poziomo.png (to samo obrócone, 2480×1205, pod widok poziomy w DYMO Connect)

Druk termiczny: tylko czysta czerń, bez szarości i bez cienkich linii < 0,25 mm.
Fonty i logo z ../karta-katalogowa (szablon zamrożony, tu tylko import).
"""
import html, json, sys, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent
KK = ROOT.parent / "karta-katalogowa"
sys.path.insert(0, str(KK))
from buduj_karte import fonts_css, qr_svg  # noqa: E402

e = html.escape

IKONY = {
    "szklo": '<svg viewBox="0 0 40 40"><path d="M12 4h16l-1.5 13a6.5 6.5 0 0 1-13 0z" fill="none" stroke="#000" stroke-width="2.6"/><path d="M20 23.5V35M13 36h14" stroke="#000" stroke-width="2.6" fill="none"/><path d="M19 8l-2 4 3 1-2 4" stroke="#000" stroke-width="1.8" fill="none"/></svg>',
    "gora": '<svg viewBox="0 0 40 40"><path d="M13 30V9M27 30V9M7 15l6-7 6 7M21 15l6-7 6 7" fill="none" stroke="#000" stroke-width="2.6" stroke-linejoin="round"/><path d="M6 36h28" stroke="#000" stroke-width="2.6"/></svg>',
    "wilgoc": '<svg viewBox="0 0 40 40"><path d="M5 19a15 13 0 0 1 30 0z" fill="none" stroke="#000" stroke-width="2.6" stroke-linejoin="round"/><path d="M20 19v12a3 3 0 0 1-6 0" fill="none" stroke="#000" stroke-width="2.6"/><path d="M20 4v2M9 8l1 1.5M31 8l-1 1.5" stroke="#000" stroke-width="2.2"/></svg>',
}


def zbuduj(d):
    logo = (KK / "logo.svg").read_text()
    logo = logo[logo.index("<svg"):]
    wiersze = "".join(f'<div class="r"><span>{e(k)}</span><i></i><b>{e(v)}</b></div>' for k, v in d["dane"])
    return f"""<style>
{fonts_css()}
@page {{ size: 102mm 210mm; margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: #fff; }}
.et {{ width: 102mm; height: 210mm; padding: 6mm 6.5mm 5mm; color: #000; font-family: 'Jost', sans-serif;
      display: flex; flex-direction: column; overflow: hidden; }}
.ramka {{ border: 1.5mm double #000; flex: 1; padding: 5mm 5mm 3.5mm; display: flex; flex-direction: column; }}
.logo {{ text-align: center; }}
.logo svg {{ width: 46mm; height: auto; display: inline-block; }}
.logo svg path {{ fill: #000; }}
.sep {{ display: flex; align-items: center; gap: 2.5mm; margin: 3.5mm 0 3mm; }}
.sep::before, .sep::after {{ content: ""; flex: 1; border-top: .3mm solid #000; }}
.sep span {{ width: 1.8mm; height: 1.8mm; background: #000; transform: rotate(45deg); }}
.rodzaj {{ text-align: center; font-size: 8.5pt; letter-spacing: .32em; text-transform: uppercase; font-weight: 500; }}
.nazwa {{ text-align: center; font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: 33pt; line-height: .98; margin: 2mm 0 .5mm; }}
.rozmiar {{ text-align: center; font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 19pt; line-height: 1; }}
.kod {{ text-align: center; font-size: 8pt; letter-spacing: .2em; margin-top: 2mm; }}
.dane {{ margin-top: 1mm; font-size: 8.2pt; line-height: 1.2; }}
.r {{ display: flex; align-items: baseline; gap: 1.5mm; padding: .6mm 0; }}
.r span {{ white-space: nowrap; }}
.r i {{ flex: 1; border-bottom: .35mm dotted #000; transform: translateY(-.7mm); min-width: 3mm; }}
.r b {{ font-weight: 500; white-space: nowrap; }}
.zam {{ margin-top: 3mm; border: .4mm solid #000; text-align: center; padding: 1.7mm 0 1.5mm; font-size: 8.5pt; letter-spacing: .26em; text-transform: uppercase; font-weight: 500; }}
.dol {{ display: grid; grid-template-columns: 25mm 1fr; gap: 4mm; margin-top: 3.5mm; align-items: stretch; }}
.qr {{ text-align: center; }}
.qr svg {{ width: 25mm; height: 25mm; display: block; color: #000; }}
.qr p {{ margin: 1.4mm 0 0; font-size: 6.6pt; line-height: 1.25; letter-spacing: .04em; }}
.ean {{ border: .35mm dashed #000; display: flex; flex-direction: column; justify-content: space-between; padding: 1.5mm 2mm; font-size: 6.6pt; letter-spacing: .2em; }}
.ean em {{ font-style: normal; text-align: right; }}
.ikony {{ display: flex; justify-content: space-between; margin-top: 3mm; }}
.ik {{ width: 20mm; text-align: center; font-size: 6.2pt; line-height: 1.2; text-transform: uppercase; letter-spacing: .06em; }}
.ik svg {{ width: 9mm; height: 9mm; display: block; margin: 0 auto 1mm; }}
.pola {{ margin-top: auto; padding-top: 2.5mm; display: grid; grid-template-columns: 1fr auto; gap: 3mm; font-size: 7.4pt; }}
.pola div {{ display: flex; align-items: baseline; gap: 1.2mm; white-space: nowrap; }}
.pola u {{ flex: 1; border-bottom: .3mm solid #000; text-decoration: none; min-width: 9mm; }}
.stopka {{ text-align: center; font-size: 6.2pt; line-height: 1.35; margin-top: 2.5mm; letter-spacing: .02em; }}
.stopka b {{ font-weight: 500; letter-spacing: .14em; }}
</style>
<div class="et"><div class="ramka">
  <div class="logo">{logo}</div>
  <div class="sep"><span></span></div>
  <div class="rodzaj">{e(d["rodzaj"])}</div>
  <div class="nazwa">{e(d["nazwa"])}</div>
  <div class="rozmiar">{e(d["rozmiar"])}</div>
  <div class="kod">KOD {e(d["kod"])}</div>
  <div class="sep"><span></span></div>
  <div class="dane">{wiersze}</div>
  <div class="zam">Wykonano na zamówienie</div>
  <div class="dol">
    <div class="qr">{qr_svg(d["url"])}<p>Zeskanuj:<br>karta produktu</p></div>
    <div class="ean"><span>EAN</span><em>miejsce na kod kreskowy</em></div>
  </div>
  <div class="ikony">
    <div class="ik">{IKONY["szklo"]}Kryształ<br>ostrożnie</div>
    <div class="ik">{IKONY["gora"]}Tą stroną<br>do góry</div>
    <div class="ik">{IKONY["wilgoc"]}Chronić przed<br>wilgocią</div>
  </div>
  <div class="pola">
    <div>Nr zamówienia <u></u></div>
    <div>Karton <u style="min-width:5mm"></u> z <u style="min-width:5mm"></u></div>
  </div>
  <div class="stopka"><b>MARGOT DECOR</b> · margotdecor.com<br>Ari Erdmann Worlds Sp. z o.o. · ul. Prochowa 5, 89-600 Chojnice</div>
</div></div>"""


def main():
    dane = pathlib.Path(sys.argv[1])
    d = json.loads(dane.read_text())
    out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else dane.parent
    out.mkdir(parents=True, exist_ok=True)
    h = out / f'{d["plik"]}.html'
    h.write_text(zbuduj(d))
    pdf, png = out / f'{d["plik"]}.pdf', out / f'{d["plik"]}-300dpi.png'
    subprocess.run(["node", str(ROOT / "render.js"), str(h), str(pdf)], check=True)
    # PNG dokładnie 102×210 mm przy 300 dpi = 1205×2480 px, czysta czerń/biel (druk termiczny)
    tmp = out / "_tmp"
    subprocess.run(["pdftoppm", "-gray", "-png", "-singlefile", "-scale-to-x", "1205", "-scale-to-y", "2480", str(pdf), str(tmp)], check=True)
    from PIL import Image
    im = Image.open(f"{tmp}.png").point(lambda v: 255 if v > 150 else 0).convert("1")
    im.save(png, dpi=(300, 300))
    # wersja obrócona: DYMO Connect domyślnie pokazuje tę etykietę poziomo (210 × 102 mm)
    im.rotate(90, expand=True).save(out / f'{d["plik"]}-300dpi-poziomo.png', dpi=(300, 300))
    pathlib.Path(f"{tmp}.png").unlink()


if __name__ == "__main__":
    main()
