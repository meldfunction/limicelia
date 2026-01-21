import re
from pathlib import Path

base_dir = Path(__file__).parent.resolve()
changed = []

# process all markdown files in this folder and stewards.html
md_files = sorted(base_dir.glob("*.md"))
html_file = base_dir / "stewards.html"


def record(fp: Path, orig: str, new: str):
    try:
        rel = str(fp.relative_to(base_dir))
    except Exception:
        rel = str(fp)
    changed.append((rel, orig, new))


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
        # normalize to leading /limicelia/stewards/...
        if target.startswith("/stewards/"):
            doc = "/limicelia" + target
        elif target.startswith("stewards/"):
            doc = "/limicelia/" + target
        elif target.startswith("/limicelia/stewards/"):
            doc = target
        else:
            doc = "/" + target.lstrip("/")
        new = f"viewer.html?doc={doc}"
        record(fp, target, new)
        return f"[{label}]({new})"

    text = md_link_re.sub(md_link_repl, text)

    # 2) Convert bare .md links anywhere pointing to stewards -> viewer.html?doc=...
    bare_md_re = re.compile(r'(?<!["\'])(\/?(?:limicelia\/)?stewards\/[^\s\)\]\},"\']+\.md)', flags=re.IGNORECASE)

    def bare_md_repl(m):
        target = m.group(1)
        if target.startswith("/stewards/"):
            doc = "/limicelia" + target
        elif target.startswith("stewards/"):
            doc = "/limicelia/" + target
        elif target.startswith("/limicelia/stewards/"):
            doc = target
        else:
            doc = "/" + target.lstrip("/")
        new = f"viewer.html?doc={doc}"
        record(fp, target, new)
        return new

    text = bare_md_re.sub(bare_md_repl, text)

    # 3) Convert absolute site-directory URLs that point to the stewards dir to stewards.html
    site_dir_re = re.compile(r'(https?://[^\s"\'\)]+?/(?:limicelia/)?stewards)(/)?(?=[\s"\')\]])', flags=re.IGNORECASE)

    def site_dir_repl(m):
        orig_url = m.group(0)
        base = m.group(1)
        new = base.rstrip("/") + "/stewards.html"
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


def normalize_stewards_html(fp: Path):
    if not fp.exists():
        print(f"✗ File not found: {fp.name}")
        return False
    text = fp.read_text(encoding="utf-8")
    orig = text

    # Convert anchors href="/limicelia/stewards/xxx.md" or href="/stewards/xxx.md" to viewer.html?doc=/limicelia/stewards/xxx.md
    a_re = re.compile(
        r'<a\b([^>]*)\bhref=(["\'])(\/?(?:limicelia\/)?stewards\/[^"\']+)(["\'])([^>]*)>(.*?)</a>',
        flags=re.IGNORECASE | re.DOTALL,
    )

    def a_repl(m):
        before_attrs = (m.group(1) or "") + " " + (m.group(5) or "")
        href_target = m.group(3)
        inner = m.group(6)
        # normalize path
        if href_target.startswith("/stewards/"):
            doc = "/limicelia" + href_target
        elif href_target.startswith("stewards/"):
            doc = "/limicelia/" + href_target
        elif href_target.startswith("/limicelia/stewards/"):
            doc = href_target
        else:
            doc = "/" + href_target.lstrip("/")
        new_href = f'href="viewer.html?doc={doc}"'
        # ensure class="doc-item"
        attrs = ensure_doc_item_attr(before_attrs)
        record(fp, href_target, f"viewer.html?doc={doc}")
        return f'<a {new_href} {attrs}>{inner}</a>'

    # small helper to ensure class
    def ensure_doc_item_attr(attrs: str) -> str:
        attrs = attrs or ""
        attrs = re.sub(r'\s+', ' ', attrs).strip()
        m = re.search(r'\bclass\s*=\s*"([^"]*)"', attrs, flags=re.IGNORECASE)
        if m:
            classes = m.group(1)
            if "doc-item" not in classes.split():
                classes = (classes + " doc-item").strip()
            attrs = re.sub(r'\bclass\s*=\s*"[^"]*"', f'class="{classes}"', attrs, flags=re.IGNORECASE)
        else:
            if attrs:
                attrs = attrs + ' class="doc-item"'
            else:
                attrs = 'class="doc-item"'
        return re.sub(r'\s+', ' ', attrs).strip()

    text = a_re.sub(a_repl, text)

    # Normalize existing viewer.html?doc= anchors to ensure class
    viewer_re = re.compile(r'<a\b([^>]*)\bhref=(["\'])viewer\.html\?doc=(\/(?:limicelia\/)?stewards\/[^"\']+)\2([^>]*)>(.*?)</a>', flags=re.IGNORECASE | re.DOTALL)

    def viewer_repl(m):
        before = (m.group(1) or "") + " " + (m.group(4) or "")
        doc = m.group(3)
        inner = m.group(5)
        attrs = ensure_doc_item_attr(before)
        record(fp, f"viewer.html?doc={doc}", f"viewer.html?doc={doc} (ensured doc-item)")
        return f'<a href="viewer.html?doc={doc}" {attrs}>{inner}</a>'

    text = viewer_re.sub(viewer_repl, text)

    if text != orig:
        fp.write_text(text, encoding="utf-8")
        print(f"✓ Updated {fp.name}")
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
    updated_count = 0
    # normalize all md files
    for md in md_files:
        if normalize_md_file(md):
            updated_count += 1

    # normalize stewards.html anchors
    if normalize_stewards_html(html_file):
        updated_count += 1

    print("=" * 60)
    print(f"Complete! Updated {updated_count} of {len(md_files) + 1} files.")
    write_report()


if __name__ == "__main__":
    main()