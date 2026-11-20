const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [mode, out] = [process.argv[2], process.argv[3]];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve(__dirname, 'reel.html') + '?render');
  await p.evaluate(() => document.fonts.ready);
  const el = await p.$('#stage');
  if (mode === 'check') {
    for (const t of process.argv.slice(4).map(Number)) {
      await p.evaluate(t => render(t), t);
      await el.screenshot({ path: `${out}/t${t}.png` });
    }
  } else {
    const { DUR, FPS } = await p.evaluate(() => ({ DUR, FPS }));
    const n = Math.round(DUR * FPS);
    for (let i = 0; i < n; i++) {
      await p.evaluate(t => render(t), i / FPS);
      await el.screenshot({ path: `${out}/f${String(i).padStart(5, '0')}.png` });
    }
  }
  await b.close();
})();
