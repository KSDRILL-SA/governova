# C2 — Backend Implementation Guide

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C2 — Backend Implementation Guide                                  |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | Both Stacks                                                        |
| **Paired With**    | C2 — Backend Constitution                                          |

---

> *"A standard tells you what must be true. This guide tells you how to make it true."*

---

## Opening Statement

This guide is the operational companion to the C2 Backend Constitution. Every practice
here satisfies a specific standard in C2. When the constitution says "the service layer
owns business logic" (S2.1), this guide shows exactly how to structure that service in
both Next.js and FastAPI. When the constitution says "all error responses use the standard
shape" (S2.22), this guide gives you the shared utility that produces it.

This document contains code, commands, file structures, and step-by-step procedures.
The constitution contains the why. This guide contains the how. Read the constitution
first. Use this guide when building.

Practices evolve as tooling evolves. Any practice change that would cause a constitutional
standard to be violated requires a constitutional amendment first, then an update here.

---

## Table of Contents

| Section | Title |
|---------|-------|
| P2.1 | Project Structure |
| P2.2 | Service Layer Patterns |
| P2.3 | Extension-First Patterns |
| P2.4 | OpenAPI Contract Setup |
| P2.5 | Standard Response Utilities |
| P2.6 | Validation Layer |
| P2.7 | Database Access Patterns |
| P2.8 | Performance Patterns |
| P2.9 | Resilience Patterns |
| P2.10 | Security Implementation |
| P2.11 | Observability Setup |
| P2.12 | FastAPI Implementation |
| P2.13 | Next.js API Route Implementation |
| P2.14 | API Versioning |
| P2.15 | Tools & Commands Reference |


---

## P2.1 — Project Structure

### Next.js Stack Structure (S2.70)

```
src/
├── app/
│   └── api/
│       └── v1/
│           ├── students/
│           │   ├── route.ts
│           │   └── [id]/route.ts
│           ├── scholarships/
│           │   ├── route.ts
│           │   └── [id]/route.ts
│           └── health/route.ts
├── lib/
│   ├── prisma.ts          # Singleton Prisma client (S2.75)
│   ├── auth.ts            # NextAuth config (S2.71)
│   ├── error-handler.ts   # Shared error handler (S2.73)
│   ├── response.ts        # Standard response utilities (S2.19–S2.22)
│   ├── validate.ts        # Validation middleware (S2.23)
│   ├── pagination.ts      # Pagination helpers (S2.14)
│   ├── rate-limit.ts      # Brute force protection (S2.55)
│   └── logger.ts          # Structured logger (S2.56)
├── services/
│   ├── student.service.ts
│   ├── scholarship.service.ts
│   └── audit.service.ts
├── schemas/               # Generated from OpenAPI — never hand-written (S2.24)
│   └── student.schema.ts
└── types/
    ├── api.types.ts
    └── errors.ts
```

### FastAPI Stack Structure (S2.63)

```
app/
├── main.py                # Router registration + middleware only
├── core/
│   ├── database.py        # DB connection lifecycle
│   ├── security.py        # JWT validation, password hashing
│   ├── config.py          # Pydantic Settings (S2.67)
│   ├── logger.py          # Structured logger (S2.56)
│   ├── response.py        # Standard response helpers
│   └── errors.py          # AppError class + error codes
├── students/
│   ├── router.py          # Route definitions — delegates to service
│   ├── service.py         # Business logic
│   └── models.py          # Pydantic request/response models
├── scholarships/
│   ├── router.py
│   ├── service.py
│   └── models.py
├── ai/                    # Isolated AI module (S2.68)
│   ├── router.py
│   └── service.py
└── health/
    └── router.py
```

---

## P2.2 — Service Layer Patterns

### Next.js Service Function (S2.1, S2.2, S2.5)

```typescript
// services/student.service.ts
import { prisma } from '@/lib/prisma'
import { AppError } from '@/types/errors'
import { activeWhere } from '@/lib/db-helpers'

// Explicit return type — never inferred (S2.5)
export async function getStudentById(id: string): Promise<StudentResponse> {
  const student = await prisma.student.findUnique({
    where: activeWhere({ id }),            // Always filter soft-deleted (S2.28, S2.35)
    select: {                              // Explicit field selection (S2.31)
      id: true, name: true, email: true, gpa: true, createdAt: true,
    },
  })
  if (!student) throw new AppError('Student not found', 'NOT_FOUND', 404)
  return student
}

export async function createStudent(
  data: CreateStudentInput,
  requestingUserId: string,    // Auth context passed as param — never from global state
): Promise<StudentResponse> {
  const student = await prisma.student.create({
    data: { ...data, createdBy: requestingUserId },
    select: { id: true, name: true, email: true, gpa: true, createdAt: true },
  })
  await auditLog({ userId: requestingUserId, action: 'CREATE', entity: 'Student', entityId: student.id })
  return student
}
```

### FastAPI Service Function (S2.1, S2.2, S2.5)

