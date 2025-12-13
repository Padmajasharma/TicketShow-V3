# backend/resources/auth.py
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
from extensions import db
from models import User

signup_parser = reqparse.RequestParser()
signup_parser.add_argument("email", type=str, required=True, help="User email")
signup_parser.add_argument("username", type=str, required=True, help="Username")
signup_parser.add_argument("password", type=str, required=True, help="Password")

login_parser = reqparse.RequestParser()
login_parser.add_argument("username", type=str, required=True, help="Username")
login_parser.add_argument("password", type=str, required=True, help="Password")


class SignupResource(Resource):
    def post(self):
        args = signup_parser.parse_args()
        email = args["email"]
        username = args["username"]
        password = args["password"]

        if not username or not password or not email:
            return {"message": "Missing fields!"}, 400

        user = User.query.filter_by(username=username).first()
        if user:
            return {"message": "Username already exists!"}, 409

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(
            identity=username,
            additional_claims={"is_admin": user.is_admin},
        )
        return {"token": access_token, "is_admin": user.is_admin}, 201


class LoginResource(Resource):
    def post(self):
        args = login_parser.parse_args()
        username = args["username"]
        password = args["password"]

        if not username or not password:
            return {"message": "Invalid credentials!"}, 401

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            access_token = create_access_token(
                identity=username,
                additional_claims={"is_admin": user.is_admin},
            )
            return {"token": access_token, "is_admin": user.is_admin}, 200
        else:
            return {"message": "Wrong username or password!"}, 401
