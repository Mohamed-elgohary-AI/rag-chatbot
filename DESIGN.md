---
name: Handbook Assistant
description: A library card catalog for a handbook RAG demo; every answer is filed to numbered cards the visitor can pull and check.
colors:
  steel: "#1f2d4a"
  steel-raised: "#2c3d5f"
  steel-ink: "#f3f1ea"
  steel-ink-muted: "#c5cbd8"
  brass: "#b8924a"
  brass-light: "#ecd39d"
  catalog-red: "#b03524"
  catalog-red-dark: "#a63322"
  ground: "#f4f1ea"
  ground-dark: "#10141d"
  ground-ink: "#1d2533"
  ground-ink-dark: "#ebe8e0"
  ground-ink-muted: "#4a5462"
  ground-ink-muted-dark: "#b9bdc7"
  ground-hair: "#d8d2c4"
  ground-hair-dark: "#2c3444"
  card-stock: "#fbf9f4"
  card-stock-dark: "#e6e2d8"
  paper: "#ffffff"
  paper-dark: "#eeebe3"
  ink: "#1d2533"
  ink-muted: "#4a5462"
  ink-muted-dark: "#474f5c"
  hair: "#d8d2c4"
  hair-dark: "#c4bfb3"
  ruled-blue: "#dbe3ef"
  ruled-blue-dark: "#c7d0dd"
  highlight: "#f1e2ae"
  link: "#2c5aa0"
  focus-dark: "#8fb3ff"
  verdict-pass: "#2f6b45"
  verdict-partial: "#8a5a00"
typography:
  display:
    fontFamily: "Atkinson Hyperlegible, system-ui, sans-serif"
    fontSize: "clamp(26px, 3.4vw, 36px)"
    fontWeight: 700
    lineHeight: 1.2
  headline:
    fontFamily: "Atkinson Hyperlegible, system-ui, sans-serif"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: 1.3
  title:
    fontFamily: "Atkinson Hyperlegible, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 700
    lineHeight: 1.55
  body:
    fontFamily: "Atkinson Hyperlegible, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.55
  body-small:
    fontFamily: "Atkinson Hyperlegible, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Atkinson Hyperlegible, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 700
    lineHeight: 1.55
    letterSpacing: "0.06em"
  call-number:
    fontFamily: "Atkinson Hyperlegible Mono, ui-monospace, monospace"
    fontSize: "13px"
    fontWeight: 500
    lineHeight: 1.4
rounded:
  xs: "2px"
  sm: "3px"
  md: "4px"
  control: "5px"
  panel: "6px"
  field: "8px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "14px"
  lg: "20px"
  xl: "32px"
  2xl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.steel}"
    textColor: "{colors.steel-ink}"
    typography: "{typography.title}"
    rounded: "{rounded.control}"
    padding: "8px 18px"
  button-ghost:
    backgroundColor: "{colors.steel}"
    textColor: "{colors.steel-ink}"
    typography: "{typography.body-small}"
    rounded: "{rounded.md}"
    padding: "6px 12px"
  button-ghost-hover:
    backgroundColor: "{colors.steel-raised}"
  button-retry:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.card-stock}"
    rounded: "{rounded.md}"
    padding: "7px 14px"
  card-mark:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.card-stock}"
    typography: "{typography.call-number}"
    rounded: "{rounded.sm}"
    height: "24px"
    padding: "0 6px"
  card-mark-hover:
    backgroundColor: "{colors.catalog-red}"
  chip:
    backgroundColor: "{colors.card-stock}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "7px 12px"
  catalog-card:
    backgroundColor: "{colors.card-stock}"
    textColor: "{colors.ink}"
    rounded: "0 0 3px 3px"
    padding: "12px 18px 14px"
  answer-panel:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "20px 24px"
  composer-field:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    padding: "8px 8px 8px 14px"
  label-plate:
    backgroundColor: "{colors.card-stock}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "3px 14px"
  drawer-header:
    backgroundColor: "{colors.steel}"
    textColor: "{colors.steel-ink}"
    padding: "12px 20px"
