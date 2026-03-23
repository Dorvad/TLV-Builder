#!/usr/bin/env python3
"""
TLV Builder — Asset Organizer
==============================
Run this after extracting Mobile_game.rar to ./raw_assets/

Usage:
    python3 scripts/organize_assets.py --source ./raw_assets --output ./assets

It will:
1. Recursively scan the source folder
2. Classify files by type and content
3. Copy them into a clean organized structure
4. Generate an asset_manifest.json for use by the game
5. Write ASSET_REPORT.md documenting decisions
"""

import os
import sys
import shutil
import json
import hashlib
from pathlib import Path
from collections import defaultdict

SOURCE_DIR = Path(sys.argv[sys.argv.index('--source')+1]) if '--source' in sys.argv else Path('./raw_assets')
OUTPUT_DIR = Path(sys.argv[sys.argv.index('--output')+1]) if '--output' in sys.argv else Path('./assets')

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif'}
AUDIO_EXTS = {'.wav', '.mp3', '.ogg', '.flac'}
DATA_EXTS  = {'.json', '.txt', '.csv', '.xml'}

# Category keywords → folder mapping
CATEGORY_RULES = [
    (['tile_', 'ground', 'terrain', 'grass', 'sand', 'road', 'path', 'sidewalk'],  'tiles'),
    (['building', 'house', 'shop', 'tower', 'block', 'loft', 'bank', 'museum',
      'park', 'plaza', 'promenade', 'cafe', 'falafel', 'police'],                  'buildings'),
    (['ui_', 'icon', 'button', 'hud', 'frame', 'cursor', 'arrow'],                 'ui'),
    (['prop', 'tree', 'lamp', 'bench', 'fountain', 'sign', 'fence', 'car'],        'props'),
    (['spritesheet', 'atlas', 'sheet', 'strip', 'export'],                         'spritesheets'),
    (['wolf', 'boar', 'stag', 'badger', 'critter', 'animal'],                      'unused_medieval_critters'),
    (['iso_tile', 'isometric'],                                                     'iso_tilesets'),
]

def classify(name: str) -> str:
    lower = name.lower()
    for keywords, folder in CATEGORY_RULES:
        if any(k in lower for k in keywords):
            return folder
    return 'misc'

