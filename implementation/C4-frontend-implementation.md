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

This guide is the operational companion to C4. Every practice here satisfies a specific C4 standard. The constitution answers what and why. This guide answers how. Read the constitution first. Use this guide while building.

Practices evolve as tooling evolves. Any practice change that would cause a constitutional standard to be violated requires a constitutional amendment first, then an update here.

---

## Table of Contents

| Section | Title |
|---------|-------|
| P4.1 | Project Setup — Next.js and Angular |
| P4.2 | Tailwind + Custom CSS Design Token System |
| P4.3 | Layer Build Order — Complete Feature Example |
| P4.4 | Angular Reactive Forms with Full Validation |
| P4.5 | Angular HTTP Service with Signals |
| P4.6 | Angular OnPush + Signals Pattern |
| P4.7 | TanStack Query — Queries and Mutations |
| P4.8 | Zustand Store Pattern |
| P4.9 | React Hook Form + Zod Pattern |
| P4.10 | MSW Setup for Next.js Tests |
| P4.11 | Playwright Visual Regression at 320/375/390px |
| P4.12 | axe-core Accessibility CI Gate |
| P4.13 | Sentry Integration — Frontend and Error Boundaries |
| P4.14 | Group-Build Workflow |
| P4.15 | Tools & Commands Reference |

---

## P4.1 — Project Setup (S4.1, S4.2)

### Next.js Stack Bootstrap

```bash
npx create-next-app@latest {system-name} \
  --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

cd {system-name}

# State management and data fetching
npm install @tanstack/react-query zustand

# Forms and validation
npm install react-hook-form zod @hookform/resolvers

# UI component library
npx shadcn@latest init

# Icons (S4.17 — Lucide first)
npm install lucide-react

# Error tracking (S4.65)
npm install @sentry/nextjs

# Testing
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
npm install --save-dev msw @playwright/test @axe-core/playwright
```

### Angular Stack Bootstrap

```bash
ng new {system-name} --standalone --style=css --routing --strict

cd {system-name}

# Testing — Vitest replaces Karma (S7.2, S4.56)
npm install --save-dev vitest @analogjs/vitest-angular @vitest/coverage-v8

# Icons (S4.17)
npm install lucide-angular

# Error tracking (S4.65)
npm install @sentry/angular

# Accessibility
npm install @angular/cdk

# Playwright E2E (S7.17)
npm install --save-dev @playwright/test @axe-core/playwright

# Remove Karma completely
npm uninstall karma karma-chrome-launcher karma-coverage karma-jasmine karma-jasmine-html-reporter
```

Remove from `angular.json`:
```json
// Delete the entire "test" architect target that references karma
// It will be replaced by vitest.config.ts
```

### `vitest.config.ts` — Angular

```typescript
import { defineConfig } from "vitest/config"
import angular from "@analogjs/vitest-angular/plugin"

export default defineConfig({
  plugins: [angular()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["src/test-setup.ts"],
    include: ["src/**/*.spec.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      thresholds: {
        lines: 75,        // S7.25 — Angular minimum
        branches: 75,
        functions: 75,
        statements: 75,
      },
    },
  },
})
```

---

## P4.2 — Tailwind + Custom CSS Design Token System (S4.13, S4.14, S4.15, S4.16)

### `src/styles/tokens.css` — System-specific brand tokens

```css
/* S4.14, S4.16 — Design tokens as CSS custom properties */
/* Every system has its own token set. This is the FundsLink example. */
:root {
  /* Brand colours */
  --color-primary:        #1A4F8A;
  --color-primary-hover:  #153F6E;
  --color-primary-light:  #E8F0FA;
  --color-secondary:      #F5A623;
  --color-secondary-hover:#E09515;
  --color-success:        #22C55E;
  --color-danger:         #EF4444;
  --color-warning:        #F59E0B;

  /* Surface colours */
  --color-surface:        #FFFFFF;
  --color-surface-2:      #F8F9FA;
  --color-surface-3:      #EFF2F7;
  --color-border:         #E2E8F0;
  --color-on-surface:     #1A1A2E;
  --color-on-surface-muted: #64748B;

  /* Typography */
  --font-sans:    "Inter", system-ui, -apple-system, sans-serif;
  --font-display: "Playfair Display", Georgia, serif;
  --font-mono:    "JetBrains Mono", "Fira Code", monospace;

  /* Spacing (extends Tailwind scale) */
  --space-xs:  4px;
  --space-sm:  8px;
  --space-md:  16px;
  --space-lg:  24px;
  --space-xl:  40px;
  --space-2xl: 64px;

  /* Elevation */
  --shadow-card:     0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-elevated: 0 4px 16px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.08);
  --shadow-overlay:  0 20px 60px rgba(0,0,0,0.15);

  /* Radii */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-full: 9999px;

  /* Transitions */
  --transition-fast:   150ms ease;
  --transition-normal: 250ms ease;
  --transition-slow:   400ms ease;
}
```

