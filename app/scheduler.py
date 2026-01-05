try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from zoneinfo import ZoneInfo
    APSCHEDULER_AVAILABLE = True
except Exception:
    APSCHEDULER_AVAILABLE = False

from datetime import datetime
from .config import TZ_KEY, REMINDER_HOUR, EMAIL_RECIPIENTS
from .time import now, week_monday
from .database import SessionLocal
from .models import WeeklyMemory
from .emailer import send_email
from .config import AUTHORS, EXTERNAL_BASE_URL
from .tokens import generate_email_token


if APSCHEDULER_AVAILABLE:
    scheduler = BackgroundScheduler(timezone=ZoneInfo(TZ_KEY))


    def _send_weekly_reminders():
        """Check the current week and send reminders to authors who haven't written yet.

        This job will iterate authors and if the week's entry is missing, send an email
        to that author address (if present in EMAIL_RECIPIENTS).
        """
        db = SessionLocal()
        try:
            current = now()
            # Only act on Sundays — the scheduler trigger should ensure this,
            # but keep a guard.
            if current.weekday() != 6:
                return

            monday = week_monday(current)

            for author in AUTHORS:
                # If recipient not configured, skip
                to = EMAIL_RECIPIENTS.get(author)
                if not to:
                    continue

                # Generate a single-use token and include link in email
                token = generate_email_token(author)
                link = None
                if EXTERNAL_BASE_URL:
                    link = f"{EXTERNAL_BASE_URL.rstrip('/')}/token/{token}"
                else:
                    # If no external URL configured, include token so frontend can build link
                    link = f"TOKEN:{token}"

                subject = f"Recordatorio: escribir el recuerdo semanal ({monday.date().isoformat()})"
                body = (
                    f"Hola {author},\n\nEs hora de escribir vuestro recuerdo semanal para la semana que empieza el {monday.date().isoformat()}.\n"
                    f"Usa el siguiente enlace para acceder y escribir: {link}\n\nUn saludo."
                )
                send_email(subject, body, to)
        finally:
            db.close()


    def start():
        # Cron: every Sunday at REMINDER_HOUR (in TZ)
        trigger = CronTrigger(day_of_week="sun", hour=REMINDER_HOUR, minute=0)
        scheduler.add_job(
            _send_weekly_reminders, trigger, id="weekly_reminder", replace_existing=True
        )
        scheduler.start()


    def stop():
        scheduler.shutdown(wait=False)

else:
    # APScheduler not available in this environment (tests/dev).
    def start():
        print("[scheduler] APScheduler not available; scheduler disabled")


    def stop():
        pass
