#!/usr/bin/env python3
"""
Wrap Adreno740 iokit_physical_descriptor_close_notify and RamBlock ml_static_mfree_prepare
in #if XNU_TARGET_OS_OSX guards for iOS compatibility.
"""
import sys
import re
from pathlib import Path

def wrap_ios_guard(filepath: Path, func_name: str):
    content = filepath.read_text()
    if func_name not in content:
        return False
    
    # Find the function and wrap it in #if XNU_TARGET_OS_OSX ... #endif
    # Pattern: function definition
    pattern = rf'(^\s*(?:static\s+)?(?:inline\s+)?\w+\s+{re.escape(func_name)}\s*\([^)]*\)\s*\{)'
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        return False
    
    start = match.start()
    # Find the matching closing brace
    brace_count = 0
    in_function = False
    end = start
    for i, ch in enumerate(content[start:], start):
        if ch == '{':
            brace_count += 1
            in_function = True
        elif ch == '}':
            brace_count -= 1
            if in_function and brace_count == 0:
                end = i + 1
                break
    
    if brace_count != 0:
        return False
    
    func_body = content[start:end]
    wrapped = f"#if XNU_TARGET_OS_OSX\n{func_body}#endif"
    new_content = content[:start] + wrapped + content[end:]
    filepath.write_text(new_content)
    return True

def main(device_root: Path):
    # 1. Adreno740 - iokit_physical_descriptor_close_notify
    adreno_files = list(device_root.rglob("*Adreno*740*.c")) + list(device_root.rglob("*adreno*740*.c"))
    for f in adreno_files:
        if wrap_ios_guard(f, "iokit_physical_descriptor_close_notify"):
            print(f"Wrapped iokit_physical_descriptor_close_notify in {f}")
    
    # 2. RamBlock - ml_static_mfree_prepare
    ram_files = list(device_root.rglob("*RamBlock*.c")) + list(device_root.rglob("*ram*block*.c"))
    for f in ram_files:
        if wrap_ios_guard(f, "ml_static_mfree_prepare"):
            print(f"Wrapped ml_static_mfree_prepare in {f}")
    
    print("prepare-drivers.py completed")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: prepare-drivers.py <device_root>")
        sys.exit(1)
    main(Path(sys.argv[1]))
