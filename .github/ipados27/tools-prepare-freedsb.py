#!/usr/bin/env python3
"""
Restore locked FreeBSD source for Ath12kWifi driver.
"""
import sys
import subprocess
from pathlib import Path

def main(device_root: Path):
    freedsb_dir = device_root / "drivers" / "Ath12kWifi" / "deps" / "freedsb"
    if not freedsb_dir.exists():
        print(f"FreeDSB dir not found at {freedsb_dir}")
        return
    
    # Check if it's already initialized
    if (freedsb_dir / ".git").exists():
        try:
            # Try to fetch and reset to locked commit
            subprocess.run(["git", "fetch", "origin"], cwd=freedsb_dir, check=True, capture_output=True)
            # The locked commit should be in a lock file or known
            lock_file = freedsb_dir / "COMMIT"
            if lock_file.exists():
                commit = lock_file.read_text().strip()
                subprocess.run(["git", "reset", "--hard", commit], cwd=freedsb_dir, check=True)
                print(f"Restored FreeDSB to {commit}")
            else:
                # Try to find commit from parent repo
                print("No COMMIT lock file, FreeDSB may already be at correct revision")
        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")
    else:
        print("FreeDSB not initialized as git repo, may need submodule init")
    
    print("tools-prepare-freedsb.py completed")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: tools-prepare-freedsb.py <device_root>")
        sys.exit(1)
    main(Path(sys.argv[1]))
