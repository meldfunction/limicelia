import re
from pathlib import Path

# Define ALL files to update, including the HTML file
files_to_update = [
    'stewards.html',
    'strategic-essays.md',
    'private-collaboration-agreement.md',
    'present-of-work-canvas.md',
    'limicelia-strategy-canvases.md',
    'co-steward-constitution.md',
    '00-master-index.md'
]

def update_links_in_file(filepath):
    """Update all /stewards/ links to /limicelia/stewards/ in a file."""
    
    # Read the entire file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
        return False
    except Exception as e:
        print(f"✗ Error reading {filepath}: {e}")
        return False
    
    # Store original content for comparison
    original_content = content
    
    # Pattern to match links like href="/stewards/ or (/stewards/
    # This catches both HTML attributes and markdown links
    pattern = r'(href="|[\(])/stewards/'
    
    def replacement(match):
        """Replace while preserving the prefix (href=" or ()"""
        return match.group(1) + '/limicelia/stewards/'
    
    # Replace all occurrences
    updated_content = re.sub(pattern, replacement, content)
    
    # Check if any changes were made
    if updated_content != original_content:
        try:
            # Write back to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            # Count replacements
            count = len(re.findall(pattern, original_content))
            print(f"✓ Updated {filepath}: {count} links changed")
            return True
        except Exception as e:
            print(f"✗ Error writing {filepath}: {e}")
            return False
    else:
        print(f"- No changes needed for {filepath}")
        return False

def main():
    """Process all files in the list."""
    print("Starting link updates...")
    print("Pattern: /stewards/ → /limicelia/stewards/")
    print("=" * 70)
    
    total_updated = 0
    total_files = len(files_to_update)
    
    for filename in files_to_update:
        filepath = Path(filename)
        if update_links_in_file(filepath):
            total_updated += 1
    
    print("=" * 70)
    print(f"\nComplete! Updated {total_updated} of {total_files} files.")
    
    if total_updated > 0:
        print("\n✓ All links have been updated to /limicelia/stewards/")
    else:
        print("\n- No files needed updating (already correct or files not found)")

if __name__ == "__main__":
    main()