# C3 — Auth Implementation Guide

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C3 — Auth Implementation Guide                                     |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | Both Stacks                                                        |
| **Paired With**    | C3 — Auth Constitution                                             |

---

> *"A standard tells you what must be true. This guide tells you how to make it true."*

---

## Opening Statement

This guide is the operational companion to the C3 Auth Constitution. Every practice here satisfies a specific standard in C3. When the constitution says "access tokens in Angular memory" (S3.14), this guide shows the exact Angular service implementation. When the constitution says "RS256-signed JWT" (S3.13), this guide provides the FastAPI key configuration, token issuance, and validation code.

This document contains code, configuration, schema definitions, and step-by-step procedures. The constitution contains the why. This guide contains the how. Read the constitution first to understand what auth must do. Use this guide when building it.

---

## Table of Contents

| Section | Title |
|---------|-------|
| P3.1 | Database Schema — Auth Tables |
| P3.2 | NextAuth.js Setup — Next.js Stack |
| P3.3 | Email Verification Flow |
| P3.4 | Password Reset Flow |
| P3.5 | FastAPI JWT Setup — Angular Stack |
| P3.6 | Angular Auth Service and Token Store |
| P3.7 | HTTP Interceptor with Refresh Deduplication |
| P3.8 | Security Baseline Implementation |
| P3.9 | Audit Logging Implementation |
| P3.10 | Rate Limiting Implementation |
| P3.11 | Tools & Commands Reference |

---

## P3.1 — Database Schema — Auth Tables

### Prisma Schema — Auth Models (S3.2, S3.21, S3.33)

```prisma
// schema.prisma — Auth domain models

enum Role {
  USER
  ADMIN
  // Next.js systems
  CREATOR          // SyncUp only
  // Angular systems
  STUDENT          // FundsLink only
  FUNDER           // FundsLink only
  ACCOUNT_HOLDER   // Reserve Bank only
  WARD_ADMIN       // Maphophe only
}

model User {
  id                String    @id @default(cuid())
  created_at        DateTime  @default(now())
  updated_at        DateTime  @updatedAt
  deleted_at        DateTime?

  email             String    @unique
  email_verified    DateTime?
  password_hash     String?
  name              String?
  image             String?
  role              Role      @default(USER)

  // Next.js stack only
  sessions          Session[]
  accounts          Account[]
  verification_tokens VerificationToken[]

  // Angular stack only
  refresh_tokens    RefreshToken[]
  
  audit_logs        AuditLog[]

  @@index([email])
}

// Next.js Stack — NextAuth database session
model Session {
  id           String   @id @default(cuid())
  created_at   DateTime @default(now())
  updated_at   DateTime @updatedAt

  session_token String   @unique
  user_id       String
  expires       DateTime

  user          User     @relation(fields: [user_id], references: [id], onDelete: Cascade)

  @@index([user_id])
  @@index([session_token])
}

model Account {
  id                  String  @id @default(cuid())
  created_at          DateTime @default(now())
  updated_at          DateTime @updatedAt

  user_id             String
  type                String
  provider            String
  provider_account_id String
  refresh_token       String? @db.Text
  access_token        String? @db.Text
  expires_at          Int?
  token_type          String?
  scope               String?
  id_token            String? @db.Text
  session_state       String?

  user                User    @relation(fields: [user_id], references: [id], onDelete: Cascade)

  @@unique([provider, provider_account_id])
  @@index([user_id])
}

model VerificationToken {
  id         String   @id @default(cuid())
  created_at DateTime @default(now())

  identifier String
  token      String   @unique
  expires    DateTime

  @@unique([identifier, token])
  @@index([token])
}

// Angular Stack — JWT refresh tokens
model RefreshToken {
  id          String    @id @default(cuid())
  created_at  DateTime  @default(now())

  token_hash  String    @unique  // SHA-256 hash of raw token
  user_id     String
  expires_at  DateTime
  revoked_at  DateTime?
  replaced_by String?           // token_hash of replacement (family chain)
  device_hint String?

  user        User      @relation(fields: [user_id], references: [id], onDelete: Cascade)

  @@index([user_id])
  @@index([token_hash])
}

// Both stacks — Immutable audit log
model AuditLog {
  id         String   @id @default(cuid())
  created_at DateTime @default(now())

  user_id    String?
  event      String   // login_success | login_fail | logout | token_refresh | etc.
  ip_address String?
  user_agent String?
  metadata   Json?    // JSONB: reason, role changes, provider, etc.

  user       User?    @relation(fields: [user_id], references: [id])

  // No deleted_at — immutable by design (S3.33)
  @@index([user_id])
  @@index([event])
  @@index([created_at])
}

// SystemConfig — OAuth providers, domain allowlists (S3.26, S3.27)
model SystemConfig {
  id         String   @id @default(cuid())
  created_at DateTime @default(now())
  updated_at DateTime @updatedAt

  key        String   @unique
  value      Json

  @@index([key])
}
```

