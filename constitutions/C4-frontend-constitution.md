# C4 — Frontend Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C4 — Frontend Constitution                                         |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | Both Stacks                                                        |
| **Paired With**    | C4 — Frontend Implementation Guide                                 |

---

> *"One system. Two frameworks. Zero excuses. Build the interface that earns trust before the user reads a single word."*

---

## Opening Statement

The Frontend Constitution governs everything the user sees, touches, and experiences across all KSDRILL SA platforms. It governs two distinct frontend frameworks — Next.js App Router for Maphophe and SyncUp, Angular with strict TypeScript for FundsLink Academy and KSDRILL Reserve Bank — under one unified set of standards. Where standards differ by framework, they are explicitly scoped. Where no scope is stated, the standard applies to both frameworks without exception.

This constitution is the result of iterating the frontend approach seventeen times across real systems. It contains no theoretical rules — every standard here exists because a past version without it produced a broken experience, an inaccessible interface, a maintenance burden, or a user trust failure. The version number reflects that history; the standards reflect what survived it.

The styling philosophy is explicit and non-negotiable: **Tailwind CSS for layout, spacing, and responsive utilities; Custom CSS for brand identity, design language, complex animations, and anything that requires design precision beyond what utility classes can express**. Both are first-class tools. Neither is a fallback for the other. Using only Tailwind produces generic, indistinguishable interfaces. Using only custom CSS produces unmaintainable style sprawl. The combination produces systems that are both maintainable and beautiful.

This constitution does not govern backend API contracts — that is C2. It does not govern authentication strategy — that is C3. It does not govern database schema — that is C5. What this constitution governs is everything between the API response and the pixel the user sees: component architecture, state management, mobile-first design, accessibility, form validation, observability, and the layer build order that makes every feature predictable to build.

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| Part 0 | Framework Scope & Stack Assignment | S4.1–S4.2 |
| Part 1 | Architecture | S4.3–S4.12 |
| Part 2 | Styling: Tailwind + Custom CSS | S4.13–S4.17 |
| Part 3 | Interaction & Accessibility | S4.18–S4.27 |
| Part 4 | State & Data Management | S4.28–S4.45 |
| Part 5 | Form Standards | S4.46–S4.51 |
| Part 6 | Angular-Specific Standards | S4.52–S4.60 |
| Part 7 | MVP Realism | S4.61–S4.64 |
| Part 8 | Frontend Observability | S4.65–S4.70 |
| Part 9 | Group-Build Methodology | S4.71–S4.78 |
| Part 10 | Layer Build Order | S4.79–S4.82 |
| Anti-Patterns Index | — | AP-S4.* |
| Cross-Constitution Dependency Map | — | — |
| Amendment Log | — | — |

---

## Part 0 — Framework Scope & Stack Assignment (`S4.1`–`S4.2`)

Before applying any standard, establish which framework governs the system being built. This is determined by stack assignment in C6, not by preference.

---

### S4.1 — Framework Assignment Is Determined by Stack, Not Preference

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.1 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S6.1` (stack assignment), `S3.1` (auth strategy follows stack) |
| **Enforced By** | Architecture review · Code Review |

**Standard:**
Next.js App Router with React and TypeScript governs Maphophe and SyncUp. Angular with strict TypeScript governs FundsLink Academy and KSDRILL Reserve Bank. Standards S4.3–S4.51 apply to both frameworks. Standards S4.52–S4.60 apply to Angular only. Where a standard includes both Next.js and Angular variants, both are required. A system never mixes frameworks or installs both.

**Rationale:**
Framework mixing creates two parallel component libraries, two routing systems, two build pipelines, and two testing strategies in one codebase. The maintenance and knowledge cost is never justified by any feature requirement.

**Anti-Patterns:**
- `AP-S4.1a` — Installing Angular CDK in a Next.js project or React components in an Angular project — framework contamination that prevents clean builds and testing.

**Cross-References:** `S6.1` (stack assignment framework), `S3.1` (auth follows stack)

---

### S4.2 — Mobile-First Baseline — 320px Mandatory Across Both Frameworks

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.2 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | — |
| **Enforced By** | Visual regression tests (S7.19) · Code Review |

**Standard:**
All CSS starts at 320px and scales up. No component is designed desktop-first. Tailwind mobile-first breakpoints (`sm:`, `md:`, `lg:`) are used throughout. The 320px viewport is tested in CI visual regression on every PR that changes UI. A layout that breaks at 320px is a build failure.

**Rationale:**
KSDRILL SA builds for South African users first — a user population where mobile is the primary device and many users access the platform on entry-level hardware with 320px viewports. A desktop-first system that degrades to mobile is not acceptable for this user base.

**Anti-Patterns:**
- `AP-S4.2a` — Using `hidden md:block` on primary content — hiding primary content from mobile is not mobile-first design; restructure the component.
- `AP-S4.2b` — Designing for 1440px and adding mobile overrides — desktop-first CSS produces worse mobile experiences than mobile-first CSS extended to desktop.

**Cross-References:** `S4.3` (one adaptive system), `S7.19` (visual regression at 320/375/390px)

---

## Part 1 — Architecture (`S4.3`–`S4.12`)

Frontend architecture standards govern the structural decisions that determine whether a frontend system is maintainable at scale: component design, separation of concerns, navigation patterns, and layout primitives.

---

### S4.3 — One Adaptive System Per Platform — Never Two Separate Builds

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.3 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.2` (mobile-first) |
| **Enforced By** | Code Review |

**Standard:**
Each platform has one codebase that adapts to all screen sizes via responsive design. A separate mobile site, mobile subdomain, or mobile URL structure is forbidden. One repository, one deployment, all devices.

**Rationale:**
Separate mobile builds double the maintenance surface, create content parity problems, and introduce SEO penalties from duplicate content. Responsive design achieves the same adaptation with a fraction of the maintenance cost.

**Anti-Patterns:**
- `AP-S4.3a` — Creating `/mobile/` routes or `m.domain.com` subdomains — separate mobile builds diverge from the main build and are always neglected.

**Cross-References:** `S4.2` (mobile-first), `S8.4` (one deployment per platform)

---

