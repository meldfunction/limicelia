import re
from pathlib import Path

files = [
    'strategic-essays.md',
    'private-collaboration-agreement.md', 
    'present-of-work-canvas.md',
    'limicelia-strategy-canvases.md',
    'co-steward-constitution.md',
    '00-master-index.md'
]

for f in files:
    path = Path(f)
    if path.exists():
        content = path.read_text(encoding='utf-8')
        updated = re.sub(r'\(/stewards/', r'(/limicelia/stewards/', content)
        if content != updated:
            path.write_text(updated, encoding='utf-8')
            count = len(re.findall(r'\(/stewards/', content))
            print(f'✓ Updated {f}: {count} links changed')