### `tailwind.config.ts` — References tokens, does not duplicate them

```typescript
import type { Config } from "tailwindcss"

const config: Config = {
  content: ["./src/**/*.{ts,tsx,html}"],
  theme: {
    extend: {
      // S4.16 — Reference CSS vars, never hardcode
      colors: {
        primary: {
          DEFAULT: "var(--color-primary)",
          hover:   "var(--color-primary-hover)",
          light:   "var(--color-primary-light)",
        },
        secondary: {
          DEFAULT: "var(--color-secondary)",
          hover:   "var(--color-secondary-hover)",
        },
        surface: {
          DEFAULT: "var(--color-surface)",
          "2":     "var(--color-surface-2)",
          "3":     "var(--color-surface-3)",
        },
        border:  "var(--color-border)",
        "on-surface": {
          DEFAULT: "var(--color-on-surface)",
          muted:   "var(--color-on-surface-muted)",
        },
        success: "var(--color-success)",
        danger:  "var(--color-danger)",
        warning: "var(--color-warning)",
      },
      fontFamily: {
        sans:    ["var(--font-sans)"],
        display: ["var(--font-display)"],
        mono:    ["var(--font-mono)"],
      },
      boxShadow: {
        card:     "var(--shadow-card)",
        elevated: "var(--shadow-elevated)",
        overlay:  "var(--shadow-overlay)",
      },
      borderRadius: {
        sm:   "var(--radius-sm)",
        md:   "var(--radius-md)",
        lg:   "var(--radius-lg)",
        xl:   "var(--radius-xl)",
      },
    },
  },
  plugins: [],
}
export default config
```

### Custom CSS component example — brand-specific card

```css
/* src/styles/components.css */
/* S4.14 — Custom CSS for design patterns Tailwind cannot express precisely */

.card-primary {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  transition: box-shadow var(--transition-normal);
}

.card-primary:hover {
  box-shadow: var(--shadow-elevated);
}

/* Brand heading with custom gradient — Tailwind arbitrary values would be unmaintainable */
.heading-brand {
  font-family: var(--font-display);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* S4.22 — Respect prefers-reduced-motion for all custom animations */
@media (prefers-reduced-motion: no-preference) {
  .animate-slide-up {
    animation: slide-up var(--transition-slow) ease-out;
  }

  @keyframes slide-up {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }
}
```

---

## P4.3 — Layer Build Order: Complete Feature Example (S4.79, S4.80)

### Feature: Scholarship Application Submission

#### Commit 1 — Interface Layer (`feat(types): add scholarship application interfaces`)

```typescript
// src/lib/types/scholarship-application.ts
import { z } from "zod"

// S4.25 — Zod defines type AND validates at once
export const ApplicationFormSchema = z.object({
  scholarshipId: z.string().cuid("Invalid scholarship ID"),
  studentId:     z.string().cuid("Invalid student ID"),
  motivation:    z.string().min(100, "Minimum 100 characters").max(2000),
  academicYear:  z.number().int().min(2024).max(2030),
  gpa:           z.number().min(0).max(4).multipleOf(0.01),
})
export type ApplicationFormData = z.infer<typeof ApplicationFormSchema>

// API response shape — validated on receipt (S4.25)
export const ApplicationSubmittedSchema = z.object({
  id:          z.string().cuid(),
  status:      z.enum(["PENDING", "UNDER_REVIEW", "APPROVED", "REJECTED"]),
  submittedAt: z.string().datetime(),
  reference:   z.string(),
})
export type ApplicationSubmitted = z.infer<typeof ApplicationSubmittedSchema>
```

#### Commit 2 — Service Layer (`feat(service): add scholarship application service`)

```typescript
// src/lib/services/scholarship-application.service.ts — Next.js
import { ApplicationFormSchema, ApplicationSubmittedSchema, ApplicationFormData } from "@/lib/types/scholarship-application"

export async function submitScholarshipApplication(
  data: ApplicationFormData
): Promise<ApplicationSubmitted> {
  const validated = ApplicationFormSchema.parse(data)

  const res = await fetch("/api/v1/applications", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(validated),
  })

  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.error?.message ?? "Submission failed")
  }

  // S4.25 — Always validate the response shape
  return ApplicationSubmittedSchema.parse(await res.json())
}

export async function getApplicationStatus(applicationId: string): Promise<ApplicationSubmitted> {
  const res = await fetch(`/api/v1/applications/${applicationId}`)
  if (!res.ok) throw new Error("Failed to fetch application status")
  return ApplicationSubmittedSchema.parse(await res.json())
}
```

#### Commit 3 — Smart Component (`feat(component): add application form container`)

