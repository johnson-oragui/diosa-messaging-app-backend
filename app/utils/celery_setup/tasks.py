"""
Celery Task Module
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app.core.config import settings
from app.utils.celery_setup.setup import app
from app.utils.task_logger import create_logger


RETRY_DELAY = 60  # 60 seconds delay for retry
MAX_RETRIES = 3  # Maximum 3 retries


logger_ = create_logger("::CELERY::")


@app.task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_DELAY)
def send_email_in_background(self, context: dict):
    """
    Sends email to the user.

    Args:
        context(dict): contains recipient_email, link, subject, and template_name for the email.
    Returns:
        None
    """

    try:
        working_dir = os.getcwd()
        templates_dir = os.path.join(
            working_dir, "app", "utils", "celery_setup", "templates"
        )

        env = Environment(loader=FileSystemLoader(templates_dir))
        try:
            email_template = env.get_template(context.get("template_name", ""))
        except TemplateNotFound:
            logger_.error(
                "Template %s not found in %s",
                context.get("template_name"),
                templates_dir,
            )
            return

        # Render email content
        html = email_template.render(
            {
                "first_name": context.get("first_name"),
                "link": context.get("link"),
                "token": context.get("token"),
            }
        )

        # Create the email message
        message = MIMEMultipart("alternative")
        message["Subject"] = context.get("subject", "")
        message["From"] = settings.mail_username
        message["To"] = context.get("recipient_email", "")
        part = MIMEText(html, "html")
        message.attach(part)

        with smtplib.SMTP_SSL(settings.mail_server, int(settings.mail_port)) as server:
            server.login(
                settings.mail_username,
                settings.mail_password,
            )
            server.sendmail(
                settings.mail_username,
                context.get("recipient_email", ""),
                message.as_string(),
            )
            logger_.info("email sent to: %s", context["recipient_email"])
    except Exception as exc:  # type: ignore
        logger_.error("Email sending failed: %s", exc)
        # Retry the task in case of failure
        try:
            raise self.retry(exc=exc, countdown=RETRY_DELAY, max_retries=MAX_RETRIES)
        except self.MaxRetriesExceededError:
            # retry task incase of failure.
            logger_.error("Max retries exceeded for task: %s", self.request.id)


if __name__ == "__main__":
    pass