---

## P3.2 — NextAuth.js Setup — Next.js Stack (S3.5–S3.12)

### Installation

```bash
npm install next-auth @auth/prisma-adapter
```

### NextAuth Configuration (`src/lib/auth.ts`)

```typescript
import NextAuth, { type NextAuthOptions } from "next-auth"
import { PrismaAdapter } from "@auth/prisma-adapter"
import GoogleProvider from "next-auth/providers/google"
import CredentialsProvider from "next-auth/providers/credentials"
import { prisma } from "@/lib/prisma"
import bcrypt from "bcrypt"
import { Role } from "@prisma/client"

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),

  // S3.5 — Database sessions, never JWT
  session: {
    strategy: "database",
    maxAge: parseInt(process.env.SESSION_MAX_AGE_SECONDS ?? "2592000"), // S3.9
  },

  // S3.6 — HttpOnly cookies
  cookies: {
    sessionToken: {
      name: `__Secure-next-auth.session-token`,
      options: {
        httpOnly: true,
        sameSite: "lax",
        path: "/",
        secure: true,
      },
    },
  },

  providers: [
    // S3.10 — OAuth through NextAuth only
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),

    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null

        const user = await prisma.user.findFirst({
          where: { email: credentials.email, deleted_at: null },
          select: {
            id: true, email: true, name: true,
            role: true, image: true, password_hash: true,
            email_verified: true,
          },
        })

        if (!user || !user.password_hash) return null

        const valid = await bcrypt.compare(credentials.password, user.password_hash)
        if (!valid) return null

        // S3.8 — Return safe fields only
        const { password_hash, ...safeUser } = user
        return safeUser
      },
    }),
  ],

  callbacks: {
    // S3.8 — Safe fields only in session
    async session({ session, user }) {
      return {
        ...session,
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          image: user.image,
          role: (user as any).role as Role,
        },
      }
    },

    async signIn({ user, account }) {
      // S3.27 — Domain validation for institutional systems
      if (account?.provider !== "credentials") {
        const config = await prisma.systemConfig.findUnique({
          where: { key: "oauth_domain_allowlist" },
        })
        if (config?.value) {
          const allowedDomains = config.value as string[]
          const emailDomain = user.email?.split("@")[1]
          if (allowedDomains.length > 0 && !allowedDomains.includes(emailDomain ?? "")) {
            return `/auth/error?error=DomainNotAllowed`
          }
        }
      }
      return true
    },
  },

  // S3.11 — CSRF protection never disabled (NextAuth default: enabled)
  pages: {
    signIn: "/auth/login",
    error: "/auth/error",
    verifyRequest: "/auth/verify-email",
  },
}

export default NextAuth(authOptions)
```

### Route Protection Middleware (`middleware.ts`) — S3.7

```typescript
import { withAuth } from "next-auth/middleware"
import { NextResponse } from "next/server"

export default withAuth(
  function middleware(req) {
    const token = req.nextauth.token
    const path = req.nextUrl.pathname

    // Role-based route protection (S3.21, S3.23)
    if (path.startsWith("/admin") && token?.role !== "ADMIN") {
      return NextResponse.redirect(new URL("/auth/login", req.url))
    }

    return NextResponse.next()
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
  }
)

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/admin/:path*",
    "/api/v1/:path*",
  ],
}
```

---

## P3.3 — Email Verification Flow (S3.12)

### Generate Verification Token (`src/lib/auth/email-verification.ts`)