```python
# students/service.py
from students.models import StudentResponse, CreateStudentInput
from core.errors import AppError

async def get_student_by_id(student_id: str, db) -> StudentResponse:
    student = await db.student.find_unique(
        where={"id": student_id, "deleted_at": None},  # Soft delete filter (S2.28)
    )
    if not student:
        raise AppError("Student not found", "NOT_FOUND", 404)
    return StudentResponse.model_validate(student)

async def create_student(
    data: CreateStudentInput,
    requesting_user_id: str,
    db,
) -> StudentResponse:
    student = await db.student.create(
        data={**data.model_dump(), "created_by": requesting_user_id}
    )
    return StudentResponse.model_validate(student)
```

### Route Handler — Delegate Only (S2.1, S2.2)

```typescript
// app/api/v1/students/[id]/route.ts
export async function GET(request: Request, { params }: { params: { id: string } }) {
  try {
    const session = await auth()
    if (!session) return errorResponse('UNAUTHORIZED', 401)

    const student = await getStudentById(params.id)  // Delegate to service
    return successResponse(student)                  // Standard shape (S2.19)
  } catch (error) {
    return handleError(error)                        // Shared handler (S2.73)
  }
}
```

---

## P2.3 — Extension-First Patterns

### New Role — Extend Alongside, Never Modify (S2.7)

```typescript
// WRONG — modifying existing function for new role
export function canApprove(role: string): boolean {
  return role === 'FUNDER' || role === 'ADMIN' || role === 'SENIOR_FUNDER' // modification!
}

// CORRECT — new class alongside existing one, existing code untouched
export class FunderPermission {
  static canApprove(role: string): boolean {
    return role === 'FUNDER' || role === 'ADMIN'
  }
}
export class SeniorFunderPermission extends FunderPermission {
  static canAccessPremiumReports(role: string): boolean {
    return role === 'SENIOR_FUNDER' || role === 'ADMIN'
  }
}
```

### New Notification Channel — New Function Alongside (S2.7)

```typescript
// Existing — untouched
export async function sendEmailNotification(payload: NotificationPayload): Promise<void> { }

// New — added alongside, not inside existing
export async function sendSmsNotification(payload: NotificationPayload): Promise<void> { }

// Orchestrator composes channels — neither function modified
export async function sendNotification(
  payload: NotificationPayload,
  channels: ('email' | 'sms')[]
): Promise<void> {
  const handlers = { email: sendEmailNotification, sms: sendSmsNotification }
  await Promise.all(channels.map(c => handlers[c](payload)))
}
```

---

## P2.4 — OpenAPI Contract Setup

### OpenAPI Spec (S2.11)

```yaml
# openapi/v1/students.yaml
openapi: '3.0.3'
info:
  title: KSDRILL SA Students API
  version: '1.0.0'
paths:
  /api/v1/students/{id}:
    get:
      summary: Get student by ID
      tags: [Students]
      security:
        - bearerAuth: []              # Every protected endpoint declares auth (S2.13)
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string }
      responses:
        '200':
          content:
            application/json:
              schema: { $ref: '#/components/schemas/StudentSingleResponse' }
        '401': { $ref: '#/components/responses/Unauthorized' }
        '404': { $ref: '#/components/responses/NotFound' }
        '500': { $ref: '#/components/responses/InternalError' }

components:
  schemas:
    StudentSingleResponse:           # Standard single object shape (S2.19)
      type: object
      required: [data, message]
      properties:
        data: { $ref: '#/components/schemas/Student' }
        message: { type: string }
    ErrorResponse:                   # Standard error shape (S2.22)
      type: object
      required: [error, code, status]
      properties:
        error: { type: string }
        code: { type: string, enum: [UNAUTHORIZED, NOT_FOUND, VALIDATION_ERROR, INTERNAL_SERVER_ERROR] }
        status: { type: integer }
  securitySchemes:
    bearerAuth: { type: http, scheme: bearer, bearerFormat: JWT }
```

### Generate Schemas from OpenAPI (S2.24)

```bash
# Next.js — generate Zod from OpenAPI (never hand-write schemas)
npm install -D openapi-zod-client
npx openapi-zod-client openapi/v1/students.yaml -o src/schemas/students.schema.ts

# FastAPI — generate Pydantic from OpenAPI
pip install datamodel-code-generator
datamodel-codegen --input openapi/v1/students.yaml \
  --output app/students/models.py \
  --output-model-type pydantic_v2.BaseModel
```

---

## P2.5 — Standard Response Utilities

### Next.js Response Utilities (S2.19, S2.20, S2.21, S2.22)

```typescript
// lib/response.ts
import { NextResponse } from 'next/server'

export function successResponse<T>(data: T, message = 'Success', status = 200) {
  return NextResponse.json({ data, message }, { status })
}

export function createdResponse<T>(data: T, message = 'Created successfully') {
  return successResponse(data, message, 201)
}

export function listResponse<T>(data: T[], count: number, page: number, pageSize: number) {
  return NextResponse.json({
    data,
    count,
    page,
    totalPages: Math.ceil(count / pageSize),
  }, { status: 200 })
}

export function errorResponse(
  code: string,
  status: number,
  error?: string,
  fields?: { field: string; message: string }[]
) {
  const defaults: Record<string, string> = {
    UNAUTHORIZED: 'Authentication required',
    FORBIDDEN: 'You do not have permission',
    NOT_FOUND: 'The requested resource was not found',
    VALIDATION_ERROR: 'Validation failed',
    DUPLICATE_RECORD: 'A record with these details already exists',
    INTERNAL_SERVER_ERROR: 'An unexpected error occurred',
  }
  return NextResponse.json(
    { error: error ?? defaults[code] ?? 'An error occurred', code, status, ...(fields && { fields }) },
    { status }
  )
}
```

