# 🌆 TLV Builder

A mobile-first isometric city builder set in Tel Aviv.  
Build your district — Bauhaus blocks, cafes, falafel stands, museums and landmarks.  
Balance funds, happiness, tourism and upkeep. Grow until Dizengoff Square rises.

**[▶️ Play Live →](https://YOUR_USERNAME.github.io/tlv-builder/)**

---

## Features

- **Isometric canvas renderer** — procedural 3-face pixel art, painter's-algorithm sorted
- **Full city simulation** — 1-second tick with income, upkeep, net income
- **13 buildings** across 5 categories: Residential, Commercial, Culture, Services, Landmarks
- **Adjacency & synergy system** — placement quality hints + income multipliers
- **4 population archetypes** — Hipsters, High-Class, Locals, Dense
- **Progression & unlocks** — 15 milestones, 8 unlockable buildings
- **District identity** — dynamic label system (Hipster District, Global City, etc.)
- **Mobile-first UX** — drag to pan, tap to select, bottom build drawer, confirm/cancel placement
- **Bulldoze tool** — 40% refund on demolition
- **Zero dependencies** — single HTML file, no build step, no CDN, no backend

---

## Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Runtime | Vanilla JS + Canvas 2D | Zero build, instant load, GitHub Pages compatible |
| Rendering | Custom isometric renderer | No Phaser overhead for this scope |
| Fonts | Google Fonts (Syne + Space Mono) | Only external dependency |
| Deployment | GitHub Pages + Actions | Static, free, reliable |

---

## Repo Structure

```
tlv-builder/
├── index.html              ← The entire game (HTML + CSS + JS, ~65KB)
├── .github/
│   └── workflows/
│       └── deploy.yml      ← Auto-deploy to GitHub Pages on push to main
├── scripts/
│   └── organize_assets.py  ← Asset ingestion pipeline (run locally after extracting RAR)
├── docs/
│   └── ASSET_REPORT.md     ← Generated asset inventory (after running script)
└── assets/                 ← Generated after running organize_assets.py
    ├── iso_tilesets/
    ├── buildings/
    ├── tiles/
    ├── props/
    ├── ui/
    ├── spritesheets/
    ├── audio/
    ├── misc/
    └── unused_medieval_critters/
```

---

## Run Locally

No install required. Just open the file:

```bash
# Option 1 — direct file open
open index.html

# Option 2 — local server (avoids any CORS issues with future assets)
python3 -m http.server 8080
# then visit http://localhost:8080
```

---

## Deploy to GitHub Pages

### Automatic (recommended)

1. Create a new GitHub repository (e.g. `tlv-builder`)
2. Push this repo to it:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/tlv-builder.git
   git push -u origin main
   ```
3. In GitHub → Settings → Pages → Source: **GitHub Actions**
4. The workflow in `.github/workflows/deploy.yml` will run automatically
5. Your game will be live at `https://YOUR_USERNAME.github.io/tlv-builder/`

### Manual (one-time)

In GitHub → Settings → Pages → Source: **Deploy from branch** → `main` → `/ (root)`.  
The `index.html` at the root will be served directly.

---

## Asset Pipeline (for future sprite integration)

The game currently uses procedural canvas rendering.  
The supplied `Mobile_game.rar` contains:

- **115 isometric ground tiles** — ready to replace procedural terrain
- **Isoverse medieval pack** — texture reference (not TLV-themed)
- **AI-generated road/sidewalk tiles** — usable as road tile type
- **Critter animations** — preserved but not used (medieval theme)

To integrate sprites:

```bash
# 1. Extract the RAR (requires unrar or 7z)
unrar x Mobile_game.rar raw_assets/
# or
7z x Mobile_game.rar -oraw_assets/

# 2. Run the organizer
python3 scripts/organize_assets.py --source ./raw_assets --output ./assets

# 3. Check docs/ASSET_REPORT.md for the inventory
```

Then in `index.html`, replace `renderTileShape()` with image-based tile rendering  
using the spritesheet from `assets/iso_tilesets/spritesheet.png`.

Current repo now also supports a lightweight runtime manifest:

- `assets/asset_manifest.json` defines candidate texture paths for ground/buildings
- The game loads from manifest first, then falls back to procedural rendering if files fail
- You can run quick invariants with:
  ```bash
  node scripts/smoke_test.js
  ```

---

## Building Roster

| Building | Category | Cost | Unlock |
|----------|----------|------|--------|
| Bauhaus Block | Residential | ₪100 | From start |
| Hipster Loft | Residential | ₪140 | From start |
| Luxury Tower | Residential | ₪300 | 30 residents |
| Dense Housing | Residential | ₪70 | 5 buildings |
| Café | Commercial | ₪120 | From start |
| Falafel Stand | Commercial | ₪80 | From start |
| Bank | Commercial | ₪250 | ₪500 earned |
| Mall | Commercial | ₪350 | 50 residents |
| Park | Culture | ₪90 | From start |
| Museum | Culture | ₪220 | 3 buildings |
| Police Station | Services | ₪180 | 4 buildings |
| Dizengoff Square | Landmark | ₪220 | 50 residents |
| Azrieli Towers | Landmark | ₪600 | ₪2000 earned |
| Beach Promenade | Landmark | ₪280 | 50 tourism |

---

## Economy Model

```
totalIncome = residentialIncome + commercialIncome + tourismIncome
  residentialIncome = Σ (population × popRate)  [hipster=1.8, highclass=3.5, locals=1.5, dense=0.8]
  commercialIncome  = Σ (baseIncome × adjacencyMultiplier)
  tourismIncome     = tourismScore × 0.5 × happinessFactor

netIncome = totalIncome - totalUpkeep
funds += netIncome  (each second)
```

Happiness (0–100) starts at 60, modified by building placements and synergies.  
Low happiness reduces tourism income. Funds below zero reduces happiness.

---

## Synergy System (radius = 2 tiles Manhattan distance)

| Building | Synergises With | Penalised By |
|----------|----------------|--------------|
| Hipster Loft | Café, Park, Museum, Dizengoff | Bank |
| Luxury Tower | Museum, Bank, Dizengoff, Park | Falafel Stand, Dense Housing |
| Café | Hipster Loft, Park, Bauhaus | — |
| Museum | Dizengoff, Park, Luxury, Hipster | Dense Housing |
| Bank | Luxury Tower, Café | Hipster Loft |

---

## Roadmap / Future Iterations

- [ ] Sprite integration from extracted asset pack
- [ ] Sound effects (place, income tick, milestone)
- [ ] Road/path tiles for street layout
- [ ] Save/load to `localStorage`
- [ ] Day/night cycle visual mode
- [ ] Population animations (pedestrians)
- [ ] Seasonal events (White Night TLV, Yom Kippur bike day)

---

## Credits

Built by Dor Vaadia as a portfolio demo.  
Asset packs: Isometric Tileset (itch.io), Isoverse Medieval Free, critter sprites.  
Font: Syne + Space Mono via Google Fonts.  
No frameworks. No servers. Just a city.