### S4.4 — Smart/Container and Presentational Component Separation

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.4 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S1.1` (design first) |
| **Enforced By** | Code Review |

**Standard:**
Frontend components are separated into two categories. Smart components (containers): own state, call services/APIs, perform data transformation, pass data down via props or inputs. Presentational components: receive data via props/inputs, emit events via outputs, contain no business logic, no API calls, no direct state management. Business logic never lives in presentational components.

**Rationale:**
Presentational components with embedded business logic cannot be reused without bringing the business logic with them. Testing presentational components requires mocking services they should know nothing about. The separation is what makes frontend systems testable and reusable.

**Anti-Patterns:**
- `AP-S4.4a` — Calling an API directly inside a presentational button component — the button now cannot be used in any context where the API call is wrong, and testing it requires mocking network calls.

**Cross-References:** `S4.28` (state management), `S4.79` (layer build order)

---

### S4.5 — Brand Always Visible — Minimum 20px Logo, Never Hidden

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.5 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | — |
| **Enforced By** | Visual regression tests · Code Review |

**Standard:**
The platform logo or brand name is visible on every page at every screen size. Minimum rendered height is 20px. The brand never collapses on mobile and never hides behind a hamburger menu trigger. Brand visibility is a non-negotiable user trust signal.

**Anti-Patterns:**
- `AP-S4.5a` — Hiding the logo on mobile to save space — brand-less mobile experiences reduce trust and navigation confidence.

**Cross-References:** `S4.6` (navigation standards), `S4.2` (mobile-first)

---

### S4.6 — Navigation — Horizontal at Desktop, Structured at Mobile

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.6 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.2` (mobile-first) |
| **Enforced By** | Visual regression tests · Code Review |

**Standard:**
Desktop navigation is horizontal with dropdowns. Mobile navigation is a bottom sheet drawer or horizontally scrollable row. Accordion-style navigation that expands vertically and pushes page content down is forbidden on all screen sizes. Full-page overlay navigation is forbidden.

**Rationale:**
Accordion navigation disrupts reading position and causes layout shift. Bottom sheet drawers and horizontal scroll navigation maintain the user's context while enabling mobile navigation.

**Anti-Patterns:**
- `AP-S4.6a` — Accordion navigation on mobile — pushes all content down when open, loses user's reading position, and causes cumulative layout shift.
- `AP-S4.6b` — Full-page overlay navigation — completely removes context; the user must navigate blind.

**Cross-References:** `S4.2` (mobile-first baseline), `S4.19` (keyboard accessibility)

---

### S4.7 — Hero Sections Use `min-height` — Never Fixed Height

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.7 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.2` (mobile-first) |
| **Enforced By** | Code Review |

**Standard:**
Hero sections use `min-h-screen` or `min-height: 100dvh`. Fixed pixel heights and `height: 100vh` are forbidden on hero sections (100vh breaks on mobile browsers due to the URL bar). `100dvh` (dynamic viewport height) is the correct unit.

**Anti-Patterns:**
- `AP-S4.7a` — `height: 100vh` on hero sections — iOS Safari's URL bar makes 100vh larger than the visible viewport; content is cut off on every iPhone.

**Cross-References:** `S4.2` (320px baseline)

---

### S4.8 — Sticky Headers Shrink on Scroll — Never Obscure Content

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.8 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | — |
| **Enforced By** | Code Review |

**Standard:**
Sticky headers shrink on scroll (reduced padding). `scroll-padding-top` is set equal to header height so anchor links land at the correct position. The sticky header never permanently obscures content.

**Anti-Patterns:**
- `AP-S4.8a` — Fixed-height sticky header without `scroll-padding-top` — anchor navigation lands underneath the header, hiding the linked content.

**Cross-References:** `S4.6` (navigation standards)

---

### S4.9 — No Page-Level Horizontal Scroll

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.9 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.2` (mobile-first) |
| **Enforced By** | Visual regression tests · Code Review |

**Standard:**
The page body never scrolls horizontally at any screen width. Horizontal scrolling is permitted only inside explicitly bounded containers (e.g., `overflow-x: auto` on a table wrapper with a fixed parent width). `overflow-x: hidden` is set on the body.

**Anti-Patterns:**
- `AP-S4.9a` — An absolutely positioned element wider than its parent causing page-level horizontal scroll — common on mobile when desktop-width elements are not made responsive.

**Cross-References:** `S4.2` (320px baseline), `S7.19` (visual regression)

---

### S4.10 — Visual Regression Tests at 320/375/390px on Every UI PR

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.10 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S7.19` (Playwright visual regression) |
| **Enforced By** | CI — Playwright visual tests |

**Standard:**
CI runs visual regression tests at exactly 320px, 375px, and 390px viewport widths on every PR that contains frontend changes. Layout breakage at these widths is a build failure. Tests live in `tests/visual/` (Next.js) or `e2e/visual/` (Angular).

**Rationale:**
Manual testing at three viewport widths on every PR is not reliably enforced. Automated visual regression at the exact breakpoints that matter for the user base makes mobile regression a hard CI gate rather than a soft reminder.

**Anti-Patterns:**
- `AP-S4.10a` — Only testing at 1280px in CI — the user base that experiences mobile breakage is the largest segment of the user population.

**Cross-References:** `S7.19` (visual regression implementation), `S4.2` (320px baseline)

---

### S4.11 — Async State Has Three States: Loading, Error, Success — Always

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.11 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.28` (state management) |
| **Enforced By** | Code Review |

**Standard:**
Every asynchronous operation in the UI has three explicitly rendered states: loading (skeleton or spinner), error (error message with actionable guidance), and success. Empty state is a fourth state for list/collection responses. An async operation without an explicit loading or error state is a code review block.

**Rationale:**
Async operations without loading states appear broken to users on slow connections. Operations without error states leave users with no recovery path when network requests fail. Skeleton loaders are preferred over spinners — they prevent layout shift on data load.

**Anti-Patterns:**
- `AP-S4.11a` — Rendering nothing while a request is in-flight — users see a blank page and cannot distinguish between "loading" and "broken."
- `AP-S4.11b` — `console.log(error)` as the only error handling in a UI component — the user sees nothing; the developer sees everything.

**Cross-References:** `S4.28` (TanStack Query / Angular Signals), `S4.46` (form state management)

---