```typescript
import crypto from "crypto"
import { prisma } from "@/lib/prisma"

const VERIFICATION_EXPIRY_HOURS = 24
const RESEND_LIMIT_PER_HOUR = 3

export async function generateVerificationToken(email: string): Promise<string> {
  // Check resend rate limit (S3.12)
  const recentCount = await prisma.verificationToken.count({
    where: {
      identifier: email,
      created_at: { gte: new Date(Date.now() - 3_600_000) },
    },
  })
  if (recentCount >= RESEND_LIMIT_PER_HOUR) {
    throw new Error("RESEND_LIMIT_EXCEEDED")
  }

  // Delete previous tokens for this email
  await prisma.verificationToken.deleteMany({ where: { identifier: email } })

  const rawToken = crypto.randomBytes(32).toString("hex")
  const hashedToken = crypto.createHash("sha256").update(rawToken).digest("hex")

  await prisma.verificationToken.create({
    data: {
      identifier: email,
      token: hashedToken,
      expires: new Date(Date.now() + VERIFICATION_EXPIRY_HOURS * 3_600_000),
    },
  })

  return rawToken // Send raw token in email; store hash
}

export async function verifyEmailToken(token: string): Promise<boolean> {
  const hashedToken = crypto.createHash("sha256").update(token).digest("hex")

  const record = await prisma.verificationToken.findUnique({
    where: { token: hashedToken },
  })

  if (!record || record.expires < new Date()) return false

  await prisma.$transaction([
    prisma.user.updateMany({
      where: { email: record.identifier },
      data: { email_verified: new Date() },
    }),
    prisma.verificationToken.delete({ where: { token: hashedToken } }),
  ])

  return true
}
```

---

## P3.4 — Password Reset Flow (S3.30)

### Password Reset Implementation (`src/lib/auth/password-reset.ts`)

```typescript
import crypto from "crypto"
import bcrypt from "bcrypt"
import { prisma } from "@/lib/prisma"

const RESET_EXPIRY_HOURS = 1
const BCRYPT_ROUNDS = parseInt(process.env.BCRYPT_ROUNDS ?? "12") // S3.3

// Always returns identical message — enumeration-proof (S3.30)
const RESET_RESPONSE = "If an account exists with that email, a reset link has been sent."

export async function initiatePasswordReset(email: string): Promise<string> {
  const user = await prisma.user.findFirst({
    where: { email, deleted_at: null },
    select: { id: true },
  })

  // Return identical message regardless of whether user exists (S3.30)
  if (!user) return RESET_RESPONSE

  const rawToken = crypto.randomBytes(32).toString("hex")
  const hashedToken = crypto.createHash("sha256").update(rawToken).digest("hex")

  await prisma.verificationToken.create({
    data: {
      identifier: `reset:${email}`,
      token: hashedToken,
      expires: new Date(Date.now() + RESET_EXPIRY_HOURS * 3_600_000),
    },
  })

  // Send email with rawToken (implementation in email service)
  return RESET_RESPONSE
}

export async function completePasswordReset(
  token: string,
  newPassword: string
): Promise<boolean> {
  const hashedToken = crypto.createHash("sha256").update(token).digest("hex")

  const record = await prisma.verificationToken.findUnique({
    where: { token: hashedToken },
  })

  if (!record || record.expires < new Date()) return false

  const email = record.identifier.replace("reset:", "")
  const user = await prisma.user.findFirst({
    where: { email, deleted_at: null },
    select: { id: true },
  })

  if (!user) return false

  const newHash = await bcrypt.hash(newPassword, BCRYPT_ROUNDS)

  // S3.35 — Invalidate all sessions and tokens on password change
  await prisma.$transaction([
    prisma.user.update({
      where: { id: user.id },
      data: { password_hash: newHash },
    }),
    prisma.session.deleteMany({ where: { user_id: user.id } }),
    prisma.verificationToken.delete({ where: { token: hashedToken } }),
  ])

  return true
}
```

---

## P3.5 — FastAPI JWT Setup — Angular Stack (S3.13–S3.20)

### RS256 Key Generation

```bash
# Generate RS256 key pair (run once per environment)
openssl genrsa -out private_key.pem 2048
openssl rsa -in private_key.pem -pubout -out public_key.pem

# Store in Railway Secrets (S3.20):
# RS256_PRIVATE_KEY = contents of private_key.pem
# RS256_PUBLIC_KEY = contents of public_key.pem
# Delete local files immediately after storing in Railway
```

