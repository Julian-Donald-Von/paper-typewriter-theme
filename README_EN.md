> 中文版（Chinese）：[README.md](README.md)

# Paper Typewriter

**A vintage typewriter paper-texture theme for Typora** — aged paper grain that scrolls 1:1 with your text and parallaxes with the cursor, Courier-style typewriter fonts + Zhuque Fangsong, light/dark dual modes, eye-friendly warm tones.

**[▶ Live Demo](https://julian-donald-von.github.io/paper-typewriter-theme/demo/demo.html)** ｜ **[Download Theme](https://github.com/Julian-Donald-Von/paper-typewriter-theme/archive/refs/heads/theme-source.zip)** ｜ [Installation](#1-quick-start)

| Light | Dark |
|:---:|:---:|
| ![Light preview](demo/preview-light.png) | ![Dark preview](demo/preview-dark.png) |

| | |
|---|---|
| **Paper grain** | Pre-baked paper fiber (feTurbulence + feDiffuseLighting) + neutral grain + four-edge vignette, with zero paper-color drift (error 0.5/255) |
| **Scroll & parallax** | Paper scrolls 1:1 with text; optional cursor parallax (CDP injection, no modification to Typora itself) |
| **Fonts** | Courier Prime / Zhuque Fangsong / TeX Gyre Cursor / Commit Mono / Patrick Hand / Zen Old Mincho / Gowun Batang, all bundled locally under SIL OFL |
| **Eye care** | Warm paper `#f1ead8` + warm ink `#443d33`, body contrast 8.92:1, line-height 1.8, texture does not change effective contrast |
| **Compatibility** | Typewriter mode (last line centered) · Focus mode · Source mode · Export PDF (auto-switches to white paper / black ink) · all official UI variables |
| **Size** | Theme core 9.2MB (18 woff2 subsets bundled, works offline) |

> The demo is a **single self-contained file** (CSS and fonts inlined, 2.3MB) — view online or double-click after download. Generated from `demo/demo.md` by `tools/build_demo.py`.

---

## 1. Quick Start

1. Copy the three items — **`paper-typewriter.css`, `paper-typewriter.meta.json`, and `paper-typewriter/`** — into your Typora theme folder:
   - Windows: `%APPDATA%\Typora\themes\`
   - macOS: `~/Library/Application Support/abnerworks.Typora/themes/`
   - Open it via: Typora → Preferences → Appearance → Open Theme Folder
2. Restart Typora (or switch themes once), then menu **Themes → Paper Typewriter**.

> Keep the sibling structure (css at themes root, assets in `paper-typewriter/` subfolder), otherwise fonts and paper grain won't load.

### See it in action

- Open `demo/demo.md` in Typora (covers all typographic elements);
- Or open `demo/demo.html` directly in a browser: **single self-contained file** (online: <https://julian-donald-von.github.io/paper-typewriter-theme/demo/demo.html>) (CSS and fonts inlined as data URIs, 2.3MB), double-click to view, no external files needed; generated from `demo/demo.md` by `tools/build_demo.py` (pymdown extensions; `~~strikethrough~~` / `==highlight==` / task lists / front matter restored to Typora semantics; math degrades to monospace).

---

## 2. Directory Structure

```
paper-typewriter-package/
├─ paper-typewriter.css          # Theme styles (single file, includes dark media query)
├─ paper-typewriter.meta.json    # Theme metadata (name/author/tags)
├─ paper-typewriter/
│  ├─ fonts/                     # 18 woff2 subsets (~9MB, all SIL OFL / LPPL, distributable)
│  ├─ img/                       # Pre-baked paper-fiber SVGs + neutral grain PNG
│  └─ follow/                    # "paper follows cursor" script (optional, see §5)
├─ tools/
│  └─ build_demo.py              # Generate self-contained demo.html from demo.md
├─ demo/
│  ├─ demo.md                    # Element showcase document (open in Typora)
│  ├─ demo.html                  # Self-contained static preview (2.3MB, single distributable file)
│  ├─ preview-light.png / preview-dark.png
├─ README_EN.md
├─ README.md
```

At runtime the theme only uses `paper-typewriter.css` + `paper-typewriter/`; `demo/` and `README*.md` are documentation and may be omitted.

---

## 3. Fonts

| Usage | Font | License |
|---|---|---|
| Body (Latin) | **Courier Prime** (typewriter standard, 4 styles) | SIL OFL 1.1 |
| Body (Chinese, Simplified/Traditional) | **Zhuque Fangsong** v0.212 (Republican-era "Southern Song" movable-type revival, 11472 glyphs) | SIL OFL 1.1 |
| Headings | **TeX Gyre Cursor** (faithful Courier remaster, heavier strokes, full 4 styles) + Zhuque fallback | GUST / LPPL 1.3c+ |
| Code / Math | **Commit Mono** (low-contrast geometric skeleton, mechanically stamped strokes) | SIL OFL 1.1 |
| Quotes / Footnotes (margin notes) | **Patrick Hand** (Latin handwriting) + **Zhuque Fangsong** (Chinese, same source as body) | SIL OFL 1.1 |
| Japanese | **Zen Old Mincho** (classic Mincho, Regular + SemiBold) | SIL OFL 1.1 |
| Korean | **Gowun Batang** (classical batang, Regular + Bold) | SIL OFL 1.1 |

Character-based fallback: Latin → corresponding Latin font; Simplified Chinese → Zhuque Fangsong; kana and Japan-specific glyphs → Zen Old Mincho; Korean → Gowun Batang.
Every role is a "Latin font + Zhuque Fangsong" pairing (body Courier Prime, headings TeX Gyre Cursor, code Commit Mono, margin notes Patrick Hand), so Chinese always shares one source — no inconsistent mixing.

> Font availability verified individually (glyph counts / Latin·Chinese·kana·Korean coverage): Courier Prime 246, Zhuque Fangsong 11472 (Simp/Trad), Zen Old Mincho 7452 (kana), Gowun Batang 11844 (Korean), Commit Mono 744, TeX Gyre Cursor 239, Patrick Hand 199 (Latin only).
> The previously trialed "LXGW WenKai GB" had only 1291 glyphs and incomplete Chinese coverage (margin notes would drop glyphs and fall back), so it was dropped and removed from the package.

> Regarding "Zhuque looks like a Kai (brush) style": this is a deliberate design choice, not a bug — based on Republican-era "Southern Song" movable type, with v0.212 preview intentionally softening stroke contrast, giving strokes a paused, handwritten feel. Rendering/packaging issues were ruled out by testing (correct font stack, `document.fonts.check` passes, official TTF and subset render identically).

---

## 4. Paper Grain System

Typora themes can only load CSS and cannot inject DOM, so the paper grain is entirely implemented with **pre-baked assets + pseudo-elements**:

| Layer | Pseudo-element | Asset | Blend | Role |
|---|---|---|---|---|
| Paper fiber | `#write::before` | `paper-fiber-a.svg` | `background-blend-mode: multiply` | Paper body (baked via `feTurbulence` + `feDiffuseLighting`, mean compensated to 0.968) |
| Grain | `html::before` | `grain-tile.png` | `mix-blend-mode: overlay` | Neutral grain, mean pinned at 128, zero-mean drift (no contrast loss) |
| Vignette | `html::after` | — | `box-shadow: inset` | Darken four edges, reduce glare |

- **Zero paper-color drift**: `--paper-raw` (multiply input color) × fiber mean 0.968 = effective paper color `--paper`. When changing paper color, also update `--paper-raw = --paper ÷ 0.968`.
- **Paper scrolls 1:1 with text**: the paper layer is anchored on `#write` — which sits inside Typora's real scroll container `<CONTENT>`, so it scrolls at the same speed as text, like a single sheet laid under the words.
- Dark mode uses a separately baked dark fiber (mean 0.848): on dark paper the dynamic headroom for multiply is minimal, so light-mode parameters are invisible on a dark base.

**⚠️ Three hard constraints to read before modifying the theme** (all learned the hard way):

1. **Do not add `position: relative` to `body`**. Typora's `<CONTENT>` (the editor scroll container) is `position:absolute` based on the initial containing block, while body has no in-flow content (`window.css` has `body{height:100%;overflow:hidden}`, actual height 0). Once body becomes a positioned element, `<CONTENT>` re-bases on body and collapses to 0 height — **text and paper grain both vanish**.
2. **Do not occupy `#write::after`**. Typewriter mode injects `#write:after{height:Mpx}` to push the last line to screen center (this pseudo-element is pre-set in `base-control.css` as an inline placeholder `content:"";display:block;height:0`). Using `position:absolute` on it ⇒ placeholder fails ⇒ last line sinks to the bottom.
3. **Do not extend the paper layer vertically** (`top/bottom:0`). A vertically overflowing absolutely-positioned element inflates `<CONTENT>`'s scroll height, so when you scroll to the bottom the last line is pushed off by the same distance.

---

## 5. Motion (Paper Follows Text / Paper Follows Cursor)

**① Paper follows text (pure CSS, out of the box)**: see above — the paper layer is inside the scroll container, naturally 1:1.

**② Paper follows cursor (needs the follow script, optional)**: Typora themes cannot read pointer position (official `setTheme` only loads `.css`), so `paper-typewriter/follow/` provides it:

```
follow/
├─ paper-follow.js   # pointermove → rAF → writes --paper-px/--paper-py (max displacement 26px)
├─ inject.py         # injects via Chrome DevTools Protocol, no modification to Typora core
└─ 启动随动.bat      # one-click: launch Typora with debug port + inject
```

Usage: **first fully quit Typora from the tray** (Electron's single-instance forwards launch args to the already-running instance, so the port won't open), then double-click `启动随动.bat`.

One-time setup: Typora Preferences → open advanced settings (`conf/user.json`) and add

```json
"flags": [
  ["remote-debugging-port", "9333"],
  ["remote-allow-origins", "*"]
]
```

After that, Typora launches with the port every time; run `inject.py` once more (or set it to auto-start on boot). **Without the script, the paper still scrolls 1:1 with text — visually complete**, it just doesn't track the pointer.

> Requires Python 3 + `websocket-client` (`pip install websocket-client`). Chrome 111+ WebSocket handshake requires `--remote-allow-origins`, missing it returns 403.

---

## 6. Compatibility with Typora Native Features

| Feature | Status | Notes |
|---|---|---|
| Typewriter mode (cursor centered) | ✅ tested | Last line can center: measured offset −28px (native theme baseline −24px) |
| Focus mode | ✅ tested | Focused block keeps body color; non-focused blocks and children fade to `--blur-text-color` |
| Source mode | ✅ | Monospace stack + inline-code coloring |
| Outline / Sidebar / Menu / Dialog | ✅ | All driven by official UI variables |
| Export PDF | ✅ | Print styles auto-switch to white paper / black ink, strip texture |
| Export HTML | ⚠️ | Texture and font assets are not inlined on export (true of all local-asset themes) |

Focus mode fading is handled by Typora's native mechanism (`base-control.css` uses `--blur-text-color !important` to fade children of `.md-end-block` and `li[cid]`); the theme only sets that variable to a paper-family color and adds a "block itself" fade (the official `*` rule doesn't reach bare text). **Do not invent your own `opacity` rules** (would double-fade to gray), and don't piggyback on `.typewriter-mode .md-end-block:not(.md-focus)` (Typewriter mode has no `md-focus` class, so it would fade the whole document).