### S4.12 — No Business Logic in UI Components

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.12 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.4` (smart/presentational separation) |
| **Enforced By** | Code Review |

**Standard:**
UI components (React components, Angular components) contain rendering logic only. Business logic — calculations, data transformations, validation rules, multi-step operations — lives in services, hooks, or utility functions. A component that requires understanding domain logic to understand its rendering is incorrectly structured.

**Anti-Patterns:**
- `AP-S4.12a` — Interest rate calculation inside a Balance component — the calculation logic cannot be tested without rendering the component; business logic is coupled to UI lifecycle.

**Cross-References:** `S4.4` (smart/presentational separation), `S2.1` (service layer owns business logic)

---

## Part 2 — Styling: Tailwind + Custom CSS (`S4.13`–`S4.17`)

The styling philosophy for all KSDRILL SA frontends is explicit: Tailwind CSS and Custom CSS are **both first-class tools**. Neither replaces the other. The combination produces interfaces that are maintainable and visually distinctive.

---

### S4.13 — Tailwind for Layout, Spacing, and Responsive Utilities

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.13 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | — |
| **Enforced By** | Code Review |

**Standard:**
Tailwind CSS utility classes govern all layout (flexbox, grid), spacing (padding, margin, gap), responsive breakpoints, and common state variants (hover, focus, disabled). Tailwind is the default tool for structure — it produces consistent spacing and responsive behaviour with minimal CSS overhead.

**Rationale:**
Tailwind's utility-first approach is highly maintainable for layout concerns. Every developer reading a component can understand its layout without navigating to a separate CSS file. Responsive breakpoints are co-located with the markup that they govern.

**Anti-Patterns:**
- `AP-S4.13a` — Writing a custom CSS class for `margin-top: 16px` when `mt-4` exists — unnecessary custom CSS for standard spacing that Tailwind covers natively.

**Cross-References:** `S4.14` (custom CSS for brand), `S4.15` (no duplication between Tailwind and custom CSS)

---

### S4.14 — Custom CSS for Brand Identity, Design Language, and Complex Visual Patterns

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.14 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.13` (Tailwind for layout) |
| **Enforced By** | Code Review |

**Standard:**
Custom CSS (via CSS Modules in Next.js or component styles in Angular) governs brand identity tokens (custom colour palettes, typography scales, shadow systems), complex animations and transitions, design patterns that require precision beyond Tailwind's utility vocabulary, and system-specific visual languages. Custom CSS transforms a Tailwind-structured interface into a KSDRILL SA platform — without it, all platforms look identical.

**Rationale:**
Tailwind produces structurally consistent but visually generic interfaces. Custom CSS is what makes FundsLink look like FundsLink and Maphophe look like Maphophe. The two tools serve different purposes; both are needed.

**Anti-Patterns:**
- `AP-S4.14a` — Applying brand colours only through Tailwind `arbitrary values` like `bg-[#1A2B3C]` — arbitrary values become unmaintainable at scale and bypass the design token system.
- `AP-S4.14b` — Using Custom CSS for layout concerns that Tailwind covers — duplicates the styling system and creates conflicts between Tailwind and custom CSS specificity.

**Cross-References:** `S4.13` (Tailwind for layout), `S4.15` (no duplication), `S4.16` (design tokens)

---

### S4.15 — No Duplication Between Tailwind and Custom CSS

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.15 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.13` (Tailwind), `S4.14` (custom CSS) |
| **Enforced By** | Code Review |

**Standard:**
A style property is defined in exactly one place — either Tailwind utility class or Custom CSS, never both. When both define the same property on the same element, one of them is wrong. Specificity conflicts between Tailwind and custom CSS are a code review block.

**Rationale:**
Duplication creates unpredictable specificity battles. The winning style depends on load order, which changes with build output. The solution is clear separation of responsibility.

**Anti-Patterns:**
- `AP-S4.15a` — A component that has both `class="flex items-center"` and a custom CSS `.component { display: flex; align-items: center; }` — one will override the other depending on build output order.

**Cross-References:** `S4.13` (Tailwind), `S4.14` (custom CSS)

---

### S4.16 — Design Tokens as CSS Custom Properties — System-Specific

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.16 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.14` (custom CSS) |
| **Enforced By** | Code Review |

**Standard:**
Brand colours, typography scales, shadow systems, and spacing tokens are defined as CSS custom properties (`--color-primary`, `--font-display`, etc.) in a root stylesheet. Tailwind's `tailwind.config.js` references these custom properties via the `theme.extend` section. Custom CSS references them directly. This creates a single source of truth for all design tokens that works across both styling systems.

**Anti-Patterns:**
- `AP-S4.16a` — Hardcoding colour hex values in both Tailwind config and custom CSS independently — changing the brand primary colour requires finding and replacing in two separate systems.

**Cross-References:** `S4.13` (Tailwind config), `S4.14` (custom CSS)

---

### S4.17 — No Emojis in UI Code — Lucide Icons First

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.17 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | — |
| **Enforced By** | ESLint `no-emoji-in-ui` rule |

**Standard:**
Emojis are forbidden in UI component code (JSX, Angular templates, CSS `content` values). Icon priority: Lucide icons → Heroicons → custom inline SVG. Font Awesome is not used. Emojis are permitted only in user-generated content display (where the user themselves entered the emoji).

**Rationale:**
Emoji rendering varies across operating systems and browsers — the same emoji looks different on iOS, Android, Windows, and macOS. Icon libraries render consistently across all environments.

**Anti-Patterns:**
- `AP-S4.17a` — Using `🔒` as a lock icon in a security badge component — renders differently on every OS; use `<LockIcon />` from Lucide instead.

**Cross-References:** `S4.21` (accessibility — icons need aria-labels)

---

## Part 3 — Interaction & Accessibility (`S4.18`–`S4.27`)

Accessibility is not an optional enhancement — it is a constitutional requirement. WCAG 2.1 AA is the minimum. Keyboard navigation, touch targets, colour contrast, and motion reduction are governed standards, not guidelines.

---

### S4.18 — Touch Targets — 44×44px Mobile, 32×32px Desktop

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.18 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.2` (mobile-first) |
| **Enforced By** | axe-core CI scan · Code Review |

**Standard:**
Every interactive element (button, link, icon button, checkbox, toggle) must be at minimum 44×44px on mobile and 32×32px on desktop. Use padding, not `width/height`, to meet this requirement without breaking visual layout.

**Rationale:**
Touch targets below 44px cause tap errors on mobile — users tap adjacent elements or miss entirely. This is a primary usability failure on touch devices.

**Anti-Patterns:**
- `AP-S4.18a` — An icon button with `w-4 h-4` and no padding — 16px touch target; users will tap-miss on every mobile device.

**Cross-References:** `S4.2` (mobile-first), `S7.20` (accessibility CI gate)

---

### S4.19 — Full Keyboard Accessibility — Tab, Enter, Escape, Arrow Keys

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.19 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | — |
| **Enforced By** | axe-core CI scan · Manual keyboard audit |

**Standard:**
Every interactive element is reachable and operable by keyboard alone. Tab navigates focus, Enter activates, Escape closes dialogs and drawers. Custom components (dropdowns, modals, date pickers) implement full ARIA keyboard patterns. Focus never disappears (no `outline: none` without a custom focus indicator).

**Rationale:**
Keyboard-only navigation is required by users with motor impairments, power users, and screen reader users. A UI that cannot be keyboard-navigated fails an entire user population.

**Anti-Patterns:**
- `AP-S4.19a` — `*:focus { outline: none; }` in global CSS — removes all keyboard focus indicators across the entire application.
- `AP-S4.19b` — Custom dropdown that does not close on Escape — violates ARIA dialog pattern and traps keyboard users inside the dropdown.

**Cross-References:** `S4.21` (ARIA labels), `S7.20` (accessibility CI)

---

### S4.20 — Body Text Minimum 16px

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.20 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.2` (mobile-first) |
| **Enforced By** | axe-core CI scan |

