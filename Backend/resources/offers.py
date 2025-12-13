from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from datetime import datetime

from extensions import db
from models import Offer, Show, Theatre
from .admin import admin_required


class OffersResource(Resource):
    @jwt_required()
    def get(self):
        # Public listing (only active offers)
        offers = Offer.query.filter_by(active=True).all()
        out = []
        for o in offers:
            out.append({
                "id": o.id,
                "code": o.code,
                "description": o.description,
                "discount_type": o.discount_type,
                "discount_value": o.discount_value,
                "show_id": o.show_id,
                "theatre_id": o.theatre_id,
                "active": o.active,
                "starts_at": o.starts_at.isoformat() if o.starts_at else None,
                "ends_at": o.ends_at.isoformat() if o.ends_at else None,
            })
        return {"offers": out}

    @admin_required
    def post(self):
        data = request.get_json(force=True)
        code = data.get("code")
        if not code:
            return {"message": "code is required"}, 400

        exists = Offer.query.filter_by(code=code).first()
        if exists:
            return {"message": "Offer code already exists"}, 400

        o = Offer(
            code=code,
            description=data.get("description"),
            discount_type=data.get("discount_type", "percent"),
            discount_value=float(data.get("discount_value", 0)),
            show_id=data.get("show_id"),
            theatre_id=data.get("theatre_id"),
            active=bool(data.get("active", True)),
        )
        # optional times
        try:
            if data.get("starts_at"):
                o.starts_at = datetime.fromisoformat(data.get("starts_at"))
            if data.get("ends_at"):
                o.ends_at = datetime.fromisoformat(data.get("ends_at"))
        except Exception:
            pass

        db.session.add(o)
        db.session.commit()
        return {"message": "Offer created", "id": o.id}, 201


class OfferDetailResource(Resource):
    @admin_required
    def put(self, offer_id):
        o = Offer.query.get(offer_id)
        if not o:
            return {"message": "Offer not found"}, 404
        data = request.get_json(force=True)
        for k in ["description", "discount_type", "discount_value", "show_id", "theatre_id", "active", "usage_limit"]:
            if k in data:
                setattr(o, k, data.get(k))
        try:
            if data.get("starts_at"):
                o.starts_at = datetime.fromisoformat(data.get("starts_at"))
            if data.get("ends_at"):
                o.ends_at = datetime.fromisoformat(data.get("ends_at"))
        except Exception:
            pass
        db.session.commit()
        return {"message": "Offer updated"}

    @admin_required
    def delete(self, offer_id):
        o = Offer.query.get(offer_id)
        if not o:
            return {"message": "Offer not found"}, 404
        db.session.delete(o)
        db.session.commit()
        return {"message": "Offer deleted"}


class PricingResource(Resource):
    """Return price for a show, optionally applying an offer code."""
    def get(self, show_id):
        show = Show.query.get(show_id)
        if not show:
            return {"message": "Show not found"}, 404

        price = float(show.ticket_price or 0.0)
        offer_code = request.args.get("offer_code")
        applied = None
        final_price = price
        if offer_code:
            offer = Offer.query.filter_by(code=offer_code, active=True).first()
            now = datetime.utcnow()
            if offer and (not offer.starts_at or offer.starts_at <= now) and (not offer.ends_at or offer.ends_at >= now):
                # check scope
                if offer.show_id and int(offer.show_id) != int(show_id):
                    offer = None
                elif offer.theatre_id and int(offer.theatre_id) != int(show.theatre_id):
                    offer = None

            if offer:
                if offer.discount_type == 'percent':
                    final_price = max(0.0, price * (1.0 - (offer.discount_value or 0.0) / 100.0))
                else:
                    final_price = max(0.0, price - (offer.discount_value or 0.0))
                applied = {"code": offer.code, "discount_type": offer.discount_type, "discount_value": offer.discount_value}

        return {"show_id": show_id, "base_price": price, "final_price": final_price, "applied_offer": applied}
