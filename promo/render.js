// Renders promo.html to an MP4: node render.js [out.mp4] [fps]
// 9:16 version: PORTRAIT=1 node render.js gamepadmouse-promo-9x16.mp4
// Each frame is drawn by window.seek(t), so the output is deterministic.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const out = process.argv[2] || path.join(__dirname, 'gamepadmouse-promo.mp4');
const fps = Number(process.argv[3] || 30);
const stills = process.env.STILLS;
const portrait = !!process.env.PORTRAIT; // 9:16 version // e.g. "1,5,9" -> write PNGs instead of video

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: portrait ? { width: 1080, height: 1920 } : { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(__dirname, 'promo.html') + (portrait ? '?portrait' : ''));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);

  if (stills) {
    for (const t of stills.split(',').map(Number)) {
      await page.evaluate(t => window.seek(t), t);
      await page.screenshot({ path: path.join(process.env.STILL_DIR || __dirname, `still-${t}.png`) });
    }
    return browser.close();
  }

  const duration = await page.evaluate(() => window.DURATION);
  const total = Math.round(duration * fps);
  // soundtrack.wav (from soundtrack.py) is muxed in when present
  const wav = path.join(__dirname, 'soundtrack.wav');
  const audio = require('fs').existsSync(wav) ? ['-i', wav, '-c:a', 'aac', '-b:a', '192k', '-shortest'] : [];
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', ...audio,
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < total; i++) {
    await page.evaluate(t => window.seek(t), i / fps);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) process.stdout.write(`frame ${i}/${total}\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('wrote', out);
})();