**Standard:**
All paragraph text, form labels, input values, and descriptions are minimum 16px. Captions and metadata may go to 12px. `text-xs` (12px) is forbidden on body copy or form labels. iOS Safari zooms into inputs with `font-size < 16px` — this standard also prevents unwanted mobile zoom.

**Anti-Patterns:**
- `AP-S4.20a` — Form input with `font-size: 14px` — iOS Safari automatically zooms the viewport into the input on focus, breaking the layout.

**Cross-References:** `S4.2` (mobile-first), `S4.15` (WCAG contrast)

---

### S4.21 — WCAG 2.1 AA Colour Contrast — 4.5:1 for Normal Text

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.21 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.16` (design tokens) |
| **Enforced By** | axe-core CI scan |

**Standard:**
All text meets WCAG 2.1 AA minimum contrast ratios: 4.5:1 for text below 18px, 3:1 for text 18px or larger and bold text. Automated contrast checks run in CI using axe-core. No exception for brand colours — if the brand colour does not meet contrast requirements, the brand colour is adjusted.

**Anti-Patterns:**
- `AP-S4.21a` — Light grey text on white background "for aesthetics" — low-contrast text is inaccessible regardless of aesthetic intent.

**Cross-References:** `S4.16` (design tokens — colours must be defined to be validated)

---

### S4.22 — Respect `prefers-reduced-motion` — All Animations Conditional

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.22 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | — |
| **Enforced By** | Code Review |

**Standard:**
All animations and transitions are wrapped in a `@media (prefers-reduced-motion: no-preference)` check. When `prefers-reduced-motion: reduce` is set, animations are disabled or reduced to instant transitions. This applies to CSS animations, JavaScript-driven animations, and scroll-based effects.

**Anti-Patterns:**
- `AP-S4.22a` — Motion-heavy page entrance animations without a `prefers-reduced-motion` check — causes nausea, migraines, and vestibular disorder symptoms in users who have enabled reduced motion.

**Cross-References:** `S4.14` (custom CSS governs animations)

---

### S4.23 — ARIA Labels on All Icon-Only Interactive Elements

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.23 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.17` (Lucide icons), `S4.19` (keyboard accessibility) |
| **Enforced By** | axe-core CI scan |

**Standard:**
Every icon-only button or link has an `aria-label` describing its action. Icon buttons without visible text that lack `aria-label` are invisible to screen readers. The label describes the action, not the icon: `aria-label="Close dialog"` not `aria-label="X icon"`.

**Anti-Patterns:**
- `AP-S4.23a` — `<button><CloseIcon /></button>` without `aria-label="Close"` — screen reader announces "button" with no description of its purpose.

**Cross-References:** `S4.17` (icons), `S4.19` (keyboard accessibility)

---

### S4.24 — Skeleton Loaders — Preferred Over Spinners for Content Loading

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.24 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.11` (async state — three states) |
| **Enforced By** | Code Review |

**Standard:**
Content loading states use skeleton loaders (placeholder shapes matching the expected content layout) as the preferred pattern. Spinners are used for action feedback (button click, form submission). Skeleton loaders prevent layout shift when content loads and produce a better perceived performance experience.

**Anti-Patterns:**
- `AP-S4.24a` — A loading spinner occupying the entire content area — causes layout shift when the actual content loads at a different height.

**Cross-References:** `S4.11` (three async states)

---

### S4.25 — Zod Validation on Every API Response — Next.js

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.25 |
| **Priority**    | Critical |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S2.14` (Zod/Pydantic parity) |
| **Enforced By** | Code Review |

**Standard:**
Every API response consumed by the Next.js frontend is validated against a Zod schema before the data is used in state or rendered in UI. Unvalidated API responses are treated as untrusted data. Zod schemas for API responses are co-located with the API client functions that fetch them.

**Anti-Patterns:**
- `AP-S4.25a` — `const data = await response.json()` used directly in components without Zod validation — API shape changes cause silent runtime errors instead of caught schema validation failures.

**Cross-References:** `S2.14` (OpenAPI-first contract parity), `S4.46` (form validation)

---

### S4.26 — Angular Validators on All API Responses — Angular Stack

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.26 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S2.14` (Zod/Pydantic parity), `S4.55` (Angular services) |
| **Enforced By** | Code Review |

**Standard:**
Angular services validate API responses using TypeScript interfaces with runtime type guards before passing data to components. Pydantic models on the FastAPI side and TypeScript interfaces on the Angular side maintain schema parity. Any response that fails validation is treated as an error and handled via the error state, not silently consumed.

**Anti-Patterns:**
- `AP-S4.26a` — Casting API responses with `as SomeType` without runtime validation — TypeScript type assertions do not validate data at runtime; a schema change produces a runtime error in production.

**Cross-References:** `S2.14` (Pydantic/Zod parity), `S4.55` (Angular service layer)

---

### S4.27 — No `console.log` in Production — Sentry for Error Tracking

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.27 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.65` (frontend observability) |
| **Enforced By** | ESLint `no-console` rule · CI |

**Standard:**
`console.log`, `console.error`, and `console.warn` are forbidden in production code. Errors and unexpected states are reported to Sentry via the frontend error boundary. Development-only logging uses an environment-gated logger utility that no-ops in production.

**Anti-Patterns:**
- `AP-S4.27a` — `console.error(error)` as the catch block in an API call — the error is swallowed; no alert is triggered; no error tracking captures it.

**Cross-References:** `S4.65` (frontend Sentry integration), `S4.66` (error boundaries)

---

## Part 4 — State & Data Management (`S4.28`–`S4.45`)

State management is the most common source of frontend complexity. These standards govern the tool selection, the scope boundaries, and the patterns that make state predictable.

---

