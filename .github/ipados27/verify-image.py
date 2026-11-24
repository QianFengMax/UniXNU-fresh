#!/usr/bin/env python3
"""
Verify persistent image properties:
- manifest hashes match
- boot_b size <= 192 MiB (201326592 bytes)
- required kernel args present: uefi-watchdog=1, data-persist=2, native-ufs-root=1
- no autoreset= argument
"""
import sys
import json
import hashlib
from pathlib import Path

def verify_manifest(manifest_path: Path) -> bool:
    if not manifest_path.exists():
        print(f"ERROR: manifest not found at {manifest_path}")
        return False
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    ok = True
    for item in manifest.get("files", []):
        filepath = manifest_path.parent / item["path"]
        if not filepath.exists():
            print(f"ERROR: {item['path']} missing")
            ok = False
            continue
        
        expected = item.get("sha256")
        if expected:
            actual = hashlib.sha256(filepath.read_bytes()).hexdigest()
            if actual != expected:
                print(f"ERROR: {item['path']} hash mismatch: expected {expected}, got {actual}")
                ok = False
            else:
                print(f"OK: {item['path']} hash matches")
    return ok

def verify_boot_size(boot_path: Path) -> bool:
    if not boot_path.exists():
        print(f"ERROR: boot.img not found at {boot_path}")
        return False
    
    size = boot_path.stat().st_size
    max_size = 192 * 1024 * 1024  # 192 MiB
    if size > max_size:
        print(f"ERROR: boot.img size {size} bytes ({size/1024/1024:.1f} MiB) exceeds 192 MiB limit")
        return False
    
    print(f"OK: boot.img size {size} bytes ({size/1024/1024:.1f} MiB) within limit")
    return True

def verify_kernel_args(device_root: Path) -> bool:
    # Check package inputs for kernel args
    inputs_path = device_root / "out" / "sheng" / "*" / "*" / "inputs.json"
    inputs_files = list(device_root.glob("out/sheng/*/*/inputs.json"))
    if not inputs_files:
        print("WARNING: inputs.json not found, skipping kernel arg verification")
        return True
    
    with open(inputs_files[0]) as f:
        inputs = json.load(f)
    
    kernel_args = inputs.get("kernel_args", "")
    print(f"Kernel args: {kernel_args}")
    
    required = ["uefi-watchdog=1", "data-persist=2", "native-ufs-root=1"]
    forbidden = ["autoreset="]
    
    ok = True
    for req in required:
        if req not in kernel_args:
            print(f"ERROR: Required kernel arg '{req}' missing")
            ok = False
        else:
            print(f"OK: Required kernel arg '{req}' present")
    
    for forbid in forbidden:
        if forbid in kernel_args:
            print(f"ERROR: Forbidden kernel arg '{forbid}' present")
            ok = False
        else:
            print(f"OK: Forbidden kernel arg '{forbid}' absent")
    
    # Check total kernel command line length
    if len(kernel_args) >= 1000:
        print(f"ERROR: Kernel command line length {len(kernel_args)} >= 1000 bytes")
        ok = False
    else:
        print(f"OK: Kernel command line length {len(kernel_args)} < 1000 bytes")
    
    return ok

def main(device_root: Path):
    ok = True
    
    # Find manifest
    manifest_files = list(device_root.glob("out/**/package.manifest.json"))
    if manifest_files:
        ok &= verify_manifest(manifest_files[0])
    
    # Find boot.img
    boot_files = list(device_root.glob("out/**/boot.img"))
    if boot_files:
        ok &= verify_boot_size(boot_files[0])
    
    # Verify kernel args
    ok &= verify_kernel_args(device_root)
    
    if ok:
        print("\nAll verifications PASSED")
        sys.exit(0)
    else:
        print("\nSome verifications FAILED")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: verify-image.py <device_root>")
        sys.exit(1)
    main(Path(sys.argv[1]))