```tsx
// src/components/applications/ApplicationFormContainer.tsx
"use client"
import { useMutation, useQueryClient } from "@tanstack/react-query" // S4.28
import { submitScholarshipApplication } from "@/lib/services/scholarship-application.service"
import { ApplicationFormData } from "@/lib/types/scholarship-application"
import { ApplicationForm } from "./ApplicationForm"
import * as Sentry from "@sentry/nextjs"

interface Props { scholarshipId: string; studentId: string }

export function ApplicationFormContainer({ scholarshipId, studentId }: Props) {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: submitScholarshipApplication,
    onSuccess: () => {
      // Invalidate related queries (S4.35 — never mutate cache directly)
      queryClient.invalidateQueries({ queryKey: ["applications", studentId] })
    },
    onError: (error) => {
      Sentry.captureException(error) // S4.65
    },
  })

  return (
    <ApplicationForm
      scholarshipId={scholarshipId}
      studentId={studentId}
      onSubmit={mutation.mutate}
      isLoading={mutation.isPending}   // S4.11 — explicit loading state
      isSuccess={mutation.isSuccess}
      error={mutation.error?.message}  // S4.11 — explicit error state
    />
  )
}
```

#### Commit 4 — UI Layer (`feat(ui): add scholarship application form`)

```tsx
// src/components/applications/ApplicationForm.tsx — Presentational (S4.4)
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { ApplicationFormSchema, ApplicationFormData } from "@/lib/types/scholarship-application"
import { LockIcon, SendIcon } from "lucide-react" // S4.17 — Lucide icons

interface ApplicationFormProps {
  scholarshipId: string
  studentId: string
  onSubmit: (data: ApplicationFormData) => void
  isLoading: boolean
  isSuccess: boolean
  error?: string
}

export function ApplicationForm({ scholarshipId, studentId, onSubmit, isLoading, isSuccess, error }: ApplicationFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ApplicationFormData>({
    resolver: zodResolver(ApplicationFormSchema), // S4.46
    defaultValues: { scholarshipId, studentId },
  })

  if (isSuccess) {
    return (
      <div role="status" className="card-primary p-6 text-center">
        <p className="text-success font-semibold text-base">Application submitted successfully</p>
      </div>
    )
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      noValidate
      className="card-primary p-6 space-y-4"
    >
      {/* S4.11 — Error state rendered explicitly */}
      {error && (
        <div role="alert" className="bg-red-50 border border-danger rounded-md p-3">
          <p className="text-danger text-base">{error}</p> {/* S4.20 — min 16px */}
        </div>
      )}

      <div className="space-y-1">
        {/* S4.20 — label text min 16px */}
        <label htmlFor="motivation" className="block text-base font-medium text-on-surface">
          Motivation Letter
          <span className="text-danger ml-1" aria-hidden="true">*</span>
        </label>
        <textarea
          id="motivation"
          rows={6}
          className="w-full rounded-md border border-border p-3 text-base" /* S4.20 */
          aria-describedby="motivation-error motivation-hint"
          aria-required="true"
          {...register("motivation")}
        />
        <p id="motivation-hint" className="text-sm text-on-surface-muted">
          100–2000 characters
        </p>
        {errors.motivation && (
          <p id="motivation-error" role="alert" className="text-sm text-danger">
            {errors.motivation.message}
          </p>
        )}
      </div>

      <div className="space-y-1">
        <label htmlFor="gpa" className="block text-base font-medium text-on-surface">
          Current GPA (0.00–4.00)
          <span className="text-danger ml-1" aria-hidden="true">*</span>
        </label>
        <input
          id="gpa"
          type="number"
          step="0.01"
          min="0"
          max="4"
          className="w-full rounded-md border border-border p-3 text-base" /* S4.20 */
          aria-required="true"
          {...register("gpa", { valueAsNumber: true })}
        />
        {errors.gpa && (
          <p role="alert" className="text-sm text-danger">{errors.gpa.message}</p>
        )}
      </div>

      {/* S4.18 — min-h-[44px] touch target; S4.51 — disabled during submit */}
      <button
        type="submit"
        disabled={isLoading}
        aria-busy={isLoading}
        className="w-full min-h-[44px] flex items-center justify-center gap-2 
                   bg-primary hover:bg-primary-hover text-white rounded-md
                   font-semibold text-base transition-colors
                   disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <span role="status">Submitting…</span>
        ) : (
          <>
            <SendIcon size={16} aria-hidden="true" />
            Submit Application
          </>
        )}
      </button>
    </form>
  )
}
```

---

## P4.4 — Angular Reactive Forms with Full Validation (S4.47, S4.48)

