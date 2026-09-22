#!/usr/bin/env python3
"""
Find Ed Checkpoint Restoration Tool
===================================
Run this script at any time to restore the project back to the stable checkpoint state:
    python restore_checkpoint.py
"""

import sys
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CHECKPOINT_DIR = BASE_DIR / ".checkpoints" / "fallback"

def main():
    if not CHECKPOINT_DIR.exists():
        print(f"❌ Error: Fallback checkpoint directory not found at {CHECKPOINT_DIR}")
        sys.exit(1)
        
    print(f"🔄 Restoring Find Ed from checkpoint: {CHECKPOINT_DIR} ...")
    
    count = 0
    for item in CHECKPOINT_DIR.iterdir():
        dst = BASE_DIR / item.name
        if item.is_dir():
            shutil.copytree(item, dst, dirs_exist_ok=True)
            print(f"  ✓ Restored directory: {item.name}/")
        else:
            shutil.copy2(item, dst)
            print(f"  ✓ Restored file: {item.name}")
        count += 1
        
    print(f"\n✅ Successfully restored {count} items to the fallback checkpoint state.")
    print("Application is in the verified stable state.")

if __name__ == "__main__":
    main()
