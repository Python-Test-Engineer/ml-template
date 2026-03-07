# Technical Specification: Single-Page Website
_Derived from: `_plans/webpage_plan.md`_

---

## 1. Deliverable

One file: `index.html`

- Self-contained: all CSS inside `<style>` in `<head>`, all JS inside `<script>` at end of `<body>`
- No external stylesheets, no external JS libraries, no build step
- Opens correctly from the filesystem (file://) and from any static host

---

## 2. HTML Document Structure

```
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>...</title>
    <style> ... </style>
  </head>
  <body>
    <header>
      <nav> ... </nav>
    </header>
    <main>
      <section id="home">   ... </section>
      <section id="about">  ... </section>
      <section id="services">... </section>
      <section id="portfolio">... </section>
      <section id="contact">... </section>
    </main>
    <footer> ... </footer>
    <script> ... </script>
  </body>
</html>
```

Section `id` values must exactly match the href anchors in the navbar (`#home`, `#about`, `#services`, `#portfolio`, `#contact`).

---

## 3. CSS Specification

### 3.1 Reset

Apply a full element reset (box-sizing, margin, padding, border, font-size, font-family, vertical-align, text-decoration) to all HTML elements, exactly as in the provided `webpage.css` reset block.

### 3.2 Custom Properties

Declare on `:root`:

```css
:root {
  --bg:           #F4EFEA;        /* warm off-white */
  --text:         #383838;        /* dark charcoal */
  --text-muted:   rgba(56,56,56,0.55);
  --card-bg:      #EDE8E2;
  --border:       rgba(56,56,56,0.15);
  --accent:       #383838;        /* used for CTA border/text */

  --font:         "Aeonik Mono", ui-monospace, "Courier New", monospace;

  --header-h-desktop: 90px;
  --header-h-mobile:  70px;

  --section-pad-v:  100px;        /* vertical padding on each section */
  --section-pad-h:  48px;         /* horizontal padding (container sides) */
  --max-width:      1200px;
}
```

### 3.3 Base Styles

```
body
  background-color: var(--bg)
  color: var(--text)
  font-family: var(--font)
  font-size: 1rem
  line-height: 1.6
  min-height: 100vh

:root
  scroll-behavior: auto           /* NO smooth scroll */
  scroll-padding-top: var(--header-h-desktop)

.container
  max-width: var(--max-width)
  margin: 0 auto
  padding: 0 var(--section-pad-h)
```

### 3.4 Navbar

```
<header>
  position: fixed
  top: 0
  left: 0
  width: 100%
  height: var(--header-h-desktop)   [mobile: var(--header-h-mobile)]
  background: var(--bg)
  border-bottom: 1px solid var(--border)
  z-index: 1000

  Inner layout: display flex; justify-content space-between; align-items center
  Padding: 0 var(--section-pad-h)

.nav-logo
  font-size: 1rem
  font-weight: 700
  text-transform: uppercase
  letter-spacing: 0.1em
  color: var(--text)

.nav-links  (desktop)
  display: flex
  gap: 2rem
  list-style: none

.nav-links a
  font-size: 0.875rem
  font-weight: 500
  color: var(--text)
  text-transform: uppercase
  letter-spacing: 0.05em

.nav-links a.active
  border-bottom: 1px solid var(--text)

.hamburger  (mobile only, hidden on desktop)
  display: none          [desktop]
  cursor: pointer
  flex-direction: column
  gap: 5px
  Three <span> bars: width 24px, height 2px, background var(--text)

Mobile nav open state (.nav-open class on <header>):
  .nav-links
    display: flex
    flex-direction: column
    position: absolute
    top: var(--header-h-mobile)
    left: 0
    width: 100%
    background: var(--bg)
    border-bottom: 1px solid var(--border)
    padding: 1.5rem var(--section-pad-h)
    gap: 1.5rem
```

### 3.5 Main Content Offset

```
main
  padding-top: var(--header-h-desktop)   [mobile: var(--header-h-mobile)]
```

### 3.6 Section: Home

```
#home
  min-height: calc(100vh - var(--header-h-desktop))
  display: flex
  align-items: center
  padding: var(--section-pad-v) var(--section-pad-h)

.hero-headline
  font-size: clamp(2.5rem, 6vw, 5rem)
  font-weight: 700
  text-transform: uppercase
  letter-spacing: -0.02em
  line-height: 1.05
  max-width: 800px

.hero-sub
  font-size: 1.125rem
  color: var(--text-muted)
  margin-top: 1.5rem
  max-width: 520px

.btn-outline
  display: inline-block
  margin-top: 2.5rem
  padding: 0.75rem 2rem
  border: 1px solid var(--accent)
  color: var(--accent)
  font-size: 0.875rem
  font-weight: 500
  text-transform: uppercase
  letter-spacing: 0.08em
  background: transparent
  cursor: pointer
```

### 3.7 Section: About

```
#about
  padding: var(--section-pad-v) var(--section-pad-h)

.about-grid
  display: grid
  grid-template-columns: 1fr 1fr
  gap: 4rem
  align-items: center

  [mobile: grid-template-columns: 1fr]

.about-image-placeholder
  width: 100%
  aspect-ratio: 4 / 3
  background: var(--card-bg)

.section-heading
  font-size: clamp(1.5rem, 3vw, 2.5rem)
  font-weight: 700
  text-transform: uppercase
  letter-spacing: -0.01em
  line-height: 1.1
  margin-bottom: 1.5rem

.body-copy
  font-size: 1rem
  line-height: 1.7
  color: var(--text-muted)
```

### 3.8 Section: Services

```
#services
  padding: var(--section-pad-v) var(--section-pad-h)
  background: var(--card-bg)       /* subtle differentiation */

.services-grid
  display: grid
  grid-template-columns: repeat(3, 1fr)
  gap: 2rem
  margin-top: 3rem

  [mobile: grid-template-columns: 1fr]

.service-card
  background: var(--bg)
  padding: 2rem
  border: 1px solid var(--border)

.service-card h3
  font-size: 1rem
  font-weight: 700
  text-transform: uppercase
  letter-spacing: 0.05em
  margin-bottom: 0.75rem

.service-card p
  font-size: 0.9375rem
  line-height: 1.6
  color: var(--text-muted)
```

### 3.9 Section: Portfolio

```
#portfolio
  padding: var(--section-pad-v) var(--section-pad-h)

.portfolio-grid
  display: grid
  grid-template-columns: repeat(2, 1fr)
  gap: 2rem
  margin-top: 3rem

  [mobile: grid-template-columns: 1fr]

.portfolio-tile
  border: 1px solid var(--border)

.portfolio-tile-image
  width: 100%
  aspect-ratio: 16 / 9
  background: var(--card-bg)

.portfolio-tile-body
  padding: 1.5rem

.portfolio-tile-body h3
  font-size: 1rem
  font-weight: 700
  text-transform: uppercase
  letter-spacing: 0.04em
  margin-bottom: 0.5rem

.portfolio-tile-body p
  font-size: 0.9375rem
  line-height: 1.6
  color: var(--text-muted)
```

### 3.10 Section: Contact

```
#contact
  padding: var(--section-pad-v) var(--section-pad-h)
  background: var(--card-bg)

.contact-inner
  max-width: 600px

.contact-form
  margin-top: 3rem
  display: flex
  flex-direction: column
  gap: 1.25rem

.form-group
  display: flex
  flex-direction: column
  gap: 0.375rem

.form-group label
  font-size: 0.8125rem
  font-weight: 500
  text-transform: uppercase
  letter-spacing: 0.06em

.form-group input,
.form-group textarea
  background: var(--bg)
  border: 1px solid var(--border)
  padding: 0.75rem 1rem
  font-family: var(--font)
  font-size: 1rem
  color: var(--text)
  width: 100%
  resize: vertical           /* textarea only */

.form-group textarea
  min-height: 130px

.btn-submit  (same visual as .btn-outline)
  align-self: flex-start
  padding: 0.75rem 2.5rem
  border: 1px solid var(--accent)
  background: transparent
  color: var(--accent)
  font-size: 0.875rem
  font-weight: 500
  text-transform: uppercase
  letter-spacing: 0.08em
  cursor: pointer

.contact-meta
  margin-top: 2.5rem
  font-size: 0.9375rem
  color: var(--text-muted)
```

### 3.11 Footer

```
footer
  padding: 1.5rem var(--section-pad-h)
  border-top: 1px solid var(--border)
  display: flex
  justify-content: space-between
  align-items: center
  flex-wrap: wrap
  gap: 1rem

  [mobile: flex-direction: column; text-align: center]

footer p
  font-size: 0.8125rem
  color: var(--text-muted)

.footer-links
  display: flex
  gap: 1.5rem
  list-style: none

.footer-links a
  font-size: 0.8125rem
  color: var(--text-muted)
  text-transform: uppercase
  letter-spacing: 0.04em
```

### 3.12 No-Animation Rule

There must be zero occurrences of:
- `transition`
- `animation`
- `@keyframes`
- `transform` (except static `translate` for layout if needed)

---

## 4. Responsive Breakpoint

Single breakpoint at `@media (max-width: 768px)`:

| Change | Desktop | Mobile |
|---|---|---|
| Header height | 90px | 70px |
| `scroll-padding-top` | 90px | 70px |
| `main` padding-top | 90px | 70px |
| Nav links | flex row, visible | hidden; shown via `.nav-open` |
| Hamburger | hidden | visible |
| About grid | 2-col | 1-col |
| Services grid | 3-col | 1-col |
| Portfolio grid | 2-col | 1-col |
| Section padding-h | 48px | 20px |
| Footer | row | column |

---

## 5. JavaScript Specification

Location: single `<script>` tag at the bottom of `<body>`, before `</body>`.

Behaviour:
1. Select the `<header>` element and the `.hamburger` button
2. On click of `.hamburger`, toggle the class `nav-open` on `<header>`
3. On click of any `.nav-links a`, remove `nav-open` from `<header>` (closes menu after navigation)
4. No other JS. No event listeners beyond the above two.

No `setTimeout`, `setInterval`, `requestAnimationFrame`, or DOM manipulation beyond class toggling.

---

## 6. Content Placeholders

All copy is placeholder text. Use the following:

| Section | Headline | Body |
|---|---|---|
| Home | "YOUR HEADLINE HERE" | "A short subheading that describes what you do in one or two lines." |
| About | "About Us" | Two short paragraphs of Lorem Ipsum |
| Services | Titles: "Service One", "Service Two", "Service Three" | One sentence each |
| Portfolio | Titles: "Project One" – "Project Four" | One sentence each |
| Contact | "Get In Touch" | — |
| Footer | © 2026 Your Name | — |
| Logo | "LOGO" | — |

Placeholder image blocks are `<div>` elements with a fixed aspect ratio and `background: var(--card-bg)`. No `<img>` tags.

---

## 7. Accessibility Requirements

| Requirement | Implementation |
|---|---|
| Landmark roles | Implicit via `<header>`, `<nav>`, `<main>`, `<footer>` |
| Section labels | Each `<section>` has `aria-labelledby` pointing to its heading `id` |
| Hamburger button | `aria-label="Toggle navigation"`, `aria-expanded` toggled by JS |
| Form inputs | Each has a `<label>` with matching `for`/`id` pair |
| Skip link | `<a href="#home" class="skip-link">Skip to content</a>` as first child of `<body>`; visually hidden (position absolute, off-screen), visible on `:focus` |
| Colour contrast | All text on background meets WCAG AA (charcoal on off-white passes) |
| Tab order | Natural DOM order; no `tabindex` needed |

---

## 8. Validation Checklist (pre-delivery)

- [ ] Valid HTML5 (no unclosed tags, no duplicate `id`s)
- [ ] All five section `id`s present and matching navbar hrefs
- [ ] Zero `transition`, `animation`, `@keyframes` in `<style>`
- [ ] Mobile hamburger opens/closes menu correctly
- [ ] All form `<label>` elements correctly associated
- [ ] `scroll-padding-top` prevents navbar overlap on anchor jump
- [ ] Page renders without a server (file://)
- [ ] No external requests (no CDN fonts, no external scripts)
