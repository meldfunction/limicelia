import re
from pathlib import Path
from urllib.parse import urlparse

base_dir = Path(__file__).parent.resolve()
changed = []


def record(fp: Path, orig: str, new: str):
    try:
        rel = str(fp.relative_to(base_dir))
    except Exception:
        rel = str(fp)
    changed.append((rel, orig, new))


# Canonicalize any input into exactly one absolute path starting with /limicelia/stewards/
def normalize_to_limicelia_stewards(target: str) -> str:
    """
    Return a canonical path that always begins with '/limicelia/stewards/' and never duplicates 'limicelia'.
    Examples:
      "stewards/x.md"                -> "/limicelia/stewards/x.md"
      "/stewards/x.md"               -> "/limicelia/stewards/x.md"
      "limicelia/stewards/x.md"      -> "/limicelia/stewards/x.md"
      "/limicelia/stewards/x.md"     -> "/limicelia/stewards/x.md"
      "https://.../limicelia/stewards/x.md" -> "/limicelia/stewards/x.md"
    """
    s = (target or "").strip()

    # If full URL, extract its path
    parsed = urlparse(s)
    if parsed.scheme and parsed.netloc:
        path = parsed.path or ""
    else:
        path = s

    # Find the first occurrence of 'stewards/' and capture the remainder (the tail)
    m = re.search(r'stewards/(.*)$', path, flags=re.IGNORECASE)
    if m:
        tail = m.group(1)
    else:
        # fallback: use the last path segment(s)
        tail = path.strip('/')

    tail = tail.lstrip('/')
    if tail:
        return '/limicelia/stewards/' + tail
    else:
        return '/limicelia/stewards/'


def normalize_md_file(fp: Path):
    text = fp.read_text(encoding="utf-8")
    orig = text

    # 1) Convert markdown links: [label](/limicelia/stewards/xx.md) or [label](limicelia/stewards/xx.md) or [label](/stewards/xx.md)
    md_link_re = re.compile(
        r'\[([^\]]+)\]\(\s*(["\']?)(\/?(?:limicelia\/)?stewards\/[^\)\s"\']+\.md)(["\']?)\s*\)',
        flags=re.IGNORECASE,
    )

    def md_link_repl(m):
        label = m.group(1)
        target = m.group(3)
        doc = normalize_to_limicelia_stewards(target)
        new = f"viewer.html?doc={doc}"
        record(fp, target, new)
        return f"[{label}]({new})"

    text = md_link_re.sub(md_link_repl, text)

    # 2) Convert bare .md links anywhere pointing to stewards -> viewer.html?doc=...
    bare_md_re = re.compile(r'(?<!["\'])(\/?(?:limicelia\/)?stewards\/[^\s\)\]\},"\']+\.md)', flags=re.IGNORECASE)

    def bare_md_repl(m):
        target = m.group(1)
        doc = normalize_to_limicelia_stewards(target)
        new = f"viewer.html?doc={doc}"
        record(fp, target, new)
        return new

    text = bare_md_re.sub(bare_md_repl, text)

    # 3) Convert absolute site-directory URLs that point to the stewards dir to stewards.html
    site_dir_re = re.compile(r'(https?://[^\s"\'\)]+?/(?:limicelia/)?stewards)(/)?(?=[\s"\')\]])', flags=re.IGNORECASE)

    def site_dir_repl(m):
        orig_url = m.group(0)
        base = m.group(1)
        parsed = urlparse(base)
        host = f"{parsed.scheme}://{parsed.netloc}"
        # canonical path for the stewards directory (no duplicate limicelia)
        canon_path = normalize_to_limicelia_stewards(parsed.path)
        new = host.rstrip('/') + canon_path + '/stewards.html'
        record(fp, orig_url, new)
        return new

    text = site_dir_re.sub(site_dir_repl, text)

    if text != orig:
        fp.write_text(text, encoding="utf-8")
        print(f"✓ Updated {fp.name}")
        return True
    else:
        print(f"- No changes needed for {fp.name}")
        return False


