#!/usr/bin/env python3
"""
Parallel integration: wires new Limicelia pages into existing infrastructure.

Phase 1 (parallel):
  - Insert AI Confessional + Accompaniment Cohort sections into ai.html
  - Add Mission link to nav + footer across all site pages

Phase 2:
  - Add AI Practice link to services.html footer
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE = Path('/home/user/limicelia')

# ── Sections 05 + 06 to insert into ai.html ───────────────────────────────
# Inserted AFTER the <hr> that currently separates section 04 from the CTA.
# Starts with the Confessional section; ends with an <hr> before the CTA.

SECTION_05_06 = """\
<!-- EVENT MODULE: THE AI CONFESSIONAL -->
<section style="padding:clamp(4rem,7vw,7rem) clamp(2rem,7vw,7rem);position:relative;z-index:2">
  <div class="sec-label reveal"><span class="sec-num">05 /</span> A gathering</div>
  <h2 class="sec-title reveal" style="margin-bottom:2.5rem">Coming in 2026.<br><em>The AI Confessional.</em></h2>
  <div class="reveal rd1" style="display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--rul)">
    <div style="background:var(--ink);padding:2rem 2.2rem;display:flex;flex-direction:column;gap:1.2rem">
      <p style="font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.14em;text-transform:uppercase;color:var(--amber);opacity:.65">Invite-only evening · Thirty people · 2026</p>
      <p style="font-size:1.05rem;font-weight:300;line-height:1.82;color:var(--ts);max-width:52ch">What is actually happening with AI inside organizations — told honestly, in a room built for it. Four or five leaders share what the public conversation won&#39;t say. The room responds. Nothing leaves without permission.</p>
      <div style="display:flex;gap:2.5rem;flex-wrap:wrap;padding:1.2rem 0;border-top:1px solid var(--rul);border-bottom:1px solid var(--rul)">
        <div><p style="font-family:'DM Mono',monospace;font-size:.52rem;letter-spacing:.12em;text-transform:uppercase;color:var(--amber);opacity:.55;margin-bottom:.2rem">Duration</p><p style="font-size:.9rem;font-weight:300;color:var(--tp)">Two hours</p></div>
        <div><p style="font-family:'DM Mono',monospace;font-size:.52rem;letter-spacing:.12em;text-transform:uppercase;color:var(--amber);opacity:.55;margin-bottom:.2rem">Format</p><p style="font-size:.9rem;font-weight:300;color:var(--tp)">5 speakers · open conversation</p></div>
        <div><p style="font-family:'DM Mono',monospace;font-size:.52rem;letter-spacing:.12em;text-transform:uppercase;color:var(--amber);opacity:.55;margin-bottom:.2rem">Attendance</p><p style="font-size:.9rem;font-weight:300;color:var(--tp)">Invite-only</p></div>
      </div>
      <a href="limicelia-confessional-v3.html" style="display:inline-flex;align-items:center;gap:.6rem;font-family:'DM Mono',monospace;font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:var(--amber);transition:opacity .3s" class="btn-g">Learn more &amp; request an invitation</a>
    </div>
    <div style="background:var(--sur);padding:2rem 2.2rem;display:flex;flex-direction:column;justify-content:center;gap:1.2rem">
      <p style="font-family:'DM Mono',monospace;font-size:.58rem;letter-spacing:.12em;text-transform:uppercase;color:var(--tm)">The gap</p>
      <p style="font-size:clamp(1.1rem,1.6vw,1.3rem);font-weight:300;line-height:1.55;color:var(--tp);font-style:italic">&#8220;Companies declared they no longer need engineers the way they used to. They are quietly posting hundreds of engineering roles. The public narrative about AI has come apart from lived reality.&#8221;</p>
      <p style="font-family:'DM Mono',monospace;font-size:.56rem;letter-spacing:.1em;text-transform:uppercase;color:var(--amber);opacity:.55">This gathering is for the people holding that distance.</p>
    </div>
  </div>