### S4.28 — TanStack Query for Server State — Next.js Stack

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.28 |
| **Priority**    | Critical |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.4` (smart/presentational separation) |
| **Enforced By** | Code Review |

**Standard:**
TanStack Query (React Query) manages all server state in Next.js applications. Server state (API data, remote data) is never managed with `useState` + `useEffect` combinations. TanStack Query provides caching, background refetching, loading/error states, and mutation tracking — all concerns that `useState` + `useEffect` patterns implement incorrectly.

**Anti-Patterns:**
- `AP-S4.28a` — `const [data, setData] = useState(null); useEffect(() => { fetch(url).then(r => r.json()).then(setData) }, [])` — no loading state, no error state, no caching, no refetch on window focus, stale data on navigation.

**Cross-References:** `S4.11` (three async states), `S4.29` (Zustand for client state)

---

### S4.29 — Zustand for Client State — Next.js Stack

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.29 |
| **Priority**    | High |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.28` (TanStack Query for server state) |
| **Enforced By** | Code Review |

**Standard:**
Zustand manages client-side application state (UI state, modal open/close, filter selections, wizard step, user preferences). Redux is not used. Context API is used only for dependency injection (themes, i18n) — not for state management. The separation between server state (TanStack Query) and client state (Zustand) is maintained strictly.

**Anti-Patterns:**
- `AP-S4.29a` — Caching API responses in Zustand alongside UI state — duplicates TanStack Query's cache management without its invalidation, deduplication, or background refetch capabilities.

**Cross-References:** `S4.28` (TanStack Query for server state)

---

### S4.30 — Angular Signals for Reactive State — Angular Stack

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.30 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.4` (smart/presentational separation) |
| **Enforced By** | Code Review |

**Standard:**
Angular Signals are the primary state management tool for all new Angular code. RxJS Observables are used for HTTP requests, WebSocket streams, and complex async compositions. BehaviorSubject is used only where signals cannot serve the use case. NgRx is not introduced unless the system complexity specifically justifies it, documented in an ADR.

**Anti-Patterns:**
- `AP-S4.30a` — Using BehaviorSubject for simple local component state that a Signal handles more cleanly — over-engineering that makes the state harder to reason about.

**Cross-References:** `S4.52` (Angular OnPush), `S4.55` (Angular services)

---

### S4.31 — Zustand and Signal Stores Are Flat — No Nested State Trees

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.31 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.29` (Zustand), `S4.30` (Signals) |
| **Enforced By** | Code Review |

**Standard:**
Client state stores are flat — no deeply nested state objects. Nested state requires nested update logic that is error-prone. If state naturally nests, separate it into distinct stores or signals with explicit cross-references.

**Anti-Patterns:**
- `AP-S4.31a` — A single Zustand store with `user.preferences.notifications.email.daily` depth — immutable update of deeply nested state is complex and error-prone.

**Cross-References:** `S4.29` (Zustand), `S4.30` (Signals)

---

### S4.32 — No Prop Drilling Beyond Two Levels — Context or State Store

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.32 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.4` (smart/presentational), `S4.29` (Zustand), `S4.30` (Signals) |
| **Enforced By** | Code Review |

**Standard:**
Props that need to pass through more than two component levels are moved to a context provider or state store. Prop drilling beyond two levels creates implicit coupling between components that should have no dependency on each other's data needs.

**Anti-Patterns:**
- `AP-S4.32a` — Passing `currentUser` through five component levels when a Zustand store makes it directly available — every intermediate component takes a dependency on a prop it doesn't use.

**Cross-References:** `S4.4` (component separation), `S4.29` (Zustand), `S4.30` (Signals)

---

### S4.33–S4.45 — Additional State Standards

> **S4.33** — API error responses are always surfaced to the user with an actionable message — never silently swallowed. Error messages use plain language: "Could not load applications — try again" not "Error 500."

> **S4.34** — Optimistic updates include rollback logic — if the API call fails, the UI reverts to its pre-update state and displays an error.

> **S4.35** — Data fetched for display is never mutated directly — TanStack Query invalidation or Signal derivation produces new values; mutation of cache data directly is forbidden.

> **S4.36** — Infinite scroll and paginated lists use cursor-based pagination (aligned with S2.39) — offset pagination breaks when items are added or removed between pages.

> **S4.37** — Local state that does not need to survive page navigation is component-scoped, not store-scoped — not everything belongs in a global store.

> **S4.38** — WebSocket connections are managed in services (Angular) or custom hooks (Next.js), not in components — components subscribe to the stream, they do not own the connection.

> **S4.39** — Derived state is computed, not stored — if a value can be derived from existing state, it is a computed value, not a stored value.

> **S4.40** — Real-time feature state falls back to polling on WebSocket disconnect — fallback prevents silent data staleness.

> **S4.41** — Forms are not server state — form inputs and draft state live in local component state or form libraries, not in TanStack Query or global stores.

> **S4.42** — Feature flag state is read from the database via API on session start — never hardcoded in frontend code.

> **S4.43** — Dark mode preference is stored in localStorage and applied before first paint — prevents flash of wrong theme.

> **S4.44** — URL state (filters, pagination, sort) is encoded in query parameters — enables deep linking and browser back/forward navigation to work correctly.

> **S4.45** — State resets on route navigation unless explicitly preserved — stale state from a previous route contaminating a new route is a code review block.

---

## Part 5 — Form Standards (`S4.46`–`S4.51`)

---

### S4.46 — React Hook Form + Zod for All Forms — Next.js Stack

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.46 |
| **Priority**    | Critical |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.25` (Zod validation), `S2.14` (contract parity) |
| **Enforced By** | Code Review |

**Standard:**
All forms use React Hook Form with Zod for validation. Uncontrolled form state management with `useState` per field is forbidden. Zod schemas define validation rules and TypeScript types simultaneously — the schema is the single source of truth for form shape.

**Anti-Patterns:**
- `AP-S4.46a` — `const [email, setEmail] = useState("")` for every form field individually — uncontrolled form state management that does not provide validation, error state, or submit handling.

**Cross-References:** `S4.25` (Zod on API responses), `S2.14` (Zod/Pydantic contract parity)

---

### S4.47 — Angular Reactive Forms for All Forms — Angular Stack

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.47 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.26` (Angular validators) |
| **Enforced By** | Code Review |

**Standard:**
All Angular forms use Reactive Forms (`FormBuilder`, `FormGroup`, `FormControl`). Template-driven forms are forbidden. Reactive Forms are testable, provide synchronous validation, and enable complex validation patterns. Form state is managed by the `FormGroup` — not by component properties.

**Anti-Patterns:**
- `AP-S4.47a` — `[(ngModel)]` two-way binding for form inputs — template-driven forms are untestable without full component rendering and cannot express complex cross-field validation.

**Cross-References:** `S4.26` (Angular validators), `S4.52` (standalone components)

---

### S4.48 — Client-Side Validation Is UX — Server-Side Is Authoritative

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.48 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.46` (React Hook Form), `S4.47` (Reactive Forms), `S2.23` (backend validation) |
| **Enforced By** | Code Review |

