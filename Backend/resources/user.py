# backend/resources/user.py
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import User, Ticket, Show, ShowRating


class UserProfileResource(Resource):
    @jwt_required()
    def get(self):
        current_user_username = get_jwt_identity()
        current_user = User.query.filter_by(username=current_user_username).first()

        if not current_user:
            return {"message": "User not found"}, 404

        booked_tickets = Ticket.query.filter_by(user_id=current_user.id).all()
        booked_shows = {}

        for ticket in booked_tickets:
            show = Show.query.get(ticket.show_id)
            if show:
                show_id = show.id
                if show_id not in booked_shows:
                    # Get user's rating for this show
                    user_rating = ShowRating.query.filter_by(
                        user_id=current_user.id, show_id=show_id
                    ).first()
                    
                    booked_shows[show_id] = {
                        "show_id": show_id,
                        "show_name": show.name,
                        "show_start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "show_end_time": show.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "ticket_count": 1,
                        "ticket_ids": [ticket.id],
                        "ticket_price": show.ticket_price,
                        "image": show.image,
                        "tags": show.tags,
                        "show_rating": show.rating,
                        "user_rating": user_rating.rating if user_rating else None,
                    }
                else:
                    booked_shows[show_id]["ticket_count"] += 1
                    booked_shows[show_id].setdefault("ticket_ids", []).append(ticket.id)

        # Calculate stats
        total_bookings = len(booked_shows)
        total_tickets = sum(s["ticket_count"] for s in booked_shows.values())
        total_spent = sum(s["ticket_count"] * s["ticket_price"] for s in booked_shows.values())

        return {
            "user": {
                "username": current_user.username,
                "email": current_user.email,
            },
            "booked_shows": list(booked_shows.values()),
            "stats": {
                "total_bookings": total_bookings,
                "total_tickets": total_tickets,
                "total_spent": total_spent,
            }
        }


class RateShowResource(Resource):
    @jwt_required()
    def post(self, show_id):
        current_user_username = get_jwt_identity()
        current_user = User.query.filter_by(username=current_user_username).first()

        if not current_user:
            return {"message": "User not found"}, 404

        data = request.get_json()
        rating_value = data.get("rating")

        if not rating_value or not (1 <= int(rating_value) <= 5):
            return {"message": "Rating must be between 1 and 5"}, 400

        show = Show.query.get(show_id)
        if not show:
            return {"message": "Show not found"}, 404

        # Check if user has booked this show
        ticket = Ticket.query.filter_by(user_id=current_user.id, show_id=show_id).first()
        if not ticket:
            return {"message": "You can only rate shows you have booked"}, 403

        # Update or create rating
        existing_rating = ShowRating.query.filter_by(
            user_id=current_user.id, show_id=show_id
        ).first()

        if existing_rating:
            existing_rating.rating = int(rating_value)
        else:
            new_rating = ShowRating(
                user_id=current_user.id,
                show_id=show_id,
                rating=int(rating_value),
            )
            db.session.add(new_rating)

        # Update show's average rating
        ratings = ShowRating.query.filter_by(show_id=show_id).all()
        total_ratings = sum(r.rating for r in ratings)
        average_rating = total_ratings / len(ratings) if ratings else 0
        show.rating = average_rating

        db.session.commit()

        return {"message": "Rating submitted successfully", "new_rating": int(rating_value)}