### Error Types and Global Handler (S2.22, S2.43, S2.44)

```typescript
// types/errors.ts
export class AppError extends Error {
  constructor(
    public readonly message: string,
    public readonly code: string,
    public readonly status: number,
    public readonly fields?: { field: string; message: string }[]
  ) { super(message); this.name = 'AppError' }
}

// lib/error-handler.ts
import { Prisma } from '@prisma/client'

export function handleError(error: unknown) {
  if (error instanceof AppError) {
    return errorResponse(error.code, error.status, error.message, error.fields)
  }
  if (error instanceof Prisma.PrismaClientKnownRequestError) {
    if (error.code === 'P2002') return errorResponse('DUPLICATE_RECORD', 409)
    if (error.code === 'P2003') return errorResponse('RECORD_IN_USE', 409)
    if (error.code === 'P2025') return errorResponse('NOT_FOUND', 404)
  }
  logger.error('Unhandled error', { error })
  return errorResponse('INTERNAL_SERVER_ERROR', 500)
}
```

```python
# core/errors.py
class AppError(Exception):
    def __init__(self, message: str, code: str, status: int):
        self.message = message
        self.code = code
        self.status = status

# main.py — register globally (S2.69)
@app.exception_handler(AppError)
async def app_error_handler(request, exc: AppError):
    return JSONResponse(status_code=exc.status,
                        content={"error": exc.message, "code": exc.code, "status": exc.status})

@app.exception_handler(Exception)
async def generic_handler(request, exc: Exception):
    logger.error("Unhandled exception", error=str(exc))
    return JSONResponse(status_code=500,
                        content={"error": "An unexpected error occurred",
                                 "code": "INTERNAL_SERVER_ERROR", "status": 500})
```

---

## P2.6 — Validation Layer

### Next.js Validation Middleware (S2.23, S2.26)

```typescript
// lib/validate.ts
import { z, ZodSchema } from 'zod'

export async function validateBody<T>(request: Request, schema: ZodSchema<T>) {
  try {
    const body = await request.json()
    const data = schema.parse(body)
    return { data }
  } catch (error) {
    if (error instanceof z.ZodError) {
      const fields = error.errors.map(e => ({ field: e.path.join('.'), message: e.message }))
      return { error: errorResponse('VALIDATION_ERROR', 400, 'Validation failed', fields) }
    }
    return { error: errorResponse('INVALID_INPUT', 400) }
  }
}

// Usage — validation gate before any service call
export async function POST(request: Request) {
  try {
    const session = await auth()
    if (!session) return errorResponse('UNAUTHORIZED', 401)

    const result = await validateBody(request, CreateStudentSchema)
    if ('error' in result) return result.error        // Reject immediately

    const student = await createStudent(result.data, session.user.id)
    return createdResponse(student)
  } catch (error) {
    return handleError(error)
  }
}
```

### Zod Schema with All Seven Validation Categories (S2.25, S2.51)

```typescript
// schemas/student.schema.ts — generated from OpenAPI, shown for reference
export const CreateStudentSchema = z.object({
  name: z.string().min(2).max(100).trim(),              // Required + length limits (S2.51)
  email: z.string().email().max(255).toLowerCase(),     // Format validation
  gpa: z.number().min(0).max(4.0),                      // Business rule — range
  phone: z.string().max(20).optional(),
  dateOfBirth: z.string().date().refine(                // Business rule — not future
    d => new Date(d) < new Date(),
    { message: 'Date of birth cannot be in the future' }
  ),
})
```

### Pydantic Model with Validation (S2.25, S2.51)

```python
# students/models.py
from pydantic import BaseModel, EmailStr, field_validator
from datetime import date

class CreateStudentRequest(BaseModel):
    name: str
    email: EmailStr                          # Format validation
    gpa: float
    date_of_birth: date

    model_config = {"str_max_length": 255, "str_strip_whitespace": True}  # S2.51

    @field_validator('gpa')
    @classmethod
    def validate_gpa(cls, v: float) -> float:
        if not 0.0 <= v <= 4.0:             # Business rule
            raise ValueError('GPA must be between 0.0 and 4.0')
        return v

    @field_validator('date_of_birth')
    @classmethod
    def validate_dob(cls, v: date) -> date:
        if v >= date.today():               # Business rule — not future
            raise ValueError('Date of birth cannot be in the future')
        return v
```

---

## P2.7 — Database Access Patterns

### Prisma Singleton (S2.75, S2.28)

```typescript
// lib/prisma.ts
import { PrismaClient } from '@prisma/client'
const globalForPrisma = globalThis as unknown as { prisma: PrismaClient }
export const prisma = globalForPrisma.prisma ?? new PrismaClient({
  log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
})
if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma
```

