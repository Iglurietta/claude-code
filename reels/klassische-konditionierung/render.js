// Rendert reel.html Bild für Bild zu einem stummen MP4 und schreibt die Sound-Events nach sfx.json.
// Aufruf: node render.js [out/video_noaudio.mp4]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

(async () => {
  const out = process.argv[2] || path.join(__dirname, 'out', 'video_noaudio.mp4');
  fs.mkdirSync(path.dirname(out), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, 'reel.html') + '?render=1');
  await page.evaluate(() => document.fonts.ready);
  const { DURATION, FPS, SFX } = await page.evaluate(() => ({ DURATION, FPS, SFX }));
  fs.writeFileSync(path.join(path.dirname(out), 'sfx.json'), JSON.stringify({ DURATION, SFX }, null, 1));

  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS),
    '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out],
    { stdio: ['pipe', 'inherit', 'inherit'] });

  const frames = Math.round(DURATION * FPS);
  for (let i = 0; i < frames; i++) {
    await page.evaluate(t => seek(t), i / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log(`Frame ${i}/${frames}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('fertig:', out);
})();
