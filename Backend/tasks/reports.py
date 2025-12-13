# backend/tasks/reports.py
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app
from extensions import celery, db
from models import User, Ticket, Show, ShowRating


@celery.task
def generate_monthly_report():
    today = datetime.now()
    first_day_of_current_month = today.replace(day=1)

    users = User.query.all()
    for user in users:
        user_tickets = (
            db.session.query(User, Ticket, Show)
            .join(Ticket, Ticket.user_id == User.id)
            .join(Show, Show.id == Ticket.show_id)
            .filter(Show.start_time.between(first_day_of_current_month, today))
            .all()
        )

        user_ratings = (
            db.session.query(User.username, Show.name, ShowRating.rating)
            .join(ShowRating, User.id == ShowRating.user_id)
            .join(Show, Show.id == ShowRating.show_id)
            .filter(Show.start_time.between(first_day_of_current_month, today))
            .all()
        )

        bookings_html = "".join(
            f"<li>{u.username} purchased tickets for "
            f"{t.event.name} on {t.event.start_time.strftime('%Y-%m-%d %H:%M')}</li>"
            for u, t, s in user_tickets
        )
        ratings_html = "".join(
            f"<li>{username} rated {show_name}: {rating}/5</li>"
            for username, show_name, rating in user_ratings
        )

        report_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
           <title>Monthly Entertainment Report</title>
        </head>
        <body>
           <h2>Bookings Made:</h2>
           <ul>
            {bookings_html}
           </ul>

           <h2>Show Ratings:</h2>
           <ul>
              {ratings_html}
           </ul>
        </body>
        </html>
        """

        _send_report_as_email(user, report_html)


def _send_report_as_email(user, report_html):
    smtp_server = current_app.config["SMTP_SERVER"]
    smtp_port = current_app.config["SMTP_PORT"]
    smtp_username = current_app.config["SMTP_USERNAME"]
    smtp_password = current_app.config["SMTP_PASSWORD"]

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)

    msg = MIMEMultipart()
    msg["From"] = smtp_username
    msg["To"] = user.email
    msg["Subject"] = "Monthly Entertainment Report"
    msg.attach(MIMEText(report_html, "html"))

    server.sendmail(smtp_username, user.email, msg.as_string())
    server.quit()
