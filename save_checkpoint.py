#!/usr/bin/env python3
"""
Find Ed - Save Checkpoint Tool
================================
Run this script to save the CURRENT state of the project as a named checkpoint.

Usage:
    python save_checkpoint.py              # auto-names with timestamp
    python save_checkpoint.py my-name     # saves as .checkpoints/my-name/

Restore any checkpoint with:
    python restore_checkpoint.py <checkpoint-name>
    python restore_checkpoint.py           # restores 'fallback'
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR       = Path(__file__).resolve().parent
CHECKPOINTS    = BASE_DIR / ".checkpoints"

# Files / dirs to include in checkpoint
INCLUDE = [
    "app.py",
    "index.html",
    "README.md",
    "requirements.txt",
    "calculations",
    "components",
    "data",
    "research",
    "tests",
    "server.py",
    "fined_logo.jpg",
    "fined_logo_transparent.png",
]

def save(name: str):
    dest = CHECKPOINTS / name
    if dest.exists():
        answer = input(f"  Checkpoint '{name}' already exists. Overwrite? [y/N]: ").strip().lower()
        if answer != "y":
            print("  Aborted.")
            return
        shutil.rmtree(dest)

    dest.mkdir(parents=True, exist_ok=True)
    count = 0
    for item_name in INCLUDE:
        src = BASE_DIR / item_name
        if not src.exists():
            continue
        if src.is_dir():
            shutil.copytree(src, dest / item_name, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dest / item_name)
        print(f"  [OK] {item_name}")
        count += 1

    print(f"\nCheckpoint '{name}' saved with {count} items -> .checkpoints/{name}/")

def main():
    name = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("checkpoint-%Y%m%d-%H%M%S")
    print(f"Saving checkpoint: {name}")
    save(name)

if __name__ == "__main__":
    main()
