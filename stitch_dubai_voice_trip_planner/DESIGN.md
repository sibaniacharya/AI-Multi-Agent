---
name: Nocturne Oasis
colors:
  surface: '#131315'
  surface-dim: '#131315'
  surface-bright: '#39393b'
  surface-container-lowest: '#0e0e10'
  surface-container-low: '#1b1b1d'
  surface-container: '#1f1f21'
  surface-container-high: '#2a2a2c'
  surface-container-highest: '#353437'
  on-surface: '#e4e2e4'
  on-surface-variant: '#cfc4c5'
  inverse-surface: '#e4e2e4'
  inverse-on-surface: '#303032'
  outline: '#988e90'
  outline-variant: '#4c4546'
  surface-tint: '#c6c6c6'
  primary: '#c6c6c6'
  on-primary: '#303030'
  primary-container: '#000000'
  on-primary-container: '#757575'
  inverse-primary: '#5e5e5e'
  secondary: '#acc7ff'
  on-secondary: '#002f66'
  secondary-container: '#024590'
  on-secondary-container: '#8fb5ff'
  tertiary: '#c0c1ff'
  on-tertiary: '#1000a9'
  tertiary-container: '#000000'
  on-tertiary-container: '#6164ef'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e2e2e2'
  primary-fixed-dim: '#c6c6c6'
  on-primary-fixed: '#1b1b1b'
  on-primary-fixed-variant: '#474747'
  secondary-fixed: '#d7e2ff'
  secondary-fixed-dim: '#acc7ff'
  on-secondary-fixed: '#001b3f'
  on-secondary-fixed-variant: '#024590'
  tertiary-fixed: '#e1e0ff'
  tertiary-fixed-dim: '#c0c1ff'
  on-tertiary-fixed: '#07006c'
  on-tertiary-fixed-variant: '#2f2ebe'
  background: '#131315'
  on-background: '#e4e2e4'
  surface-variant: '#353437'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-padding: 24px
  gutter: 16px
  section-gap: 64px
  max-width: 1200px
---

## Brand & Style
The design system embodies a premium, nocturnal aesthetic tailored for high-end concierge services. It targets a sophisticated traveler who values efficiency and understated luxury. 

The style is **Glassmorphic Minimalism**. It utilizes deep black surfaces paired with translucent overlays to create a sense of infinite depth, mimicking the Dubai skyline at night. Emotional responses should range from "calm and focused" to "technologically advanced." High-end finishes are achieved through precise typography, generous whitespace, and atmospheric radial glows that suggest a "living" AI presence.

## Colors
The palette is rooted in absolute black (`#000000`) to maximize OLED contrast and power efficiency. 

- **Primary:** Deep Black serves as the foundation for all backgrounds.
- **Accent:** Bright Blue (`#7CA8F9`) is used sparingly for interactive elements, active states, and primary calls to action.
- **Ambient Glows:** Subtle radial gradients using Indigo (`#6366F1`) and Dark Blue are placed behind key containers to provide a sense of illumination without harsh borders.
- **Surface:** Dark Charcoal (`#1E1E20`) is used for elevated cards and buttons, often with a slight opacity (80-90%) to allow background glows to bleed through.

## Typography
This design system utilizes **Inter** for its systematic, utilitarian, yet modern feel. 

Headlines use tight letter-spacing and bold weights to command attention against the dark background. Body text maintains a generous line height to ensure legibility during long-form reading of itineraries. Labels use medium weights and slight tracking increases to maintain clarity at small scales, especially on translucent surfaces.

## Layout & Spacing
The layout follows a **Fixed Grid** philosophy for desktop to maintain a cinematic, centered feel, transitioning to a fluid model for mobile devices.

- **Desktop:** 12-column grid, 1200px max-width, 16px gutters.
- **Margins:** Large 64px vertical gaps between sections to emphasize the "minimalist" luxury.
- **Safe Areas:** Content should be padded by at least 24px from screen edges on mobile.
- **Voice Interface:** The central voice interaction hub is anchored to the bottom-center of the viewport, utilizing a "floating" container model that ignores standard grid constraints to remain accessible.

## Elevation & Depth
Depth is communicated through **Glassmorphism and Tonal Layers** rather than traditional drop shadows.

- **Layer 0:** Absolute Black (#000000) base.
- **Layer 1:** Dark Charcoal (#1E1E20) at 80% opacity with a 12px backdrop-blur. Used for secondary cards.
- **Layer 2:** High-elevation elements (modals/popovers) use the same charcoal base but with a 1px solid border at 10% white opacity to define the edge.
- **Glows:** Use `radial-gradient(circle at center, rgba(124, 168, 249, 0.15) 0%, transparent 70%)` behind interactive voice components to simulate a digital aura.

## Shapes
The design system uses a **Rounded** shape language to soften the "tech" feel and make the travel experience feel more inviting. 

- **Standard Buttons & Inputs:** 0.5rem (8px) corner radius.
- **Cards & Itinerary Modules:** 1rem (16px) corner radius.
- **Voice Orb/Pulse:** Perfectly circular (9999px).
- **Subtle Borders:** All shapes on Layer 1 and above should feature a thin, low-contrast stroke (White at 10% opacity) to ensure the dark shapes do not bleed into the absolute black background.

## Components
- **Buttons:** Primary buttons use the Bright Blue accent with White text. Secondary buttons use the Dark Charcoal background with a 1px border. All buttons feature a subtle "inner glow" on hover.
- **Voice Input:** A circular floating button with an animated "pulse" gradient using the purple and blue accents. When active, a waveform visualization replaces the static icon.
- **Cards:** Itinerary cards use the translucent charcoal background. Content is strictly aligned to a 24px internal padding. Images within cards use a soft overlay to ensure text remains legible.
- **Chips:** Small, pill-shaped tags for "Activities" or "Times" use a 10% Blue tint background with Blue text.
- **Input Fields:** Minimalist design—bottom border only or very subtle ghost-box. Focus state is indicated by the Bright Blue accent color and a subtle outer glow.
- **Lists:** Clean separation using thin 1px lines (White at 5% opacity). No icons for list bullets; use spacing and typography to denote hierarchy.