```typescript
// src/app/features/application/application-form.component.ts
import { Component, Output, EventEmitter, ChangeDetectionStrategy, inject } from "@angular/core"
import { ReactiveFormsModule, FormBuilder, Validators, AbstractControl } from "@angular/forms"
import { CommonModule } from "@angular/common"

function gpaRangeValidator(control: AbstractControl) {
  const v = parseFloat(control.value)
  if (isNaN(v) || v < 0 || v > 4) return { gpaRange: { min: 0, max: 4 } }
  return null
}

@Component({
  selector: "app-application-form",
  standalone: true,      // S4.52
  changeDetection: ChangeDetectionStrategy.OnPush, // S4.53
  imports: [ReactiveFormsModule, CommonModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="handleSubmit()" novalidate class="card-primary p-6 space-y-4">

      @if (errorMessage) {
        <div role="alert" class="bg-red-50 border border-danger rounded-md p-3">
          <p class="text-danger text-base">{{ errorMessage }}</p>
        </div>
      }

      <div class="space-y-1">
        <label for="motivation" class="block text-base font-medium">
          Motivation Letter <span class="text-danger" aria-hidden="true">*</span>
        </label>
        <textarea
          id="motivation"
          formControlName="motivation"
          rows="6"
          class="w-full rounded-md border border-border p-3 text-base"
          aria-required="true"
          [attr.aria-invalid]="isInvalid('motivation')"
        ></textarea>
        @if (isInvalid('motivation')) {
          <p role="alert" class="text-sm text-danger">
            {{ getError('motivation') }}
          </p>
        }
      </div>

      <div class="space-y-1">
        <label for="gpa" class="block text-base font-medium">
          Current GPA <span class="text-danger" aria-hidden="true">*</span>
        </label>
        <input
          id="gpa"
          type="number"
          step="0.01"
          formControlName="gpa"
          class="w-full rounded-md border border-border p-3 text-base"
          aria-required="true"
        />
        @if (isInvalid('gpa')) {
          <p role="alert" class="text-sm text-danger">
            {{ getError('gpa') }}
          </p>
        }
      </div>

      <button
        type="submit"
        [disabled]="isLoading || form.invalid"
        class="w-full min-h-[44px] bg-primary text-white rounded-md font-semibold text-base
               disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {{ isLoading ? 'Submitting…' : 'Submit Application' }}
      </button>
    </form>
  `
})
export class ApplicationFormComponent {
  // S4.55 — inject service, no HTTP in component
  private fb = inject(FormBuilder)

  @Output() submitted = new EventEmitter<{ motivation: string; gpa: number }>()
  isLoading = false
  errorMessage = ""

  form = this.fb.group({
    motivation: ["", [Validators.required, Validators.minLength(100), Validators.maxLength(2000)]],
    gpa:        [null, [Validators.required, gpaRangeValidator]],
  })

  isInvalid(field: string): boolean {
    const ctrl = this.form.get(field)
    return !!(ctrl?.invalid && (ctrl.dirty || ctrl.touched))
  }

  getError(field: string): string {
    const ctrl = this.form.get(field)
    if (!ctrl?.errors) return ""
    if (ctrl.errors["required"])    return "This field is required"
    if (ctrl.errors["minlength"])   return `Minimum ${ctrl.errors["minlength"].requiredLength} characters`
    if (ctrl.errors["maxlength"])   return `Maximum ${ctrl.errors["maxlength"].requiredLength} characters`
    if (ctrl.errors["gpaRange"])    return "GPA must be between 0.00 and 4.00"
    return "Invalid value"
  }

  handleSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched()
      return
    }
    this.submitted.emit(this.form.getRawValue() as { motivation: string; gpa: number })
  }
}
```

---

## P4.5 — Angular HTTP Service with Signals (S4.30, S4.55)

```typescript
// src/app/features/application/application.service.ts
import { Injectable, signal, inject } from "@angular/core"
import { HttpClient } from "@angular/common/http"
import { firstValueFrom } from "rxjs"

interface ApplicationSubmitted {
  id: string
  status: "PENDING" | "UNDER_REVIEW" | "APPROVED" | "REJECTED"
  submittedAt: string
  reference: string
}

@Injectable({ providedIn: "root" })
export class ApplicationService {
  private http = inject(HttpClient) // S4.55 — inject, never construct

  // S4.30 — Signals for reactive state
  private _loading   = signal(false)
  private _error     = signal<string | null>(null)
  private _submitted = signal<ApplicationSubmitted | null>(null)

  // Expose as readonly signals to components
  readonly loading   = this._loading.asReadonly()
  readonly error     = this._error.asReadonly()
  readonly submitted = this._submitted.asReadonly()

  async submitApplication(data: {
    scholarshipId: string
    studentId: string
    motivation: string
    gpa: number
  }): Promise<void> {
    this._loading.set(true)
    this._error.set(null)

    try {
      const result = await firstValueFrom(
        this.http.post<ApplicationSubmitted>("/api/v1/applications", data)
      )
      this._submitted.set(result)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Submission failed"
      this._error.set(message)
    } finally {
      this._loading.set(false)
    }
  }

  reset(): void {
    this._loading.set(false)
    this._error.set(null)
    this._submitted.set(null)
  }
}
```

---

## P4.6 — Angular OnPush + Signals — Smart Container (S4.30, S4.52, S4.53)

```typescript
// src/app/features/application/application-page.component.ts
import { Component, ChangeDetectionStrategy, inject, OnInit } from "@angular/core"
import { ActivatedRoute } from "@angular/router"
import { ApplicationService } from "./application.service"
import { ApplicationFormComponent } from "./application-form.component"
import { SkeletonCardComponent } from "@/shared/ui/skeleton-card.component"

