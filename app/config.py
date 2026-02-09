"""Configuración del proyecto: valores mutables y fáciles de cambiar."""

import os

# Autores permitidos (usado por tokens y UI)
AUTHORS = ["Jaime", "Gabi"]

# Año activo (año sobre el que se escribe)
YEAR = 2026

# Timezone a usar (zoneinfo key)
TZ_KEY = "Europe/Madrid"

# Email / scheduler settings
# Set EMAILS_ENABLED = False to disable sending emails (development)
EMAILS_ENABLED = True

# SMTP configuration. Prefer to supply sensitive values via environment variables.
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
SMTP_USER = os.environ.get("SMTP_USER", "jaimesegurapuig@gmail.com")
# SMTP_PASSWORD should NOT be committed; set as environment variable SMTP_PASSWORD

# From address used in outgoing emails
EMAIL_FROM = os.environ.get("EMAIL_FROM", "jaimesegurapuig@gmail.com")
# Recipients mapping: author name -> email address. Update to real addresses.
# Example: {"Jaime": "jaime@example.com", "Gabi": "gabi@example.com"}
EMAIL_RECIPIENTS = {
	"Jaime": os.environ.get("EMAIL_JAIME", "jaimesegurapuig@gmail.com"),
	"Gabi": os.environ.get("EMAIL_GABI", "gbrcamacho04@gmail.com"),
}

# Weekly reminder time (Sunday hour in TZ)
REMINDER_HOUR = 9

# Base URL used to build links sent in emails. Example: https://memories.example.com
# Keep empty in development; fill with your public base URL in production.
EXTERNAL_BASE_URL = os.environ.get("EXTERNAL_BASE_URL", "https://segurarodrigue.me")

# Admin credentials (for a discreet hidden admin login)
# Recommended: set these via environment variables in production and never commit secrets.
# Example (PowerShell):
#   $env:ADMIN_USER = 'admin'
#   $env:ADMIN_PASSWORD_HASH = '<bcrypt-hash>'

ADMIN_USER = os.environ.get("ADMIN_USER")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")