def file_hash(path: Path) -> str:
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    if not SOURCE_DIR.exists():
        print(f"❌  Source directory '{SOURCE_DIR}' not found.")
        print("    Extract Mobile_game.rar to ./raw_assets/ first.")
        sys.exit(1)

    print(f"📂  Scanning {SOURCE_DIR}...")
    all_files = list(SOURCE_DIR.rglob('*'))
    image_files = [f for f in all_files if f.is_file() and f.suffix.lower() in IMAGE_EXTS]
    audio_files = [f for f in all_files if f.is_file() and f.suffix.lower() in AUDIO_EXTS]
    data_files  = [f for f in all_files if f.is_file() and f.suffix.lower() in DATA_EXTS]

    print(f"   Found {len(image_files)} images, {len(audio_files)} audio, {len(data_files)} data files")

    # Dedup check
    seen_hashes = {}
    duplicates = []
    unique_images = []
    for f in image_files:
        h = file_hash(f)
        if h in seen_hashes:
            duplicates.append((f, seen_hashes[h]))
        else:
            seen_hashes[h] = f
            unique_images.append(f)

    print(f"   {len(duplicates)} duplicate images detected and skipped")

    # Copy organized
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = defaultdict(list)
    counters = defaultdict(int)

    for f in unique_images:
        cat = classify(f.name)
        dest_dir = OUTPUT_DIR / cat
        dest_dir.mkdir(parents=True, exist_ok=True)
        # Normalize name: lowercase, spaces→underscores
        clean_name = f.name.lower().replace(' ', '_')
        dest = dest_dir / clean_name
        # Avoid collision
        if dest.exists():
            stem, suf = f.stem, f.suffix
            counters[cat] += 1
            clean_name = f"{stem.lower()}_{counters[cat]}{suf.lower()}"
            dest = dest_dir / clean_name
        shutil.copy2(f, dest)
        manifest[cat].append({
            'file': str(dest.relative_to(OUTPUT_DIR)),
            'originalName': f.name,
            'originalPath': str(f.relative_to(SOURCE_DIR)),
        })

    for f in audio_files:
        dest_dir = OUTPUT_DIR / 'audio'
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f.name.lower().replace(' ', '_')
        shutil.copy2(f, dest)
        manifest['audio'].append({'file': str(dest.relative_to(OUTPUT_DIR))})

    # Write manifest
    manifest_path = OUTPUT_DIR / 'asset_manifest.json'
    with open(manifest_path, 'w') as fp:
        json.dump(dict(manifest), fp, indent=2)
    print(f"✅  Manifest written to {manifest_path}")

    # Write report
    report_lines = [
        "# TLV Builder — Asset Report",
        "",
        f"**Source:** `{SOURCE_DIR}`  ",
        f"**Output:** `{OUTPUT_DIR}`  ",
        "",
        "## Summary",
        "",
        f"| Category | Count |",
        f"|----------|-------|",
    ]
    for cat, items in manifest.items():
        report_lines.append(f"| {cat} | {len(items)} |")
    report_lines += [
        "",
        f"**Total images processed:** {len(unique_images)}  ",
        f"**Duplicates skipped:** {len(duplicates)}  ",
        "",
        "## Asset Source Inventory",
        "",
        "The RAR archive contained three main asset packs:",
        "",
        "### 1. Isometric Tileset (`isometric tileset/`)",
        "- 115 separated tile images (`tile_000.png` – `tile_114.png`)",
        "- One spritesheet (`spritesheet.png`)",
        "- **Usability:** HIGH — clean isometric ground tiles, suitable for terrain",
        "- **Mapping:** → `assets/iso_tilesets/`",
        "",
        "### 2. Isometric Jumpstart Pack (`isometric_jumpstart_v230311/`)",
        "- Cover image, export sheet, scene previews",
        "- **Usability:** MEDIUM — reference/preview images showing tileset usage",
        "- **Mapping:** → `assets/spritesheets/`",
        "",
        "### 3. Isoverse Medieval Outdoors Free",
        "- One large spritesheet (`Assets free version.png`)",
        "- **Usability:** MEDIUM — medieval theme, not directly TLV-appropriate",
        "- **Mapping:** → `assets/misc/` (usable as texture reference)",
        "",
        "### 4. Critters Pack (`critters/`)",
        "- Wolf, boar, stag, badger animations in 4 directions",
        "- **Usability:** LOW for TLV Builder — medieval/nature theme",
        "- **Mapping:** → `assets/unused_medieval_critters/` (preserved, not wired)",
        "",
        "### 5. AI-Generated Road/Sidewalk Tiles",
        "- 2 JPEG files with Gemini-generated isometric road/sidewalk tiles",
        "- **Usability:** MEDIUM — could be used for road tiles",
        "- **Mapping:** → `assets/tiles/`",
        "",
        "## Asset Decision Log",
        "",
        "Since this game version uses procedural canvas rendering, extracted assets",
        "are organized for future integration. To wire them in:",
        "",
        "1. Load `assets/iso_tilesets/` tiles for ground rendering in `renderFrame()`",
        "2. Replace `drawIsoBox()` with sprite-based rendering using building sprites",
        "3. Use `assets/tiles/` road images for optional road tile type",
        "4. Discard `unused_medieval_critters/` — incompatible with TLV theme",
        "",
        "## How to Re-Run",
        "",
        "```bash",
        "# 1. Extract the RAR",
        "unrar x Mobile_game.rar raw_assets/",
        "# or: 7z x Mobile_game.rar -oraw_assets/",
        "",
        "# 2. Run organizer",
        "python3 scripts/organize_assets.py --source ./raw_assets --output ./assets",
        "```",
    ]

    report_path = Path('docs/ASSET_REPORT.md')
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w') as fp:
        fp.write('\n'.join(report_lines))
    print(f"📋  Asset report written to {report_path}")
    print("✨  Done.")

if __name__ == '__main__':
    main()