---

## 7. UI Theme Variables

All of Typora's native UI (settings panel, dialogs, buttons, inputs, menus, sidebar) is driven by a set of official CSS variables. This theme defines the complete variable table in the `[COLORS]` section (light/dark dual values, all mapped to the paper palette), and adds explicit fallbacks in `[UI-VARS]` for bootstrap residual controls (`.btn-default` / `.long-btn` / `.form-control` inheritance chain).

If these variables are undefined, the UI falls back to Typora's default white background with blue buttons; in dark mode this even produces dark text on a dark background (e.g., megamenu large buttons become unreadable). Measured UI contrast: element-level 18/20 pass (2 are elements in an empty file tree), variable-level status match 20/20 pass, minimum 5.08:1.

---

## 8. Eye-Care Design

- **Warm paper `#f1ead8`**: no pure-white glare, low blue light, brightness between white paper and pea-green.
- **Warm ink `#443d33`**: not pure black, body contrast **8.92:1** (dark mode 10.51:1).
- **Line-height 1.8, column width 860px**: reduces line-tracking fatigue.
- **Zero texture drift**: grain mean pinned at 128, fiber mean compensated to 0.968, texture does not change effective contrast.
- **Dark carbon paper `#22201b` + warm gray ink `#d8cfbb`**: low-brightness warm tones at night.
- Vignette darkens the four edges, reducing page glare.