</section>
<hr style="height:1px;background:var(--rul);border:none;position:relative;z-index:2">
<!-- NEW OFFERING: AI ACCOMPANIMENT COHORT -->
<section id="cohort" style="padding:clamp(4rem,7vw,7rem) clamp(2rem,7vw,7rem);position:relative;z-index:2;background:var(--sur)">
  <div class="sec-label reveal"><span class="sec-num">06 /</span> Cohort programme</div>
  <h2 class="sec-title reveal" style="margin-bottom:.8rem">The AI Accompaniment<br><em>Cohort.</em></h2>
  <p class="reveal rd1 body-text" style="max-width:58ch;margin-bottom:2.5rem">A peer learning cohort for senior leaders navigating AI transformation — not a curriculum to complete, but a practice to build together. Eight sessions. A small group. Real situations brought by the people in the room.</p>
  <div class="reveal rd2" style="display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--rul);margin-bottom:2rem">
    <div style="background:var(--ink);padding:2rem 1.8rem">
      <p style="font-family:'DM Mono',monospace;font-size:.6rem;letter-spacing:.12em;text-transform:uppercase;color:var(--amber);opacity:.6;margin-bottom:.7rem">Format</p>
      <h3 style="font-size:1.05rem;font-weight:400;color:var(--tp);margin-bottom:.6rem">Eight sessions<br>over ten weeks</h3>
      <p style="font-size:.95rem;font-weight:300;line-height:1.78;color:var(--ts)">Biweekly, two hours each. In-person where possible, remote where not. The cohort stays together for the full arc — no drop-ins, no observers.</p>
    </div>
    <div style="background:var(--ink);padding:2rem 1.8rem">
      <p style="font-family:'DM Mono',monospace;font-size:.6rem;letter-spacing:.12em;text-transform:uppercase;color:var(--amber);opacity:.6;margin-bottom:.7rem">Who it&#39;s for</p>
      <h3 style="font-size:1.05rem;font-weight:400;color:var(--tp);margin-bottom:.6rem">Leaders who own<br>something real</h3>
      <p style="font-size:.95rem;font-weight:300;line-height:1.78;color:var(--ts)">CHROs, COOs, heads of transformation, L&amp;D leaders. People responsible for how AI lands in their organizations — and who want to think that through with peers, not just consultants.</p>
    </div>
    <div style="background:var(--ink);padding:2rem 1.8rem">
      <p style="font-family:'DM Mono',monospace;font-size:.6rem;letter-spacing:.12em;text-transform:uppercase;color:var(--amber);opacity:.6;margin-bottom:.7rem">Size</p>
      <h3 style="font-size:1.05rem;font-weight:400;color:var(--tp);margin-bottom:.6rem">Twelve people,<br>maximum</h3>
      <p style="font-size:.95rem;font-weight:300;line-height:1.78;color:var(--ts)">Small enough that everyone&#39;s situation gets genuine attention. Diverse enough that the range of experiences is useful. Curated, not open enrollment.</p>
    </div>
  </div>
  <div class="reveal rd1" style="display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--rul);margin-bottom:2rem">
    <div style="background:var(--ink);padding:1.8rem 2rem">
      <p style="font-family:'DM Mono',monospace;font-size:.58rem;letter-spacing:.12em;text-transform:uppercase;color:var(--amber);opacity:.6;margin-bottom:.8rem">Focus areas — your choice</p>
      <div style="display:flex;flex-direction:column;gap:.6rem">
        <div style="display:flex;align-items:baseline;gap:.8rem;padding:.5rem 0;border-bottom:1px solid var(--rul)"><span style="font-family:'DM Mono',monospace;font-size:.52rem;color:var(--amber);opacity:.5;white-space:nowrap">A</span><span style="font-size:.95rem;font-weight:300;color:var(--ts)">AI governance &amp; decision-making — who decides, and how</span></div>
        <div style="display:flex;align-items:baseline;gap:.8rem;padding:.5rem 0;border-bottom:1px solid var(--rul)"><span style="font-family:'DM Mono',monospace;font-size:.52rem;color:var(--amber);opacity:.5;white-space:nowrap">B</span><span style="font-size:.95rem;font-weight:300;color:var(--ts)">Workflow redesign with employees — not for them</span></div>
        <div style="display:flex;align-items:baseline;gap:.8rem;padding:.5rem 0;border-bottom:1px solid var(--rul)"><span style="font-family:'DM Mono',monospace;font-size:.52rem;color:var(--amber);opacity:.5;white-space:nowrap">C</span><span style="font-size:.95rem;font-weight:300;color:var(--ts)">Trust, culture &amp; the relational cost of AI adoption</span></div>
        <div style="display:flex;align-items:baseline;gap:.8rem;padding:.5rem 0;border-bottom:1px solid var(--rul)"><span style="font-family:'DM Mono',monospace;font-size:.52rem;color:var(--amber);opacity:.5;white-space:nowrap">D</span><span style="font-size:.95rem;font-weight:300;color:var(--ts)">Participatory AI design — giving affected communities a real role</span></div>
        <div style="display:flex;align-items:baseline;gap:.8rem;padding:.5rem 0"><span style="font-family:'DM Mono',monospace;font-size:.52rem;color:var(--amber);opacity:.5;white-space:nowrap">E</span><span style="font-size:.95rem;font-weight:300;color:var(--ts)">Values&#8211;technology alignment — closing the gap between what you say and what you do</span></div>
      </div>
    </div>
    <div style="background:var(--ink);padding:1.8rem 2rem;display:flex;flex-direction:column;gap:1rem">
      <p style="font-family:'DM Mono',monospace;font-size:.58rem;letter-spacing:.12em;text-transform:uppercase;color:var(--amber);opacity:.6">How each session works</p>
      <div style="display:flex;gap:.8rem;align-items:baseline"><span style="font-family:'DM Mono',monospace;font-size:.54rem;color:var(--amber);opacity:.5;flex-shrink:0">01</span><p style="font-size:.95rem;font-weight:300;line-height:1.7;color:var(--ts)"><strong style="color:var(--tp);font-weight:400">A real situation</strong> brought by one member — live, unresolved, genuinely uncertain</p></div>
      <div style="display:flex;gap:.8rem;align-items:baseline"><span style="font-family:'DM Mono',monospace;font-size:.54rem;color:var(--amber);opacity:.5;flex-shrink:0">02</span><p style="font-size:.95rem;font-weight:300;line-height:1.7;color:var(--ts)"><strong style="color:var(--tp);font-weight:400">The cohort responds</strong> — not to fix, but to think alongside. Facilitated by Limicelia</p></div>
      <div style="display:flex;gap:.8rem;align-items:baseline"><span style="font-family:'DM Mono',monospace;font-size:.54rem;color:var(--amber);opacity:.5;flex-shrink:0">03</span><p style="font-size:.95rem;font-weight:300;line-height:1.7;color:var(--ts)"><strong style="color:var(--tp);font-weight:400">A practitioner or researcher</strong> joins select sessions — not to lecture, but to enrich</p></div>
      <div style="display:flex;gap:.8rem;align-items:baseline"><span style="font-family:'DM Mono',monospace;font-size:.54rem;color:var(--amber);opacity:.5;flex-shrink:0">04</span><p style="font-size:.95rem;font-weight:300;line-height:1.7;color:var(--ts)"><strong style="color:var(--tp);font-weight:400">Between sessions</strong> — brief written reflection shared with the group. No homework. One question.</p></div>
    </div>
  </div>
  <div class="reveal rd2" style="border:1px solid var(--amber-dim);padding:1.6rem 2rem;background:var(--amber-glow);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1.5rem">
    <div>
      <p style="font-family:'DM Mono',monospace;font-size:.58rem;letter-spacing:.12em;text-transform:uppercase;color:var(--amber);margin-bottom:.4rem">First cohort — 2026</p>
      <p style="font-size:1rem;font-weight:300;color:var(--ts);max-width:52ch">We are forming the first cohort now. If this sounds like what you need, reach out. We will tell you honestly whether the fit is right.</p>
    </div>
    <a href="contact.html" style="display:inline-flex;align-items:center;gap:.7rem;font-family:'DM Mono',monospace;font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink);background:var(--amber);padding:.7rem 1.8rem;white-space:nowrap;flex-shrink:0">Express interest</a>
  </div>
