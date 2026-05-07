#!/usr/bin/env node
/**
 * generate.js — Limicelia service guide PDF generator
 *
 * Prints each service-*.html to a PDF using Puppeteer + local Chrome.
 * Run from _pdfs/: node generate.js
 * Or from repo root: node _pdfs/generate.js
 *
 * Output: _pdfs/*.pdf
 *
 * Two modes via CLI flag:
 *   node generate.js           → design guide PDFs (anatomy + prompts)
 *   node generate.js --onepager → client-facing PDFs (strips staging/anatomy)
 */

const puppeteer = require('./node_modules/puppeteer');
const path = require('path');
const fs = require('fs');

const REPO = path.resolve(__dirname, '..');
const OUT  = __dirname;

const PAGES = [
  { file: 'service-org-design.html',    name: 'limicelia-org-design' },
  { file: 'service-leadership.html',    name: 'limicelia-leadership' },
  { file: 'service-conflict.html',      name: 'limicelia-conflict' },
  { file: 'service-org-memory.html',    name: 'limicelia-org-memory' },
  { file: 'service-community.html',     name: 'limicelia-community' },
  { file: 'service-field-building.html',name: 'limicelia-field-building' },
];

// CSS injected before printing
const PRINT_CSS = `
  /* ── kill heavy backgrounds (grain texture + canvas glow) ── */
  body::after { display: none !important; }
  #mc { display: none !important; }
  body {
    background: #fff !important;
    color: #1a1714 !important;
  }
  /* ── amber stays amber, dim it slightly for print legibility ── */
  :root {
    --ink: #ffffff !important;
    --tp:  #1a1714 !important;
    --ts:  rgba(26,23,20,.75) !important;
    --tm:  rgba(26,23,20,.5) !important;
    --sur: #f5f0e8 !important;
    --rul: rgba(26,23,20,.12) !important;
    --amber-glow: transparent !important;
    --amber-dim: rgba(150,96,28,.4) !important;
  }

  /* ── always hide ── */
  .ps, .hamburger, .hnav-links { display: none !important; }

  /* ── reveal: show everything without animation ── */
  .reveal { opacity: 1 !important; transform: none !important; }

  /* ── anatomy popup: show inline below card ── */
  .anat-popup {
    opacity: 1 !important; transform: none !important;
    position: relative !important; bottom: auto !important;
    margin-top: .8rem; box-shadow: none !important;
    border: 1px solid rgba(150,96,28,.3) !important;
    background: rgba(150,96,28,.05) !important;
    pointer-events: auto !important;
  }
  .anatomy-card { transform: none !important; box-shadow: none !important; }

  /* ── page breaks ── */
  .anatomy-grid, .example-grid, .prompt-stack, .perf-grid { break-inside: avoid; }
  .anatomy-card, .example-card, .prompt-row, .perf-card { break-inside: avoid; }
  section { break-inside: avoid; }
  hr { break-after: avoid; }

  /* ── typography ── */
  body { font-size: 13px !important; }
  .guide-h1 { font-size: 2rem !important; }
  .sec-h2 { font-size: 1.6rem !important; }

  /* ── nav: static, no shadow ── */
  .hnav { position: relative !important; border-bottom: 1px solid #ddd; }
`;

const ONE_PAGER_CSS = `
  /* In onepager mode: hide anatomy (§A), prompts (§C), perf (§D) */
  /* Keep: hero, §B live example, CTA */
`;

async function run() {
  const onepaperMode = process.argv.includes('--onepager');
  const suffix = onepaperMode ? '-onepager' : '-guide';

  console.log(`\nMode: ${onepaperMode ? 'CLIENT ONE-PAGER' : 'DESIGN GUIDE'}`);
  console.log(`Output dir: ${OUT}\n`);

  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    headless: true,
  });

  for (const { file, name } of PAGES) {
    const src = path.join(REPO, file);
    if (!fs.existsSync(src)) {
      console.log(`  SKIP ${file} — not found`);
      continue;
    }

    const url = `file://${src}`;
    const out = path.join(OUT, `${name}${suffix}.pdf`);

    console.log(`  → ${file}`);

    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 });

    // Wait for fonts
    await new Promise(r => setTimeout(r, 1200));

    // Make all reveals visible
    await page.evaluate(() => {
      document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
    });

    // Inject print CSS
    await page.addStyleTag({ content: PRINT_CSS });

    if (onepaperMode) {
      // Hide staging banner + anatomy/prompts/perf sections in onepager mode
      await page.evaluate(() => {
        document.querySelectorAll('.staging-banner, .perf-banner, .perf-grid').forEach(el => el.style.display = 'none');
        // Hide §A anatomy and §C prompts and §D sections by their sec-label text
        document.querySelectorAll('.pad').forEach(pad => {
          const label = pad.querySelector('.sec-label');
          if (!label) return;
          const t = label.textContent || '';
          if (t.includes('A /') || t.includes('C /') || t.includes('D /')) {
            pad.style.display = 'none';
          }
        });
        // Also hide adjacent <hr> before hidden pads
        document.querySelectorAll('hr').forEach(hr => {
          const next = hr.nextElementSibling;
          if (next && next.style && next.style.display === 'none') {
            hr.style.display = 'none';
          }
        });
      });
      await page.addStyleTag({ content: ONE_PAGER_CSS });
    }

    await page.pdf({
      path: out,
      format: 'Letter',
      margin: { top: '0.6in', right: '0.7in', bottom: '0.6in', left: '0.7in' },
      printBackground: false,
      displayHeaderFooter: true,
      headerTemplate: '<span></span>',
      footerTemplate: `
        <div style="width:100%;font-family:'DM Mono',monospace;font-size:8px;color:#888;
                    display:flex;justify-content:space-between;padding:0 0.7in">
          <span>limicelia.org</span>
          <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
        </div>`,
    });

    await page.close();
    console.log(`     ✓ ${path.basename(out)}`);
  }

  await browser.close();
  console.log('\nDone.\n');
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