### FastAPI Auth Configuration (`app/auth/jwt.py`)

```python
import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import redis

# RS256 keys from Railway Secrets (S3.20)
PRIVATE_KEY = os.environ["RS256_PRIVATE_KEY"]
PUBLIC_KEY = os.environ["RS256_PUBLIC_KEY"]
ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

redis_client = redis.from_url(os.environ["REDIS_URL"])
bearer_scheme = HTTPBearer()


def create_access_token(user_id: str, role: str, email: str) -> str:
    """Issue RS256-signed access token with required claims (S3.13)."""
    jti = str(uuid4())
    payload = {
        "sub": user_id,
        "role": role,
        "email": email,
        "jti": jti,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)


def create_refresh_token() -> tuple[str, str]:
    """Generate 64-byte random refresh token; return (raw, sha256_hash). (S3.13)"""
    raw = secrets.token_bytes(64).hex()
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db=Depends(get_db),
):
    """
    FastAPI Depends() for JWT validation (S3.17).
    Decodes RS256 → verifies expiry → checks JTI deny-list → queries User.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials, PUBLIC_KEY, algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        if user_id is None or jti is None:
            raise credentials_exception

        # Check JTI deny-list (S3.18)
        if redis_client.get(f"jti_deny:{jti}"):
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = await db.get_user_by_id(user_id)
    if user is None or user.deleted_at is not None:
        raise credentials_exception

    return user


def require_role(*roles: str):
    """Role-based dependency that wraps get_current_user (S3.17)."""
    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in roles and current_user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker
```

### Login Endpoint (`app/auth/router.py`)

```python
from fastapi import APIRouter, Response, Cookie
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/login")
async def login(credentials: LoginSchema, response: Response, db=Depends(get_db)):
    user = await db.get_user_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user.password_hash):
        # S3.4 — Identical error for invalid credentials and locked accounts
        await log_auth_event(db, None, "login_fail", reason="invalid_credentials")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(user.id, user.role, user.email)
    raw_refresh, hashed_refresh = create_refresh_token()

    await db.create_refresh_token(
        user_id=user.id,
        token_hash=hashed_refresh,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    # S3.14 — Refresh token in HttpOnly cookie; access token in response body (→ Angular memory)
    response.set_cookie(
        key="refresh_token",
        value=raw_refresh,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/api/v1/auth",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    await log_auth_event(db, user.id, "login_success")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh_token(
    response: Response,
    refresh_token: str = Cookie(None),
    db=Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    hashed = hashlib.sha256(refresh_token.encode()).hexdigest()
    token_record = await db.get_refresh_token(hashed)

    if not token_record or token_record.revoked_at or token_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # S3.16 — Replay detection: if token was already replaced, revoke all tokens
    if token_record.replaced_by:
        await db.revoke_all_user_tokens(token_record.user_id)
        await log_auth_event(db, token_record.user_id, "token_theft_detected")
        # Alert: Sentry.capture_event(...)
        raise HTTPException(status_code=401, detail="Token reuse detected")

    user = await db.get_user_by_id(token_record.user_id)
    new_access = create_access_token(user.id, user.role, user.email)
    raw_new_refresh, hashed_new_refresh = create_refresh_token()

    # Rotate — mark old as replaced, create new (S3.16)
    await db.rotate_refresh_token(
        old_hash=hashed,
        new_hash=hashed_new_refresh,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    response.set_cookie(
        key="refresh_token",
        value=raw_new_refresh,
        httponly=True, secure=True, samesite="strict",
        path="/api/v1/auth",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return {"access_token": new_access, "token_type": "bearer"}
```

---

## P3.6 — Angular Auth Service and Token Store (S3.14)

### Auth State Service (`src/app/auth/auth.service.ts`)

