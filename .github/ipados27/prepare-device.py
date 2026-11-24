#!/usr/bin/env python3
"""
Add QcomGeniSpi to iPadOS 27 components and fix sheng-startup-failure-log.patch anchor.
"""
import sys
import re
from pathlib import Path

def main(device_root: Path):
    # 1. Add QcomGeniSpi to iPadOS 27 component list
    config_dir = device_root / "configs"
    for config_file in config_dir.glob("*.toml"):
        content = config_file.read_text()
        if 'ios_version = "27"' in content or 'ios_version = 27' in content:
            # Find the components list and add QcomGeniSpi
            if 'QcomGeniSpi' not in content:
                # Add to components array after existing SPI entries
                content = re.sub(
                    r'(components\s*=\s*\[[^\]]*)',
                    r'\1, "QcomGeniSpi"',
                    content,
                    count=1
                )
                config_file.write_text(content)
                print(f"Added QcomGeniSpi to {config_file}")
    
    # 2. Fix sheng-startup-failure-log.patch anchor if it exists
    patch_file = device_root / "patches" / "sheng-startup-failure-log.patch"
    if patch_file.exists():
        content = patch_file.read_text()
        # Fix the anchor line that was causing failures
        if 'platform/apple/startup.c' in content and 'platform/apple/startup.c.orig' not in content:
            content = content.replace(
                '--- a/platform/apple/startup.c',
                '--- a/platform/apple/startup.c.orig'
            ).replace(
                '+++ b/platform/apple/startup.c',
                '+++ b/platform/apple/startup.c'
            )
            patch_file.write_text(content)
            print(f"Fixed anchor in {patch_file}")
    
    print("prepare-device.py completed")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: prepare-device.py <device_root>")
        sys.exit(1)
    main(Path(sys.argv[1]))