@Component({
  selector: "app-application-page",
  standalone: true,           // S4.52
  changeDetection: ChangeDetectionStrategy.OnPush, // S4.53
  imports: [ApplicationFormComponent, SkeletonCardComponent],
  template: `
    @if (service.submitted()) {
      <div role="status" class="card-primary p-8 text-center">
        <p class="text-success font-semibold text-lg">
          Application submitted — Reference: {{ service.submitted()!.reference }}
        </p>
      </div>
    } @else {
      <app-application-form
        (submitted)="onSubmit($event)"
        [isLoading]="service.loading()"
        [errorMessage]="service.error() ?? ''"
      />
    }
  `
})
export class ApplicationPageComponent implements OnInit {
  protected service = inject(ApplicationService)
  private route    = inject(ActivatedRoute)

  scholarshipId = ""
  studentId     = ""

  ngOnInit(): void {
    this.scholarshipId = this.route.snapshot.params["scholarshipId"]
    this.studentId     = this.route.snapshot.params["studentId"]
  }

  async onSubmit(data: { motivation: string; gpa: number }): Promise<void> {
    await this.service.submitApplication({
      ...data,
      scholarshipId: this.scholarshipId,
      studentId:     this.studentId,
    })
  }
}
```

---

## P4.7 — TanStack Query — Queries and Mutations (S4.28, S4.29, S4.11)

### Query with loading / error / success (S4.11)

```tsx
// src/components/scholarships/ScholarshipList.tsx
"use client"
import { useQuery } from "@tanstack/react-query"
import { z } from "zod"
import { ScholarshipCardSkeleton } from "./ScholarshipCardSkeleton" // S4.24
import { ScholarshipCard } from "./ScholarshipCard"

const ScholarshipSchema = z.object({
  id:     z.string().cuid(),
  title:  z.string(),
  amount: z.string(), // Decimal serialised as string (S5.28)
  status: z.enum(["ACTIVE", "PAUSED", "CLOSED"]),
})
const ScholarshipsResponseSchema = z.array(ScholarshipSchema)

async function fetchScholarships() {
  const res = await fetch("/api/v1/scholarships")
  if (!res.ok) throw new Error("Failed to load scholarships")
  return ScholarshipsResponseSchema.parse(await res.json()) // S4.25
}

export function ScholarshipList() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["scholarships"],
    queryFn:  fetchScholarships,
    staleTime: 5 * 60 * 1000,
  })

  // S4.11 — Explicit loading state
  if (isLoading) return (
    <div role="status" aria-label="Loading scholarships">
      {Array.from({ length: 3 }).map((_, i) => <ScholarshipCardSkeleton key={i} />)}
    </div>
  )

  // S4.11 — Explicit error state
  if (isError) return (
    <div role="alert" className="card-primary p-6 text-center">
      <p className="text-danger text-base">
        {error.message} — <button className="underline" onClick={() => window.location.reload()}>Try again</button>
      </p>
    </div>
  )

  // S4.11 — Empty state (fourth state for collections)
  if (!data?.length) return (
    <p className="text-on-surface-muted text-base text-center py-8">
      No scholarships available at this time.
    </p>
  )

  return (
    <ul className="space-y-4">
      {data.map(s => <ScholarshipCard key={s.id} scholarship={s} />)}
    </ul>
  )
}
```

### Skeleton loader component (S4.24)

```tsx
// src/components/scholarships/ScholarshipCardSkeleton.tsx
export function ScholarshipCardSkeleton() {
  return (
    <div className="card-primary p-5 space-y-3 animate-pulse" aria-hidden="true">
      <div className="h-5 w-3/4 bg-surface-3 rounded-md" />
      <div className="h-4 w-1/2 bg-surface-3 rounded-md" />
      <div className="h-4 w-1/4 bg-surface-3 rounded-md" />
    </div>
  )
}
```

---

## P4.8 — Zustand Client State Store (S4.29, S4.31, S4.37)

```typescript
// src/lib/stores/ui-store.ts
import { create } from "zustand"

// S4.31 — Flat state structure, no nesting
interface UIState {
  activeFilter:      string
  currentPage:       number
  isFilterDrawerOpen: boolean
  setActiveFilter:   (filter: string) => void
  setCurrentPage:    (page: number) => void
  toggleFilterDrawer: () => void
  resetFilters:      () => void
}

