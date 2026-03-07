# Webpage Plan

## Overview

A single-page website with five navbar sections: Home, About, Services, Portfolio, and Contact. Style is clean, no animations, warm off-white background inspired by the MotherDuck reference screenshot.

---

## Design Tokens (from webpage.css)

| Token | Value |
|---|---|
| Background | `rgb(244, 239, 234)` — warm off-white |
| Text | `rgb(56, 56, 56)` — dark charcoal |
| Font | `"Aeonik Mono", sans-serif` |
| Header height (desktop) | `90px` |
| Header height (mobile) | `70px` |

---

## File Structure

```
index.html      — single file: markup + inline <style> + inline <script>
```

Single self-contained HTML file. No build tools, no frameworks, no external JS.

---

## Layout & Sections

### Navbar (fixed, top)
- Logo / site name on the left
- Nav links on the right: Home · About · Services · Portfolio · Contact
- Height: 90px desktop / 70px mobile
- Sticky: `position: fixed; top: 0`
- Background: same warm off-white, thin bottom border `1px solid rgba(56,56,56,0.15)`
- Active link underline (static, no animation)
- Hamburger menu on mobile (toggle class, no animation)

### 1. Home
- Full-viewport hero
- Large headline (bold, uppercase, tight letter-spacing — referencing MotherDuck style)
- Short subheading
- Single CTA button (outlined style)

### 2. About
- Two-column layout on desktop, single column on mobile
- Left: heading + body copy
- Right: placeholder image block (grey rectangle)

### 3. Services
- Three-card grid (desktop), stacked (mobile)
- Each card: short title, brief description, no icons or imagery

### 4. Portfolio
- 2×2 grid of project tiles on desktop, 1-col on mobile
- Each tile: title + short description + placeholder image block

### 5. Contact
- Simple form: Name, Email, Message, Submit button
- No backend — form is presentational only
- Below form: email address and optional social links

### Footer
- Single row: copyright + nav links repeated

---

## CSS Approach

- CSS reset inline (derived from webpage.css reset rules)
- CSS custom properties for colours and spacing
- No external stylesheet; everything in `<style>` tag in `<head>`
- No CSS frameworks
- Responsive via two breakpoints: `max-width: 768px` (tablet/mobile)
- No transitions, no keyframes, no animations

---

## JavaScript

- Minimal inline `<script>` at bottom of `<body>`
- Only purpose: toggle mobile hamburger menu open/close class
- No libraries

---

## Typography Scale

| Element | Size | Weight |
|---|---|---|
| Hero headline | `clamp(2.5rem, 6vw, 5rem)` | 700 |
| Section heading | `clamp(1.5rem, 3vw, 2.5rem)` | 700 |
| Subheading | `1.125rem` | 400 |
| Body | `1rem` | 400 |
| Nav links | `0.875rem` | 500 |

---

## Colour Palette

| Role | Value |
|---|---|
| Background | `#F4EFEa` |
| Text | `#383838` |
| Accent (CTA, borders) | `#383838` |
| Card background | `#EDE8E2` |
| Muted text | `rgba(56,56,56,0.55)` |

---

## Accessibility Notes

- Semantic HTML: `<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`
- Each section has a unique `id` matching its nav link (`#home`, `#about`, etc.)
- Scroll offset for fixed navbar accounted for via `scroll-padding-top` on `:root`
- Keyboard-navigable nav links
- Form fields have `<label>` elements

---

## What is NOT in scope

- Animations or transitions of any kind
- External fonts (Aeonik Mono will be declared with system-sans fallback unless a CDN link is provided later)
- Backend / form submission
- CMS or dynamic content
- Any JavaScript beyond the hamburger toggle
