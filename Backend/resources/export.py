# backend/resources/export.py
import io
import csv
import base64
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from extensions import celery
from models import Theatre, Show


class ExportTheatreResource(Resource):
    @jwt_required()
    def get(self, theatre_id):
        try:
            # Trigger Celery task
            result = export_theatre_csv.delay(theatre_id)
            # Wait for result (with timeout)
            csv_data = result.get(timeout=30)

            if csv_data:
                # Return as base64 encoded data for frontend to download
                encoded = base64.b64encode(csv_data.encode('utf-8')).decode('utf-8')
                return {
                    "status": "success",
                    "filename": f"theatre_{theatre_id}_report.csv",
                    "data": encoded,
                    "content_type": "text/csv"
                }, 200

            return {"status": "error", "message": "No data generated"}, 500
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500


@celery.task(name="export_theatre_csv")
def export_theatre_csv(theatre_id):
    """Celery task to generate theatre CSV report"""
    from run import app
    
    with app.app_context():
        theatre = Theatre.query.get(theatre_id)
        if not theatre:
            raise Exception(f"Theatre with ID {theatre_id} not found")

        shows = Show.query.filter_by(theatre_id=theatre_id).all()
        
        num_bookings = sum(
            1 for show in shows for ticket in show.tickets if ticket.user_id is not None
        )
        avg_rating = (
            sum(show.rating or 0 for show in shows) / len(shows)
            if shows
            else 0
        )

        # Create CSV data
        csv_output = io.StringIO()
        csv_writer = csv.writer(csv_output)
        
        # Write header and data
        csv_writer.writerow(["Theatre Report"])
        csv_writer.writerow([])
        csv_writer.writerow(["Theatre Name", theatre.name])
        csv_writer.writerow(["Location", theatre.place])
        csv_writer.writerow(["Capacity", theatre.capacity])
        csv_writer.writerow(["Number of Shows", len(shows)])
        csv_writer.writerow(["Number of Bookings", num_bookings])
        csv_writer.writerow(["Average Rating", f"{avg_rating:.2f}"])
        csv_writer.writerow([])
        csv_writer.writerow(["Shows:"])
        csv_writer.writerow(["Name", "Start Time", "End Time", "Price", "Capacity", "Rating"])
        
        for show in shows:
            csv_writer.writerow([
                show.name,
                show.start_time.isoformat() if show.start_time else "",
                show.end_time.isoformat() if show.end_time else "",
                show.ticket_price,
                show.capacity,
                show.rating or "N/A"
            ])

        return csv_output.getvalue()
