# backend/resources/files.py
import os
from flask_restful import Resource
from flask import request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class UploadFileResource(Resource):
    @jwt_required()
    def post(self):
        if "image" not in request.files:
            return jsonify({"message": "No image part in the request"}), 400

        image_file = request.files["image"]

        if image_file.filename == "":
            return jsonify({"message": "No selected file"}), 400

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            image_file.save(image_path)
            return jsonify({"url": filename}), 201
        else:
            return jsonify({"message": "Invalid file format"}), 400


class UploadedFileResource(Resource):
    def get(self, filename):
        return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
