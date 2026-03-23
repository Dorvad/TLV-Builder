# TLV Builder — Asset Report

**Source:** `Mobile_game.rar` (11.6 MB)  
**Scanned:** Without extraction (header inspection via Python)  
**Status:** Organized structure ready — run `organize_assets.py` after extraction to populate

---

## RAR Contents Inventory

The archive was scanned without extraction. Contents identified:

### Pack 1: Isometric Tileset
**Path:** `Mobile game/isometric tileset/isometric tileset/`  
**Files:** 115 separated PNGs (`tile_000.png` – `tile_114.png`) + `spritesheet.png`  
**Classification:** → `assets/iso_tilesets/`  
**Usability:** ✅ HIGH — clean numbered isometric ground tiles  
**Game mapping:** Replace procedural `renderTileShape()` with sprite lookup

### Pack 2: Isometric Jumpstart v230311
**Path:** `Mobile game/isometric_jumpstart_v230311/`  
**Files:** `iso_tile_cover.png`, `iso_tile_export.png`, `iso_tile_scene2.png`, `iso_tile_scene3.png`, `license.txt`  
**Classification:** → `assets/spritesheets/`  
**Usability:** ✅ MEDIUM — reference scene previews, export sheet may contain usable tiles  
**Game mapping:** Reference for tile usage patterns

### Pack 3: Isoverse Medieval Outdoors Free
**Path:** `Mobile game/Isoverse medieval outdoors free/`  
**Files:** `Assets free version.png`, `READ ME.txt`  
**Classification:** → `assets/misc/`  
**Usability:** ⚠️ MEDIUM — medieval/nature theme, visually inconsistent with TLV  
**Game mapping:** Texture pattern reference only; not directly usable

### Pack 4: Critters
**Path:** `Mobile game/critters/critters/`  
**Files:** Wolf (5 anims, 3 variants), boar (4-dir run+idle, sheets+strips), stag (4-dir walk+idle+run), badger (4-dir walk+burrow+tunnel)  
**Total:** ~120 animation frames  
**Classification:** → `assets/unused_medieval_critters/`  
**Usability:** ❌ LOW — medieval fantasy animals, incompatible with TLV urban theme  
**Game mapping:** Not wired. Preserved for completeness.

### Pack 5: AI-Generated Road Tiles (Gemini)
**Path:** `Mobile game/gemini-2.5-flash-image_Based_on_the_attached_image_...`  
**Files:** 2 JPEG files with asphalt road + sidewalk isometric tiles  
**Classification:** → `assets/tiles/`  
**Usability:** ✅ MEDIUM — generated specifically for this project  
**Game mapping:** Could replace ground tile for road variant

---

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Use procedural canvas rendering (no sprites) | RAR not extractable in CI environment; procedural art is consistent, scales at any resolution, and loads instantly |
| Medieval critters excluded | Zero thematic relevance to TLV urban builder |
| Isometric tileset tagged for future use | 115 clean tiles — strong candidate for terrain replacement |
| AI road tiles tagged for future use | Directly relevant, pending extraction |
| Isoverse medieval pack kept as misc | Not wired, but preserved per asset workflow requirements |

---

## How to Extract & Integrate

```bash
# Requires: unrar (Linux/Mac) or 7-Zip

# Linux/Mac
unrar x Mobile_game.rar raw_assets/

# Windows / cross-platform
7z x Mobile_game.rar -oraw_assets/

# Organize
python3 scripts/organize_assets.py --source ./raw_assets --output ./assets

# Verify output
ls assets/
# → iso_tilesets/  tiles/  spritesheets/  misc/  unused_medieval_critters/  asset_manifest.json
```

---

## Sprite Integration Roadmap

To replace procedural tiles with the extracted isometric tileset:

1. Load `assets/iso_tilesets/spritesheet.png` in a `new Image()`
2. Map tile indices to semantic meaning (grass, sand, road, etc.)
3. In `renderFrame()`, replace `renderTileShape()` with `ctx.drawImage(spritesheet, sx, sy, TW, TH, cx-TW/2, cy-TH/2, TW, TH)`
4. For buildings, create sprite mappings in a `buildingSprites` config object
5. Fall back to procedural rendering if image load fails