---

# Design System: Handbook Assistant

## Overview

**Creative North Star: "The Card Catalog"**

The interface is a library catalog cabinet. A navy drawer front runs across the top with a brass label holder carrying the product name; below it, on a warm cream ground, the visitor's question and the answer sit on the left and the catalog cards that answer drew on sit in a rail on the right. Every claim in an answer carries a small numbered mark, and pressing it pulls the matching card out of the rail. The card is where trust is earned: call number in mono, section, the exact sentence highlighted on ruled card stock, a link to the source.

Density is moderate and reading-first: one typeface family (Atkinson Hyperlegible) at a generous 17px body, hairlines rather than boxes to divide fields, and a single red top rule that identifies card stock at a glance. Light and dark are both first-class. Dark is the cabinet room with the lights down: the ground darkens, but the steel header, the brass and paper plate and the light card stock all stay, so cards keep reading as physical objects. The catalog stays literal and modern; there is no typewriter type and no paper texture.

**Key Characteristics:**
- Steel drawer-front header with a brass-bordered paper label plate.
- Answers on white paper panels; sources on off-white card stock with a 4px red top rule.
- Numbered ink marks in the answer that pull a card (slide left, lift, focus).
- One family: Atkinson Hyperlegible for all text, its Mono only for call numbers, card marks and code.
- Both schemes keep the materials; only the ground and the text set on it change.

## Colors

A muted institutional palette: navy steel, brass and catalog red over warm cream stock, with blue reserved for links and focus.

### Primary
- **Drawer Steel** (steel): the sticky header, the Search button and the composer field's border. The cabinet itself. Its raised tone (steel-raised) is only the hover fill for ghost buttons on steel.
- **Catalog Red** (catalog-red; catalog-red-dark in dark): the 4px top rule on every card, call numbers, the "Not held in this collection" stamp, the error-card border and the hovered card mark. It names the source, never decorates.

### Secondary
- **Label Brass** (brass): the 3px border of the label plate, the drawer-group holder glyph, the loading bar. Brass Light (brass-light) is the only accent text on steel (the audited score) and the focus ring inside the header.

### Tertiary
- **Catalog Blue** (link; focus-dark on the dark ground): links and focus rings on card stock and paper (link), and focus on the dark ground (focus-dark). Ruled Blue (ruled-blue) draws the faint card lines behind excerpts.
- **Index Highlight** (highlight): the highlighted cited sentence on a card and text selection.

### Neutral
- **Cabinet Ground** (ground; ground-dark): the page background.
- **Ground Ink** (ground-ink, ground-ink-muted, and their dark variants): text set directly on the ground: questions, headings, notes, fine print.
- **Card Stock** (card-stock; card-stock-dark): catalog cards, the label plate, chips, table heads.
- **Paper** (paper; paper-dark): answer panels, drawer groups, the not-held card, the composer field, tables.
- **Ink** (ink, ink-muted): text on stock and paper. Ink does not change between schemes, because the stock stays light.
- **Hairline** (hair, ground-hair): 1px field dividers on stock and the turn separator on the ground.
- **Verdict colors** (verdict-pass, verdict-partial, with catalog-red for incorrect): results-page verdict tags only.

### Named Rules
**The Two Inks Rule.** Text on the ground uses ground-ink tokens; text on card stock or paper uses ink tokens. In dark mode these diverge, so never set ink directly on the ground or ground-ink on stock.

**The Blue Means Go Rule.** Blue appears only on links and focus rings. Accent color for emphasis comes from red (source identity) or brass (holders and labels on steel).

**The Lights Down Rule.** Dark mode darkens the ground only. Steel, brass, paper and card stock stay light enough that ink text on them is unchanged.

## Typography

