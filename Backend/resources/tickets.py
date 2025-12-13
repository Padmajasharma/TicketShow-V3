from flask import request, send_file, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from io import BytesIO
from datetime import datetime, timedelta
import os
from reportlab.lib.units import mm
import logging

from extensions import db
from models import Ticket, Show, User
from cache.seat_cache import seat_cache

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
except Exception:
    QR_AVAILABLE = False


def generate_ticket_pdf_bytes(ticket: Ticket) -> bytes:
    """Generate a simple PDF for a ticket and return bytes. Requires reportlab."""
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError('reportlab not installed')
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    margin = 72

    # Header - centered show / product name
    c.setFont('Helvetica-Bold', 22)
    title = (ticket.event.name if getattr(ticket, 'event', None) and ticket.event.name else 'Ticket')
    c.drawCentredString(width / 2, height - margin, title)

    # Subheader - theatre/place and booking id
    c.setFont('Helvetica', 11)
    y = height - margin - 28
    theatre_name = (ticket.event.theatre.name if getattr(ticket, 'event', None) and ticket.event.theatre else '')
    if theatre_name:
        c.drawCentredString(width / 2, y, theatre_name)
        y -= 18

    # Ticket metadata box (left column)
    left_x = margin
    col_y = y
    c.setFont('Helvetica', 12)
    c.drawString(left_x, col_y, f'Ticket ID: {ticket.id}')
    col_y -= 16

    # Show date/time formatting
    show_time_text = 'N/A'
    try:
        show_obj = ticket.event if getattr(ticket, 'event', None) else None
        if not show_obj:
            from models import Show
            show_obj = Show.query.get(ticket.show_id) if ticket.show_id else None

        if show_obj and getattr(show_obj, 'start_time', None):
            # Format like: Sun 14 Dec 2025 • 07:30 PM
            show_time_text = show_obj.start_time.strftime('%a %d %b %Y • %I:%M %p')
    except Exception:
        show_time_text = getattr(ticket, 'start_time', 'N/A') or 'N/A'

    c.drawString(left_x, col_y, f'Date/Time: {show_time_text}')
    col_y -= 16

    # Seats - prefer seat_id, else row+number, else quantity
    seats_text = 'General Admission'
    try:
        if ticket.seat_id:
            seats_text = ticket.seat_id
        elif ticket.seat_row and ticket.seat_number:
            seats_text = f"{ticket.seat_row}{ticket.seat_number}"
        elif ticket.quantity and ticket.quantity > 1:
            seats_text = f"{ticket.quantity} seats"
    except Exception:
        seats_text = 'N/A'

    c.drawString(left_x, col_y, f'Seat(s): {seats_text}')
    col_y -= 16

    c.drawString(left_x, col_y, f'Price: ₹{ticket.price}')
    col_y -= 16
    c.drawString(left_x, col_y, f'Booked By: {ticket.purchased_by.username if getattr(ticket, "purchased_by", None) else "N/A"}')
    col_y -= 26

    # Footer generated timestamp
    c.setFont('Helvetica-Oblique', 9)
    c.drawString(left_x, col_y, f'Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}')

    # Embed QR code (if available) at bottom-right
    try:
        if QR_AVAILABLE:
            # Prefer a configured base URL so QR links directly to a downloadable URL when scanned.
            base = os.environ.get('TICKETS_BASE_URL')
            if base:
                qr_payload = f"{base.rstrip('/')}/tickets/{ticket.id}/download"
            else:
                qr_payload = f"ticket:{ticket.id}"

            # Create a reasonably-sized QR and embed as points (PDF units)
            qr_img = qrcode.make(qr_payload, box_size=8, border=2).convert('RGB')
            qr_size_pt = 120  # points (~1.67 inches)
            ir = ImageReader(qr_img)
            qr_x = width - margin - qr_size_pt
            qr_y = margin
            c.drawImage(ir, qr_x, qr_y, width=qr_size_pt, height=qr_size_pt)

            # Small caption under QR
            c.setFont('Helvetica', 8)
            c.drawCentredString(qr_x + (qr_size_pt / 2), qr_y - 10, 'Scan to view ticket')
    except Exception:
        # Don't fail PDF generation for QR issues
        logging.exception('QR generation failed for ticket %s', getattr(ticket, 'id', 'unknown'))

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.read()


