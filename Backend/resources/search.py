# backend/resources/search.py
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from models import Theatre, Show


class SearchTheatresResource(Resource):
    def get(self):
        try:
            search_query = request.args.get("name")
            place_query = request.args.get("place")

            if search_query:
                theatres = Theatre.query.filter(
                    Theatre.name.ilike(f"%{search_query}%")
                ).all()
            elif place_query:
                theatres = Theatre.query.filter(
                    Theatre.place.ilike(f"%{place_query}%")
                ).all()
            else:
                theatres = []

            result = [
                {"id": t.id, "name": t.name, "place": t.place} for t in theatres
            ]
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


class SearchShowsResource(Resource):
    def get(self):
        try:
            tags_query = request.args.get("tags")
            rating_query = request.args.get("rating")

            if tags_query:
                shows = Show.query.filter(Show.tags.ilike(f"%{tags_query}%")).all()
                result = [
                    {"id": s.id, "name": s.name, "tags": s.tags} for s in shows
                ]
                return jsonify(result)

            if rating_query is not None:
                try:
                    rating_query = float(rating_query)
                except ValueError:
                    return jsonify(
                        {"message": "Invalid rating value. It should be a number."}
                    ), 400

                tolerance = 0.1
                shows = Show.query.filter(
                    Show.rating >= rating_query - tolerance,
                    Show.rating <= rating_query + tolerance,
                ).all()
                result = [
                    {"id": s.id, "name": s.name, "rating": s.rating} for s in shows
                ]
                return jsonify(result)

            return jsonify([])
        except Exception as e:
            return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