export const useUIStore = create<UIState>((set) => ({
  // State — flat (S4.31)
  activeFilter:       "all",
  currentPage:        1,
  isFilterDrawerOpen: false,

  // Actions
  setActiveFilter:   (filter) => set({ activeFilter: filter, currentPage: 1 }),
  setCurrentPage:    (page)   => set({ currentPage: page }),
  toggleFilterDrawer: ()      => set((s) => ({ isFilterDrawerOpen: !s.isFilterDrawerOpen })),

  // S4.45 — Reset state on navigation
  resetFilters: () => set({ activeFilter: "all", currentPage: 1 }),
}))
```

---

## P4.9 — React Hook Form + Zod Multi-Step Form (S4.46, S4.50)

```tsx
// src/components/profile/ProfileSetupWizard.tsx
"use client"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"

const Step1Schema = z.object({
  firstName: z.string().min(1, "Required"),
  lastName:  z.string().min(1, "Required"),
  phone:     z.string().regex(/^\+27[0-9]{9}$/, "South African number: +27XXXXXXXXX"),
})

const Step2Schema = z.object({
  institution:   z.string().min(1, "Required"),
  yearOfStudy:   z.number().int().min(1).max(7),
  qualification: z.string().min(1, "Required"),
})

type Step1Data = z.infer<typeof Step1Schema>
type Step2Data = z.infer<typeof Step2Schema>

export function ProfileSetupWizard() {
  const [step, setStep] = useState(1)
  // S4.50 — step 1 data preserved when moving to step 2
  const [step1Data, setStep1Data] = useState<Step1Data | null>(null)

  const step1Form = useForm<Step1Data>({ resolver: zodResolver(Step1Schema) })
  const step2Form = useForm<Step2Data>({ resolver: zodResolver(Step2Schema) })

  const handleStep1 = step1Form.handleSubmit((data) => {
    setStep1Data(data) // Preserve step 1 (S4.50)
    setStep(2)
  })

  const handleStep2 = step2Form.handleSubmit(async (data) => {
    if (!step1Data) return
    // Submit combined data
    await fetch("/api/v1/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...step1Data, ...data }),
    })
  })

  return (
    <div className="card-primary p-6 max-w-lg mx-auto">
      <div className="flex gap-2 mb-6">
        {[1, 2].map(n => (
          <div key={n} className={`h-2 flex-1 rounded-full ${n <= step ? "bg-primary" : "bg-surface-3"}`} />
        ))}
      </div>

      {step === 1 && (
        <form onSubmit={handleStep1} className="space-y-4">
          <input
            {...step1Form.register("firstName")}
            placeholder="First name"
            className="w-full rounded-md border border-border p-3 text-base" /* S4.20 */
          />
          <button type="submit" className="w-full min-h-[44px] bg-primary text-white rounded-md">
            Next
          </button>
        </form>
      )}

      {step === 2 && (
        <form onSubmit={handleStep2} className="space-y-4">
          <button
            type="button"
            onClick={() => setStep(1)}
            className="text-primary text-base underline min-h-[44px]" /* S4.18 */
          >
            ← Back
          </button>
          <button type="submit" className="w-full min-h-[44px] bg-primary text-white rounded-md">
            Complete Profile
          </button>
        </form>
      )}
    </div>
  )
}
```

---

## P4.10 — MSW Setup for Next.js Tests (S7.14)

### Install and configure

```bash
npm install --save-dev msw
npx msw init public/ --save
```

### `src/mocks/handlers.ts` — API handlers

```typescript
import { http, HttpResponse } from "msw"

export const handlers = [
  // Mock scholarship list endpoint
  http.get("/api/v1/scholarships", () => {
    return HttpResponse.json([
      {
        id:     "clx7abc123",
        title:  "National Student Financial Aid",
        amount: "15000.00", // Decimal as string (S5.28)
        status: "ACTIVE",
      },
    ])
  }),

  // Mock application submission
  http.post("/api/v1/applications", () => {
    return HttpResponse.json({
      id:          "clxapp456",
      status:      "PENDING",
      submittedAt: new Date().toISOString(),
      reference:   "APP-2026-001",
    })
  }),

  // Mock 401 for auth tests
  http.get("/api/v1/applications/protected", () => {
    return new HttpResponse(
      JSON.stringify({ success: false, error: { code: "UNAUTHORIZED", message: "Not authenticated" } }),
      { status: 401 }
    )
  }),
]
```

### `src/mocks/server.ts` — Node test server

```typescript
import { setupServer } from "msw/node"
import { handlers } from "./handlers"

export const server = setupServer(...handlers)
```

### `jest.setup.ts`

```typescript
import "@testing-library/jest-dom"
import { server } from "./src/mocks/server"

beforeAll(() => server.listen({ onUnhandledRequest: "error" }))
afterEach(() => server.resetHandlers()) // S7.13 — reset between tests
afterAll(() => server.close())
```

### Test using MSW

```typescript
// src/components/scholarships/__tests__/ScholarshipList.test.tsx
import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ScholarshipList } from "../ScholarshipList"
import { server } from "@/mocks/server"
import { http, HttpResponse } from "msw"

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
    {children}
  </QueryClientProvider>
)

