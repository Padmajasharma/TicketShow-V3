# backend/resources/show.py
from datetime import datetime
from flask import request, jsonify
from flask_restful import Resource, reqparse, fields, marshal_with, inputs
from flask_jwt_extended import jwt_required

from extensions import db
from models import Show, Theatre, Ticket


show_parser = reqparse.RequestParser()
show_parser.add_argument("name", type=str, required=True, help="The name of the show")
show_parser.add_argument(
    "start_time",
    type=inputs.datetime_from_iso8601,
    required=True,
    help="The start time of the show in ISO 8601 format",
)
show_parser.add_argument(
    "end_time",
    type=inputs.datetime_from_iso8601,
    required=True,
    help="The end time of the show in ISO 8601 format",
)
show_parser.add_argument("tags", type=str, help="Tags for the show")
show_parser.add_argument(
    "ticket_price", type=float, required=True, help="The ticket price of the show"
)
show_parser.add_argument(
    "theatre_id", type=int, required=True, help="The ID of the theatre for the show"
)
show_parser.add_argument(
    "image",
    type=str,
    help="The image URL for the show (e.g., TMDB URL)",
)
# TMDB metadata arguments
show_parser.add_argument("tmdb_id", type=int, help="TMDB movie/show ID")
show_parser.add_argument("overview", type=str, help="Movie description from TMDB")
show_parser.add_argument("runtime", type=int, help="Duration in minutes")
show_parser.add_argument("release_date", type=str, help="Release date YYYY-MM-DD")
show_parser.add_argument("tmdb_rating", type=float, help="TMDB vote average")
show_parser.add_argument("backdrop", type=str, help="Backdrop image URL")

show_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "start_time": fields.DateTime(dt_format="iso8601"),
    "end_time": fields.DateTime(dt_format="iso8601"),
    "tags": fields.String,
    "ticket_price": fields.Float,
    "image": fields.String,
    "theatre_id": fields.Integer,
    "capacity": fields.Integer,
    "tmdb_id": fields.Integer,
    "overview": fields.String,
    "runtime": fields.Integer,
    "release_date": fields.String,
    "tmdb_rating": fields.Float,
    "backdrop": fields.String,
}


class ShowResource(Resource):
    def get(self):
        shows = Show.query.all()
        show_list = []
        for show in shows:
            rating = show.rating if show.rating is not None else 0.0
            # Return image URL directly from database (supports TMDB URLs)
            img_url = show.image if show.image else None
            show_list.append(
                {
                    "id": show.id,
                    "name": show.name,
                    "start_time": show.start_time.isoformat() if show.start_time else None,
                    "end_time": show.end_time.isoformat() if show.end_time else None,
                    "rating": rating,
                    "tags": show.tags,
                    "ticket_price": show.ticket_price,
                    "image": img_url,
                    "theatre_id": show.theatre_id,
                    "capacity": show.capacity,
                    "tmdb_id": show.tmdb_id,
                    "overview": show.overview,
                    "runtime": show.runtime,
                    "release_date": show.release_date,
                    "tmdb_rating": show.tmdb_rating,
                    "backdrop": show.backdrop,
                }
            )
        return jsonify(show_list)

    def post(self):
        from flask import current_app

        # JSON request
        if request.is_json:
            data = request.get_json()
            name = data.get("name")
            start_time_str = data.get("start_time")
            end_time_str = data.get("end_time")
            tags = data.get("tags")
            ticket_price = data.get("ticket_price")
            image_url = data.get("image")  # Now accepts full URL (TMDB, etc.)
            theatre_id = data.get("theatre_id")
            
            # TMDB metadata
            tmdb_id = data.get("tmdb_id")
            overview = data.get("overview")
            runtime = data.get("runtime")
            release_date = data.get("release_date")
            tmdb_rating = data.get("tmdb_rating")
            backdrop = data.get("backdrop")

            if not name or not theatre_id:
                return {"message": "Name and theatre_id are required"}, 400
            
            if not start_time_str or not end_time_str:
                return {"message": "start_time and end_time are required"}, 400

            theatre = Theatre.query.get(theatre_id)
            if not theatre:
                return {"message": "Theatre not found"}, 404

            try:
                start_time = datetime.fromisoformat(start_time_str)
                end_time = datetime.fromisoformat(end_time_str)
            except (ValueError, TypeError) as e:
                return {"message": f"Invalid date format: {str(e)}"}, 400

            capacity = int(theatre.capacity)

            new_show = Show(
                name=name,
                start_time=start_time,
                end_time=end_time,
                tags=tags,
                ticket_price=ticket_price,
                image=image_url,  # Store full URL directly
                theatre_id=theatre_id,
                capacity=capacity,
                tmdb_id=tmdb_id,
                overview=overview,
                runtime=runtime,
                release_date=release_date,
                tmdb_rating=tmdb_rating,
                backdrop=backdrop,
            )
            db.session.add(new_show)
            db.session.commit()
            return {"message": "Show created successfully"}, 201

        # Form-data request (accepts image URL)
        data = request.form
        name = data.get("name")
        start_time_str = data.get("start_time")
        end_time_str = data.get("end_time")
        tags = data.get("tags")
        ticket_price = data.get("ticket_price")
        image_url = data.get("image")  # Accept URL from form
        theatre_id = data.get("theatre_id")

        if not name or not theatre_id:
            return {"message": "Name and theatre_id are required"}, 400

        theatre = Theatre.query.get(theatre_id)
        if not theatre:
            return {"message": "Theatre not found"}, 404

        try:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
        except (ValueError, TypeError) as e:
            return {"message": f"Invalid date format: {str(e)}"}, 400
            
        capacity = int(theatre.capacity)

        new_show = Show(
            name=name,
            start_time=start_time,
            end_time=end_time,
            tags=tags,
            ticket_price=ticket_price,
            image=image_url,  # Store URL directly
            theatre_id=theatre_id,
            capacity=capacity,
        )

        db.session.add(new_show)
        db.session.commit()
        return {"message": "Show created successfully"}, 201