def ensure_doc_item_attr(attrs: str) -> str:
    attrs = (attrs or "").strip()
    attrs = re.sub(r'\s+', ' ', attrs).strip()
    m = re.search(r'\bclass\s*=\s*"([^"]*)"', attrs, flags=re.IGNORECASE)
    if m:
        classes = m.group(1)
        if 'doc-item' not in classes.split():
            classes = (classes + ' doc-item').strip()
        attrs = re.sub(r'\bclass\s*=\s*"[^"]*"', f'class="{classes}"', attrs, flags=re.IGNORECASE)
    else:
        if attrs:
            attrs = attrs + ' class="doc-item"'
        else:
            attrs = 'class="doc-item"'
    return re.sub(r'\s+', ' ', attrs).strip()


def convert_stewards_html_to_viewer(fp: Path) -> bool:
    if not fp.exists():
        print(f"✗ File not found: {fp.name}")
        return False

    text = fp.read_text(encoding="utf-8")
    orig = text

    # Convert anchors href="/limicelia/stewards/xxx.md" or href="stewards/xxx.md" to viewer.html?doc=/limicelia/stewards/xxx.md
    a_re = re.compile(
        r'<a\b([^>]*)\bhref=(["\'])(\/?(?:limicelia\/)?stewards\/[^"\']+)(["\'])([^>]*)>(.*?)</a>',
        flags=re.IGNORECASE | re.DOTALL,
    )

    def a_repl(m):
        before = (m.group(1) or "") + " " + (m.group(5) or "")
        href_target = m.group(3)
        inner = m.group(6)
        doc = normalize_to_limicelia_stewards(href_target)
        new_href = f'href="viewer.html?doc={doc}"'
        attrs = ensure_doc_item_attr(before)
        record(fp, href_target, f"viewer.html?doc={doc}")
        return f'<a {new_href} {attrs}>{inner}</a>'

    text = a_re.sub(a_repl, text)

    # Ensure existing viewer anchors use canonical path and have class
    viewer_re = re.compile(
        r'<a\b([^>]*)\bhref=(["\'])viewer\.html\?doc=(\/?(?:limicelia\/)?stewards\/[^"\']+)\2([^>]*)>(.*?)</a>',
        flags=re.IGNORECASE | re.DOTALL,
    )

    def viewer_repl(m):
        before = (m.group(1) or "") + " " + (m.group(4) or "")
        doc_target = m.group(3)
        inner = m.group(5)
        doc = normalize_to_limicelia_stewards(doc_target)
        attrs = ensure_doc_item_attr(before)
        record(fp, f'viewer.html?doc={doc_target}', f'viewer.html?doc={doc} (ensured doc-item)')
        return f'<a href="viewer.html?doc={doc}" {attrs}>{inner}</a>'

    text = viewer_re.sub(viewer_repl, text)

    if text != orig:
        fp.write_text(text, encoding="utf-8")
        print(f"✓ Converted {fp.name}")
        return True
    else:
        print(f"- No viewer conversion needed in {fp.name}")
        return False


def write_report():
    if not changed:
        print("\n- No link changes recorded.")
        return
    rpt = base_dir / "stewards_changed_links_report.txt"
    with rpt.open("w", encoding="utf-8") as f:
        for fp, o, n in changed:
            f.write(f"{fp} | {o} -> {n}\n")
    print(f"\nReport written: {rpt}")


def main():
    print("Starting link updates...")
    print("Base dir:", base_dir)
    print("=" * 60)

    files_to_update = [
        'stewards.html',
        'strategic-essays.md',
        'private-collaboration-agreement.md',
        'present-of-work-canvas.md',
        'limicelia-strategy-canvases.md',
        'co-steward-constitution.md',
        '00-master-index.md'
    ]

    updated_count = 0
    # process listed markdown files
    for name in files_to_update:
        fp = base_dir / name
        if name == 'stewards.html':
            if convert_stewards_html_to_viewer(fp):
                updated_count += 1
        else:
            if normalize_md_file(fp):
                updated_count += 1

    # also process any other md files
    for md in sorted(base_dir.glob('*.md')):
        if md.name in files_to_update:
            continue
        if normalize_md_file(md):
            updated_count += 1

    print("=" * 60)
    print(f"Complete! Updated {updated_count} files.")
    write_report()


if __name__ == '__main__':
    main()