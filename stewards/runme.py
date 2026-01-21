# ...existing code...
import re
from pathlib import Path

# Record of changes: list of tuples (filepath, original_href, new_href)
changed_links = []

# Base directory (script location)
base_dir = Path(__file__).parent.resolve()

# Files to process (relative to base_dir)
files_to_update = [
    'stewards.html',
    'strategic-essays.md',
    'private-collaboration-agreement.md',
    'present-of-work-canvas.md',
    'limicelia-strategy-canvases.md',
    'co-steward-constitution.md',
    '00-master-index.md'
]


def record_change(filepath: Path, orig: str, new: str):
    changed_links.append((str(filepath.relative_to(base_dir)), orig, new))


def ensure_doc_item_attr(attrs: str) -> str:
    """Ensure attrs string contains class=\"doc-item\" (append if missing)."""
    # preserve other attributes; normalize whitespace
    attrs = attrs or ''
    attrs = re.sub(r'\s+', ' ', attrs).strip()
    # search for class=""
    m = re.search(r'\bclass\s*=\s*"([^"]*)"', attrs, flags=re.IGNORECASE)
    if m:
        classes = m.group(1)
        if 'doc-item' not in classes.split():
            new_classes = (classes + ' doc-item').strip()
            attrs = re.sub(r'\bclass\s*=\s*"[^"]*"', f'class="{new_classes}"', attrs, flags=re.IGNORECASE)
    else:
        if attrs:
            attrs = attrs + ' class="doc-item"'
        else:
            attrs = 'class="doc-item"'
    attrs = re.sub(r'\s+', ' ', attrs).strip()
    return attrs


def normalize_existing_viewer_anchors(filepath: Path, text: str) -> (str, int):
    """
    Ensure existing viewer.html?doc=/limicelia/stewards/... anchors include class='doc-item'.
    Returns (updated_text, count_changes).
    """
    pattern = re.compile(
        r'<a\b([^>]*)\bhref=(["\'])viewer\.html\?doc=(\/(?:limicelia\/)?stewards\/[^"\']+)\2([^>]*)>(.*?)</a>',
        flags=re.IGNORECASE | re.DOTALL
    )

    def repl(m):
        pre = (m.group(1) or '') + ' ' + (m.group(4) or '')
        doc_path = m.group(3)
        inner = m.group(5)
        attrs = ensure_doc_item_attr(pre)
        # Record if class was missing or updated
        record_change(filepath, f'viewer.html?doc={doc_path}', f'viewer.html?doc={doc_path} (ensured doc-item)')
        return f'<a href="viewer.html?doc={doc_path}" {attrs}>{inner}</a>'

    updated, n = pattern.subn(repl, text)
    return updated, n


def convert_plain_stewards_anchors_to_viewer(filepath: Path, text: str) -> (str, int):
    """
    Convert anchors with href="/stewards/..." or href="/limicelia/stewards/..." to
    href="viewer.html?doc=/limicelia/stewards/..." and ensure class="doc-item".
    Returns (updated_text, count_converted).
    """
    pattern = re.compile(
        r'<a\b([^>]*)\bhref=(["\'])(\/(?:limicelia\/)?stewards\/[^"\']+)\2([^>]*)>(.*?)</a>',
        flags=re.IGNORECASE | re.DOTALL
    )

    def repl(m):
        left_before = m.group(1) or ''
        href_path = m.group(3)
        left_after = m.group(4) or ''
        inner = m.group(5)
        # normalize path to start with /limicelia/stewards/
        if href_path.startswith('/stewards/'):
            doc_path = '/limicelia' + href_path
        else:
            doc_path = href_path
        new_href = f'viewer.html?doc={doc_path}'
        attrs = ensure_doc_item_attr((left_before + ' ' + left_after).strip())
        record_change(filepath, href_path, new_href)
        return f'<a href="{new_href}" {attrs}>{inner}</a>'

    updated, n = pattern.subn(repl, text)
    return updated, n


