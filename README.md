<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=2563EB&height=200&section=header&text=System%20Design%20Template&fontSize=48&fontColor=white&fontAlignY=40&fontAlign=50" alt="Header" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/System_Design_Template-2563EB?style=for-the-badge&logo=codefactor&logoColor=white" alt="System Design Template" />
</p>

<h1 align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Inter&weight=600&size=32&duration=2800&pause=500&color=2563EB&center=true&vCenter=true&width=650&lines=10+Locked+Constitutions;355+Total+Rules;Production-Grade+Governance;Build+in+the+Right+Order" alt="Typing animation" />
</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Locked-2563EB?style=flat-square" alt="Status Locked" />
  <img src="https://img.shields.io/badge/Version-v1.0-2563EB?style=flat-square" alt="Version 1.0" />
  <img src="https://img.shields.io/badge/Total_Rules-355-2563EB?style=flat-square" alt="Total Rules 355" />
  <img src="https://img.shields.io/badge/Constitutions-10-2563EB?style=flat-square" alt="10 Constitutions" />
  <img src="https://img.shields.io/badge/License-MIT-25D366?style=flat-square" alt="MIT License" />
</p>

<p align="center">
  <i>"We build fast within strict constitutional boundaries. Failures are predictable, traceable, and easy to debug."</i>
</p>

---

<br/>

## Table of Contents

