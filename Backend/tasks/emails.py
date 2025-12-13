"""backend/tasks/emails.py
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

from flask import current_app
from extensions import celery
from models import User, Show, Ticket


@celery.task
def send_booking_confirmation(user_id, show_id, ticket_count, total_price, ticket_ids=None):
    """Celery task to send booking confirmation email asynchronously."""
    try:
        user = User.query.get(user_id)
        show = Show.query.get(show_id)

        if not user or not show:
            logging.error(f"User {user_id} or Show {show_id} not found for booking confirmation")
            return False

        smtp_server = current_app.config.get("SMTP_SERVER", "localhost")
        smtp_port = current_app.config.get("SMTP_PORT", 587)
        smtp_username = current_app.config.get("SMTP_USERNAME", "")
        smtp_password = current_app.config.get("SMTP_PASSWORD", "")

        subject = f"Booking Confirmation - {show.name}"
        message = (
            f"Hello {user.username},\n\n"
            f"Your booking has been confirmed!\n\n"
            f"📽️ Show: {show.name}\n"
            f"🎟️ Tickets: {ticket_count}\n"
            f"💰 Total Price: ₹{total_price}\n\n"
            f"Thank you for booking with NovaSeat!\n\n"
            f"Best regards,\nThe NovaSeat Team"
        )

        # Prepare email message
        msg = MIMEMultipart()
        # Only attach PDFs if reportlab is available and ticket ids provided
        attachments_added = 0

        if ticket_ids and isinstance(ticket_ids, (list, tuple)):
            try:
                # Import PDF generator lazily to avoid import cycles when worker isn't configured
                from resources.tickets import generate_ticket_pdf_bytes
                for tid in ticket_ids:
                    try:
                        ticket = Ticket.query.get(int(tid))
                        if not ticket:
                            continue
                        pdf_bytes = generate_ticket_pdf_bytes(ticket)
                        part = MIMEText('')
                        from email.mime.base import MIMEBase
                        from email import encoders
                        part = MIMEBase('application', 'pdf')
                        part.set_payload(pdf_bytes)
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename="ticket_{ticket.id}.pdf"')
                        msg.attach(part)
                        attachments_added += 1
                    except Exception as e:
                        logging.error(f"Failed to generate PDF for ticket {tid}: {e}")
                        continue
            except Exception:
                logging.info('PDF generation not available or failed; sending email without attachments')

        # Prepare headers and body
        from_display = current_app.config.get("EMAIL_FROM_NAME", "NovaSeat")
        # Prefer using smtp_username as the envelope sender if provided, otherwise use a configured FROM_EMAIL
        envelope_from = smtp_username or current_app.config.get("EMAIL_FROM", "no-reply@localhost")
        msg["From"] = formataddr((Header(from_display, 'utf-8').encode(), envelope_from))
        recipient_name = user.username or user.email
        msg["To"] = formataddr((Header(recipient_name, 'utf-8').encode(), user.email))
        msg["Subject"] = Header(subject, 'utf-8')
        msg.attach(MIMEText(message, "plain", "utf-8"))

        # Attempt to send via SMTP. Many dev SMTP servers (MailHog, Mailtrap, etc.) don't require auth/TLS.
        try:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            # If credentials are provided, attempt STARTTLS and login.
            if smtp_username and smtp_password:
                try:
                    server.starttls()
                except Exception:
                    # STARTTLS may not be supported by dev SMTP; continue without it
                    logging.debug('STARTTLS not supported by SMTP server; continuing without TLS')
                server.login(smtp_username, smtp_password)

            server.sendmail(envelope_from, [user.email], msg.as_string())
            server.quit()
            logging.info(f"Booking confirmation email sent to {user.email} (attachments: {attachments_added})")
            try:
                # Audit: email sent
                from utils.audit import log_action
                log_action(user_id, show_id, None, 'email_sent', {'ticket_count': ticket_count, 'attachments': attachments_added})
            except Exception:
                pass
        except Exception as e:
            logging.error(f"Error sending booking confirmation: {e}")
            return False

        return True
    except Exception as e:
        logging.error(f"Error preparing booking confirmation: {e}")
        return False


@celery.task
def send_email_reminder():
    """Send a daily reminder email to all users."""
    users = User.query.all()

    smtp_server = current_app.config.get("SMTP_SERVER", "localhost")
    smtp_port = current_app.config.get("SMTP_PORT", 587)
    smtp_username = current_app.config.get("SMTP_USERNAME", "")
    smtp_password = current_app.config.get("SMTP_PASSWORD", "")

    for user in users:
        subject = "Daily Reminder: Visit/Book Something!"
        message = (
            f"Hello {user.username},\n\n"
            "Don't forget to visit or book something on our Ticket Show platform today!\n\n"
            "Best regards,\nThe Ticket Show Team"
        )

        if not (smtp_username and smtp_password):
            logging.info(f"SMTP not configured. Would send to {user.email}: {subject}")
            continue

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)

            msg = MIMEMultipart()
            from_display = current_app.config.get("EMAIL_FROM_NAME", "Ticket Show")
            msg["From"] = formataddr((Header(from_display, 'utf-8').encode(), smtp_username))
            recipient_name = user.username or user.email
            msg["To"] = formataddr((Header(recipient_name, 'utf-8').encode(), user.email))
            msg["Subject"] = Header(subject, 'utf-8')
            msg.attach(MIMEText(message, "plain", "utf-8"))

            server.sendmail(smtp_username, [user.email], msg.as_string())
            server.quit()

            logging.info(f"Reminder email sent to {user.email}")
        except Exception as e:
            logging.error(f"Error sending reminder email to {user.email}: {e}")
