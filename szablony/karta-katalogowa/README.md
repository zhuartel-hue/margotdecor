# Szablon karty katalogowej Margot Decor (v1, 02.11.2026)

Wzór: Sophia Gleam 50-40 (wersja testowa w `sophia-gleam-50-40-test/`).
Format: PDF A4, 2 strony, do druku i wysyłki klientom. Tylko język polski.

## Strona 1 – okładka
1. Nagłówek: logo Margot Decor, „Karta katalogowa”, nazwa modelu.
2. Zdjęcie główne: aranżacja z karty produktu (zdjęcie nr 1 z galerii), cała lampa z rozetą.
3. Typ lampy + kolekcja, nazwa (imię + słowo) i wymiar złotą kursywą, zdanie intro (z `md_catalog.intro_pl`).
4. Pasek 4 kluczowych danych: średnica/szerokość, wysokość, gwint żarówki (albo „LED”), jedna cecha modelu (np. liczba kryształów).
5. Cena brutto + „Wykonywana na zamówienie · realizacja 1–3 miesiące · 100% przedpłaty” + „Żarówki nie są w zestawie” (dla lamp z LED pomijamy) + kod QR do produktu w sklepie.

## Strona 2 – szczegóły
1. „O modelu”: tekst z `md_catalog.about_pl` (bez powtarzania liczb z danych technicznych).
2. Dwa zdjęcia detali: te same co `md_catalog.detail_media` na karcie produktu (prawdziwe zdjęcia z galerii), z podpisami.
3. „Dane techniczne” w 3 grupach, kolejność wierszy jak na karcie produktu:
   - Wymiary i masa: Średnica/Szerokość, Wysokość bez łańcucha, Maksymalny zwis, Masa stelaża, (Masa akcesoriów montażowych)
   - Światło i zasilanie: Liczba żarówek (ZAWSZE), Źródło światła, Gwint żarówki, Napięcie zasilania, Wbudowany zasilacz (jeśli LED), Montaż
   - Cechy modelu: kryształy, koraliki, elementy, masy
4. Ramka: Zamówienie i montaż + Pasujące żarówki z cenami (z `custom.matching_bulb`).
5. Stopka: dane firmy, kontakt, „Stan danych: <data>”.

## Zasady
- Dane tylko ze sklepu (metafield `md_catalog`, cena z wariantu). Nic nie zgadujemy.
- Brak danej = w wersji TEST napis „DO UZUPEŁNIENIA”; wersja FINAL (`--final`) nie zbuduje się, dopóki są braki.
- Zdjęcia: kwadratowe 2048×2048 z karty produktu, wyretuszowane, bez duplikatów.
- Nazwa pliku: `<model>-karta-katalogowa.pdf`, folder lampy w Bibliotece.
- Po zatwierdzeniu karty PDF można podpiąć w sklepie (`md_catalog.catalogue_url` + `catalogue_approved`) – tylko za zgodą Arkadiusza.

## Jak zbudować kartę nowej lampy
1. Skopiuj `zrodla/wzor-dane-sophia-gleam-50-40.json`, uzupełnij dane i ścieżki zdjęć.
2. Czcionki i logo są w folderze (nic nie pobieramy z internetu). Potrzebny Python 3 z `qrcode` oraz Node z `playwright`. Polecenie: `python3 buduj_karte.py <lampa>.json` (TEST) albo z `--final`.
3. Powstaje PDF (druk), HTML (podgląd) i PNG.
