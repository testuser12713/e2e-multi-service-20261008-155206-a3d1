# Design — Project Identity

> This document is project-long-lived. Tokens are not changed without
> the Architect's approval. Developers MUST use these tokens
> instead of improvising their own colors/spacings.

## Style Direction

Calm, dark developer-console look: deep slate surfaces, one electric indigo accent, monospace for all data (ids, timestamps, results), status always encoded by color plus text — reference Linear/Stripe, no decorative flourish.

## Colors

- `--color-bg`: **#0F1115**
- `--color-surface`: **#171A21**
- `--color-surfaceRaised`: **#1E222B**
- `--color-fg`: **#E6E9EF**
- `--color-fgMuted`: **#9BA3B4**
- `--color-muted`: **#6B7280**
- `--color-border`: **#2A2F3A**
- `--color-borderStrong`: **#3A4150**
- `--color-accent`: **#6366F1**
- `--color-accentHover`: **#818CF8**
- `--color-accentActive`: **#4F52D9**
- `--color-accentSoft`: **#1E2140**
- `--color-statusPending`: **#E3B341**
- `--color-statusPendingBg`: **#2A2416**
- `--color-statusProgress`: **#58A6FF**
- `--color-statusProgressBg`: **#16233A**
- `--color-statusDone`: **#3FB950**
- `--color-statusDoneBg`: **#15281A**
- `--color-statusFailed`: **#F85149**
- `--color-statusFailedBg`: **#301716**
- `--color-focusRing`: **#818CF8**
- `--color-overlay`: **rgba(9,11,15,0.72)**

## Typography

- `font_family`: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif
- `font_mono`: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace
- `heading_weight`: 600
- `body_weight`: 400
- `label_weight`: 500
- `size_display`: 28px / 1.2 / 600
- `size_h1`: 22px / 1.25 / 600
- `size_h2`: 16px / 1.35 / 600
- `size_body`: 14px / 1.5 / 400
- `size_small`: 12px / 1.45 / 400
- `size_mono_data`: 13px / 1.5 / 400 (font_mono, tabular numbers)

## Spacing Scale

- `--space-0`: 4px
- `--space-1`: 8px
- `--space-2`: 12px
- `--space-3`: 16px
- `--space-4`: 24px
- `--space-5`: 32px
- `--space-6`: 48px

## Border-Radii

- `--radius-sm`: 6px
- `--radius-md`: 10px
- `--radius-lg`: 16px
- `--radius-pill`: 999px

## Components

### Button

Primary: bg=accent #6366F1, fg=#FFFFFF, label 14px/500, padding 12px 20px, radius md 10px, border 1px solid transparent, min-height 44px (mobile tap target), min-width 44px icon-only. States: hover bg=accentHover #818CF8; active bg=accentActive #4F52D9 + translateY(1px); focus-visible outline 2px solid #818CF8 offset 2px; disabled bg=surfaceRaised #1E222B, fg=#6B7280, border 1px solid #2A2F3A, opacity 1, cursor not-allowed (no pseudo-hover). Loading: label swaps to 'Wird gesendet…', button disabled, no layout shift (label container keeps height). Secondary/Ghost: transparent bg, fg=fgMuted, border 1px solid #2A2F3A; hover bg=surfaceRaised + fg=#E6E9EF.

### Textarea (Auftragstext)

Full width of the form column, min-height 140px, resize vertical, padding 12px 14px, radius md, bg=surface #171A21, fg=#E6E9EF, border 1px solid #2A2F3A, font 14px/1.5, placeholder fgMuted #9BA3B4. Focus: border accent #6366F1 + outline 2px solid #818CF8 offset 0. Invalid (only set after first input or first submit attempt): border #F85149, hint text below in #F85149 12px. Untouched and never submitted: NO error styling, neutral placeholder only. Character counter top-right of label row in mono 12px, fgMuted, always visible, does not turn into an error color.

### Select (Auswertungsart)

Native select for reliability, full width of form column, height 44px, padding 0 40px 0 14px, radius md, bg=surface, fg=#E6E9EF, border 1px solid #2A2F3A, custom chevron in fgMuted. Exactly three options, never empty: 'Wörter zählen' (word_count), 'Häufigste Wörter' (top_words), 'Lesezeit schätzen' (reading_time); first is preselected so the control is never in an unusable state. Focus: border accent + 2px outline #818CF8. Open dropdown uses OS styling (acceptable in MVP); the visible closed state must show the German label, never the raw enum.

### FormCard

Container for Textarea + Select + Submit. bg=surface #171A21, border 1px solid #2A2F3A, radius lg 16px, padding 24px, gap 16px between fields, 24px between field block and submit row. Title 'Neuer Auftrag' 16px/600. Sticky at top of the column on ≥1024px (top: 24px). On <1024px it stacks above the list, not sticky.

### JobRow

One row per job in the list. bg=surface #171A21, border 1px solid #2A2F3A, radius md 10px, padding 12px 16px, gap 12px vertical, full width. Line 1: job id in mono (#E6E9EF, fgMuted prefix '#'), analysis as a small pill (bg=surfaceRaised, fg=#9BA3B4, radius pill, padding 2px 10px, 12px) and the StatusBadge right-aligned. Line 2: the job text, 14px/1.5 #E6E9EF, clamped to 3 lines with ellipsis so rows stay even. Line 3: timestamps in mono 12px #9BA3B4. Result block (only when done/failed): inset bg=surfaceRaised, radius sm 6px, padding 8px 12px, mono 13px; result JSON pretty-printed with 2-space indent and wordCount/reading_time values formatted per layout rules. Newest job gets border-left 3px solid #6366F1 on first render after creation, fading out over 1s to signal arrival without flashing.

