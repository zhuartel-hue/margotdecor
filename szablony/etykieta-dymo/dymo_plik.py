#!/usr/bin/env python3
"""Pakuje PNG etykiety do pliku .dymo (DYMO Connect), etykieta 2166659 LW 102x210 mm, widok poziomy.
Użycie: python3 dymo_plik.py etykieta-300dpi-poziomo.png wynik.dymo
Uwaga: LabelName odgadnięty ze wzorca DYMO ("<nr> <nazwa>"); jeśli DYMO odrzuci plik,
zapisz pustą etykietę 2166659 w DYMO Connect i podmień LabelName/DYMORect na wartości z niej."""
import base64, sys, pathlib

LABEL_NAME = "2166659 LW 102x210 mm"
W_IN, H_IN = 210 / 25.4, 102 / 25.4   # poziomo, w calach
M = 0.04                              # margines bezpieczeństwa (cale)

def brush(a, v):
    return f'<SolidColorBrush><Color A="{a}" R="{v}" G="{v}" B="{v}"></Color></SolidColorBrush>'

def main():
    png, out = sys.argv[1], sys.argv[2]
    data = base64.b64encode(pathlib.Path(png).read_bytes()).decode()
    w, h = W_IN - 2 * M, H_IN - 2 * M
    xml = f'''﻿<?xml version="1.0" encoding="utf-8"?>
<DesktopLabel Version="1">
  <DYMOLabel Version="3">
    <Description>Margot Decor – etykieta na karton</Description>
    <Orientation>Landscape</Orientation>
    <LabelName>{LABEL_NAME}</LabelName>
    <InitialLength>0</InitialLength>
    <BorderStyle>SolidLine</BorderStyle>
    <DYMORect><DYMOPoint><X>{M:.4f}</X><Y>{M:.4f}</Y></DYMOPoint><Size><Width>{w:.4f}</Width><Height>{h:.4f}</Height></Size></DYMORect>
    <BorderColor>{brush(1, 0)}</BorderColor>
    <BorderThickness>1</BorderThickness>
    <Show_Border>False</Show_Border>
    <DynamicLayoutManager>
      <RotationBehavior>ClearObjects</RotationBehavior>
      <LabelObjects>
        <ImageObject>
          <Name>EtykietaMargot</Name>
          <Brushes>
            <BackgroundBrush>{brush(0, 0)}</BackgroundBrush>
            <BorderBrush>{brush(1, 0)}</BorderBrush>
            <StrokeBrush>{brush(1, 0)}</StrokeBrush>
            <FillBrush>{brush(0, 0)}</FillBrush>
          </Brushes>
          <Rotation>Rotation0</Rotation>
          <OutlineThickness>1</OutlineThickness>
          <IsOutlined>False</IsOutlined>
          <BorderStyle>SolidLine</BorderStyle>
          <Margin><DYMOThickness Left="0" Top="0" Right="0" Bottom="0" /></Margin>
          <Data>{data}</Data>
          <ScaleMode>Uniform</ScaleMode>
          <HorizontalAlignment>Center</HorizontalAlignment>
          <VerticalAlignment>Middle</VerticalAlignment>
          <ObjectLayout>
            <DYMOPoint><X>{M:.4f}</X><Y>{M:.4f}</Y></DYMOPoint>
            <Size><Width>{w:.4f}</Width><Height>{h:.4f}</Height></Size>
          </ObjectLayout>
        </ImageObject>
      </LabelObjects>
    </DynamicLayoutManager>
  </DYMOLabel>
  <LabelApplication>Blank</LabelApplication>
  <DataTable>
    <Columns></Columns>
    <Rows></Rows>
  </DataTable>
</DesktopLabel>
'''
    pathlib.Path(out).write_text(xml, encoding="utf-8")

if __name__ == "__main__":
    main()
