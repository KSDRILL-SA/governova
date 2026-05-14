# C4 — Frontend Implementation Guide

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C4 — Frontend Implementation Guide                                 |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | Both Stacks                                                        |
| **Paired With**    | C4 — Frontend Constitution                                         |

---

> *"A standard tells you what must be true. This guide tells you how to make it true."*

---

## Opening Statement

This guide is the operational companion to C4. Every practice satisfies a specific C4 standard. The constitution contains the why; this guide contains the how. Read the constitution first. Use this guide when building.

---

## P4.1 — Project Setup (S4.1, S4.2)

### Next.js Stack

```bash
npx create-next-app@latest {system-name} \
  --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd {system-name}
npm install @tanstack/react-query zustand react-hook-form zod
npm install lucide-react @sentry/nextjs
npx shadcn@latest init
```

### Angular Stack

```bash
ng new {system-name} --standalone --style=css --routing --strict
cd {system-name}
npm install vitest @analogjs/vitest-angular
ng add @angular/cdk
npm install @sentry/angular lucide-angular
```

---

## P4.2 — Tailwind + Custom CSS Setup (S4.13, S4.14, S4.16)

### `tailwind.config.ts` — Reference design tokens

```typescript
import type { Config } from "tailwindcss"

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      // S4.16 — Reference CSS custom properties, not hardcoded values
      colors: {
        primary: "var(--color-primary)",
        secondary: "var(--color-secondary)",
        surface: "var(--color-surface)",
        "on-surface": "var(--color-on-surface)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "sans-serif"],
        display: ["var(--font-display)", "serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
    },
  },
}
export default config
```

### `src/styles/tokens.css` — System-specific design tokens

```css
/* S4.14, S4.16 — Brand design tokens as CSS custom properties */
:root {
  /* FundsLink example — each system has its own tokens */
  --color-primary: #1A4F8A;
  --color-primary-hover: #153F6E;
  --color-secondary: #F5A623;
  --color-surface: #FFFFFF;
  --color-surface-2: #F8F9FA;
  --color-on-surface: #1A1A2E;

  --font-sans: "Inter", system-ui, sans-serif;
  --font-display: "Playfair Display", serif;
  --font-mono: "JetBrains Mono", monospace;

  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.08);
  --shadow-elevated: 0 8px 24px rgba(0, 0, 0, 0.12);

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
}
```

---

## P4.3 — Layer Build Order Implementation (S4.79, S4.80)

### Step 1 — Interface Layer (commit: `feat(types): add scholarship application interfaces`)

```typescript
// src/lib/types/scholarship-application.ts
import { z } from "zod"

// S4.25 — Zod schema defines both validation and TypeScript type
export const ScholarshipApplicationSchema = z.object({
  studentId: z.string().cuid(),
  scholarshipId: z.string().cuid(),
  motivationLetter: z.string().min(100).max(2000),
  academicYear: z.number().int().min(2020).max(2030),
})

export type ScholarshipApplication = z.infer<typeof ScholarshipApplicationSchema>

// API response type (validated on receipt — S4.25)
export const ApplicationResponseSchema = z.object({
  id: z.string().cuid(),
  status: z.enum(["PENDING", "REVIEW", "APPROVED", "REJECTED"]),
  createdAt: z.string().datetime(),
})
export type ApplicationResponse = z.infer<typeof ApplicationResponseSchema>
```

### Step 2 — Service Layer (commit: `feat(service): add scholarship application service`)

```typescript
// src/lib/services/scholarship-application.service.ts — Next.js example

import { ScholarshipApplicationSchema, ApplicationResponseSchema } from "@/lib/types/scholarship-application"

export async function submitApplication(data: ScholarshipApplication) {
  const validated = ScholarshipApplicationSchema.parse(data)
  
  const res = await fetch("/api/v1/applications", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(validated),
  })

  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.error?.message ?? "Application submission failed")
  }

  // S4.25 — Validate API response before using
  return ApplicationResponseSchema.parse(await res.json())
}
```

### Step 3 — Smart Component (commit: `feat(component): add application form container`)

```tsx
// src/components/applications/ApplicationFormContainer.tsx
"use client"

import { useMutation } from "@tanstack/react-query"  // S4.28
import { submitApplication } from "@/lib/services/scholarship-application.service"
import { ApplicationForm } from "./ApplicationForm"

export function ApplicationFormContainer({ scholarshipId }: { scholarshipId: string }) {
  const mutation = useMutation({
    mutationFn: submitApplication,
    onSuccess: () => {
      // handle success
    },
  })

  return (
    <ApplicationForm
      scholarshipId={scholarshipId}
      onSubmit={mutation.mutate}
      isLoading={mutation.isPending}
      error={mutation.error?.message}
    />
  )
}
```

