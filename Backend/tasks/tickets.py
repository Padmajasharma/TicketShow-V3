from flask import current_app
from extensions import celery
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

from models import Ticket, User, Show

from resources.tickets import generate_ticket_pdf_bytes


@celery.task
def generate_and_email_ticket(ticket_id: int):
    """Generate ticket PDF with QR code and email it to the ticket owner."""
    try:
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            logging.error(f"Ticket {ticket_id} not found for PDF generation")
            return False

        user = User.query.get(ticket.user_id) if ticket.user_id else None
        show = Show.query.get(ticket.show_id) if ticket.show_id else None

        if not user:
            logging.error(f"No user associated with ticket {ticket_id}")
            return False

        # Generate PDF bytes (may raise)
        try:
            pdf_bytes = generate_ticket_pdf_bytes(ticket)
        except Exception as e:
            logging.exception(f"PDF generation failed for ticket {ticket_id}: {e}")
            return False

        # Prepare email
        smtp_server = current_app.config.get("SMTP_SERVER", "localhost")
        smtp_port = current_app.config.get("SMTP_PORT", 587)
        smtp_username = current_app.config.get("SMTP_USERNAME", "")
        smtp_password = current_app.config.get("SMTP_PASSWORD", "")

        subject = f"Your Ticket for {show.name if show else 'Event'}"
        message = (
            f"Hello {user.username},\n\n"
            f"Attached is your ticket (ID: {ticket.id}) for {show.name if show else 'the event'}.\n\n"
            "Please present the QR code at entry.\n\n"
            "Best regards,\nThe Team"
        )

        if smtp_username and smtp_password:
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)

                msg = MIMEMultipart()
                from_display = current_app.config.get("EMAIL_FROM_NAME", "TicketShow")
                msg["From"] = formataddr((Header(from_display, 'utf-8').encode(), smtp_username))
                recipient_name = user.username or user.email
                msg["To"] = formataddr((Header(recipient_name, 'utf-8').encode(), user.email))
                msg["Subject"] = Header(subject, 'utf-8')

                msg.attach(MIMEText(message, "plain", "utf-8"))

                # attach PDF
                from email.mime.base import MIMEBase
                from email import encoders
                part = MIMEBase('application', 'pdf')
                part.set_payload(pdf_bytes)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="ticket_{ticket.id}.pdf"')
                msg.attach(part)

                server.sendmail(smtp_username, [user.email], msg.as_string())
                server.quit()
                logging.info(f"Sent ticket {ticket_id} to {user.email}")
                try:
                    from utils.audit import log_action
                    log_action(user.id, ticket.show_id if ticket else None, ticket_id, 'email_sent', {'type': 'ticket_pdf'})
                except Exception:
                    pass
            except Exception as e:
                logging.exception(f"Failed to send ticket email for {ticket_id}: {e}")
                return False
        else:
            logging.info(f"SMTP not configured. Would send ticket {ticket_id} to {user.email}")
            try:
                from utils.audit import log_action
                log_action(user.id, ticket.show_id if ticket else None, ticket_id, 'email_not_sent_smtp_unconfigured', {})
            except Exception:
                pass

        return True

    except Exception as e:
        logging.exception(f"Unhandled error in generate_and_email_ticket: {e}")
        return False
