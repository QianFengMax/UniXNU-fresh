#!/usr/bin/env python3
"""
Extend metal2vulkan host_memory/copied.rs cfg to include target_os = "ios"
"""
import sys
import re
from pathlib import Path

def main(unixnu_root: Path):
    # Find metal2vulkan submodule
    metal2vulkan_dir = unixnu_root / "metal2vulkan"
    if not metal2vulkan_dir.exists():
        # Check common submodule locations
        for p in [unixnu_root / "vendor" / "metal2vulkan", unixnu_root / "deps" / "metal2vulkan"]:
            if p.exists():
                metal2vulkan_dir = p
                break
    
    if not metal2vulkan_dir.exists():
        print("metal2vulkan not found, skipping")
        return
    
    # Target files: host_memory.rs and copied.rs
    for filename in ["host_memory.rs", "copied.rs"]:
        for filepath in metal2vulkan_dir.rglob(filename):
            content = filepath.read_text()
            
            # Look for cfg(target_os = "macos") and add ios
            pattern = r'#\[cfg\(target_os = "macos"\)\]'
            if re.search(pattern, content):
                new_content = re.sub(
                    pattern,
                    '#[cfg(any(target_os = "macos", target_os = "ios"))]',
                    content
                )
                if new_content != content:
                    filepath.write_text(new_content)
                    print(f"Updated cfg in {filepath}")
            
            # Also check for cfg(target_os = "macos") without quotes
            pattern2 = r'#\[cfg\(target_os = macos\)\]'
            if re.search(pattern2, content):
                new_content = re.sub(
                    pattern2,
                    '#[cfg(any(target_os = "macos", target_os = "ios"))]',
                    content
                )
                if new_content != content:
                    filepath.write_text(new_content)
                    print(f"Updated cfg (no quotes) in {filepath}")
    
    print("prepare-translator.py completed")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: prepare-translator.py <unixnu_root>")
        sys.exit(1)
    main(Path(sys.argv[1]))