describe("ScholarshipList", () => {
  it("renders scholarships when API returns data", async () => {
    render(<ScholarshipList />, { wrapper })

    // S4.24 — Skeleton shown during load
    expect(screen.getByRole("status", { name: /loading/i })).toBeInTheDocument()

    // S7.3 — Assert on user-visible behaviour, not implementation
    await screen.findByText("National Student Financial Aid")
    expect(screen.getByText("National Student Financial Aid")).toBeInTheDocument()
  })

  it("shows error message when API fails", async () => {
    server.use(
      http.get("/api/v1/scholarships", () =>
        new HttpResponse(null, { status: 500 })
      )
    )

    render(<ScholarshipList />, { wrapper })
    const error = await screen.findByRole("alert")
    expect(error).toBeInTheDocument()
  })
})
```

---

## P4.11 — Playwright Visual Regression at 320/375/390px (S7.19, S4.10)

### `playwright.config.ts`

```typescript
import { defineConfig, devices } from "@playwright/test"

export default defineConfig({
  testDir: "./tests",
  projects: [
    // S7.19 — three mandatory mobile breakpoints
    {
      name:  "mobile-320",
      use: { ...devices["iPhone SE"], viewport: { width: 320, height: 568 } },
      testMatch: "**/visual/**",
    },
    {
      name:  "mobile-375",
      use: { ...devices["iPhone 12"], viewport: { width: 375, height: 812 } },
      testMatch: "**/visual/**",
    },
    {
      name:  "mobile-390",
      use: { ...devices["iPhone 14 Pro"], viewport: { width: 390, height: 844 } },
      testMatch: "**/visual/**",
    },
    // E2E tests at standard desktop
    {
      name: "desktop",
      use: { ...devices["Desktop Chrome"] },
      testMatch: "**/e2e/**",
    },
  ],
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000",
    screenshot: "only-on-failure",
  },
  snapshotDir: "./tests/visual/snapshots",
})
```

### Visual regression test

```typescript
// tests/visual/scholarship-list.spec.ts
import { test, expect } from "@playwright/test"

test.describe("Scholarship List — Mobile Breakpoints", () => {
  test("renders correctly at current viewport", async ({ page }) => {
    await page.goto("/scholarships")

    // Wait for content (not skeleton)
    await page.waitForSelector("[data-testid='scholarship-card']")

    // S7.19 — Visual snapshot
    await expect(page).toHaveScreenshot("scholarship-list.png", {
      fullPage: false,
      maxDiffPixelRatio: 0.01, // 1% tolerance
    })
  })

  test("navigation is not accordion at any width", async ({ page }) => {
    await page.goto("/")
    // S4.6 — No accordion nav
    const accordion = page.locator("[data-nav-type='accordion']")
    await expect(accordion).not.toBeVisible()
  })

  test("no page-level horizontal scroll", async ({ page }) => {
    await page.goto("/")
    // S4.9 — No horizontal scroll
    const scrollWidth = await page.evaluate(() => document.body.scrollWidth)
    const clientWidth = await page.evaluate(() => document.body.clientWidth)
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth)
  })
})
```

### `package.json` scripts

```json
{
  "scripts": {
    "test:visual": "playwright test --project=mobile-320 --project=mobile-375 --project=mobile-390",
    "test:visual:update": "playwright test --update-snapshots --project=mobile-320 --project=mobile-375 --project=mobile-390",
    "test:e2e": "playwright test --project=desktop",
    "test:a11y": "playwright test tests/a11y/"
  }
}
```

---

## P4.12 — axe-core Accessibility CI Gate (S7.20, S4.21)

```typescript
// tests/a11y/accessibility.spec.ts
import { test, expect } from "@playwright/test"
import AxeBuilder from "@axe-core/playwright"

const pagesToTest = [
  { name: "Home",             path: "/" },
  { name: "Scholarship List", path: "/scholarships" },
  { name: "Login",            path: "/auth/login" },
  { name: "Application Form", path: "/scholarships/clx1/apply" },
]

for (const { name, path } of pagesToTest) {
  test(`${name} — no critical or serious accessibility violations`, async ({ page }) => {
    await page.goto(path)
    // Wait for dynamic content
    await page.waitForLoadState("networkidle")

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"]) // S4.21 — WCAG 2.1 AA
      .analyze()

    // S7.20 — Critical and serious are build failures
    const criticalOrSerious = results.violations.filter(
      v => v.impact === "critical" || v.impact === "serious"
    )

    expect(criticalOrSerious, `${name}: ${criticalOrSerious.map(v => v.description).join(", ")}`).toHaveLength(0)
  })
}
```

---

## P4.13 — Sentry Frontend Integration (S4.65, S4.66)

### Next.js — `sentry.client.config.ts`

```typescript
import * as Sentry from "@sentry/nextjs"

Sentry.init({
  dsn:         process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release:     process.env.NEXT_PUBLIC_APP_VERSION,
  tracesSampleRate:   process.env.NODE_ENV === "production" ? 0.1 : 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate:  1.0,
  integrations: [Sentry.replayIntegration()],
  // S4.65 — PII scrubbing
  beforeSend(event) {
    if (event.user) {
      delete event.user.email
      delete event.user.ip_address
    }
    return event
  },
})