### StatusBadge

Pill, height 24px, padding 0 10px, radius pill, 12px/500, with a 6px dot on the left (dot color = badge fg). Exactly four states, never more: pending → label 'wartend', fg #E3B341, bg #2A2416; in_progress → label 'in Arbeit', fg #58A6FF, bg #16233A, dot pulses (opacity 0.45→1, 1.4s ease-in-out infinite; disabled under prefers-reduced-motion, then static dot); done → label 'fertig', fg #3FB950, bg #15281A; failed → label 'fehlgeschlagen', fg #F85149, bg #301716. Unknown/unexpected status value falls back to a neutral badge with the raw string, fg #9BA3B4, bg #1E222B — never an empty pill, never a color without a label.

### ResultView

Rendering per analysis, always mono, tabular numbers. word_count: 'Wörter: 1.234'. top_words: ordered list '1. wort — 42' with count right-aligned, max 10 entries, bar-free (no chart in MVP); empty list shows 'Keine Wörter gefunden'. reading_time: 'Lesezeit: 1,5 min' plus 'Wörter: 1.234' on a second line. Failed jobs show the error instead: bg #301716, border-left 3px solid #F85149, fg #F85149, 13px, preceded by the word 'Fehler:'. While status is pending or in_progress the result area shows nothing at all — no skeleton, no placeholder text — the badge alone carries the state.

### JobList

Header row above the list: 'Aufträge' 16px/600 left, and on the right a live indicator: 8px dot in #3FB950 with a slow 2s pulse plus text 'Aktualisiert alle 3 s' in 12px fgMuted — this is a status display, not a control, so it must not look clickable. Rows stacked with 12px gap, newest first. Empty state: centered block, padding 48px 24px, radius lg, border 1px dashed #2A2F3A, headline 'Noch keine Aufträge' 16px/600 #E6E9EF, subline 'Text eingeben, Auswertung wählen, absenden.' 14px fgMuted. Loading of the very first fetch: three grey skeleton rows (bg surfaceRaised, radius md, height 84px, 1.5s shimmer) — only on first load, never during the 3s background refresh.

### InlineAlert

Used above the form for submit-level feedback (e.g. job created, API unreachable). radius md, padding 12px 14px, 14px/1.5, border-left 3px solid. Success: fg #3FB950, bg #15281A. Error: fg #F85149, bg #301716, with a 'Erneut versuchen' Ghost button inline. Auto-dismiss success after 4s; errors stay until the next successful request. Never used for field validation — that lives under the field.

### Header

Page top bar, full-bleed bg=#0F1115 with 1px bottom border #2A2F3A, inner content constrained to the container width, height 64px, padding 0 24px. Left: product name 'Auftragsverarbeitung' 16px/600; a 6px accent bar before it. Right: 'API verbunden' / 'API nicht erreichbar' in 12px mono with a matching dot (#3FB950 / #F85149), deriving from the /health ping. On <768px the right label shortens to the dot alone with an accessible title attribute — never a dead control.

### NeutralUntouchedForm

Explicit neutral state rule, not a separate widget: on first paint nothing is red, nothing is disabled unless it truly is, and the submit button is enabled (the API decides validity). Validation messages appear only after the user has typed into the textarea or pressed submit once; after that, they update live per keystroke. Submit stays enabled while invalid so pressing it yields a visible, explained error instead of a dead button.

## Layout Principles

- Container max-width 1080px, centered, horizontal padding 16px below 768px and 24px above; the whole app is one page, no routing needed.
- Breakpoints: 480px (mobile, single column, form and list full width), 768px (wider gutters, header label full), 1024px and up (two columns: form 360-400px fixed on the left, job list takes the remaining space; gap 24px).
- Section rhythm: 32px between page header and content, 24px between form column blocks, 12px between job rows, 8px between a row's text lines. Everything on the 4px spacing scale.
- Border-first, no shadows: surfaces are separated by 1px #2A2F3A borders and a subtle #171A21 vs #0F1115 contrast step; only overlays/toasts use a shadow (0 8px 24px rgba(0,0,0,0.4)).
- ONE time format everywhere: ISO-8601 UTC timestamps are displayed as 'YYYY-MM-DD HH:MM:SS UTC' (e.g. '2025-03-14 09:41:07 UTC'), in the monospace stack, tabular numbers. No relative times, no locale shift, no seconds dropped, in every place a timestamp appears.
- ONE number format everywhere: counts use German grouping with a period (1.234), the reading-time duration uses one decimal with a comma and the unit 'min' (1,5 min), and intervals use 'X s' (e.g. 'alle 3 s').
- Status is always two-channel: color plus the exact German label from {wartend, in Arbeit, fertig, fehlgeschlagen}; the raw enum never reaches the screen, and no status is ever communicated by color alone.
- Fonts: Inter for all prose and labels, the monospace stack for every datum (ids, timestamps, results, counters, health text). Never monospace for paragraphs of job text.
- Accessibility floor: body text contrast at least 4.5:1 on its surface, all interactive targets at least 44x44px, visible 2px focus ring #818CF8 on every focusable element, motion (pulsing dot, shimmer, arrival border) suppressed under prefers-reduced-motion.
- Density is calm: this is a short list an operator reads, so if a change threatens legibility or the status story, drop it rather than add it.