</section>
<hr style="height:1px;background:var(--rul);border:none;position:relative;z-index:2">
"""

# ── Nav/footer link fragments ──────────────────────────────────────────────

# Top-nav item (no inline style — matches existing nav link pattern)
NAV_MISSION = '<li><a href="mission.html">Mission</a></li>'

# Footer item (with inline style — matches existing footer link pattern)
FOOTER_MISSION = (
    '<li><a href="mission.html" style="font-family:\'DM Mono\',monospace;'
    'font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;'
    'color:var(--tm)">Mission</a></li>'
)

# Footer AI Practice item
FOOTER_AI = (
    '<li><a href="ai.html" style="font-family:\'DM Mono\',monospace;'
    'font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;'
    'color:var(--tm)">AI Practice</a></li>'
)


# ── Task functions ─────────────────────────────────────────────────────────

def update_ai(path: Path) -> str:
    html = path.read_text()
    if 'sec-num">05' in html:
        return f'SKIP {path.name}: sections 05-06 already present'

    # Find the CTA h2 to locate the CTA section
    cta_marker = '>The first conversation'
    cta_idx = html.find(cta_marker)
    if cta_idx == -1:
        return f'SKIP {path.name}: CTA marker not found'

    # Walk back to find the <section> opening tag containing the CTA
    sec_start = html.rfind('<section', 0, cta_idx)
    if sec_start == -1:
        return f'SKIP {path.name}: CTA section tag not found'

    # Find the <hr> immediately before that <section>
    hr_start = html.rfind('<hr ', 0, sec_start)
    if hr_start == -1:
        return f'SKIP {path.name}: preceding <hr> not found'

    # Insert SECTION_05_06 after the closing > of that <hr>
    hr_end = html.find('>', hr_start) + 1
    html = html[:hr_end] + '\n' + SECTION_05_06 + html[hr_end:]
    path.write_text(html)
    return f'OK   {path.name}: inserted sections 05+06'


def update_page(path: Path) -> str:
    html = path.read_text()
    changed = False
    footer_idx = html.rfind('<footer')

    # ── Top nav: add Mission after bios.html link ──────────────────────────
    # Scope search to nav area only (before footer) to avoid footer matches
    nav_scope_end = footer_idx if footer_idx != -1 else len(html)
    if 'mission.html' not in html[:nav_scope_end]:
        nav_start = html.find('<ul class="hnav-links">')
        if nav_start != -1:
            bios_in_nav = html.find('href="bios.html"', nav_start, nav_scope_end)
            if bios_in_nav != -1:
                end_li = html.find('</li>', bios_in_nav) + 5
                html = html[:end_li] + NAV_MISSION + html[end_li:]
                changed = True
                # Recalculate footer_idx after insertion
                footer_idx = html.rfind('<footer')

    # ── Footer: add Mission after bios.html link ───────────────────────────
    if footer_idx != -1 and 'mission.html' not in html[footer_idx:]:
        bios_in_footer = html.find('href="bios.html"', footer_idx)
        if bios_in_footer != -1:
            end_li = html.find('</li>', bios_in_footer) + 5
            html = html[:end_li] + FOOTER_MISSION + html[end_li:]
            changed = True

    if changed:
        path.write_text(html)
        return f'OK   {path.name}: nav+footer updated'
    return f'SKIP {path.name}: already up to date'


def add_ai_to_services(path: Path) -> str:
    html = path.read_text()
    footer_idx = html.rfind('<footer')
    if footer_idx == -1:
        return f'SKIP {path.name}: no footer found'
    if 'ai.html' in html[footer_idx:]:
        return f'SKIP {path.name}: ai.html already in footer'

    # Insert AI Practice link after the Services link in footer
    svc_in_footer = html.find('href="services.html"', footer_idx)
    if svc_in_footer == -1:
        return f'SKIP {path.name}: services.html not in footer'
    end_li = html.find('</li>', svc_in_footer) + 5
    html = html[:end_li] + FOOTER_AI + html[end_li:]
    path.write_text(html)
    return f'OK   {path.name}: AI Practice link added to footer'


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # Pages that get nav/footer treatment (all .html except stubs)
    skip = {'imagestest.html'}
    all_pages = sorted(p for p in BASE.glob('*.html') if p.name not in skip)
    # ai.html gets the section insertion; all pages get nav/footer
    ai_path = BASE / 'ai.html'

    print(f'Phase 1 — parallel ({len(all_pages) + 1} tasks)')
    tasks: dict = {}
    with ThreadPoolExecutor(max_workers=len(all_pages) + 2) as ex:
        tasks[ex.submit(update_ai, ai_path)] = ai_path.name
        for p in all_pages:
            tasks[ex.submit(update_page, p)] = p.name
        for fut in as_completed(tasks):
            try:
                print(f'  {fut.result()}')
            except Exception as exc:
                print(f'  ERR  {tasks[fut]}: {exc}')

    print('\nPhase 2 — services.html AI footer link')
    print(f'  {add_ai_to_services(BASE / "services.html")}')

    print('\nDone.')