export function setSentryUser(id: string, role: string): void {
  Sentry.setUser({ id, role }) // S4.65 — id and role only, no PII
}
```

### Error Boundary (S4.66)

```tsx
// src/components/ErrorBoundary.tsx
"use client"
import * as Sentry from "@sentry/nextjs"
import { Component, type ReactNode } from "react"

interface Props   { children: ReactNode; fallback?: ReactNode; context?: string }
interface State   { hasError: boolean; eventId?: string }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): Partial<State> {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo): void {
    const eventId = Sentry.captureException(error, {
      extra: { componentStack: info.componentStack, context: this.props.context },
    })
    this.setState({ eventId })
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div role="alert" className="card-primary p-8 text-center">
          <p className="text-on-surface font-semibold text-base">
            Something went wrong. Our team has been notified.
          </p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="mt-4 text-primary underline text-base min-h-[44px]" /* S4.18 */
          >
            Try again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
```

### Wrap routes in `src/app/layout.tsx`

```tsx
import { ErrorBoundary } from "@/components/ErrorBoundary"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {/* S4.66 — Error boundary on every route */}
        <ErrorBoundary context="root-layout">
          {children}
        </ErrorBoundary>
      </body>
    </html>
  )
}
```

---

## P4.14 — Group-Build Workflow (S4.71–S4.73, S1.27)

### Sprint start checklist

```markdown
## Sprint {N} — Group Build Start

### Group: G{N} — {description}
### Feature proposals approved: GitHub Issues #{N}, #{N}

#### Pre-code gate (S1.27 Phase 0)
- [ ] Feature proposal written and approved for each feature in this group
- [ ] Full data flow traced — no code written yet
- [ ] Constitutional standards identified per feature (document in CONSTITUTION-INDEX.md)
- [ ] Database schema reviewed / migration planned
- [ ] OpenAPI contract drafted for new endpoints (S2.7)
- [ ] CONSTITUTION-INDEX.md updated for this sprint

#### Layer build sequence for each feature:
1. All Interface/Types committed first across the group
2. All Service layers committed
3. All Smart components committed
4. All UI components committed
5. Tests committed alongside each layer (S7.1)

#### Group completion criteria (S4.73)
- [ ] All standards pass (CI green)
- [ ] All tests pass with coverage gate met
- [ ] PR merged to main
- [ ] Preview deployment functional and reviewed
- [ ] Group retrospective completed (30 min — S4.77)
```

---

## P4.15 — Tools & Commands Reference

| Task | Command |
|------|---------|
| Install shadcn component | `npx shadcn@latest add {component}` |
| Run visual regression | `npm run test:visual` |
| Update visual snapshots | `npm run test:visual:update` |
| Run accessibility gate | `npm run test:a11y` |
| Run E2E tests | `npm run test:e2e` |
| Angular unit tests | `npx vitest run --coverage` |
| Next.js unit tests | `npx jest --coverage` |
| Check Lighthouse score | `npx lhci autorun` |
| Check bundle size | `npx @next/bundle-analyzer` |
| Generate Angular component | `ng generate component features/{name} --standalone` |
| Generate Angular service | `ng generate service features/{name}/{name}` |
| Tailwind IntelliSense | Install `bradlc.vscode-tailwindcss` extension |
| Sentry source maps upload | `SENTRY_AUTH_TOKEN=... npx sentry-cli releases files` |

---

## Common Failure Patterns

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| iOS Safari zooms into form input | `font-size < 16px` on input | Add `text-base` class (S4.20) |
| Angular component not updating | `Default` change detection | Add `ChangeDetectionStrategy.OnPush` (S4.53) |
| Tailwind styles overriding custom CSS | Specificity conflict | Separate concerns per S4.15 — one tool per concern |
| Playwright snapshot fails on CI | Font rendering differs | Use `maxDiffPixelRatio: 0.02` and Docker font consistency |
| MSW test shows "unhandled request" | Handler not registered | Add handler to `src/mocks/handlers.ts` |
| `signal()` not updating component | Signal updated outside Angular zone | Use `effect()` or ensure update is in Angular context |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock — full depth implementation guide. Angular Reactive Forms (P4.4), Angular HTTP+Signals service (P4.5), Angular OnPush container (P4.6), TanStack Query queries and mutations (P4.7), Zustand store (P4.8), React Hook Form multi-step (P4.9), MSW setup and test patterns (P4.10), Playwright visual regression at 320/375/390px (P4.11), axe-core CI gate (P4.12), Sentry+ErrorBoundary (P4.13), group-build workflow (P4.14). | Expanded from thin initial version to full production-ready guide. |

---

> **LOCKED — v1.0 — 2026-05-08**
>
> This document is locked. No practice may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