```typescript
import { Injectable, signal } from "@angular/core"
import { HttpClient } from "@angular/common/http"
import { BroadcastChannel } from "broadcast-channel"
import { Observable, tap } from "rxjs"

interface AuthState {
  accessToken: string | null
  user: { id: string; email: string; role: string } | null
}

@Injectable({ providedIn: "root" })
export class AuthService {
  // S3.14 — Access token in Angular memory only — never localStorage
  private state = signal<AuthState>({ accessToken: null, user: null })
  private logoutChannel = new BroadcastChannel("auth_logout")

  readonly accessToken = this.state().accessToken
  readonly currentUser = this.state().user

  constructor(private http: HttpClient) {
    // S3.18 — Listen for logout from other tabs
    this.logoutChannel.onmessage = () => this.clearState()
  }

  login(email: string, password: string): Observable<{ access_token: string }> {
    return this.http.post<{ access_token: string }>("/api/v1/auth/login", { email, password })
      .pipe(tap(res => this.setToken(res.access_token)))
  }

  setToken(token: string): void {
    const payload = this.decodeToken(token)
    this.state.set({
      accessToken: token,
      user: { id: payload.sub, email: payload.email, role: payload.role },
    })
  }

  logout(): Observable<void> {
    return this.http.post<void>("/api/v1/auth/logout", {})
      .pipe(tap(() => {
        this.clearState()
        this.logoutChannel.postMessage("logout") // S3.18 — Notify all tabs
      }))
  }

  clearState(): void {
    this.state.set({ accessToken: null, user: null })
  }

  getAccessToken(): string | null {
    return this.state().accessToken
  }

  private decodeToken(token: string): any {
    const payload = token.split(".")[1]
    return JSON.parse(atob(payload))
  }
}
```

---

## P3.7 — HTTP Interceptor with Refresh Deduplication (S3.15)

### Auth Interceptor (`src/app/auth/auth.interceptor.ts`)

```typescript
import { Injectable } from "@angular/core"
import {
  HttpRequest, HttpHandler, HttpEvent,
  HttpInterceptor, HttpErrorResponse
} from "@angular/common/http"
import { Observable, throwError, BehaviorSubject } from "rxjs"
import { catchError, filter, take, switchMap } from "rxjs/operators"
import { AuthService } from "./auth.service"
import { v4 as uuidv4 } from "uuid"

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private isRefreshing = false
  // S3.15 — Deduplication: queue concurrent 401s during refresh
  private refreshSubject = new BehaviorSubject<string | null>(null)

  constructor(private authService: AuthService, private http: HttpClient) {}

  intercept(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const token = this.authService.getAccessToken()
    const authReq = this.addHeaders(req, token)

    return next.handle(authReq).pipe(
      catchError(error => {
        if (error instanceof HttpErrorResponse && error.status === 401) {
          return this.handle401(req, next)
        }
        return throwError(() => error)
      })
    )
  }

  private addHeaders(req: HttpRequest<unknown>, token: string | null): HttpRequest<unknown> {
    const headers: Record<string, string> = {
      "X-Request-ID": uuidv4(), // S2.60 trace propagation
    }
    if (token) headers["Authorization"] = `Bearer ${token}`
    return req.clone({ setHeaders: headers })
  }

  private handle401(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    if (this.isRefreshing) {
      // S3.15 — Already refreshing: queue this request until refresh completes
      return this.refreshSubject.pipe(
        filter(token => token !== null),
        take(1),
        switchMap(token => next.handle(this.addHeaders(req, token)))
      )
    }

    this.isRefreshing = true
    this.refreshSubject.next(null)

    return this.http.post<{ access_token: string }>("/api/v1/auth/refresh", {})
      .pipe(
        switchMap(res => {
          this.isRefreshing = false
          this.authService.setToken(res.access_token)
          this.refreshSubject.next(res.access_token)
          return next.handle(this.addHeaders(req, res.access_token))
        }),
        catchError(err => {
          this.isRefreshing = false
          this.authService.logout().subscribe()
          return throwError(() => err)
        })
      )
  }
}
```

---

## P3.8 — Security Baseline Implementation (S3.28–S3.32)

### Next.js Security Headers (`next.config.js`) — S3.31

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline'",  // tighten per system
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: https:",
              "connect-src 'self'",
            ].join("; "),
          },
        ],
      },
    ]
  },
}
module.exports = nextConfig
```

### FastAPI CORS and Security Middleware (`app/main.py`) — S3.29, S3.31

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# S3.29 — CORS locked to known origins, never wildcard
allowed_origins = os.environ["CORS_ALLOWED_ORIGINS"].split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### bcrypt Password Hashing (`app/auth/passwords.py`) — S3.3

```python
import os
import bcrypt