---

## 9. Customization Entry Points (search tags in CSS)

| Tag | Content |
|---|---|
| `[COLORS]` | All color variables (light + dark) + official UI variable table. Changing `--paper` requires syncing `--paper-raw = --paper ÷ 0.968` |
| `[FONTS]` | Font stacks (`--font-body` / `--font-heading` / `--font-code` / `--font-hand`) |
| `[PAPER]` | Paper layer, grain, vignette, pointer-parallax variables |
| `[LAYOUT]` | Column width, line-height, font-size |
| `[ELEMENTS]` | Headings/body/code/tables/quotes/lists/images/footnotes |
| `[UI]` | Sidebar / outline / source mode / menu / scrollbar |
| `[UI-VARS]` | Control fallbacks (buttons / inputs / modals) |
| `[PRINT]` | Printing and PDF export |

Common tweaks:

```css
/* Wider column */
#write { max-width: 980px; }
/* Slightly yellower paper (remember to also change --paper-raw = new paper ÷ 0.968) */
:root { --paper: #f3ecd6; --paper-raw: #fbf3dd; }
/* More pronounced pointer parallax (change AMP in follow/paper-follow.js) */
```

---

## 10. Verification & Re-runs

The theme ships re-runnable verification scripts (in the dev `tools/` and `follow/`, requires Python 3 + Playwright + local Chrome):

