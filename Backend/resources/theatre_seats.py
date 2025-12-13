# backend/resources/theatre_seats.py
from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from extensions import db
from models import Theatre, TheatreSeat
from cache.seat_cache import seat_cache


theatre_seat_parser = reqparse.RequestParser()
theatre_seat_parser.add_argument("theatre_id", type=int, required=True, help="Theatre ID is required")
theatre_seat_parser.add_argument("row_label", type=str, required=True, help="Row label is required")
theatre_seat_parser.add_argument("seat_number", type=int, required=True, help="Seat number is required")
theatre_seat_parser.add_argument("seat_type", type=str, default="regular", help="Seat type (regular, premium, wheelchair)")


class TheatreSeatResource(Resource):
    """Manage individual theatre seats"""

    @jwt_required()
    def post(self):
        """Create a new theatre seat"""
        data = theatre_seat_parser.parse_args()

        # Validate theatre exists
        theatre = Theatre.query.get(data['theatre_id'])
        if not theatre:
            return {"message": "Theatre not found"}, 404

        # Check if seat already exists
        existing_seat = TheatreSeat.query.filter_by(
            theatre_id=data['theatre_id'],
            row_label=data['row_label'],
            seat_number=data['seat_number']
        ).first()

        if existing_seat:
            return {"message": "Seat already exists"}, 400

        # Create new seat
        seat = TheatreSeat(
            theatre_id=data['theatre_id'],
            row_label=data['row_label'],
            seat_number=data['seat_number'],
            seat_type=data['seat_type']
        )

        try:
            db.session.add(seat)
            db.session.commit()
            return {
                "message": "Seat created successfully",
                "seat": {
                    "id": seat.id,
                    "theatre_id": seat.theatre_id,
                    "row_label": seat.row_label,
                    "seat_number": seat.seat_number,
                    "seat_type": seat.seat_type,
                    "seat_id": f"{seat.row_label}{seat.seat_number}"
                }
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"message": "Failed to create seat"}, 500

    @jwt_required()
    def delete(self, seat_id):
        """Delete a theatre seat"""
        seat = TheatreSeat.query.get(seat_id)
        if not seat:
            return {"message": "Seat not found"}, 404

        try:
            db.session.delete(seat)
            db.session.commit()
            # Invalidate theatre seat map cache
            try:
                seat_cache.delete_theatre_seat_map(seat.theatre_id)
            except Exception:
                pass
            return {"message": "Seat deleted successfully"}
        except Exception as e:
            db.session.rollback()
            return {"message": "Failed to delete seat"}, 500


class TheatreSeatsResource(Resource):
    """Manage all seats for a theatre"""

    def get(self, theatre_id):
        """Get all seats for a theatre - Public access for booking"""
        theatre = Theatre.query.get(theatre_id)
        if not theatre:
            return {"message": "Theatre not found"}, 404
        # Try Redis cache first
        cached = seat_cache.get_theatre_seat_map(theatre_id)
        if cached is not None:
            return {"seats": cached}

        seats = TheatreSeat.query.filter_by(theatre_id=theatre_id).all()
        seat_list = []
        for seat in seats:
            seat_list.append({
                "id": seat.id,
                "row_label": seat.row_label,
                "seat_number": seat.seat_number,
                "seat_type": seat.seat_type,
                "is_active": seat.is_active,
                "seat_id": f"{seat.row_label}{seat.seat_number}"
            })

        # Populate cache for future reads
        try:
            seat_cache.set_theatre_seat_map(theatre_id, seat_list)
        except Exception:
            pass

        return {"seats": seat_list}

    @jwt_required()
    def post(self, theatre_id):
        """Bulk create seats for a theatre"""
        data = request.get_json()

        theatre = Theatre.query.get(theatre_id)
        if not theatre:
            return {"message": "Theatre not found"}, 404

        seats_data = data.get('seats', [])
        if not seats_data:
            return {"message": "No seats data provided"}, 400

        created_seats = []
        errors = []

        for seat_data in seats_data:
            try:
                # Check if seat already exists
                existing_seat = TheatreSeat.query.filter_by(
                    theatre_id=theatre_id,
                    row_label=seat_data['row_label'],
                    seat_number=seat_data['seat_number']
                ).first()

                if existing_seat:
                    errors.append(f"Seat {seat_data['row_label']}{seat_data['seat_number']} already exists")
                    continue

                seat = TheatreSeat(
                    theatre_id=theatre_id,
                    row_label=seat_data['row_label'],
                    seat_number=seat_data['seat_number'],
                    seat_type=seat_data.get('seat_type', 'regular')
                )

                db.session.add(seat)
                created_seats.append({
                    "row_label": seat.row_label,
                    "seat_number": seat.seat_number,
                    "seat_type": seat.seat_type,
                    "seat_id": f"{seat.row_label}{seat.seat_number}"
                })

            except Exception as e:
                errors.append(f"Error creating seat {seat_data.get('row_label', '?')}{seat_data.get('seat_number', '?')}: {str(e)}")

        if created_seats:
            try:
                db.session.commit()
                # Invalidate theatre seat map cache
                try:
                    seat_cache.delete_theatre_seat_map(theatre_id)
                except Exception:
                    pass
                return {
                    "message": f"Created {len(created_seats)} seats successfully",
                    "created_seats": created_seats,
                    "errors": errors if errors else None
                }, 201
            except Exception as e:
                db.session.rollback()
                return {"message": "Failed to create seats", "error": str(e)}, 500
        else:
            return {"message": "No seats were created", "errors": errors}, 400