### Soft Delete Helpers (S2.35, S2.28)

```typescript
// lib/db-helpers.ts
export const activeWhere = (where: object = {}) => ({ ...where, deletedAt: null })

export async function softDelete(model: string, id: string, deletedBy: string) {
  await (prisma as any)[model].update({
    where: { id },
    data: { deletedAt: new Date(), deletedBy },
  })
}

// Usage — always use activeWhere() for standard queries
const students = await prisma.student.findMany({ where: activeWhere({ gpa: { gte: 3.0 } }) })

// Deletion — always soft, never hard (S2.35)
await softDelete('student', studentId, requestingUserId)
```

### Transaction Pattern (S2.30)

```typescript
export async function createApplicationWithAudit(
  data: CreateApplicationInput,
  studentId: string,
): Promise<ApplicationResponse> {
  return await prisma.$transaction(async (tx) => {
    const application = await tx.application.create({
      data: { ...data, studentId },
      select: { id: true, status: true, createdAt: true },
    })
    await tx.auditLog.create({
      data: { userId: studentId, action: 'CREATE', entity: 'Application', entityId: application.id },
    })
    // Both succeed or both roll back — no partial state
    return application
  })
}
```

### Idempotency Pattern for Financial Writes (S2.34)

```typescript
export async function processDisbursement(
  data: DisbursementInput,
  idempotencyKey: string,
): Promise<DisbursementResponse> {
  const existing = await prisma.disbursement.findUnique({ where: { idempotencyKey } })
  if (existing) return existing  // Already processed — return same result

  return await prisma.$transaction(async (tx) => {
    const disbursement = await tx.disbursement.create({ data: { ...data, idempotencyKey } })
    await tx.auditLog.create({
      data: { userId: data.funderId, action: 'CREATE', entity: 'Disbursement',
              entityId: disbursement.id, metadata: { amount: data.amount } },
    })
    return disbursement
  })
}
```

### N+1 Prevention (S2.32)

```typescript
// WRONG — N+1 query pattern
const students = await prisma.student.findMany({ where: activeWhere() })
const withApps = await Promise.all(
  students.map(s => prisma.application.findMany({ where: { studentId: s.id } }))
)

// CORRECT — single query with eager loading
const students = await prisma.student.findMany({
  where: activeWhere(),
  include: {
    applications: { where: { deletedAt: null }, select: { id: true, status: true } },
  },
  take: pageSize,
  skip: (page - 1) * pageSize,
})
```

### Pagination Helper (S2.14, S2.20)

```typescript
// lib/pagination.ts
export function getPaginationParams(params: URLSearchParams) {
  return {
    page: Math.max(1, parseInt(params.get('page') ?? '1')),
    pageSize: Math.min(100, Math.max(1, parseInt(params.get('pageSize') ?? '20'))),
  }
}

export async function listStudents(page: number, pageSize: number) {
  const [students, count] = await prisma.$transaction([
    prisma.student.findMany({
      where: activeWhere(),
      take: pageSize,
      skip: (page - 1) * pageSize,
      select: { id: true, name: true, email: true, gpa: true },
    }),
    prisma.student.count({ where: activeWhere() }),
  ])
  return { students, count }
}
```

---

## P2.8 — Performance Patterns

### Response Time Middleware (S2.59, S2.57)

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { v4 as uuidv4 } from 'uuid'

export function middleware(request: NextRequest) {
  const requestId = request.headers.get('x-request-id') ?? uuidv4()
  const start = Date.now()
  const response = NextResponse.next()
  response.headers.set('x-request-id', requestId)
  // durationMs logged — alert fires when P95 > 2000ms (S2.59, S2.61)
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(), level: 'info',
    message: 'Request completed', requestId,
    method: request.method, path: request.nextUrl.pathname,
    durationMs: Date.now() - start,
  }))
  return response
}
```

---

## P2.9 — Resilience Patterns

### External Call with Timeout (S2.42)

```typescript
export async function fetchWithTimeout(url: string, options: RequestInit, timeoutMs = 5000) {
  const controller = new AbortController()
  const id = setTimeout(() => controller.abort(), timeoutMs)
  try {
    return await fetch(url, { ...options, signal: controller.signal })
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new AppError('External service timed out', 'SERVICE_UNAVAILABLE', 503)
    }
    throw error
  } finally {
    clearTimeout(id)
  }
}
```

### Graceful Shutdown (S2.47)

```typescript
process.on('SIGTERM', async () => {
  server.close(async () => {
    await prisma.$disconnect()
    process.exit(0)
  })
  setTimeout(() => process.exit(1), 10000)  // Force exit after 10s grace period
})
```

```python
# FastAPI lifespan — handles SIGTERM automatically (S2.47)
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await disconnect_db()  # Runs on SIGTERM

