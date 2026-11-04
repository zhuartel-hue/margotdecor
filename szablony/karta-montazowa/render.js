// Karta montażowa: HTML -> PDF (A4 poziomo) + PNG. node render.js karta.html karta.pdf karta.png
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [inp, pdf, png] = process.argv.slice(2);
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1123, height: 794 }, deviceScaleFactor: 2 });
  await pg.goto('file://' + path.resolve(inp));
  await pg.evaluate(() => document.fonts.ready);
  await pg.pdf({ path: pdf, width: '297mm', height: '210mm', printBackground: true, margin: {top:0,bottom:0,left:0,right:0} });
  if (png) await pg.screenshot({ path: png, fullPage: true });
  await b.close();
})();