def convert_stewards_html_to_viewer(filepath: Path) -> bool:
    """Read stewards.html, normalize existing viewer anchors, convert stewards hrefs to viewer,
    ensure class='doc-item' on all viewer anchors, write file if changed, and record changes."""
    if not filepath.exists():
        print(f"✗ File not found: {filepath}")
        return False

    text = filepath.read_text(encoding='utf-8')
    original = text

    # 1) Normalize existing viewer anchors (add doc-item)
    text, count_norm = normalize_existing_viewer_anchors(filepath, text)

    # 2) Convert /stewards/... or /limicelia/stewards/... anchors to viewer links
    text, count_conv = convert_plain_stewards_anchors_to_viewer(filepath, text)

    total = count_norm + count_conv
    if text != original:
        filepath.write_text(text, encoding='utf-8')
        print(f"✓ Converted {filepath.name}: {total} anchors processed ({count_conv} converted, {count_norm} normalized)")
        return True
    else:
        print(f"- No viewer conversion needed in {filepath.name}")
        return False


def update_links_in_markdown(filepath: Path) -> bool:
    """
    Replace occurrences of /stewards/ (in href=, markdown links, or plain) with /limicelia/stewards/
    and record each replacement.
    """
    if not filepath.exists():
        print(f"✗ File not found: {filepath}")
        return False

    text = filepath.read_text(encoding='utf-8')
    original = text

    # Matches href=".../stewards/...", href='...', markdown links [text](/stewards/...), and bare (/stewards/)
    pattern = re.compile(r'(?P<prefix>(href\s*=\s*["\']|[\(\[]\s*))(\/stewards/)', flags=re.IGNORECASE)

    def repl(m):
        prefix = m.group('prefix')
        record_change(filepath, m.group(0), prefix + '/limicelia/stewards/')
        return prefix + '/limicelia/stewards/'

    updated, n = pattern.subn(repl, text)

    # Also handle any remaining bare "/stewards/" occurrences (unlikely) -- replace with "/limicelia/stewards/"
    if n == 0 and '/stewards/' in text:
        updated = text.replace('/stewards/', '/limicelia/stewards/')
        if updated != original:
            # Record a generic replacement (file-level)
            record_change(filepath, '/stewards/', '/limicelia/stewards/')

    if updated != original:
        filepath.write_text(updated, encoding='utf-8')
        print(f"✓ Updated {filepath.name}: replaced /stewards/ occurrences")
        return True
    else:
        print(f"- No changes needed for {filepath.name}")
        return False


def write_report():
    if not changed_links:
        print("\n- No link changes recorded.")
        return
    report_path = base_dir / 'stewards_changed_links_report.txt'
    try:
        with report_path.open('w', encoding='utf-8') as rpt:
            for fp, orig, new in changed_links:
                rpt.write(f"{fp} | {orig} -> {new}\n")
        print(f"\nReport written: {report_path}")
    except Exception as e:
        print(f"✗ Error writing report: {e}")


def main():
    print("Starting link updates...")
    print("Base dir:", base_dir)
    print("=" * 60)

    total_updated = 0

    for name in files_to_update:
        fp = base_dir / name
        if name == 'stewards.html':
            if convert_stewards_html_to_viewer(fp):
                total_updated += 1
        else:
            if update_links_in_markdown(fp):
                total_updated += 1

    # Also consider scanning the stewards directory for other .md files not listed
    # (optional) - include anything under base_dir with .md extension
    extra_processed = 0
    for md in sorted(base_dir.glob('*.md')):
        if md.name in files_to_update:
            continue
        if update_links_in_markdown(md):
            extra_processed += 1

    if extra_processed:
        print(f"Processed {extra_processed} additional markdown files in {base_dir}")

    print("=" * 60)
    print(f"Complete! Updated {total_updated} of {len(files_to_update)} listed files.")
    write_report()


if __name__ == '__main__':
    main()
# ...existing code...