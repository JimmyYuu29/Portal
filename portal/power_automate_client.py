"""
Portal - Power Automate Email Client
=====================================
Sends password reset emails via Power Automate HTTP Flow.
Supports HMAC-SHA256 signature and fixed-token fallback.
All secrets come from environment variables.
"""

import os
import time
import hmac
import hashlib
import json
import logging
from datetime import datetime

import requests

logger = logging.getLogger(__name__)


class PowerAutomateClient:
    """Client for sending emails through Power Automate HTTP flows."""

    def __init__(self, app=None):
        self.flow_url = None
        self.shared_secret = None
        self.timeout = 10
        self.retries = 3
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize from Flask app config / environment."""
        self.flow_url = os.environ.get('POWER_AUTOMATE_URL', '')
        self.shared_secret = os.environ.get('POWER_AUTOMATE_SHARED_SECRET', '')
        self.timeout = int(os.environ.get('POWER_AUTOMATE_TIMEOUT_SECONDS', '10'))
        self.retries = int(os.environ.get('POWER_AUTOMATE_RETRIES', '3'))

    # ------------------------------------------------------------------
    # Signature generation (HMAC-SHA256)
    # ------------------------------------------------------------------

    def _compute_signature(self, to: str, ts: str, template: str) -> str:
        """
        HMAC-SHA256 signature.
        sig_base = to + "|" + ts + "|" + template
        Returns hex digest.
        """
        sig_base = f"{to}|{ts}|{template}"
        return hmac.new(
            self.shared_secret.encode('utf-8'),
            sig_base.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    # ------------------------------------------------------------------
    # Send email
    # ------------------------------------------------------------------

    def send_password_reset_email(
        self,
        to: str,
        username: str,
        reset_link: str,
        request_ip: str,
        expires_minutes: int = 30,
    ) -> bool:
        """
        Send a password reset email via Power Automate.
        Returns True on success, False on failure.
        Never raises - failures are logged server-side.
        """
        if not self.flow_url:
            logger.error("POWER_AUTOMATE_URL is not configured. Cannot send email.")
            return False

        if not self.shared_secret:
            logger.error("POWER_AUTOMATE_SHARED_SECRET is not configured. Cannot send email.")
            return False

        ts = str(int(time.time()))
        template = "PASSWORD_RESET"

        # Build signature — use HMAC when Flow supports it,
        # otherwise send the shared_secret directly for simple comparison.
        use_hmac = os.environ.get('POWER_AUTOMATE_USE_HMAC', 'false').lower() == 'true'
        if use_hmac:
            sig = self._compute_signature(to, ts, template)
        else:
            # Simple mode: send shared secret directly for Flow condition comparison
            sig = self.shared_secret

        # Build body HTML (Spanish)
        body_html = self._build_reset_email_html(
            username=username,
            reset_link=reset_link,
            expires_minutes=expires_minutes,
        )

        payload = {
            "to": to,
            "template": template,
            "language": "es",
            "subject": "Restablecer contraseña - Portal",
            "body_html": body_html,
            "meta": {
                "username": username,
                "request_ip": request_ip,
                "requested_at": datetime.utcnow().isoformat() + "Z",
                "expires_minutes": expires_minutes,
            },
            "auth": {
                "ts": ts,
                "sig": sig,
            },
        }

        # Log the request for debugging (mask secrets)
        logger.info(
            "Sending Power Automate request: url=%s..., to=%s, template=%s",
            self.flow_url[:60] if self.flow_url else 'NOT SET',
            to,
            template,
        )

        # Retry with exponential backoff
        for attempt in range(1, self.retries + 1):
            try:
                resp = requests.post(
                    self.flow_url,
                    json=payload,
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"},
                )
                if resp.status_code in (200, 202):
                    logger.info(
                        "Password reset email sent successfully (attempt %d).",
                        attempt,
                    )
                    return True
                else:
                    logger.warning(
                        "Power Automate returned HTTP %d on attempt %d. Response: %s",
                        resp.status_code,
                        attempt,
                        resp.text[:200] if resp.text else '(empty)',
                    )
            except requests.exceptions.Timeout:
                logger.warning(
                    "Power Automate request timed out on attempt %d.", attempt
                )
            except requests.exceptions.RequestException:
                logger.warning(
                    "Power Automate request failed on attempt %d.", attempt
                )

            # Exponential backoff: 1s, 2s, 4s …
            if attempt < self.retries:
                time.sleep(2 ** (attempt - 1))

        logger.error(
            "All %d attempts to send password reset email failed.", self.retries
        )
        return False

    # ------------------------------------------------------------------
    # Email HTML template (Spanish)
    # ------------------------------------------------------------------

    @staticmethod
    def _build_reset_email_html(
        username: str,
        reset_link: str,
        expires_minutes: int = 30,
    ) -> str:
        return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px;">
  <div style="max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 12px;
              box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden;">
    <!-- Header -->
    <div style="background: linear-gradient(135deg, #1e40af, #1e3a8a); padding: 28px 32px; text-align: center;">
      <h1 style="color: #ffffff; margin: 0; font-size: 22px;">Restablecer Contraseña</h1>
      <p style="color: rgba(255,255,255,0.8); margin: 6px 0 0; font-size: 14px;">Portal Forvis Mazars</p>
    </div>
    <!-- Body -->
    <div style="padding: 32px;">
      <p style="color: #333; font-size: 15px; line-height: 1.6;">
        Hola <strong>{username}</strong>,
      </p>
      <p style="color: #333; font-size: 15px; line-height: 1.6;">
        Hemos recibido una solicitud para restablecer tu contraseña. Haz clic en el botón
        de abajo para establecer una nueva contraseña:
      </p>
      <div style="text-align: center; margin: 28px 0;">
        <a href="{reset_link}"
           style="display: inline-block; background: linear-gradient(135deg, #1e40af, #3b82f6);
                  color: #ffffff; text-decoration: none; padding: 14px 36px; border-radius: 8px;
                  font-size: 15px; font-weight: 600;">
          Restablecer mi contraseña
        </a>
      </div>
      <p style="color: #666; font-size: 13px; line-height: 1.6;">
        Este enlace es válido por <strong>{expires_minutes} minutos</strong>.
        Si no solicitaste este cambio, puedes ignorar este correo de forma segura.
      </p>
      <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">
      <p style="color: #999; font-size: 12px; line-height: 1.5;">
        ⚠️ Por tu seguridad, no compartas este enlace con nadie.<br>
        Si no realizaste esta solicitud, tu cuenta sigue segura y no se han realizado cambios.
      </p>
    </div>
    <!-- Footer -->
    <div style="background: #f9fafb; padding: 16px 32px; text-align: center;">
      <p style="color: #9ca3af; font-size: 11px; margin: 0;">
        © Portal Forvis Mazars · Este es un mensaje automático, no responder.
      </p>
    </div>
  </div>
</body>
</html>"""
