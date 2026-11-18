// HTML etykiety -> PDF 102×210 mm (wektorowy, 1:1). node render.js in.html out.pdf
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [inp, pdf] = process.argv.slice(2);
  const body = fs.readFileSync(inp, 'utf8');
  const b = await chromium.launch();
  const pg = await b.newPage();
  await pg.setContent('<!doctype html><html lang="pl"><head><meta charset="utf-8"></head><body>' + body + '</body></html>');
  await pg.evaluate(() => document.fonts.ready);
  await pg.pdf({ path: pdf, width: '102mm', height: '210mm', printBackground: true, pageRanges: '1' });
  await b.close();
})();
