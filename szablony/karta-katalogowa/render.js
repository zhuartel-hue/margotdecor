// Renderuje HTML karty do PDF (A4) i PNG (podgląd). node render.js in.html out.pdf out.png
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [inp, pdf, png] = process.argv.slice(2);
  const page_ = fs.readFileSync(inp, 'utf8');
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 900, height: 1300 } });
  await pg.setContent('<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + page_ + '</body></html>');
  await pg.evaluate(() => document.fonts.ready);
  await pg.screenshot({ path: png, fullPage: true });
  await pg.emulateMedia({ media: 'print' });
  await pg.pdf({ path: pdf, format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