**Display Font:** Atkinson Hyperlegible (with system-ui, sans-serif)
**Body Font:** Atkinson Hyperlegible (with system-ui, sans-serif)
**Label/Mono Font:** Atkinson Hyperlegible Mono 500 (with ui-monospace, monospace)

**Character:** A legibility face built for low-vision readers, used in two weights only (400, 700); the mono sibling reads as a stamped call number.

### Hierarchy
- **Display** (700, clamp 26-36px, 1.2): the welcome headline and the results-page title, balanced wrap.
- **Headline** (700, 24px, 1.3; 21px under 620px): each asked question at the top of a turn. Report section heads use 22px.
- **Title** (700, 16px): the card's page title.
- **Body** (400, 17px, 1.55; 16px under 620px): answers and intros, held to 66-72ch.
- **Body Small** (400, 14px): card sections, notes, fine print (13px), detail text.
- **Label** (700, 13px, 0.06em, uppercase): standalone headings that name a set: drawer-group names, the rail's "Cards pulled · N", the sample card label, table heads (0.04em).
- **Call Number** (Mono 500, 13px): call numbers, card marks, verdict tags (12px), question IDs, inline code.

### Named Rules
**The Mono Is A Stamp Rule.** Mono is for identifiers only: call numbers, card marks, model names and question IDs. Never for prose or headings.

**The Label Names A Set Rule.** Uppercase labels are headings for a group of things (a drawer, a rail of cards, a table column). They never sit above a larger headline as an eyebrow.

## Layout

A centered 1240px frame (header and composer pad to the same edge with `max(20px, (100vw - 1240px) / 2)`). Each turn is a two-column grid: the question and answer on the left (fluid, answer capped at 72ch) and a 440px card rail on the right, 32px apart, turns divided by a ground hairline with 28px vertical padding. The welcome view uses the same split: intro and a two-column grid of drawer groups on the left, a sample pulled card on the right (48px gap).

The header is sticky at the top; the composer is sticky at the bottom over a ground-colored fade, its field capped at 840px.

Under 900px the rail stacks below the answer and the welcome stacks intro, drawers, sample. Under 620px the drawer grid goes to one column, the header scope line hides, body steps to 16px and panels tighten to 16px padding.

Spacing rhythm is small steps of 4-8px inside components and 14px between cards and drawer groups, with 24-48px between regions.

## Elevation & Depth

Mostly flat with one physical exception: catalog cards. Panels, chips and the header sit flat on hairline borders; only cards carry a soft ambient shadow, and a pulled card lifts to a deeper one. Dark mode uses black-based shadows of the same shape.

### Shadow Vocabulary
- **Card rest** (`box-shadow: 0 1px 2px rgb(29 37 51 / 8%), 0 3px 10px rgb(29 37 51 / 6%)`): every catalog card.
- **Card pulled** (`box-shadow: 0 6px 12px rgb(29 37 51 / 12%), 0 16px 32px rgb(29 37 51 / 10%)`): the card the visitor pulled.
- **Plate inset** (`box-shadow: inset 0 0 0 1px` brass at 40%): the inner bevel on the label plate.

### Named Rules
**The Only Cards Lift Rule.** Shadow belongs to catalog cards. Answer panels, drawer groups, chips and fields stay flat with a 1px hairline.

## Shapes

Small, near-square corners. Card stock is square on top (where the red rule sits) and 3px at the bottom; the label plate, marks and stamps use 3px; chips and small buttons 4px; the Search button 5px; paper panels 6px; the composer field 8px. Borders are 1px hairlines on stock and paper, 2px for emphasis (composer field in steel, stamp and error card in red, the dashed empty-card slot), and 3px for the brass plate and the header's darker bottom edge.

## Components

### Buttons
- **Shape:** gently squared (4-5px).
- **Primary (Search):** steel fill, steel-ink text, 700, 8px 18px; disabled at 50% opacity.
- **Ghost (New search, Ask a question, audited score):** transparent on steel, steel-ink text, 1px steel-ink-muted border, 6px 12px; hover fills steel-raised. The audited score sets its figure in bold brass-light.
- **Retry:** ink fill with card-stock text, 7px 14px, inside the error card.
- **Focus:** 2px ring, 2px offset; link blue over stock and paper, focus-dark over the dark ground, brass-light inside the header.

