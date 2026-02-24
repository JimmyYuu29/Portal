# Power Automate - Email Setup Guide / Guía de Configuración de Emails

> **Purpose**: This document provides step-by-step instructions to create a Power Automate Flow that sends password reset emails for the Portal Forvis Mazars.
>
> **Objetivo**: Este documento proporciona instrucciones paso a paso para crear un Flow de Power Automate que envía correos de restablecimiento de contraseña para el Portal Forvis Mazars.

---

## Table of Contents / Índice

1. [Overview / Resumen](#1-overview--resumen)
2. [Prerequisites / Prerequisitos](#2-prerequisites--prerequisitos)
3. [Create the Flow / Crear el Flow](#3-create-the-flow--crear-el-flow)
4. [HTTP Trigger Configuration / Configuración del Trigger HTTP](#4-http-trigger-configuration)
5. [Authentication Verification / Verificación de Autenticación](#5-authentication-verification)
6. [Send Email Action / Acción de Enviar Correo](#6-send-email-action)
7. [Response Action / Acción de Respuesta](#7-response-action)
8. [Testing / Pruebas](#8-testing--pruebas)
9. [Troubleshooting / Solución de Problemas](#9-troubleshooting--solución-de-problemas)
10. [Security Recommendations / Recomendaciones de Seguridad](#10-security-recommendations)

---

## 1. Overview / Resumen

The Portal uses **Power Automate** instead of SMTP to send password reset emails. When a user requests a password reset, the Portal sends an HTTP POST request to a Power Automate Flow, which then sends the email via the Outlook/Exchange connector.

**Architecture / Arquitectura:**

```
User → Portal (HTTP POST) → Power Automate Flow → Outlook/Exchange → User Email
```

**Authentication Strategy / Estrategia de Autenticación:**

We use a **fixed shared secret token** (Scheme 2) for simplicity and reliability. The Portal includes a shared secret in each request, and the Flow verifies it before sending the email.

> **Why not HMAC?** While HMAC-SHA256 (Scheme 1) is more secure, Power Automate does not natively support HMAC computation in its expression language without complex workarounds. The fixed token approach is simpler to maintain and sufficient for internal use when combined with IP allowlisting.

---

## 2. Prerequisites / Prerequisitos

- **Microsoft 365 account** with Power Automate Premium or standard license
- **Outlook/Exchange** connector enabled in your tenant
- **Admin access** to Power Automate (to create HTTP-triggered flows)
- The Portal server's **public IP address** (for IP allowlisting)

---

## 3. Create the Flow / Crear el Flow

### Step-by-step / Paso a paso:

1. Go to **https://make.powerautomate.com**
2. Sign in with your Microsoft 365 account
3. Click **"+ Create"** in the left sidebar
4. Select **"Instant cloud flow"**
5. Name the flow: `Portal - Password Reset Email`
6. Under "Choose how to trigger this flow", select: **"When an HTTP request is received"**
7. Click **"Create"**

---

## 4. HTTP Trigger Configuration

### 4.1 Configure the trigger

Click on the **"When an HTTP request is received"** trigger and configure:

- **Who can trigger the flow?**: `Anyone`
- **Request method**: `POST`

### 4.2 Set the Request Body JSON Schema

Click **"Use sample payload to generate schema"** and paste the following JSON:

```json
{
    "to": "john.doe@company.com",
    "template": "PASSWORD_RESET",
    "language": "es",
    "subject": "Restablecer contraseña - Portal",
    "body_html": "<html><body><h1>Reset Password</h1></body></html>",
    "meta": {
        "username": "john.doe",
        "request_ip": "10.0.0.1",
        "requested_at": "2024-01-15T10:30:00Z",
        "expires_minutes": 30
    },
    "auth": {
        "ts": "1705312200",
        "sig": "shared_secret_token_here"
    }
}
```

Click **"Done"**. The schema will be generated automatically.

### 4.3 Manually verify the generated schema matches:

```json
{
    "type": "object",
    "properties": {
        "to": { "type": "string" },
        "template": { "type": "string" },
        "language": { "type": "string" },
        "subject": { "type": "string" },
        "body_html": { "type": "string" },
        "meta": {
            "type": "object",
            "properties": {
                "username": { "type": "string" },
                "request_ip": { "type": "string" },
                "requested_at": { "type": "string" },
                "expires_minutes": { "type": "integer" }
            }
        },
        "auth": {
            "type": "object",
            "properties": {
                "ts": { "type": "string" },
                "sig": { "type": "string" }
            }
        }
    }
}
```

---

## 5. Authentication Verification

### 5.1 Add a Condition action

After the trigger, add a new action:
1. Click **"+ New step"**
2. Search for **"Condition"**
3. Select **"Condition"** (Control)

### 5.2 Configure the condition

Set the condition to verify the shared secret:

- **Left side**: Click "Dynamic content" → select `sig` (from auth object)
  - Expression: `triggerBody()?['auth']?['sig']`
- **Operator**: `is equal to`
- **Right side**: Enter your shared secret (the same value as `POWER_AUTOMATE_SHARED_SECRET` env var)
  - ⚠️ **IMPORTANT**: For better security, use a Flow variable or environment variable instead of hardcoding the secret directly in the condition.

### 5.3 Set up a variable for the secret (recommended)

Before the Condition:
1. Add **"Initialize variable"** action
2. Name: `SharedSecret`
3. Type: `String`
4. Value: `YOUR_SHARED_SECRET_HERE` (same as Portal's `POWER_AUTOMATE_SHARED_SECRET`)

Then in the Condition, use the variable for comparison:
- **Right side**: `variables('SharedSecret')`

### 5.4 If No (authentication failed)

In the **"If no"** branch:
1. Add **"Response"** action
2. Set Status Code: `403`
3. Body:
```json
{
    "ok": false,
    "error": "Authentication failed"
}
```

---

## 6. Send Email Action

### 6.1 In the "If yes" branch (authentication passed):

1. Click **"Add an action"**
2. Search for **"Send an email (V2)"** (Office 365 Outlook)
3. Select **"Send an email (V2)"**

### 6.2 Configure the email fields:

| Field | Value (Dynamic Content) |
|-------|-------------------------|
| **To** | `triggerBody()?['to']` — click Dynamic content → `to` |
| **Subject** | `triggerBody()?['subject']` — click Dynamic content → `subject` |
| **Body** | `triggerBody()?['body_html']` — click Dynamic content → `body_html` |
| **Is HTML** | `Yes` |
| **From (shared mailbox)** | (Optional) Use a shared mailbox like `noreply@company.com` |

### 6.3 Advanced settings (click "Show advanced options"):

- **Importance**: Normal

---

## 7. Response Action

### 7.1 After the Send Email action (still in "If yes"):

1. Add **"Response"** action
2. Configure:

| Field | Value |
|-------|-------|
| **Status Code** | `200` |
| **Headers** | `Content-Type: application/json` |
| **Body** | See below |

**Response Body:**
```json
{
    "ok": true,
    "messageId": "@{guid()}"
}
```

The `@{guid()}` expression generates a unique message ID for tracking.

### 7.2 Save the Flow

Click **"Save"** in the top bar.

### 7.3 Copy the HTTP POST URL

After saving:
1. Click on the **"When an HTTP request is received"** trigger
2. Copy the **HTTP POST URL** that appears
3. This is your `POWER_AUTOMATE_URL` — set it as the environment variable in the Portal server's systemd service file

---

## 8. Testing / Pruebas

### 8.1 Test with curl

Replace `YOUR_FLOW_URL` and `YOUR_SHARED_SECRET` with actual values:

```bash
curl -X POST "YOUR_FLOW_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "your.email@company.com",
    "template": "PASSWORD_RESET",
    "language": "es",
    "subject": "TEST - Restablecer contraseña - Portal",
    "body_html": "<html><body><h1>Prueba de Restablecimiento</h1><p>Este es un correo de prueba del Portal Forvis Mazars.</p><p><a href=\"https://example.com/reset-password/test-token\">Restablecer mi contraseña</a></p><p>Este enlace es válido por 30 minutos.</p></body></html>",
    "meta": {
        "username": "test.user",
        "request_ip": "10.0.0.1",
        "requested_at": "2024-01-15T10:30:00Z",
        "expires_minutes": 30
    },
    "auth": {
        "ts": "1705312200",
        "sig": "YOUR_SHARED_SECRET"
    }
}'
```

### 8.2 Test with Postman

1. Create a new **POST** request
2. URL: Paste the Flow's HTTP POST URL
3. Headers: `Content-Type: application/json`
4. Body → Raw → JSON: Paste the same JSON body as above
5. Click **Send**

### 8.3 Expected responses

**Success (200):**
```json
{
    "ok": true,
    "messageId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Auth failure (403):**
```json
{
    "ok": false,
    "error": "Authentication failed"
}
```

### 8.4 Verify email delivery

- Check the recipient's inbox (and spam/junk folder)
- In Power Automate, click on the Flow → **"Run history"** to see execution details

---

## 9. Troubleshooting / Solución de Problemas

### 9.1 DLP Policy Conflicts

**Symptom**: Flow creation fails or HTTP connector is blocked.

**Solution**:
1. Go to **Power Platform Admin Center** → **Data policies**
2. Check if the HTTP connector is in the "Blocked" group
3. Move it to the "Business" group (or create an exception policy)
4. Contact your IT admin if you cannot modify DLP policies

### 9.2 Flow URL Leak Risk

**Mitigations**:
1. **IP Allowlisting**: In Azure API Management or Power Automate settings, restrict the trigger to only accept requests from the Portal server's IP
2. **Shared Secret**: Always validate the `auth.sig` field (implemented in Step 5)
3. **HTTPS**: The Flow URL is always HTTPS by default
4. **Rotation**: Periodically rotate the shared secret and update both Portal env and Flow variable
5. **Monitoring**: Set up Flow run notifications for failures

### 9.3 Emails Not Arriving

1. **Check spam/junk folder**
2. Check **Flow run history** for errors
3. Verify the **"To"** address is a valid corporate email
4. Check if the sending mailbox has sufficient license/permissions
5. Review Exchange **mail flow rules** that may block the email
6. Check **message trace** in Exchange Admin Center

### 9.4 HTTP Timeout

- The Portal has a default timeout of 10 seconds (`POWER_AUTOMATE_TIMEOUT_SECONDS`)
- Power Automate may take 5-15 seconds for the first invocation (cold start)
- Consider increasing `POWER_AUTOMATE_TIMEOUT_SECONDS` to 15 if timeouts occur
- The Portal retries up to 3 times with exponential backoff

### 9.5 Flow Connector Authorization

If the Outlook connector shows "Invalid connection":
1. Click on the connection name in the Flow
2. Click **"Fix connection"**
3. Re-authenticate with the mailbox account
4. Save the Flow again

---

## 10. Security Recommendations

### Authentication

| Level | Mechanism | Status |
|-------|-----------|--------|
| **Basic** | Fixed shared secret token | ✅ Implemented |
| **Enhanced** | HMAC-SHA256 signature | ⚠️ Not native in Power Automate (complex) |
| **Network** | IP allowlisting | 📋 Recommended |

### Best Practices

1. **Rotate shared secret regularly** (at least every 90 days)
2. **Never log the Flow URL** or shared secret in application logs
3. **Use a service/shared mailbox** (e.g., `noreply@company.com`) instead of a personal account
4. **Enable Flow analytics** to monitor for unusual activity
5. **Set up alerts** for failed Flow runs
6. **Restrict Flow permissions** — only authorized admins should be able to edit the Flow

### Audit Trail

The Portal logs the following for each password reset request (without sensitive data):
- Username (who requested)
- Request IP
- Timestamp
- Success/failure of the email send attempt (not the token or URL)

Power Automate also maintains its own run history with full details of each email sent.

---

## Quick Reference / Referencia Rápida

### Portal Environment Variables

```bash
# Power Automate Flow URL (from Step 7.3)
POWER_AUTOMATE_URL=https://prod-XX.westeurope.logic.azure.com:443/workflows/...

# Shared secret (must match the value in Flow's SharedSecret variable)
POWER_AUTOMATE_SHARED_SECRET=your_long_random_secret_here

# Timeout and retries
POWER_AUTOMATE_TIMEOUT_SECONDS=10
POWER_AUTOMATE_RETRIES=3
```

### systemd (EnvironmentFile — recommended)

> ⚠️ **Do NOT use `Environment=` directly in systemd unit files for URLs containing `%`.**
> systemd interprets `%` as a specifier, which silently discards the variable.
> Always use `EnvironmentFile` instead.

```bash
# Create env file (% characters are NOT interpreted here)
sudo tee /home/rootadmin/portal-suite/portal.env << 'EOF'
POWER_AUTOMATE_URL=https://prod-XX.westeurope.logic.azure.com:443/workflows/...
POWER_AUTOMATE_SHARED_SECRET=your_long_random_secret
SECRET_KEY=your_flask_secret_key
DATA_DIR=/home/rootadmin/data/portal
PORTAL_DOMAIN=http://10.32.1.150
EOF

sudo chmod 600 /home/rootadmin/portal-suite/portal.env

# Add to systemd:
sudo systemctl edit portal.service
# [Service]
# EnvironmentFile=/home/rootadmin/portal-suite/portal.env

sudo systemctl daemon-reload
sudo systemctl restart portal.service

# Verify:
sudo cat /proc/$(systemctl show -p MainPID portal.service --value)/environ | tr '\0' '\n' | grep POWER_AUTOMATE
```

### Flow Summary

| Step | Action | Purpose |
|------|--------|---------|
| 1 | HTTP Trigger | Receive POST from Portal |
| 2 | Initialize Variable | Store shared secret |
| 3 | Condition | Verify auth.sig == SharedSecret |
| 4 | Send Email (V2) | Send reset email via Outlook |
| 5 | Response 200 | Return success to Portal |
| 6 | Response 403 | Return auth failure |

---

*Document Version: 2.1.0 | Last Updated: February 2026*
