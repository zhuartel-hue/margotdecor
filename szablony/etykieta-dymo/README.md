# Etykieta na karton – DYMO LabelWriter XL

Etykieta: DYMO 2166659 „Białe etykiety wysyłkowe DHL”, 102 × 210 mm, druk termiczny czarno-biały.
Szablon v1 (2026-11-04), wzór: Olivia Cascade 95-45. Tylko język polski.

## Zawartość etykiety
Logo Margot Decor · rodzaj lampy · pełna nazwa modelu + rozmiar · kod produktu · dane techniczne ·
„Wykonano na zamówienie” · QR do strony produktu · puste pole na EAN · symbole: kryształ ostrożnie,
tą stroną do góry, chronić przed wilgocią · pola do wpisania: nr zamówienia, karton _ z _ · dane firmy.

## Nowa lampa
1. Skopiuj `dane-olivia-cascade-95-45.json`, zmień dane (adres URL = strona produktu).
2. `python3 buduj_etykiete.py dane-<lampa>.json <katalog>` (wymaga: pip qrcode pillow, playwright, pdftoppm).
3. Wynik: PDF 1:1, PNG 300 dpi pionowo i poziomo (1-bit, czysta czerń).

## Druk w DYMO Connect
Nowy → etykieta 2166659 → Dodaj → Obraz → wybierz PNG `-poziomo` (etykieta jest w programie pozioma)
→ rozciągnij obraz na całą etykietę → Zapisz (.dymo = gotowy szablon tej lampy) → Drukuj.

Kod produktu (np. MD-OC-9545) to propozycja – w sklepie produkty nie mają jeszcze SKU.