**Standard:**
Client-side form validation provides immediate user feedback (UX). Server-side validation is the authoritative gate. Every form submission is validated on the server — client-side validation is never the security or data integrity layer.

**Anti-Patterns:**
- `AP-S4.48a` — Removing a required field from the Zod schema without updating the Pydantic model — client no longer validates the field but the server still rejects it; or vice versa, creating a gap.

**Cross-References:** `S2.23` (backend Zod/Pydantic validation), `S4.25` (Zod)

---

### S4.49–S4.51 — Additional Form Standards

> **S4.49** — Form errors display inline, adjacent to the field that caused them — not as a modal or toast. Toast is reserved for async operation feedback (save success, delete confirmation), not form validation.

> **S4.50** — Multi-step forms preserve completed step data on back navigation — users never lose work by clicking back.

> **S4.51** — Form submission disables the submit button and shows a loading indicator during the API call — prevents double-submission.

---

## Part 6 — Angular-Specific Standards (`S4.52`–`S4.60`)

---

### S4.52 — Standalone Components — Preferred Over NgModules

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.52 |
| **Priority**    | High |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.1` (Angular stack) |
| **Enforced By** | Code Review |

**Standard:**
All new Angular components, directives, and pipes use the `standalone: true` pattern. NgModules are used only for third-party library integration that requires module-based bootstrapping. Standalone components have explicit imports and are independently testable.

**Anti-Patterns:**
- `AP-S4.52a` — Creating a new NgModule to organise a feature when a standalone component with explicit imports achieves the same result — NgModules add indirection without benefit in modern Angular.

**Cross-References:** `S4.30` (Signals), `S4.47` (Reactive Forms)

---

### S4.53 — OnPush Change Detection — All Components

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.53 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.30` (Signals), `S4.52` (standalone) |
| **Enforced By** | Code Review · Angular lint rules |

**Standard:**
All Angular components use `ChangeDetectionStrategy.OnPush`. Default change detection is forbidden in production Angular code. OnPush components only re-render when their input references change, an async pipe emits, or a Signal changes — this is a prerequisite for performant Angular applications.

**Anti-Patterns:**
- `AP-S4.53a` — `ChangeDetectionStrategy.Default` on components — Angular re-checks every component on every event, creating performance degradation at scale.

**Cross-References:** `S4.30` (Signals trigger OnPush re-render correctly), `S4.52` (standalone components)

---

### S4.54 — Angular Route Guards — UX Protection Only (Server Is Authoritative)

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.54 |
| **Priority**    | Standard |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.19` (C3 — route guards are UX only), `S3.17` (FastAPI Depends() is authoritative) |
| **Enforced By** | Code Review |

**Standard:**
Angular route guards redirect unauthenticated users to the login page for UX purposes. They are not the authorisation mechanism. The FastAPI `Depends()` layer is the authoritative security gate. See S3.19 for the security rationale.

**Anti-Patterns:**
- `AP-S4.54a` — Treating route guard bypass as a security incident — the server-side auth prevented data access; the route guard only prevented the Angular navigation.

**Cross-References:** `S3.19` (C3 Auth — route guards are UX), `S3.17` (FastAPI Depends())

---

### S4.55 — Angular Services for All API Calls and State — No Direct HTTP in Components

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.55 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.4` (smart/presentational separation) |
| **Enforced By** | Code Review |

**Standard:**
All API calls, state management, and business logic live in injectable Angular services. Components inject services and subscribe to their outputs. Direct `HttpClient` calls inside components are forbidden. This makes components testable without mocking HTTP.

**Anti-Patterns:**
- `AP-S4.55a` — `this.http.get('/api/students')` inside an Angular component constructor — the component cannot be unit-tested without a mock HTTP backend.

**Cross-References:** `S4.4` (smart/presentational), `S4.30` (Signals in services)

---

### S4.56 — Vitest for Angular Unit Tests — Never Karma or Jasmine

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.56 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S7.2` (test runner assignment) |
| **Enforced By** | CI · package.json audit |

**Standard:**
Angular unit tests use Vitest with `@analogjs/vitest-angular`. Karma and Jasmine are not installed or used. Playwright handles E2E and visual regression. This aligns the Angular testing toolchain with the Next.js testing approach (both use Vite-compatible tooling).

**Anti-Patterns:**
- `AP-S4.56a` — Keeping Karma in `angular.json` alongside Vitest — dual test runner configurations produce inconsistent results and CI complexity.

**Cross-References:** `S7.2` (testing toolchain assignment), `S7.8` (Angular TestBed patterns)

---

### S4.57–S4.60 — Additional Angular Standards

> **S4.57** — The `async` pipe is used in templates to subscribe to Observables — manual subscriptions in `ngOnInit` that are not unsubscribed are a memory leak.

> **S4.58** — Angular CLI generates all components, services, and guards — no hand-crafted Angular boilerplate.

> **S4.59** — Environment files (`environment.ts`, `environment.prod.ts`) reference only variable names, not values — actual values come from Railway Secrets via build configuration.

> **S4.60** — `ngFor` always uses a `trackBy` function — prevents full re-render of list items on data update.

---

## Part 7 — MVP Realism (`S4.61`–`S4.64`)

---

### S4.61 — shadcn/ui for Next.js Component Library — No Custom Primitives from Scratch

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.61 |
| **Priority**    | High |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.19` (keyboard accessibility) |
| **Enforced By** | Code Review |

**Standard:**
shadcn/ui is the Next.js component library. Buttons, forms, dialogs, dropdowns, and tables use shadcn/ui as the base. Custom components extend or compose shadcn/ui primitives. Building accessible, keyboard-navigable UI primitives from scratch in v1 is not justified when shadcn/ui provides them correctly.

**Anti-Patterns:**
- `AP-S4.61a` — Building a custom accessible Modal component for v1 when shadcn/ui's `<Dialog>` already implements the ARIA dialog pattern correctly.

**Cross-References:** `S4.19` (keyboard accessibility included in shadcn/ui)

---

### S4.62–S4.64 — Additional MVP Realism Standards

> **S4.62** — Admin dashboards are Group 3 features — not built before the primary user workflow is complete and shipped.

> **S4.63** — Animation libraries (Framer Motion, GSAP) are deferred to v2 unless the animation is core to the primary user workflow — no animation in v1 that is not directly tied to a user-facing functional interaction.

> **S4.64** — Frontend internationalisation (i18n) is not implemented in v1 for any system — the user base is English-speaking South African users; i18n is a v2 feature when the user base has been confirmed.

---

## Part 8 — Frontend Observability (`S4.65`–`S4.70`)

---