### Chips
- **Style:** card-stock fill, ink text, 1px hairline border, 4px radius, 15px text, 7px 12px; hover darkens the border to ink-muted. Used for follow-up and "try another" questions.
- **Drawer question:** a borderless full-width row inside a drawer group; hover fills card stock.

### Cards / Containers
- **Catalog card:** card stock, 1px hairline, 4px catalog-red top rule, 0 0 3px 3px corners, 12px 18px 14px padding, card-rest shadow. Fields top to bottom: call number row (№ n, path in caps, mono red, hairline below), title, § section, excerpt on ruled lines (27px line pitch) with the cited sentence highlighted, a "Show the full card" disclosure, and "Open in the handbook" with an external-arrow SVG.
- **Answer panel / drawer group / not-held card:** paper, 1px hairline, 6px radius, 14-24px padding, no shadow. Drawer-group headings carry a small brass-outlined holder rectangle (26 x 8px) before the label; the not-held drawer's holder is red.
- **Empty slot:** 2px dashed ground hairline, 3px radius, ground-ink-muted text.
- **Error card:** paper with a 2px catalog-red border.

### Inputs / Fields
- **Composer:** paper field, 2px steel border, 8px radius, auto-growing textarea up to 160px, Search button inside on the right. Focus-within turns the border link blue. Placeholder uses ink-muted at full opacity.

### Navigation
- **Drawer header:** sticky steel bar with a 3px darker steel bottom edge. Left: the label plate (paper/card stock, 3px brass border, 700, 18px; 16px on phones) and the scope line in steel-ink-muted 14px (hidden under 620px). Right: ghost actions.

### Card Mark and Pull (signature)
A numbered mark inline in the answer (ink fill, card-stock mono 13px, 24px tall, 3px radius; hover turns catalog red). Pressing it pulls the matching card: any other pulled card in that rail is returned, the card slides 14px left and lifts to the pulled shadow over 0.45s `cubic-bezier(.16, 1, .3, 1)`, scrolls to center and takes focus. Under 900px the pull is a 4px rise instead of a slide. Reduced motion removes all transitions and animation.

### Not Held Stamp
An uppercase 13px 700 stamp in catalog red with a 2px red border and 3px radius, heading the refusal card ("Not held in this collection"), followed by suggestion chips. The rail shows "Cards pulled · 0" over an empty slot.

### Loading Bar
A 56 x 6px hairline track with a brass segment sliding back and forth (1.1s, alternate) beside "Searching the catalog…". Shown only while a request runs; off under reduced motion.

### Results Table
Paper table in a 6px hairline wrapper; card-stock uppercase heads; tabular numerals right-aligned; verdict tags as mono 12px uppercase outlined in their verdict color.

## Do's and Don'ts

### Do:
- **Do** give every sourced claim a numbered mark that pulls a catalog card; the card, not the answer, carries the evidence.
- **Do** mark card stock with the 4px catalog-red top rule and divide its fields with 1px hairlines.
- **Do** set text on the ground in ground-ink tokens and text on stock or paper in ink tokens.
- **Do** keep steel, brass, paper and card stock unchanged in dark mode; darken only the ground.
- **Do** use Atkinson Hyperlegible Mono only for call numbers, card marks, model names and IDs.
- **Do** reserve blue for links and focus rings.

### Don't:
- **Don't** put answers in chat bubbles or a centered chat column; answers sit on paper panels beside the card rail.
- **Don't** add shadows to panels, chips or fields; only catalog cards lift.
- **Don't** add typewriter type or paper texture to the catalog.
- **Don't** set an uppercase label above a larger headline as an eyebrow.
- **Don't** use GitLab logos, wordmarks or brand colors.