### Step 4 — UI Layer (commit: `feat(ui): add application form presentational component`)

```tsx
// src/components/applications/ApplicationForm.tsx — Presentational
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { ScholarshipApplicationSchema, ScholarshipApplication } from "@/lib/types/scholarship-application"

interface ApplicationFormProps {
  scholarshipId: string
  onSubmit: (data: ScholarshipApplication) => void
  isLoading: boolean  // S4.11 — explicit loading state
  error?: string      // S4.11 — explicit error state
}

export function ApplicationForm({ scholarshipId, onSubmit, isLoading, error }: ApplicationFormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<ScholarshipApplication>({
    resolver: zodResolver(ScholarshipApplicationSchema),  // S4.46
    defaultValues: { scholarshipId },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* S4.11 — Error state */}
      {error && <div role="alert" className="text-red-600">{error}</div>}
      
      {/* S4.20 — Minimum 16px text */}
      <label className="text-base font-medium">
        Motivation Letter
        <textarea
          {...register("motivationLetter")}
          className="mt-1 text-base"  /* S4.20 */
          aria-describedby="letter-error"
        />
      </label>
      {errors.motivationLetter && (
        <p id="letter-error" className="text-sm text-red-600">
          {errors.motivationLetter.message}
        </p>
      )}

      {/* S4.18 — 44px touch target, S4.51 — disable during submit */}
      <button
        type="submit"
        disabled={isLoading}
        className="min-h-[44px] px-6 py-3"
      >
        {isLoading ? <SkeletonButton /> : "Submit Application"}
      </button>
    </form>
  )
}
```

---

## P4.4 — Angular OnPush + Signals Pattern (S4.30, S4.53)

```typescript
// Angular component with OnPush + Signals (S4.30, S4.53)
import { Component, ChangeDetectionStrategy, inject } from "@angular/core"
import { ScholarshipService } from "../services/scholarship.service"

@Component({
  selector: "app-scholarship-list",
  standalone: true,  // S4.52
  changeDetection: ChangeDetectionStrategy.OnPush,  // S4.53
  template: `
    @if (scholarships().length === 0 && !loading()) {
      <p>No scholarships found</p>
    }
    @for (s of scholarships(); track s.id) {
      <app-scholarship-card [scholarship]="s" />
    }
    @if (loading()) {
      <app-skeleton-list />  <!-- S4.24 skeleton loader -->
    }
  `
})
export class ScholarshipListComponent {
  private service = inject(ScholarshipService)  // S4.55 — inject, not constructor
  
  protected scholarships = this.service.scholarships  // Signal from service
  protected loading = this.service.loading
}
```

---

## P4.5 — Sentry Integration (S4.65, S4.66)

### Next.js: `src/lib/sentry.ts`

```typescript
import * as Sentry from "@sentry/nextjs"

export function initSentry() {
  Sentry.init({
    dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
    environment: process.env.NODE_ENV,
    tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,
  })
}

export function setSentryUser(userId: string, role: string) {
  // S4.65 — user context, never PII beyond what Sentry scrubs
  Sentry.setUser({ id: userId, role })
}
```

### Error Boundary (`src/components/ErrorBoundary.tsx`)

```tsx
"use client"
import * as Sentry from "@sentry/nextjs"
import { Component, type ReactNode } from "react"

export class ErrorBoundary extends Component<
  { children: ReactNode; fallback: ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error) {
    Sentry.captureException(error)  // S4.65
  }

  render() {
    return this.state.hasError ? this.props.fallback : this.props.children
  }
}
```

---

## P4.6 — Tools & Commands Reference

| Task | Command |
|------|---------|
| Install shadcn component | `npx shadcn@latest add button` |
| Run visual regression tests | `npx playwright test tests/visual/ --project=chromium` |
| Run axe accessibility check | `npx playwright test tests/a11y/` |
| Check Tailwind purge | `npx tailwindcss --dry-run` |
| Angular standalone migration | `ng generate @angular/core:standalone` |
| Check bundle size | `npx @next/bundle-analyzer` |
| Lighthouse CI | `npx lhci autorun` |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock | Tailwind + Custom CSS dual-tool pattern formalised. Layer build order code examples added. Angular Signals + OnPush pattern documented. |

---

> **LOCKED — v1.0 — 2026-05-08**