### S4.65 — Sentry Frontend Integration — Error Capture and User Context

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.65 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S2.56` (structured logging), `S8.12` (Sentry backend integration) |
| **Enforced By** | Code Review · Sentry project verification |

**Standard:**
Sentry is initialised in every frontend application with: DSN from environment variable, release version from build metadata, user context set on authentication (id, role — never email or PII beyond what Sentry's PII scrubbing can handle), and environment tag (development/staging/production). Every unhandled Promise rejection and React/Angular error boundary catch is sent to Sentry.

**Anti-Patterns:**
- `AP-S4.65a` — Sentry `console.error` integration without explicit user context — errors arrive in Sentry with no way to identify affected users or correlate with backend errors from the same session.

**Cross-References:** `S2.56` (X-Request-ID for cross-service correlation), `S4.66` (error boundaries)

---

### S4.66 — Error Boundaries on Every Route and Async Feature Area

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.66 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.65` (Sentry), `S4.11` (three async states) |
| **Enforced By** | Code Review |

**Standard:**
React error boundaries wrap every page/route and every major async feature area in Next.js. Angular's global error handler and component-level error handling cover Angular systems. An uncaught render error must not take down the entire application — it shows an error UI for that section only.

**Anti-Patterns:**
- `AP-S4.66a` — No error boundary around the dashboard feature area — an error in one widget unmounts the entire dashboard.

**Cross-References:** `S4.65` (Sentry captures boundary errors), `S4.11` (three states)

---

### S4.67–S4.70 — Additional Observability Standards

> **S4.67** — Vercel Analytics is enabled on all Next.js deployments — Core Web Vitals (LCP, CLS, FID) are tracked per deployment and reviewed post-deploy.

> **S4.68** — `X-Request-ID` header is attached to every frontend API call — enables correlation between frontend Sentry errors and backend log entries for the same request.

> **S4.69** — Performance budget: Lighthouse performance score ≥ 80 on mobile in CI — a score below 80 is a build warning, below 70 is a build failure.

> **S4.70** — Real-time features log connection and disconnection events to Sentry with user context — enables diagnosing WebSocket reliability issues in production.

---

## Part 9 — Group-Build Methodology (`S4.71`–`S4.78`)

The group-build methodology governs how feature groups are structured and sequenced within a sprint. It is the execution layer for the feature lifecycle defined in C1 Part 6.

---

### S4.71 — Feature Groups Define Build Sequence Within Each Sprint

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.71 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S1.27` (feature lifecycle), `S9.8` (feature group hierarchy) |
| **Enforced By** | Sprint planning · Code Review |

**Standard:**
Within each sprint, frontend features are built in group order: Group 1 (core primary workflow) → Group 2 (supporting primary workflow) → Group 3 (secondary features). No Group 3 feature begins before Group 1 and 2 features for that sprint are complete and merged. Group ordering within the frontend build sequence follows the same logic as the platform-level group ordering in C9.

**Anti-Patterns:**
- `AP-S4.71a` — Building the admin dashboard (Group 3) before the primary submission form (Group 1) is complete — when Group 1 encounters a blocking issue, Group 3 work is wasted.

**Cross-References:** `S1.27` (feature lifecycle), `S9.9` (Groups 1+2 in v1 only)

---

### S4.72–S4.78 — Group-Build Standards

> **S4.72** — Each feature group has one designated owner who signs off on the group's completion before the next group begins.

> **S4.73** — Group completion criteria: all standards pass, all tests pass, CI green, PR merged to main, preview deployment functional.

> **S4.74** — Group 1 features ship before any Group 2 feature is started within the same sprint.

> **S4.75** — Cross-group dependencies are documented in the feature proposal — if Group 2 depends on Group 1 data, this is explicit and tracked.

> **S4.76** — A group that slips (incomplete at sprint end) is moved to the next sprint as Group 1 priority — partial groups are never shipped.

> **S4.77** — Group retrospective: after each group ships, 30 minutes reviewing what the group revealed about the next group's requirements — not a process ceremony, a design input.

> **S4.78** — Group build history is tracked in the system context file (`system-contexts/{system}-context.md`) — current group, completed groups, next group, open issues per group.

---

## Part 10 — Layer Build Order (`S4.79`–`S4.82`)

The layer build order governs the sequence in which frontend features are implemented within a feature. It is the enforcement mechanism for design-first development at the implementation level.

---

### S4.79 — Layer Build Order: Interface → Service → Component → UI

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.79 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S1.1` (design first), `S1.45` (author self-review checklist) |
| **Enforced By** | Code Review · Commit log audit |

**Standard:**
Every frontend feature is built in this exact layer order: (1) **Interface/Types** — TypeScript interfaces, Zod schemas, Angular service interfaces. (2) **Service layer** — Angular services or Next.js API client functions that communicate with the backend. (3) **Smart component** — the container that calls services and manages state. (4) **UI/Presentational components** — pure rendering components that receive data via props/inputs. Each layer is committed separately before the next begins.

**Rationale:**
Building in layer order forces the interface contract to be defined before implementation. It prevents the common failure of building UI and then discovering the data shape doesn't fit. It produces a commit history that documents how the feature was assembled, making code review and debugging dramatically more tractable.

**Anti-Patterns:**
- `AP-S4.79a` — Building the UI component first and working backwards to the API — the UI shape drives the API shape, reversing the contract-first principle.
- `AP-S4.79b` — One giant commit containing all four layers — layers cannot be reviewed independently; the build history is opaque.

**Cross-References:** `S1.1` (design first), `S2.7` (OpenAPI contract before endpoints), `S1.45` (self-review checklist includes layer verification)

---

