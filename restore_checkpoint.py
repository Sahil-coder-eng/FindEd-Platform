#!/usr/bin/env python3
"""
Find Ed Checkpoint Restoration Tool
=====================================
Restore any saved checkpoint back into the project directory.

Usage:
    python restore_checkpoint.py               # restores 'fallback' (original stable)
    python restore_checkpoint.py chaos-mode    # restores 'chaos-mode' checkpoint
    python restore_checkpoint.py --list        # list all available checkpoints
"""

import sys
import shutil
from pathlib import Path

BASE_DIR    = Path(__file__).resolve().parent
CHECKPOINTS = BASE_DIR / ".checkpoints"

def list_checkpoints():
    if not CHECKPOINTS.exists():
        print("No checkpoints found.")
        return
    names = [d.name for d in CHECKPOINTS.iterdir() if d.is_dir()]
    if not names:
        print("No checkpoints found.")
    else:
        print("Available checkpoints:")
        for n in sorted(names):
            print(f"  - {n}")

def restore(name: str):
    checkpoint_dir = CHECKPOINTS / name
    if not checkpoint_dir.exists():
        print(f"ERROR: Checkpoint '{name}' not found at {checkpoint_dir}")
        print("Run with --list to see available checkpoints.")
        sys.exit(1)

    print(f"Restoring from checkpoint: {name} ...")
    count = 0
    for item in checkpoint_dir.iterdir():
        dst = BASE_DIR / item.name
        if item.is_dir():
            shutil.copytree(item, dst, dirs_exist_ok=True)
            print(f"  [OK] Restored directory: {item.name}/")
        else:
            shutil.copy2(item, dst)
            print(f"  [OK] Restored file: {item.name}")
        count += 1

    print(f"\nSuccessfully restored {count} items from checkpoint '{name}'.")

def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "fallback"
    if arg == "--list":
        list_checkpoints()
    else:
        restore(arg)

if __name__ == "__main__":
    main()