class UserTicketsResource(Resource):
    @jwt_required()
    def get(self):
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            return {'message': 'User not found'}, 404

        include_cancelled = request.args.get('all', 'false').lower() == 'true'
        query = Ticket.query.filter_by(user_id=user.id)
        if not include_cancelled:
            query = query.filter(Ticket.status != 'cancelled')

        tickets = query.order_by(Ticket.id.desc()).all()
        out = []
        for t in tickets:
            out.append({
                'id': t.id,
                'show_id': t.show_id,
                'show_name': t.event.name if t.event else None,
                'seat_id': t.seat_id,
                'quantity': t.quantity,
                'price': t.price,
                'status': t.status,
                'booked_at': t.booked_at.isoformat() if t.booked_at else None
            })
        return {'tickets': out}

    # Allow preflight CORS checks without authentication
    def options(self):
        return ('', 200)


class TicketDetailResource(Resource):
    @jwt_required()
    def get(self, ticket_id):
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return {'message': 'Ticket not found'}, 404
        if ticket.user_id != user.id:
            return {'message': 'Not authorized'}, 403

        return {
            'id': ticket.id,
            'show_id': ticket.show_id,
            'show_name': ticket.event.name if ticket.event else None,
            'seat_id': ticket.seat_id,
            'quantity': ticket.quantity,
            'price': ticket.price,
            'status': ticket.status,
            'booked_at': ticket.booked_at.isoformat() if ticket.booked_at else None
        }

    # Support CORS preflight
    def options(self, ticket_id=None):
        return ('', 200)


class TicketDownloadResource(Resource):
    @jwt_required()
    def get(self, ticket_id):
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return {'message': 'Ticket not found'}, 404
        if ticket.user_id != user.id:
            return {'message': 'Not authorized'}, 403

        # Generate PDF on-the-fly
        if not REPORTLAB_AVAILABLE:
            return {'message': 'PDF generation requires reportlab (pip install reportlab)'}, 501

        try:
            pdf_bytes = generate_ticket_pdf_bytes(ticket)
            return send_file(
                BytesIO(pdf_bytes),
                as_attachment=True,
                download_name=f'ticket_{ticket.id}.pdf',
                mimetype='application/pdf'
            )
        except Exception as e:
            logging.exception('Failed to generate PDF')
            return {'message': f'Failed to generate PDF: {e}'}, 500

    # Allow preflight CORS checks
    def options(self, ticket_id=None):
        return ('', 200)


class TicketCancelResource(Resource):
    @jwt_required()
    def post(self, ticket_id):
        """Cancel a ticket if allowed (before show start - configurable window)."""
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return {'message': 'Ticket not found'}, 404
        if ticket.user_id != user.id:
            return {'message': 'Not authorized'}, 403
        if ticket.status == 'cancelled':
            return {'message': 'Ticket already cancelled'}, 400

        show = Show.query.get(ticket.show_id)
        if not show:
            return {'message': 'Associated show not found'}, 404

        # Allow cancellation until 1 hour before start_time
        cutoff = show.start_time - timedelta(hours=1) if show.start_time else None
        if cutoff and datetime.utcnow() > cutoff:
            return {'message': 'Cancellation window has passed'}, 400

        try:
            # Mark ticket cancelled
            ticket.status = 'cancelled'
            db.session.add(ticket)

            # Restore capacity on show and update Redis cache
            try:
                show.capacity = (show.capacity or 0) + ticket.quantity
                db.session.add(show)
                db.session.commit()
                seat_cache.set_show_capacity(show.id, show.capacity)
            except Exception:
                db.session.rollback()
                # still mark the ticket cancelled locally
                db.session.commit()

            return {'message': 'Ticket cancelled successfully', 'ticket_id': ticket.id}
        except Exception as e:
            logging.exception('Failed to cancel ticket')
            db.session.rollback()
            return {'message': 'Failed to cancel ticket'}, 500

        # Allow preflight CORS checks
        def options(self, ticket_id=None):
            return ('', 200)
