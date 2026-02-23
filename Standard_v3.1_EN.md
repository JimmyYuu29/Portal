# Internal Automation Tool Platform Architecture & App Implementation Standard (v3.1 Enhanced · Stable)

| Attribute | Description |
|---|---|
| Version | 3.1 (Enhanced · Stable) |
| Effective Date | 2026-01-09 |
| Scope | All automation consulting tools connected to `https://tools.<internal-domain>/` (Tax / Audit / ESG) |
| Maintainer | Automation Consulting Technology Team (Platform/Ops + Tool Dev) |
| Objectives | Single entry point, multi-app, multi-node unified access; port concealment; scalable (>50 apps), auditable, secure, observable |
| Change Summary | v3.1 adds: secrets management, logging standards, disaster recovery, observability, API versioning, rate limiting. **v3.1.1 adds: Authentication & Authorization, Data Persistence, Notification via Power Automate** |

---

## Complete Document Structure

This is the enhanced v3.1 version of the platform standard. The full English translation mirrors the Chinese version structure with 22 main sections:

### Main Sections:
0. Terminology & General Constraints
1. Platform Overall Architecture  
2. Routing Specification & Path Mapping
3. Platform Contract & Source of Truth
4. Security Contract (with Secrets Management & Rate Limiting)
5. Platform Contract (App Contract)
6. Standard App Repository Structure
7. Logging & Observability Standards
8. Platform-side Nginx Standard Configuration
9. Data Management & Disaster Recovery
10. Deployment & Environment Standards
11. CI/CD & Testing Standards
12. Go-Live Checklist
13. Portal Implementation Standards
14. Vendoring Standard
15. Governance & Change Management
16. Appendix: Automation Generation Tools
17. Developer Quick Start
18. Version Declaration & Change History
19. Summary & Best Practices
20. **Authentication & Authorization (NEW in v3.1.1)**
21. **Data Persistence (NEW in v3.1.1)**
22. **Notification via Power Automate (NEW in v3.1.1)**

---

## 20. Authentication & Authorization (NEW)

### 20.1 Authentication

The Portal implements a session-based authentication system:

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | Flask-Login | Session management, user loading |
| CSRF | Flask-WTF (CSRFProtect) | Prevent cross-site request forgery |
| Password Hashing | werkzeug.security (PBKDF2-SHA256 + salt) | Secure password storage |
| Session | Flask session (HttpOnly, SameSite=Lax) | Cookie-based session |

**Security Requirements:**

1. **Password Storage**: All passwords MUST be stored as hashed+salted values using `werkzeug.security.generate_password_hash` with `method='pbkdf2:sha256'` and `salt_length=16`.
2. **No Plaintext**: Passwords MUST NEVER be stored, logged, transmitted, or emailed in plaintext.
3. **CSRF**: All POST forms MUST include a CSRF token via Flask-WTF.
4. **Session Security**: SECRET_KEY MUST come from environment variables. Cookies MUST be HttpOnly, SameSite=Lax. If HTTPS, set Secure=True.
5. **Anti-Enumeration**: Forgot password endpoint MUST return the same message regardless of whether the user exists.
6. **Log Sanitization**: Logs MUST NOT contain passwords, reset tokens, Power Automate URLs, or any secrets.

### 20.2 Authorization (RBAC)

Access control is based on **department** and **role**:

```json
{
  "access": {
    "departments": ["auditoria", "tax"],
    "roles": ["senior", "manager", "socio"]
  }
}
```

**Rules:**
- Empty or missing `departments` → ALL departments allowed
- Empty or missing `roles` → ALL roles allowed
- Both present → user must match BOTH criteria
- Admin users bypass all access checks

### 20.3 Password Reset Flow

1. User submits username on Forgot Password page
2. System always shows: "Si la cuenta existe, recibirás un correo con instrucciones en unos minutos."
3. If user exists and is enabled:
   - Generate one-time token (48 bytes, URL-safe)
   - Token expires in 30 minutes
   - Store in `password_reset_tokens` table
   - Send email via Power Automate
4. User clicks reset link → validates token → sets new password
5. Token is marked as used immediately after successful reset

---

## 21. Data Persistence (NEW)

### 21.1 External Data Directory

All persistent data lives outside the git repository:

```
DATA_DIR = /home/rootadmin/data/portal/
├── users.db           # SQLite database
└── apps_config.json   # Application configuration
```

### 21.2 Synchronization Mechanism

The script `scripts/sync-portal-data.sh` manages data persistence:

1. **First install**: Creates DATA_DIR, copies default `apps_config.json`, initializes `users.db`
2. **Subsequent deploys**: Creates symlinks from repo to DATA_DIR (idempotent)
3. **Called automatically** by `deploy.sh` and `restart-all.sh`

### 21.3 Symlink Strategy

```bash
portal/apps_config.json  →  DATA_DIR/apps_config.json   (ln -sfn)
```

The `users.db` database is accessed directly by Flask using the `DATA_DIR` environment variable.

### 21.4 Requirements

- `deploy.sh` and `restart-all.sh` MUST call `sync-portal-data.sh`
- `git pull` MUST NOT overwrite DATA_DIR contents
- systemd service user MUST have read/write access to DATA_DIR
- Changes to `DATA_DIR/apps_config.json` MUST be reflected after service restart

---

## 22. Notification via Power Automate (NEW)

### 22.1 Architecture

```
Portal → HTTP POST → Power Automate Flow → Outlook/Exchange → User Email
```

### 22.2 Security

| Layer | Mechanism |
|-------|-----------|
| Transport | HTTPS (Power Automate URLs are always HTTPS) |
| Authentication | HMAC-SHA256 or shared secret token |
| Anti-Enumeration | Uniform response regardless of user existence |
| Secret Storage | Environment variables (never hardcoded) |

### 22.3 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `POWER_AUTOMATE_URL` | Yes | Flow HTTP Trigger URL |
| `POWER_AUTOMATE_SHARED_SECRET` | Yes | Shared secret for authentication |
| `POWER_AUTOMATE_TIMEOUT_SECONDS` | No (default: 10) | HTTP timeout |
| `POWER_AUTOMATE_RETRIES` | No (default: 3) | Retry count |

### 22.4 Failure Handling

- Exponential backoff retries (1s, 2s, 4s...)
- Failures logged server-side (no sensitive data in logs)
- User always sees the same message (anti-enumeration)
- Optional audit table for tracking

### 22.5 Setup Guide

See: [docs/POWER_AUTOMATE_EMAIL_SETUP.md](docs/POWER_AUTOMATE_EMAIL_SETUP.md)

---

**Key enhancements in v3.1:**
- Mandatory secrets management via Vault/equivalent
- Structured JSON logging with Request-ID tracing
- Prometheus metrics and alerting framework
- Comprehensive backup/recovery procedures
- CI/CD pipeline with automated testing
- Governance processes for app lifecycle
- Developer quick-start guide and troubleshooting

**Key additions in v3.1.1:**
- Session-based authentication with Flask-Login
- Role-based access control (RBAC) by department and role
- Password reset via Power Automate (no SMTP)
- External data directory persistence (DATA_DIR)
- Anti-enumeration and log sanitization requirements

---

For questions or clarification, contact: **Platform Team** (platform@company.com)