| Section | Link |
| :--- | :--- |
| **The Philosophy** | [goto →](#the-philosophy) |
| **What Is This Repository?** | [goto →](#what-is-this-repository) |
| **The Constitutional Order** | [goto →](#the-constitutional-order) |
| **Phase 0: Foundation** | [goto →](#phase-0-foundation) |
| **Phase 1: Core Architecture** | [goto →](#phase-1-core-architecture) |
| **Phase 2: Quality & Reliability** | [goto →](#phase-2-quality--reliability) |
| **Phase 3: Product & Improvement** | [goto →](#phase-3-product--improvement) |
| **Quick Start** | [goto →](#quick-start) |
| **How to Use This Template** | [goto →](#how-to-use-this-template) |
| **Repository Structure** | [goto →](#repository-structure) |
| **Industry Standards** | [goto →](#industry-standards) |
| **Progress Tracker** | [goto →](#progress-tracker) |
| **License** | [goto →](#license) |

---

<br/>

## <a id="the-philosophy"></a><img src="https://img.shields.io/badge/The_Philosophy-2563EB?style=for-the-badge&logo=philosophy&logoColor=white" alt="The Philosophy" />

<br/>

### 🧠 Controlled Imperfection Engineering

This system does **not** claim to prevent all bugs. That is impossible in real-world systems.

Instead, it ensures that **when failures happen** — and they will — they are:

| Principle | How This System Delivers |
| :--- | :--- |
| **Observable** | X-Request-ID, structured logging, error codes |
| **Traceable** | Request tracing across all services |
| **Isolated** | Circuit breakers, timeouts, retries |
| **Predictable** | 3-state UI, standard `ApiResponse<T>` format |
| **Reversible** | Rollback plans, feature flags, idempotency |

> *"We don't remove failure. We shape it, limit it, expose it, and make it recoverable."*

### 🎯 What These Constitutions Actually Do

| Without Rules | With Your Constitutions |
| :--- | :--- |
| Infinite possible bugs | Known categories of bugs |
| Random UI crashes | Predictable error states |
| Inconsistent API responses | Standard `ApiResponse<T>` format |
| Unpredictable state bugs | 3-state system (loading/error/success) |

### 🧠 AI's Role

**AI reduces randomness, not errors.** It increases predictability of system behavior under failure.

| Without AI | With AI |
| :--- | :--- |
| Random inconsistencies | Enforced patterns |
| Manual validation everywhere | Generated Zod schemas from OpenAPI |
| Slow debugging | Structured failure analysis |

### ⚖️ The Maturity Scale

| Level | Mindset | This System |
| :--- | :--- | :--- |
| Beginner | "Just build it and see what happens" | ❌ |
| Intermediate | "Try to prevent all bugs" | ❌ |
| Senior | "Assume everything breaks and design for failure" | ✅ |
| **Architect** | **"Define boundaries so failure is structured, visible, and cheap to fix"** | ✅✅ |

---

<br/>

## <a id="what-is-this-repository"></a><img src="https://img.shields.io/badge/What_Is_This_Repository-2563EB?style=for-the-badge&logo=aboutdotme&logoColor=white" alt="What Is This Repository" />

<br/>

This repository contains **10 locked constitutions** that govern every aspect of building production-grade systems. Each constitution defines **non-negotiable rules** for a specific domain:

| Constitution | Focus |
| :--- | :--- |
| **Team & Process** | How the team operates |
| **Code Quality** | How code is written |
| **Backend** | How APIs are built |
| **Auth Domain** | How users authenticate |
| **Frontend** | How UIs are built |
| **Database** | How data is stored |
| **Testing** | How code is verified |
| **Infrastructure** | Where code runs |
| **Incident Response** | How failures are handled |
| **Product & Feature** | What to build next |

**Total: 355 rules + Auth Domain specification**

---

<br/>

## <a id="the-constitutional-order"></a><img src="https://img.shields.io/badge/The_Constitutional_Order-FF6F00?style=for-the-badge&logo=stack&logoColor=white" alt="The Constitutional Order" />

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/BUILD_ORDER_FOUNDATION-2563EB?style=for-the-badge&logo=rocket&logoColor=white" alt="Foundation" />
  <img src="https://img.shields.io/badge/⬇-2563EB?style=for-the-badge" alt="Arrow" />
  <img src="https://img.shields.io/badge/CORE_ARCHITECTURE-2563EB?style=for-the-badge&logo=code&logoColor=white" alt="Core Architecture" />
  <img src="https://img.shields.io/badge/⬇-2563EB?style=for-the-badge" alt="Arrow" />
  <img src="https://img.shields.io/badge/QUALITY_&_RELIABILITY-2563EB?style=for-the-badge&logo=shield&logoColor=white" alt="Quality" />
  <img src="https://img.shields.io/badge/⬇-2563EB?style=for-the-badge" alt="Arrow" />
  <img src="https://img.shields.io/badge/PRODUCT_&_IMPROVEMENT-2563EB?style=for-the-badge&logo=chart&logoColor=white" alt="Product" />
</p>

> **Golden Rule:** Build constitutions in the order your system would fail without them.

---

<br/>

## <a id="phase-0-foundation"></a><img src="https://img.shields.io/badge/Phase_0_Foundation-181717?style=for-the-badge&logo=foundation&logoColor=white" alt="Phase 0 Foundation" />

<br/>

| Order | Constitution | Why First | Status |
| :---: | :--- | :--- | :--- |
| **1** | **Team & Process** | Without team process, no other constitution will be followed | <img src="https://img.shields.io/badge/Pending-FF6F00?style=flat-square" alt="Pending" /> |
| **2** | **Code Quality & Review** | Set coding standards before writing any code | <img src="https://img.shields.io/badge/Pending-FF6F00?style=flat-square" alt="Pending" /> |

---

<br/>

## <a id="phase-1-core-architecture"></a><img src="https://img.shields.io/badge/Phase_1_Core_Architecture-FF6F00?style=for-the-badge&logo=architecture&logoColor=white" alt="Phase 1 Core Architecture" />

<br/>

| Order | Constitution | Why This Order | Status |
| :---: | :--- | :--- | :--- |
| **3** | **Backend Constitution** | Foundation of your system — APIs, auth, database patterns | <img src="https://img.shields.io/badge/Locked-25D366?style=flat-square" alt="Locked" /> |
| **4** | **Auth Domain Specification** | First feature every system needs — security-critical | <img src="https://img.shields.io/badge/Pending-FF6F00?style=flat-square" alt="Pending" /> |
| **5** | **Frontend Constitution** | Depends on backend and auth — build after they're locked | <img src="https://img.shields.io/badge/Locked-25D366?style=flat-square" alt="Locked" /> |
| **6** | **Database Constitution** | Source of truth — lock after backend patterns are defined | <img src="https://img.shields.io/badge/Pending-FF6F00?style=flat-square" alt="Pending" /> |

---

<br/>

## <a id="phase-2-quality--reliability"></a><img src="https://img.shields.io/badge/Phase_2_Quality_&_Reliability-25D366?style=for-the-badge&logo=quality&logoColor=white" alt="Phase 2 Quality & Reliability" />

<br/>

| Order | Constitution | Why This Order | Status |
| :---: | :--- | :--- | :--- |
| **7** | **Testing Constitution** | Need to trust your code before production | <img src="https://img.shields.io/badge/Pending-FF6F00?style=flat-square" alt="Pending" /> |
| **8** | **Infrastructure Constitution** | Need to deploy before production | <img src="https://img.shields.io/badge/Pending-FF6F00?style=flat-square" alt="Pending" /> |
| **9** | **Incident Response Constitution** | Need to handle failures before launch | <img src="https://img.shields.io/badge/Pending-FF6F00?style=flat-square" alt="Pending" /> |

---

<br/>

## <a id="phase-3-product--improvement"></a><img src="https://img.shields.io/badge/Phase_3_Product_&_Improvement-764ABC?style=for-the-badge&logo=product&logoColor=white" alt="Phase 3 Product & Improvement" />

<br/>

| Order | Constitution | Why Last | Status |
| :---: | :--- | :--- | :--- |
| **10** | **Product & Feature Constitution** | After launch — decide what to build next | <img src="https://img.shields.io/badge/Pending-FF6F00?style=flat-square" alt="Pending" /> |

---

<br/>

## <a id="quick-start"></a><img src="https://img.shields.io/badge/Quick_Start-2563EB?style=for-the-badge&logo=rocket&logoColor=white" alt="Quick Start" />

<br/>

### For a New System

```bash
# Step 1: Clone this repository into your project
git clone https://github.com/MALULEKE-KS/system-design-template.git .system-design

# Step 2: Open the constitutional order
open .system-design/00-ORDER/constitutional-order.html

# Step 3: Follow the 10-step order
# Step 4: Use the checklist to track progress
# Step 5: Build your Auth Domain code
```

For Solo Founder

```bash
# Same steps — each constitution is designed to work for solo founders
# Simplified versions, less ceremony, same rigor
```

---

<br/>

<a id="how-to-use-this-template"></a><img src="https://img.shields.io/badge/How_to_Use_This_Template-25D366?style=for-the-badge&logo=code&logoColor=white" alt="How to Use This Template" />

<br/>

<details>
<summary><strong>Click to expand — detailed instructions</strong></summary>

<br/>

With AI (Cursor/Copilot):

1. Clone this repo into .system-design/
2. Tell your AI: "Read .system-design/00-ORDER/constitutional-order.html and guide me through Phase 0"
3. Follow the AI's guidance

Manually:

1. Open 00-ORDER/constitutional-order.html in your browser
2. Start with Constitution #1 (Team & Process)
3. Read the rules, implement them
4. Check off items in 00-ORDER/build-checklist.md
5. Move to the next constitution

Pro Tip: Don't skip Phase 0. Team & Process and Code Quality are the foundation that makes everything else work.

</details>

---

<br/>

<a id="repository-structure"></a><img src="https://img.shields.io/badge/Repository_Structure-181717?style=for-the-badge&logo=stackshare&logoColor=white" alt="Repository Structure" />

<br/>

```text
system-design-template/
│
├── 📄 README.md                        # This file
├── 📄 LICENSE                          # MIT License
├── 📄 .gitignore                       # Git ignore rules
│
├── 📁 00-ORDER/                        # START HERE
│   └── 📄 constitutional-order.html    # The 10-step build order
│
├── 📁 01-FOUNDATION/                   # Phase 0
│   ├── 📄 team-process-constitution.html
│   └── 📄 code-quality-constitution.html
│
├── 📁 02-CORE-ARCHITECTURE/            # Phase 1
│   ├── 📄 backend-constitution.html
│   ├── 📄 auth-domain-specification.html
│   ├── 📄 frontend-constitution.html
│   └── 📄 database-constitution.html
│
├── 📁 03-QUALITY-RELIABILITY/          # Phase 2
│   ├── 📄 testing-constitution.html
│   ├── 📄 infrastructure-constitution.html
│   └── 📄 incident-response-constitution.html
│
└── 📁 04-PRODUCT/                      # Phase 3
    └── 📄 product-feature-constitution.html
```

---

<br/>

<a id="industry-standards"></a><img src="https://img.shields.io/badge/Industry_Standards-412991?style=for-the-badge&logo=award&logoColor=white" alt="Industry Standards" />

<br/>

All constitutions are built on industry best practices from:

<p align="center">
  <img src="https://img.shields.io/badge/Google_SRE-4285F4?style=flat-square&logo=google&logoColor=white" alt="Google SRE" />
  <img src="https://img.shields.io/badge/AWS_Well_Architected-FF9900?style=flat-square&logo=amazonaws&logoColor=white" alt="AWS" />
  <img src="https://img.shields.io/badge/Stripe_Engineering-635BFF?style=flat-square&logo=stripe&logoColor=white" alt="Stripe" />
  <img src="https://img.shields.io/badge/GitHub_Engineering-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub" />
  <img src="https://img.shields.io/badge/Basecamp_Shape_Up-25D366?style=flat-square&logo=basecamp&logoColor=white" alt="Basecamp" />
  <img src="https://img.shields.io/badge/OWASP-000000?style=flat-square&logo=owasp&logoColor=white" alt="OWASP" />
</p>

---

<br/>

<a id="progress-tracker"></a><img src="https://img.shields.io/badge/Progress_Tracker-FF6F00?style=for-the-badge&logo=checklist&logoColor=white" alt="Progress Tracker" />

<br/>

Phase Constitutions Progress
Phase 0 2 <img src="https://progress-bar.dev/0/?title=0%25&color=2563EB" alt="0%" />
Phase 1 4 <img src="https://progress-bar.dev/50/?title=50%25&color=25D366" alt="50%" /> <sub>(Backend ✅, Frontend ✅, Auth ⏳, Database ⏳)</sub>
Phase 2 3 <img src="https://progress-bar.dev/0/?title=0%25&color=2563EB" alt="0%" />
Phase 3 1 <img src="https://progress-bar.dev/0/?title=0%25&color=2563EB" alt="0%" />
Total 10 <img src="https://progress-bar.dev/20/?title=20%25&color=25D366" alt="20%" /> <sub>2 of 10 constitutions locked</sub>

---

<br/>

<a id="license"></a><img src="https://img.shields.io/badge/License-25D366?style=for-the-badge&logo=opensource&logoColor=white" alt="License" />

<br/>

This project is licensed under the MIT License — see the LICENSE file for details.

```
MIT License

Copyright (c) 2026 MALULEKE-KS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

<br/>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=2563EB&height=100&section=footer" alt="Footer wave" />
</p>

<p align="center">
  <i>Built with African roots • Designed for global impact</i><br/>
  <i>The Sky Is The Limit — by KSDRILL-SA</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Locked-2026--04--08-2563EB?style=for-the-badge" alt="Locked Date" />
  <img src="https://img.shields.io/badge/Next_Review-2026--07--07-FF6F00?style=for-the-badge" alt="Next Review" />
</p>