class UpdateShowResource(Resource):
    def get(self, show_id):
        show = Show.query.get(show_id)
        if show is None:
            return {"message": "Show not found"}, 404
        
        rating = show.rating if show.rating is not None else 0.0
        return {
            "id": show.id,
            "name": show.name,
            "start_time": show.start_time.isoformat() if show.start_time else None,
            "end_time": show.end_time.isoformat() if show.end_time else None,
            "rating": rating,
            "tags": show.tags,
            "ticket_price": show.ticket_price,
            "image": show.image,
            "theatre_id": show.theatre_id,
            "capacity": show.capacity,
            "tmdb_id": show.tmdb_id,
            "overview": show.overview,
            "runtime": show.runtime,
            "release_date": show.release_date,
            "tmdb_rating": show.tmdb_rating,
            "backdrop": show.backdrop,
        }

    @marshal_with(show_fields)
    @jwt_required()
    def put(self, show_id):
        args = show_parser.parse_args()
        show = Show.query.get(show_id)

        if show is None:
            return {"message": "Show not found"}, 404

        if args["name"]:
            show.name = args["name"]
        if args["start_time"]:
            show.start_time = args["start_time"]
        if args["end_time"]:
            show.end_time = args["end_time"]
        if args["tags"]:
            show.tags = args["tags"]
        if args["ticket_price"] is not None:
            show.ticket_price = args["ticket_price"]
        if args["image"]:
            show.image = args["image"]
        if args["theatre_id"]:
            show.theatre_id = args["theatre_id"]

        db.session.commit()
        return show

    @jwt_required()
    def delete(self, show_id):
        show = Show.query.get(show_id)

        if show:
            db.session.delete(show)
            db.session.commit()
            return {"message": "Show deleted"}
        else:
            return {"message": "Show not found"}, 404


class ShowBookedSeatsResource(Resource):
    """Get booked seats for a specific show - Public access for booking"""

    def get(self, show_id):
        try:
            show = Show.query.get(show_id)
            if not show:
                return {"message": "Show not found"}, 404

            # Get all booked seats for this show
            booked_tickets = Ticket.query.filter_by(show_id=show_id).all()
            booked_seat_ids = [ticket.seat_id for ticket in booked_tickets if ticket.seat_id]

            # Also include active holds from Redis so frontend can treat held seats as temporarily unavailable
            try:
                from cache.seat_cache import seat_cache
                active_holds = seat_cache.get_active_holds(show_id)
                # Build a mapping seat_id -> reservation_id
                held_map = {h['seat_id']: h['reservation_id'] for h in active_holds}
                held_seat_ids = list(held_map.keys())
            except Exception as e:
                # Log and continue with empty holds
                import logging
                logging.exception(f"Failed to retrieve active holds for show {show_id}: {e}")
                held_map = {}
                held_seat_ids = []

            return {
                "show_id": show_id,
                "booked_seats": booked_seat_ids,
                "held_seats_map": held_map,
                "held_seats": held_seat_ids,
                "total_booked": len(booked_seat_ids)
            }
        except Exception as e:
            import logging, traceback
            logging.exception(f"Unhandled error in ShowBookedSeatsResource.get: {e}\n{traceback.format_exc()}")
            return {"message": "Failed to load booked seats", "error": str(e)}, 500


class ShowByTMDBResource(Resource):
    """Get show by TMDB ID instead of database ID - Public access"""

    def get(self, tmdb_id):
        show = Show.query.filter_by(tmdb_id=tmdb_id).first()
        if not show:
            return {"message": "Show not found"}, 404

        rating = show.rating if show.rating is not None else 0.0
        return {
            "id": show.id,  # Return database ID for frontend use
            "tmdb_id": show.tmdb_id,
            "name": show.name,
            "start_time": show.start_time.isoformat() if show.start_time else None,
            "end_time": show.end_time.isoformat() if show.end_time else None,
            "rating": rating,
            "tags": show.tags,
            "ticket_price": show.ticket_price,
            "image": show.image,
            "theatre_id": show.theatre_id,
            "capacity": show.capacity,
            "overview": show.overview,
            "runtime": show.runtime,
            "release_date": show.release_date,
            "tmdb_rating": show.tmdb_rating,
            "backdrop": show.backdrop,
        }
