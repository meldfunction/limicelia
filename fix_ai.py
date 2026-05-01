#!/usr/bin/env python3
"""Sequential fix for ai.html: correct nav/footer + insert sections 05+06."""
import sys
sys.path.insert(0, '/home/user/limicelia')

# Load constants from integrate.py
exec(open('/home/user/limicelia/integrate.py').read().split('if __name__')[0])

from pathlib import Path
path = Path('/home/user/limicelia/ai.html')
html = path.read_text()

# 1. Nav: add Mission after bios.html
footer_idx = html.rfind('<footer')
nav_scope_end = footer_idx if footer_idx != -1 else len(html)
if 'mission.html' not in html[:nav_scope_end]:
    nav_start = html.find('<ul class="hnav-links">')
    if nav_start != -1:
        bios_in_nav = html.find('href="bios.html"', nav_start, nav_scope_end)
        if bios_in_nav != -1:
            end_li = html.find('</li>', bios_in_nav) + 5
            html = html[:end_li] + NAV_MISSION + html[end_li:]
            footer_idx = html.rfind('<footer')
    print('  nav: Mission added')
else:
    print('  nav: already present')

# 2. Footer: add Mission after bios.html
if footer_idx != -1 and 'mission.html' not in html[footer_idx:]:
    bios_in_footer = html.find('href="bios.html"', footer_idx)
    if bios_in_footer != -1:
        end_li = html.find('</li>', bios_in_footer) + 5
        html = html[:end_li] + FOOTER_MISSION + html[end_li:]
    print('  footer: Mission added')
else:
    print('  footer: already present')

# 3. Insert sections 05+06 before CTA section
if 'sec-num">05' not in html:
    cta_marker = '>The first conversation'
    cta_idx = html.find(cta_marker)
    sec_start = html.rfind('<section', 0, cta_idx)
    hr_start = html.rfind('<hr ', 0, sec_start)
    hr_end = html.find('>', hr_start) + 1
    html = html[:hr_end] + '\n' + SECTION_05_06 + html[hr_end:]
    print('  sections 05+06: inserted')
else:
    print('  sections 05+06: already present')

path.write_text(html)

lines = html.count('\n')
has_05 = 'sec-num">05' in html
has_06 = 'sec-num">06' in html
has_mission_nav = 'mission.html' in html[:html.rfind('<footer')]
has_mission_footer = 'mission.html' in html[html.rfind('<footer'):]
ends_ok = html.strip().endswith('</html>')
print(f'  lines={lines}, 05={has_05}, 06={has_06}, mission_nav={has_mission_nav}, mission_footer={has_mission_footer}, ends_ok={ends_ok}')
