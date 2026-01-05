"""Configuración del proyecto: valores mutables y fáciles de cambiar."""

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
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USE_TLS = True
SMTP_USER = "jaimesegurapuig@gmail.com"
# SMTP_PASSWORD should NOT be committed; set as environment variable SMTP_PASSWORD

# From address used in outgoing emails
EMAIL_FROM = "jaimesegurapuig@gmail.com"
# Recipients mapping: author name -> email address. Update to real addresses.
# Example: {"Jaime": "jaime@example.com", "Gabi": "gabi@example.com"}
EMAIL_RECIPIENTS = {"Jaime": "jaimesegurapuig@gmail.com", "Gabi": "jaimesegurapuig2@gmail.com"}

# Weekly reminder time (Sunday hour in TZ)
REMINDER_HOUR = 9

# Base URL used to build links sent in emails. Example: https://memories.example.com
# Keep empty in development; fill with your public base URL in production.
EXTERNAL_BASE_URL = ""