app = FastAPI(lifespan=lifespan)
```

### Health Check (S2.48)

```typescript
// app/api/v1/health/route.ts
export async function GET() {
  try {
    await prisma.$queryRaw`SELECT 1`
    return Response.json({ status: 'healthy', database: 'connected',
                           timestamp: new Date().toISOString() }, { status: 200 })
  } catch {
    return Response.json({ status: 'unhealthy', database: 'disconnected',
                           timestamp: new Date().toISOString() }, { status: 503 })
  }
}
```

```python
# health/router.py (FastAPI)
@router.get("/health")
async def health_check(db=Depends(get_db)):
    try:
        await db.execute_raw("SELECT 1")
        return {"status": "healthy", "database": "connected",
                "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception:
        raise HTTPException(status_code=503,
                            detail={"status": "unhealthy", "database": "disconnected"})
```

---

## P2.10 — Security Implementation

### Sensitive Operation Re-Verification (S2.50)

```typescript
// lib/reverify.ts — call before any sensitive operation, never trust JWT alone
export async function reVerifyUser(userId: string) {
  const user = await prisma.user.findUnique({
    where: { id: userId },
    select: { id: true, role: true, status: true, deletedAt: true },
  })
  if (!user || user.deletedAt) throw new AppError('Account not found', 'UNAUTHORIZED', 401)
  if (user.status === 'LOCKED') throw new AppError('Account locked', 'ACCOUNT_LOCKED', 403)
  return user
}

// Usage in financial write service (S2.50)
export async function approveDisbursement(disbursementId: string, approverId: string) {
  const approver = await reVerifyUser(approverId)   // DB check — not JWT payload
  if (!['FUNDER', 'ADMIN'].includes(approver.role)) {
    throw new AppError('Insufficient permissions', 'FORBIDDEN', 403)
  }
  return await prisma.disbursement.update({
    where: { id: disbursementId },
    data: { status: 'APPROVED', approvedBy: approverId, approvedAt: new Date() },
  })
}
```

### Ownership Validation (S2.53)

```typescript
export async function validateOwnership(entity: string, id: string, userId: string) {
  const record = await (prisma as any)[entity].findUnique({
    where: { id, deletedAt: null },
    select: { studentId: true },
  })
  if (!record) throw new AppError('Resource not found', 'NOT_FOUND', 404)
  if (record.studentId !== userId) throw new AppError('Access denied', 'FORBIDDEN', 403)
}
```

### Brute Force Protection (S2.55)

```typescript
// lib/rate-limit.ts
import { LRUCache } from 'lru-cache'
const attempts = new LRUCache<string, number>({ max: 500, ttl: 1000 * 60 * 15 })

export function checkBruteForce(ip: string) {
  if ((attempts.get(ip) ?? 0) >= 10) {
    throw new AppError('Too many failed attempts', 'RATE_LIMIT_EXCEEDED', 429)
  }
}
export const recordFailedAttempt = (ip: string) => attempts.set(ip, (attempts.get(ip) ?? 0) + 1)
export const clearFailedAttempts = (ip: string) => attempts.delete(ip)
```

---

## P2.11 — Observability Setup

### Structured Logger (S2.56, S2.57)

```typescript
// lib/logger.ts
export const logger = {
  info: (message: string, meta?: object) => log('info', message, meta),
  warn: (message: string, meta?: object) => log('warn', message, meta),
  error: (message: string, meta?: object) => log('error', message, meta),
}

function log(level: string, message: string, meta: object = {}) {
  process.stdout.write(JSON.stringify({
    timestamp: new Date().toISOString(),
    level, message,
    service: process.env.SERVICE_NAME ?? 'ksdrill-api',
    ...meta,
  }) + '\n')
}
```

```python
# core/logger.py
import sys, json
from datetime import datetime, timezone

class StructuredLogger:
    def __init__(self, service: str):
        self.service = service

    def _log(self, level: str, message: str, **kwargs):
        entry = {"timestamp": datetime.now(timezone.utc).isoformat(),
                 "level": level, "message": message, "service": self.service, **kwargs}
        sys.stdout.write(json.dumps(entry) + "\n")
        sys.stdout.flush()

    def info(self, msg: str, **kw): self._log("info", msg, **kw)
    def error(self, msg: str, **kw): self._log("error", msg, **kw)
    def warn(self, msg: str, **kw): self._log("warn", msg, **kw)

logger = StructuredLogger(service="fundslink-api")
```

---

## P2.12 — FastAPI Implementation

### Application Entry Point (S2.63, S2.65, S2.69)

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.config import settings
from core.database import connect_db, disconnect_db
from core.errors import AppError
from core.logger import logger
from students.router import router as students_router
from scholarships.router import router as scholarships_router
from ai.router import router as ai_router
from health.router import router as health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    logger.info("Database connected")
    yield
    await disconnect_db()

app = FastAPI(title="FundsLink Academy API", version="1.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware,
    allow_origins=settings.allowed_origins,   # From env — never wildcard (S2.17)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"])

app.include_router(health_router)
app.include_router(students_router, prefix="/api/v1")     # Versioned prefix (S2.76)
app.include_router(scholarships_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status,
                        content={"error": exc.message, "code": exc.code, "status": exc.status})

@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception", error=str(exc))
    return JSONResponse(status_code=500,
                        content={"error": "An unexpected error occurred",
                                 "code": "INTERNAL_SERVER_ERROR", "status": 500})
```

### Pydantic Settings (S2.67)

```python
# core/config.py
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str                      # Missing = startup failure (S1.68)
    mongo_uri: str
    jwt_secret: str
    jwt_expiry_minutes: int = 15
    allowed_origins: List[str]
    service_name: str = "fundslink-api"
    environment: str = "development"
    sentry_dsn: str = ""

    model_config = {"env_file": ".env", "case_sensitive": False}

@lru_cache
def get_settings() -> Settings: return Settings()
settings = get_settings()
```

### FastAPI Router Pattern (S2.63, S2.64)

```python
# students/router.py
from fastapi import APIRouter, Depends
from students.models import CreateStudentRequest, StudentResponse
from students import service as student_service
from core.database import get_db
from core.security import get_current_user, require_role

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/", response_model=dict)
async def list_students(
    page: int = 1, page_size: int = 20,
    db=Depends(get_db),
    current_user=Depends(require_role(["ADMIN", "FUNDER"])),  # Explicit auth (S2.13)
):
    return await student_service.list_students(page, page_size, db)

@router.post("/", response_model=StudentResponse, status_code=201)
async def create_student(
    data: CreateStudentRequest,            # Pydantic validates at boundary (S2.23)
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await student_service.create_student(data, current_user.id, db)

@router.delete("/{student_id}", status_code=204)
async def delete_student(
    student_id: str, db=Depends(get_db),
    current_user=Depends(require_role(["ADMIN"])),
):
    await student_service.soft_delete_student(student_id, current_user.id, db)  # S2.35
```

---

## P2.13 — Next.js API Route Implementation

### Complete Route File (S2.70–S2.75)

```typescript
// app/api/v1/students/route.ts
import { auth } from '@/lib/auth'
import { validateBody } from '@/lib/validate'
import { CreateStudentSchema } from '@/schemas/student.schema'
import { listStudents, createStudent } from '@/services/student.service'
import { listResponse, createdResponse, errorResponse } from '@/lib/response'
import { handleError } from '@/lib/error-handler'
import { getPaginationParams } from '@/lib/pagination'

export async function GET(request: Request) {
  try {
    const session = await auth()
    if (!session) return errorResponse('UNAUTHORIZED', 401)

    const { searchParams } = new URL(request.url)
    const { page, pageSize } = getPaginationParams(searchParams)
    const { students, count } = await listStudents(page, pageSize)
    return listResponse(students, count, page, pageSize)
  } catch (error) { return handleError(error) }
}

export async function POST(request: Request) {
  try {
    const session = await auth()
    if (!session) return errorResponse('UNAUTHORIZED', 401)

    const result = await validateBody(request, CreateStudentSchema)
    if ('error' in result) return result.error

    const student = await createStudent(result.data, session.user.id)
    return createdResponse(student, 'Student created successfully')
  } catch (error) { return handleError(error) }
}
```

---

## P2.14 — API Versioning

### URL Prefix Strategy (S2.76, S2.79)

```typescript
// Next.js — directory structure enforces versioning automatically
// app/api/v1/students/route.ts  ← v1 handler
// app/api/v2/students/route.ts  ← v2 handler (when introduced, v1 stays)
```

```python
# FastAPI — both versions coexist in same deployment (S2.79)
from students.router_v1 import router as students_v1
from students.router_v2 import router as students_v2  # Added when needed

app.include_router(students_v1, prefix="/api/v1")  # Still active
app.include_router(students_v2, prefix="/api/v2")  # New version alongside
```

### Deprecation Header During Sunset (S2.78)

```typescript
export function withDeprecation(response: NextResponse, sunsetDate: string): NextResponse {
  response.headers.set('Deprecation', 'true')
  response.headers.set('Sunset', sunsetDate)
  response.headers.set('Link', '</api/v2/students>; rel="successor-version"')
  return response
}
```

---

## P2.15 — Tools & Commands Reference

### Next.js Stack

```bash
# Install
npm install prisma @prisma/client zod next-auth uuid lru-cache
npm install -D openapi-zod-client @types/uuid

# Prisma
npx prisma init
npx prisma generate
npx prisma migrate dev --name <migration-name>
npx prisma migrate deploy               # Production — runs before service starts (S2.33)
npx prisma studio

# Generate schemas from OpenAPI (never hand-write — S2.24)
npx openapi-zod-client openapi/v1/*.yaml -o src/schemas/

# Dev
npm run dev
npm run build && npm run start
```

### FastAPI Stack

```bash
# Install
pip install fastapi uvicorn[standard] pydantic pydantic-settings prisma beanie \
            motor httpx python-jose[cryptography] passlib[bcrypt] --break-system-packages

# Linting and type checking
ruff check app/              # Lint (S1.62)
ruff format app/             # Format (S1.62)
mypy app/                    # Type check (S1.57)
isort app/                   # Import order (S1.61)

# Generate Pydantic from OpenAPI (S2.24)
datamodel-codegen --input openapi/v1/students.yaml \
  --output app/students/models.py --output-model-type pydantic_v2.BaseModel

# Run
uvicorn app.main:app --reload            # Development
uvicorn app.main:app --workers 4        # Production

# Prisma (Python client)
prisma generate
prisma migrate deploy                    # Before service start (S2.33)
```

### Environment Variables (Both Stacks)

```bash
# .env.example — names only, never values (S1.84, S2.10)
DATABASE_URL=
MONGO_URI=
JWT_SECRET=
JWT_EXPIRY_MINUTES=
ALLOWED_ORIGINS=
NEXTAUTH_SECRET=
NEXTAUTH_URL=
SENTRY_DSN=
BETTER_STACK_SOURCE_TOKEN=
SERVICE_NAME=
ENVIRONMENT=
```

### Common Failure Patterns

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| Connection pool exhausted | Multiple `PrismaClient` instances | Use `lib/prisma.ts` singleton (S2.75) |
| Soft-deleted records appearing | Missing `deletedAt: null` filter | Use `activeWhere()` helper (S2.35) |
| Duplicate financial records | No idempotency key | Add `idempotencyKey` field + pre-check (S2.34) |
| Stack trace in API response | Error bypassed global handler | Ensure all routes use `handleError()` (S2.44) |
| CORS error in production | Wildcard or hardcoded origin | Set `ALLOWED_ORIGINS` env var (S2.17) |
| Migration fails on deploy | Service started before migrate | Fix pipeline order: migrate → start (S2.33) |
| Sensitive data in logs | `console.log(req.headers)` | Remove — use structured logger (S2.52) |
| N+1 slow queries | Loop with individual DB calls | Use Prisma `include` (S2.32) |
| Stale account in financial op | JWT payload trusted without re-verify | Call `reVerifyUser()` first (S2.50) |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock | Paired implementation guide for C2 Backend Constitution v1.0. Covers project structure, service layer patterns, extension-first patterns, OpenAPI setup and schema generation, standard response utilities, validation layer, database access (soft delete, transactions, idempotency, N+1 prevention, pagination), performance (response time middleware), resilience (timeouts, graceful shutdown, health check), security (re-verification, ownership, brute force), structured observability, complete FastAPI and Next.js implementations, API versioning, and tools reference. |

---

> **LOCKED — v1.0 — 2026-05-08**
>
> Practices may be updated to reflect tooling changes without a constitutional amendment,
> provided the updated practice continues to satisfy the standard it implements. Any
> practice change that would cause a constitutional standard to be violated requires
> a constitutional amendment first. Amendments follow C0 §8 protocol.

---

## P2.16 — Raw SQL Repository Pattern (S2.28e, S2.28f)

Added in v1.1 — implements the governed raw SQL escape hatch for queries that exceed
ORM capability. All four safety requirements (S2.28f) are demonstrated in every example.

### Repository File Structure (S2.28e)

```
services/
├── student.service.ts          # Business logic — no raw SQL
└── repositories/
    └── student.repository.ts   # Raw SQL only — when ORM cannot do it
```

```
app/students/
├── service.py                  # Business logic — no raw SQL
└── repository.py               # Raw SQL only — when ORM cannot do it
```

### Next.js Repository Pattern — All Four Safety Requirements

```typescript
// services/repositories/student.repository.ts
import { prisma, Prisma } from '@/lib/prisma'
import { z } from 'zod'

// Output schema — validates raw SQL result before leaving repository (Requirement 4)
const StudentRankingSchema = z.object({
  id: z.string(),
  name: z.string(),
  gpa: z.number(),
  facultyRank: z.number(),
  cohortSize: z.number(),
})
type StudentRanking = z.infer<typeof StudentRankingSchema>

export async function getStudentFacultyRankings(facultyId: string): Promise<StudentRanking[]> {
  // JUSTIFICATION: Prisma has no native support for PostgreSQL window functions.
  // RANK() OVER (PARTITION BY) cannot be expressed in Prisma's query builder.
  // Equivalent approach would require post-query sorting with N+1 count queries. (Requirement 3)
  const raw = await prisma.$queryRaw<unknown[]>`
    SELECT
      s.id,
      s.name,
      s.gpa,
      RANK() OVER (PARTITION BY s.faculty_id ORDER BY s.gpa DESC) AS "facultyRank",
      COUNT(*) OVER (PARTITION BY s.faculty_id)::int AS "cohortSize"
    FROM students s
    WHERE s.deleted_at IS NULL              -- Soft delete filter (Requirement 2)
      AND s.faculty_id = ${facultyId}       -- Parameterised input (Requirement 1)
  `
  // Validate and type the result before returning (Requirement 4)
  return StudentRankingSchema.array().parse(raw)
}

// Example: complex financial reporting query
const DisbursementReportSchema = z.object({
  funderId: z.string(),
  funderName: z.string(),
  totalDisbursed: z.number(),
  disbursementCount: z.number(),
  avgDisbursement: z.number(),
  lastDisbursementDate: z.date(),
})

export async function getDisbursementReport(
  fromDate: Date,
  toDate: Date,
): Promise<z.infer<typeof DisbursementReportSchema>[]> {
  // JUSTIFICATION: This aggregation across funders, disbursements, and students
  // with HAVING and date range filtering generates 4 separate Prisma queries.
  // Raw SQL produces a single optimised query plan. (Requirement 3)
  const raw = await prisma.$queryRaw<unknown[]>`
    SELECT
      f.id AS "funderId",
      f.name AS "funderName",
      SUM(d.amount)::numeric AS "totalDisbursed",
      COUNT(d.id)::int AS "disbursementCount",
      AVG(d.amount)::numeric AS "avgDisbursement",
      MAX(d.created_at) AS "lastDisbursementDate"
    FROM funders f
    INNER JOIN disbursements d ON d.funder_id = f.id
    WHERE f.deleted_at IS NULL            -- Soft delete (Requirement 2)
      AND d.deleted_at IS NULL            -- Soft delete on joined table (Requirement 2)
      AND d.created_at BETWEEN ${fromDate} AND ${toDate}  -- Parameterised (Requirement 1)
      AND d.status = 'APPROVED'
    GROUP BY f.id, f.name
    HAVING SUM(d.amount) > 0
    ORDER BY "totalDisbursed" DESC
  `
  return DisbursementReportSchema.array().parse(raw)  // Validated (Requirement 4)
}
```

### FastAPI Repository Pattern — All Four Safety Requirements

```python
# students/repository.py
from prisma import Prisma
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Output schema — validates raw SQL result (Requirement 4)
class StudentRanking(BaseModel):
    id: str
    name: str
    gpa: float
    faculty_rank: int
    cohort_size: int

async def get_student_faculty_rankings(
    faculty_id: str,
    db: Prisma,
) -> list[StudentRanking]:
    # JUSTIFICATION: PostgreSQL window functions (RANK OVER PARTITION) are not
    # supported in Prisma Python client's query builder. (Requirement 3)
    raw = await db.query_raw(
        """
        SELECT
            s.id,
            s.name,
            s.gpa,
            RANK() OVER (PARTITION BY s.faculty_id ORDER BY s.gpa DESC) AS faculty_rank,
            COUNT(*) OVER (PARTITION BY s.faculty_id)::int AS cohort_size
        FROM students s
        WHERE s.deleted_at IS NULL          -- Soft delete filter (Requirement 2)
          AND s.faculty_id = $1            -- Parameterised (Requirement 1)
        """,
        faculty_id,                         # Parameter — never interpolated
    )
    # Validate with Pydantic before returning (Requirement 4)
    return [StudentRanking.model_validate(row) for row in raw]


class DisbursementSummary(BaseModel):
    funder_id: str
    funder_name: str
    total_disbursed: float
    disbursement_count: int
    last_disbursement_date: datetime

async def get_disbursement_summary(
    from_date: datetime,
    to_date: datetime,
    db: Prisma,
) -> list[DisbursementSummary]:
    # JUSTIFICATION: GROUP BY with HAVING and multi-table aggregation across
    # funders and disbursements produces 3 separate Prisma queries.
    # Single raw SQL query is significantly more efficient. (Requirement 3)
    raw = await db.query_raw(
        """
        SELECT
            f.id AS funder_id,
            f.name AS funder_name,
            SUM(d.amount) AS total_disbursed,
            COUNT(d.id)::int AS disbursement_count,
            MAX(d.created_at) AS last_disbursement_date
        FROM funders f
        INNER JOIN disbursements d ON d.funder_id = f.id
        WHERE f.deleted_at IS NULL          -- Soft delete (Requirement 2)
          AND d.deleted_at IS NULL          -- Soft delete on joined table (Requirement 2)
          AND d.created_at BETWEEN $1 AND $2  -- Parameterised (Requirement 1)
          AND d.status = 'APPROVED'
        GROUP BY f.id, f.name
        HAVING SUM(d.amount) > 0
        """,
        from_date, to_date,
    )
    return [DisbursementSummary.model_validate(row) for row in raw]  # Validated (Req 4)
```

### Service Layer Calls Repository — Never Knows It Is Raw SQL

```typescript
// services/student.service.ts — calls repository, never sees raw SQL
import { getStudentFacultyRankings } from './repositories/student.repository'

export async function getStudentRankings(
  facultyId: string,
  requestingUserId: string,
): Promise<StudentRanking[]> {
  // Re-verify for sensitive read (S2.50)
  await reVerifyUser(requestingUserId)

  // Service calls repository — does not know or care if ORM or raw SQL (S2.2)
  return await getStudentFacultyRankings(facultyId)
}
```

### When NOT to Use Raw SQL — Common Mistakes

```typescript
// These are NOT valid justifications for raw SQL — use Prisma instead

// WRONG justification: "It's simpler to write in SQL"
// CORRECT: Use prisma.student.findMany() with proper select/include

// WRONG justification: "I'm more comfortable with SQL than Prisma"
// CORRECT: Learn Prisma — comfort is not a performance justification

// WRONG justification: "The query is complex"
// CORRECT: Complex Prisma queries are still Prisma queries — complexity alone
// is not sufficient. The ORM must be demonstrably incapable or demonstrably
// slower beyond the two-second target (S2.36).
```


---

> **Amendment — v1.1 — 2026-05-08:** Added P2.16 Raw SQL Repository Pattern
> implementing S2.28e and S2.28f. All four safety requirements demonstrated with
> Next.js and FastAPI examples for window functions, aggregations, and financial
> reporting queries. Follows C0 §8 amendment protocol.