ROUNDS = int(os.environ.get("BCRYPT_ROUNDS", "12"))  # S3.3 — env var, never hardcoded

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=ROUNDS)).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

---

## P3.9 — Audit Logging Implementation (S3.33)

### Audit Log Service (`src/lib/auth/audit.ts` and `app/auth/audit.py`)

**Next.js Audit Service:**

```typescript
import { prisma } from "@/lib/prisma"

type AuthEvent =
  | "login_success" | "login_fail" | "logout"
  | "token_refresh" | "token_theft" | "password_change"
  | "password_reset_request" | "password_reset_complete"
  | "email_verification" | "role_change"
  | "account_lock" | "account_unlock"
  | "registration" | "oauth_link" | "oauth_reject"

export async function logAuthEvent(
  userId: string | null,
  event: AuthEvent,
  request: Request,
  metadata?: Record<string, unknown>
): Promise<void> {
  const ip = request.headers.get("x-forwarded-for") ?? "unknown"
  const userAgent = request.headers.get("user-agent") ?? "unknown"

  await prisma.auditLog.create({
    data: {
      user_id: userId,
      event,
      ip_address: ip,
      user_agent: userAgent,
      metadata: metadata ?? {},
    },
  })
}
```

**FastAPI Audit Service:**

```python
from datetime import datetime, timezone
from typing import Optional

async def log_auth_event(
    db,
    user_id: Optional[str],
    event: str,
    ip_address: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> None:
    # S3.33 — Append-only, never update or delete
    await db.create_audit_log(
        user_id=user_id,
        event=event,
        ip_address=ip_address,
        metadata=metadata or {},
    )
```

---

## P3.10 — Rate Limiting Implementation (S3.4)

### Three-Layer Rate Limiting — FastAPI

```python
import redis
from datetime import datetime, timezone

redis_client = redis.from_url(os.environ["REDIS_URL"])

async def check_rate_limits(email: str, ip: str) -> None:
    # Layer 1 — IP-based (10 requests/IP/15min)
    ip_key = f"rl_ip:{ip}"
    ip_count = redis_client.incr(ip_key)
    if ip_count == 1:
        redis_client.expire(ip_key, 900)  # 15 min TTL
    if ip_count > 10:
        raise HTTPException(status_code=429, detail="Too many requests")

    # Layer 2 — Account-based locking (5 failures → 15min lock)
    lock_key = f"account_lock:{email}"
    if redis_client.get(lock_key):
        # S3.4 — Identical error — enumeration-proof
        raise HTTPException(status_code=401, detail="Invalid credentials")

    fail_key = f"login_fail:{email}"
    fail_count = int(redis_client.get(fail_key) or 0)
    if fail_count >= 5:
        redis_client.setex(lock_key, 900, "locked")  # 15 min
        # Send security email to user
        raise HTTPException(status_code=401, detail="Invalid credentials")
```

---

## P3.11 — Tools & Commands Reference

| Task | Command |
|------|---------|
| Generate RS256 key pair | `openssl genrsa -out private.pem 2048 && openssl rsa -in private.pem -pubout -out public.pem` |
| Run Prisma auth migration | `npx prisma migrate dev --name add_auth_tables` |
| Deploy Prisma migration (prod) | `npx prisma migrate deploy` |
| Seed roles enum | Run `npx prisma db seed` with seed file |
| Test NextAuth session | `curl -I https://your-app.vercel.app/api/auth/session` |
| Check FastAPI JWT decode | `python -c "from jose import jwt; print(jwt.decode(TOKEN, PUBLIC_KEY, algorithms=['RS256']))"` |
| Flush Redis deny-list | `redis-cli KEYS "jti_deny:*" \| xargs redis-cli DEL` |
| Audit log query (last 100 auth events) | `prisma.auditLog.findMany({ orderBy: { created_at: 'desc' }, take: 100 })` |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock | Rebuilt from Auth Implementation Blueprint v1.1. localStorage regression corrected in P3.6 (access token in Angular memory via Signal, never localStorage). Deduplication logic added to interceptor (P3.7). bcrypt environment variable pattern standardised (P3.8). |

---

> **LOCKED — v1.0 — 2026-05-08**
>
> This document is locked. No practice may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Any practice change that would cause a constitutional standard to be violated
> requires a constitutional amendment to C3 first, then an update here.
