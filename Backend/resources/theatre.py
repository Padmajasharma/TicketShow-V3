# backend/resources/theatre.py
from flask_restful import Resource, reqparse, fields, marshal_with
from flask_jwt_extended import jwt_required
from extensions import db
from models import Theatre

theatre_parser = reqparse.RequestParser()
theatre_parser.add_argument("name", type=str, required=True, help="The name of the theater")
theatre_parser.add_argument("place", type=str, required=True, help="The location of the theater")
theatre_parser.add_argument(
    "capacity", type=int, required=True, help="The seating capacity of the theater"
)

theatre_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "place": fields.String,
    "capacity": fields.Integer,
}


class TheaterResource(Resource):
    @marshal_with(theatre_fields)
    def get(self):
        """Get all theatres - Public access for booking"""
        theatres = Theatre.query.all()
        return theatres

    @marshal_with(theatre_fields)
    @jwt_required()
    def post(self, theatre_id=None):
        args = theatre_parser.parse_args()
        new_theatre = Theatre(
            name=args["name"],
            place=args["place"],
            capacity=args["capacity"],
        )
        db.session.add(new_theatre)
        db.session.commit()
        return new_theatre, 201


class TheaterUpdateResource(Resource):
    @marshal_with(theatre_fields)
    def get(self, theatre_id):
        """Get theatre by ID - Public access for booking"""
        theatre = Theatre.query.get(theatre_id)
        if theatre is None:
            return {"message": "Theatre not found"}, 404
        return theatre

    @marshal_with(theatre_fields)
    @jwt_required()
    def put(self, theatre_id):
        args = theatre_parser.parse_args()
        theatre = Theatre.query.get(theatre_id)

        if theatre is None:
            return {"message": "Theatre not found"}, 404

        theatre.name = args["name"]
        theatre.place = args["place"]
        theatre.capacity = args["capacity"]
        db.session.commit()
        return theatre

    @jwt_required()
    def delete(self, theatre_id):
        theatre = Theatre.query.get(theatre_id)

        if theatre:
            db.session.delete(theatre)
            db.session.commit()
            return {"message": "Theatre deleted"}
        else:
            return {"message": "Theatre not found"}, 404
