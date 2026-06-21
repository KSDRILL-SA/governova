# Stack-Selection Guide — Choosing Any Stack Under Governova

| Attribute | Value |
|-----------|-------|
| **Document** | Universal Stack-Selection Guide |
| **Layer** | Index / decision support |
| **Governed By** | C6 — Full-Stack Architecture (stack assignment framework S6.1–S6.7) |
| **Applies To** | Every system, any stack, any organisation |
| **Paired With** | `constitution/indexes/stack-assignment-matrix.md` · `constitution/implementation/` |

---

> *"Governova is stack-agnostic. The Framework and the Constitution Core apply to every system ever built. A stack is a choice you make under governance — not a limit the framework imposes."*

The **Framework** (Layer 1) and **Core** (Layer 2) are universal — they govern a Rust service and a Laravel monolith identically. The **Implementation layer** (Layer 3) binds those universal standards to a specific stack. This guide is how you *choose* the stack and *find or author* its binding. The two KSDRILL reference stacks are worked examples on top of which **every other stack is added** — not the boundary of what Governova supports.

---

## §1 — The Selection Dimensions

Choose a stack by scoring the system against these dimensions — never by fashion or familiarity alone.

| Dimension | Question it answers |
|-----------|--------------------|
| **System type** | Content/SEO site · dashboard · API · real-time · data/AI pipeline · mobile · embedded |
| **Rendering & SEO** | Does it need server rendering / public discoverability? |
| **Performance & concurrency** | Latency targets, throughput, CPU-bound vs IO-bound |
| **Domain & compliance** | Fintech/health/gov constraints (precision, residency, auditability) that favour a stack |
| **AI/ML needs** | Native Python pipelines? Vector DB? On-device inference? |
| **Team expertise** | What the team can operate safely *today* |
| **Ecosystem maturity** | Library/security/tooling depth for the use case |
| **Hiring & longevity** | Can you staff and maintain it for the system's lifespan? |
| **Time-to-market** | How fast must the first compliant version ship? |

A stack is a *fit*, not a *winner*. The right answer is the one that scores best across the dimensions that matter for **this** system.

---

## §2 — The Decision Path

```
Is the system content-driven / SEO-critical / public?
   → YES → SSR-capable frontend stack (Next.js [ref], Remix, Astro, Nuxt)
   → NO  → Is it an enterprise dashboard / precision-financial / native-AI system?
            → YES → typed SPA + strong backend (Angular + FastAPI [ref], React + Spring,
                    Vue + .NET) — Decimal money, native Python AI where needed
            → NO  → Is it primarily an API / service?
                     → choose backend by concurrency & team: FastAPI [ref], Go, Spring,
                       NestJS, Django, Rails, Laravel, .NET, Phoenix
   Is it mobile? → cross-platform (React Native, Flutter) or native (SwiftUI, Kotlin)
```

Then choose **datastores by data type** (C5): relational (PostgreSQL [ref], MySQL), document (MongoDB [ref], DynamoDB), cache/KV (Redis), search (Elasticsearch), vector (ChromaDB [ref]). And **auth** (C3) by IdP needs (NextAuth [ref], Auth0, Keycloak, Clerk, Supabase).

---

## §3 — The Reference Assignments (Worked Examples)

These are KSDRILL's proven, ADR-locked assignments — examples of the method, not the menu:

| System type | Reference stack | Why |
|-------------|----------------|-----|
| Content-driven, SEO-critical, public | **Next.js** | SSR, SEO, fast public delivery (Maphophe, SyncUp) |
| Enterprise dashboard, precision-financial, native-AI | **Angular + FastAPI** | Typed UI, Decimal money, native Python AI (FundsLink, Reserve Bank) |

Datastores: PostgreSQL (relational), MongoDB (document), ChromaDB (vector), Redis (cache). Auth: NextAuth / RS256 JWT. These have **full** implementation bindings; all other stacks have stubs ready to be authored.

---

## §4 — The Binding Catalogue (breadth)

The implementation layer is open-ended. Current bindings (✔ full · ◻ stub, community-contributable):

| Category | Bindings |
|----------|----------|
| **Backend (C2)** | ✔ fastapi · ◻ spring-boot, django, express, nestjs, laravel, rails, go-gin, dotnet-aspnet, phoenix-elixir |
| **Frontend (C4)** | ✔ nextjs, angular · ◻ react, vue, svelte, solidjs, remix, astro |
| **Mobile (C4)** | ◻ react-native, flutter, swiftui-ios, kotlin-android |
| **Database (C5)** | ✔ prisma-postgresql, beanie-mongodb, chromadb · ◻ mysql, redis, dynamodb, elasticsearch, sqlite |
| **Auth (C3)** | ✔ nextauth · ◻ auth0, keycloak, clerk, supabase-auth |

The list grows through the contribution process — it is not a fixed set. **Any stack a team uses can be governed**: if a binding does not exist, the universal core still applies, and the binding is authored from the template.

---

## §5 — Adding a New Stack

1. Score the system (§1) and pick the stack.
2. If the assignment differs from the reference defaults, **write an ADR** (`governance/decisions/`) — required by C6 (S6.x).
3. If a binding exists, use it. If only a stub exists, author the full binding from `templates/implementation-guide-template.md`, using the proven reference bindings as the pattern, and contribute it (`CONTRIBUTING.md`).
4. Compile the project's CONSTITUTION-INDEX: Framework + Core + your binding(s) + domain(s).

No stack is outside Governova. The framework never changes; only the binding is new.

---

## §6 — The Rule

> The Framework and Core are universal. The stack is a governed choice with an ADR when it deviates from the reference defaults. A missing binding is a *gap to author*, never a reason a system cannot be governed.