### S4.80 — One Commit Per Layer — Not One Commit Per Feature

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S4.80 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S4.79` (layer build order), `S1.17` (conventional commits) |
| **Enforced By** | Code Review · Commit log audit |

**Standard:**
The commit log for a feature contains four commits minimum: one per layer from S4.79. Commits use conventional commit format. Each commit is pushed before the next layer begins. This is not bureaucratic process — it is the discipline that makes rollbacks layer-precise and code review layer-scoped.

**Rationale:**
A single `feat: add scholarship application form` commit containing 800 lines of changes across all layers cannot be meaningfully reviewed. Four layer-scoped commits of 200 lines each can be reviewed with precision. If the UI layer is wrong, only that commit needs revision.

**Anti-Patterns:**
- `AP-S4.80a` — `git add . && git commit -m "feat: application form"` after completing all four layers — unreviewed layer mixing; makes rollback impossible at the layer level.

**Cross-References:** `S4.79` (layer build order), `S1.17` (conventional commits)

---

### S4.81–S4.82 — Additional Layer Build Standards

> **S4.81** — TypeScript interfaces and Zod schemas defined in the first layer commit are never changed without updating the service and component layers in the same PR — interface changes cascade downward, never upward.

> **S4.82** — The layer build order applies to bug fixes as well as features — a bug fix that touches all four layers follows the same layer sequence in separate commits.

---

## Anti-Patterns Index

| ID | Description | Violated Standard | Severity |
|----|-------------|-------------------|----------|
| `AP-S4.1a` | Framework mixing (Angular CDK in Next.js or vice versa) | S4.1 | Critical |
| `AP-S4.2a` | `hidden md:block` on primary content | S4.2 | High |
| `AP-S4.2b` | Desktop-first CSS with mobile overrides | S4.2 | High |
| `AP-S4.3a` | Separate mobile subdomain or `/mobile/` routes | S4.3 | Critical |
| `AP-S4.4a` | API call inside a presentational component | S4.4 | Critical |
| `AP-S4.5a` | Logo hidden on mobile | S4.5 | High |
| `AP-S4.6a` | Accordion navigation on mobile | S4.6 | Critical |
| `AP-S4.6b` | Full-page overlay navigation | S4.6 | High |
| `AP-S4.7a` | `height: 100vh` on hero sections | S4.7 | High |
| `AP-S4.8a` | Sticky header without `scroll-padding-top` | S4.8 | Standard |
| `AP-S4.9a` | Page-level horizontal scroll from oversized element | S4.9 | High |
| `AP-S4.10a` | Visual regression CI tests at 1280px only | S4.10 | High |
| `AP-S4.11a` | Blank rendering during in-flight requests | S4.11 | High |
| `AP-S4.11b` | `console.log(error)` as sole error handling | S4.11 | High |
| `AP-S4.12a` | Business logic (calculations) inside UI components | S4.12 | Critical |
| `AP-S4.13a` | Custom CSS for standard spacing Tailwind covers | S4.13 | Standard |
| `AP-S4.14a` | Arbitrary Tailwind colour values bypassing design tokens | S4.14 | High |
| `AP-S4.14b` | Custom CSS for layout concerns Tailwind covers | S4.14 | Standard |
| `AP-S4.15a` | Both Tailwind class and custom CSS defining same property | S4.15 | High |
| `AP-S4.16a` | Colour hex values hardcoded independently in Tailwind and CSS | S4.16 | High |
| `AP-S4.17a` | Emoji used as icon in UI component code | S4.17 | Standard |
| `AP-S4.18a` | Icon button with 16px tap target | S4.18 | Critical |
| `AP-S4.19a` | `*:focus { outline: none }` in global CSS | S4.19 | Critical |
| `AP-S4.19b` | Custom dropdown that does not close on Escape | S4.19 | High |
| `AP-S4.20a` | Form input with `font-size: 14px` (iOS zoom) | S4.20 | High |
| `AP-S4.21a` | Low-contrast text "for aesthetics" | S4.21 | Critical |
| `AP-S4.22a` | Motion-heavy animations without `prefers-reduced-motion` | S4.22 | High |
| `AP-S4.23a` | Icon-only button without `aria-label` | S4.23 | High |
| `AP-S4.24a` | Full-area spinner causing layout shift on load | S4.24 | Standard |
| `AP-S4.25a` | API response used without Zod validation | S4.25 | Critical |
| `AP-S4.26a` | API response cast with `as SomeType` without runtime validation | S4.26 | Critical |
| `AP-S4.27a` | `console.error(error)` as sole catch block | S4.27 | High |
| `AP-S4.28a` | `useState` + `useEffect` for server state | S4.28 | Critical |
| `AP-S4.29a` | API responses cached in Zustand | S4.29 | High |
| `AP-S4.30a` | BehaviorSubject for simple local state | S4.30 | Standard |
| `AP-S4.31a` | Deeply nested state object in Zustand/Signal | S4.31 | Standard |
| `AP-S4.32a` | Props drilled through five component levels | S4.32 | Standard |
| `AP-S4.46a` | `useState` per field for form state | S4.46 | Critical |
| `AP-S4.47a` | `[(ngModel)]` two-way binding for forms | S4.47 | Critical |
| `AP-S4.48a` | Zod schema updated without updating Pydantic model | S4.48 | Critical |
| `AP-S4.52a` | New NgModule for feature organisation instead of standalone component | S4.52 | Standard |
| `AP-S4.53a` | `ChangeDetectionStrategy.Default` on Angular components | S4.53 | Critical |
| `AP-S4.54a` | Route guard treated as the security boundary | S4.54 | Critical |
| `AP-S4.55a` | `HttpClient` calls directly in Angular component | S4.55 | Critical |
| `AP-S4.56a` | Karma alongside Vitest in Angular project | S4.56 | High |
| `AP-S4.61a` | Building custom accessible Modal when shadcn/ui Dialog exists | S4.61 | Standard |
| `AP-S4.65a` | Sentry without user context | S4.65 | High |
| `AP-S4.66a` | No error boundary around major feature area | S4.66 | High |
| `AP-S4.71a` | Group 3 feature started before Group 1 complete | S4.71 | High |
| `AP-S4.79a` | UI-first layer build order | S4.79 | Critical |
| `AP-S4.79b` | One commit for all four layers | S4.79 | High |
| `AP-S4.80a` | `git add .` after completing all layers | S4.80 | High |

---

## Cross-Constitution Dependency Map

**This constitution depends on:**
| Dependency | Reason |
|------------|--------|
| `C0 — Constitutional Order` | Amendment protocol, terminology system |
| `C3 — Auth Constitution` | Route guards and auth state management derive from C3 auth strategy (S3.5–S3.19) |
| `C6 — Full-Stack Architecture` | Stack assignment determines which framework standards apply |

**The following constitutions depend on this one:**
| Dependent | Reason |
|-----------|--------|
| `C6 — Full-Stack Architecture` | Browser-side request flows use frontend standards |
| `C7 — Testing Constitution` | Frontend testing toolchain and test patterns derive from this constitution |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock — rebuilt from Frontend Constitution v18.0. Styling philosophy formalised: S4.13 (Tailwind for layout) + S4.14 (Custom CSS for brand) as co-equal first-class tools. Layer Build Order (S4.79–S4.82) added as Part 10. Terminology updated to Standards/Anti-Patterns. Standard IDs (`S4.N`) introduced. Group-build methodology formalised in Part 9. | Full system rebuild — HTML to Markdown, version reset. |

---

> **LOCKED — v1.0 — 2026-05-08**
>
> This document is locked. No standard may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Amendments take effect only after commit to `system-design-template`
> with a version bump and amendment log entry.