| Check | Script | Result |
|---|---|---|
| Paper color / grain presence / body contrast | `tools/verify2.py` | 9/9 (paper-color error 0.5/255) |
| Export PDF white-paper/black-ink | `tools/verify_export.py` | Primary color pure white, paper residue 0.000% |
| Typewriter last-line centering / Focus fade | `tools/ui-audit/verify_modes.py` | 6/6 |
| Paper 1:1 with text / pointer parallax / injection chain | `follow/verify_follow.py` | 5/5 |
| UI element-level / variable-level contrast | `tools/ui-audit/run_audit.py`, `verify_ui_vars.py` | 18/20, 20/20 |

Verification methodology: replicate the real Typora window (`window.html` + official CSS) in Chromium — **do not set `body.minHeight`**, otherwise it masks the real structure (body height 0, `<CONTENT>` scrolls, window doesn't scroll).

---

## 11. Known Limitations

- Pointer parallax requires external injection (Typora theme mechanism limit); without injection the paper still scrolls 1:1 with text.
- Chinese bold is browser-synthesized (Zhuque Fangsong has a single weight).
- Export HTML does not inline texture and fonts.
- Requires a fairly recent Electron (Chromium 88+); paper grain and normal layout are unaffected.

---

## 12. License

- Theme CSS: **MIT**
- Fonts: all open-source licensed (SIL OFL 1.1 / LPPL 1.3c+), redistribution with the theme is permitted; selling font files separately is a violation.

Asset sources: paper fiber and grain are self-baked by this theme (`feTurbulence` + `feDiffuseLighting`); engineering practices referenced from three official/community themes — retro-typewriter (variable partitioning structure), newsprint (@font-face packaging), github (woff2 packaging paradigm).
