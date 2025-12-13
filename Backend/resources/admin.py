from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, Show, Theatre, Ticket, TheatreSeat
import csv
import io
from datetime import datetime, timedelta


def _current_user():
    ident = get_jwt_identity()
    return User.query.filter_by(username=ident).first()


def admin_required(fn):
    def wrapper(*args, **kwargs):
        user = _current_user()
        if not user or not user.is_admin:
            return {"message": "Admin privileges required"}, 403
        return fn(*args, **kwargs)

    wrapper.__name__ = fn.__name__
    return jwt_required()(wrapper)


class AdminShowsResource(Resource):
    @admin_required
    def get(self):
        shows = Show.query.order_by(Show.start_time.desc()).all()
        out = []
        for s in shows:
            out.append({
                "id": s.id,
                "name": s.name,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "theatre_id": s.theatre_id,
                "capacity": s.capacity,
            })
        return {"shows": out}

    @admin_required
    def post(self):
        data = request.get_json(force=True)
        required = ["name", "start_time", "end_time", "theatre_id", "ticket_price"]
        for r in required:
            if r not in data:
                return {"message": f"{r} is required"}, 400

        show = Show(
            name=data.get("name"),
            start_time=datetime.fromisoformat(data.get("start_time")),
            end_time=datetime.fromisoformat(data.get("end_time")),
            theatre_id=data.get("theatre_id"),
            ticket_price=data.get("ticket_price"),
            capacity=data.get("capacity") or 0,
        )
        db.session.add(show)
        db.session.commit()
        return {"message": "Show created", "id": show.id}, 201


class AdminShowDetailResource(Resource):
    @admin_required
    def get(self, show_id):
        s = Show.query.get(show_id)
        if not s:
            return {"message": "Show not found"}, 404
        return {
            "id": s.id,
            "name": s.name,
            "start_time": s.start_time.isoformat() if s.start_time else None,
            "end_time": s.end_time.isoformat() if s.end_time else None,
            "theatre_id": s.theatre_id,
            "capacity": s.capacity,
        }

    @admin_required
    def put(self, show_id):
        s = Show.query.get(show_id)
        if not s:
            return {"message": "Show not found"}, 404
        data = request.get_json(force=True)
        for k in ["name", "start_time", "end_time", "ticket_price", "capacity", "theatre_id"]:
            if k in data:
                val = data.get(k)
                if k in ["start_time", "end_time"] and val:
                    setattr(s, k, datetime.fromisoformat(val))
                else:
                    setattr(s, k, val)
        db.session.commit()
        return {"message": "Show updated"}

    @admin_required
    def delete(self, show_id):
        s = Show.query.get(show_id)
        if not s:
            return {"message": "Show not found"}, 404
        db.session.delete(s)
        db.session.commit()
        return {"message": "Show deleted"}


class AdminTheatresResource(Resource):
    @admin_required
    def get(self):
        theatres = Theatre.query.order_by(Theatre.id).all()
        out = [{"id": t.id, "name": t.name, "place": t.place, "capacity": t.capacity} for t in theatres]
        return {"theatres": out}

    @admin_required
    def post(self):
        data = request.get_json(force=True)
        if not data.get("name") or not data.get("place") or not data.get("capacity"):
            return {"message": "name, place and capacity are required"}, 400
        t = Theatre(name=data.get("name"), place=data.get("place"), capacity=int(data.get("capacity")))
        db.session.add(t)
        db.session.commit()
        return {"message": "Theatre created", "id": t.id}, 201


class AdminTheatreDetailResource(Resource):
    @admin_required
    def get(self, theatre_id):
        t = Theatre.query.get(theatre_id)
        if not t:
            return {"message": "Theatre not found"}, 404
        return {"id": t.id, "name": t.name, "place": t.place, "capacity": t.capacity}

    @admin_required
    def put(self, theatre_id):
        t = Theatre.query.get(theatre_id)
        if not t:
            return {"message": "Theatre not found"}, 404
        data = request.get_json(force=True)
        for k in ["name", "place", "capacity"]:
            if k in data:
                setattr(t, k, data.get(k))
        db.session.commit()
        return {"message": "Theatre updated"}

    @admin_required
    def delete(self, theatre_id):
        t = Theatre.query.get(theatre_id)
        if not t:
            return {"message": "Theatre not found"}, 404
        db.session.delete(t)
        db.session.commit()
        return {"message": "Theatre deleted"}


class AdminStatsResource(Resource):
    @admin_required
    def get(self):
        # Optional query params: since_days, theatre_id
        since_days = int(request.args.get("since_days", "30"))
        theatre_id = request.args.get("theatre_id")
        since = datetime.utcnow() - timedelta(days=since_days)

        q = Ticket.query.filter(Ticket.booked_at != None)
        q = q.filter(Ticket.booked_at >= since)
        if theatre_id:
            q = q.filter(Ticket.theatre_id == int(theatre_id))

        total_bookings = q.count()
        total_revenue = sum([t.price * (t.quantity or 1) for t in q.all()])

        # Bookings per show
        per_show = db.session.query(Show.id, Show.name, db.func.count(Ticket.id).label("count"))
        per_show = per_show.join(Ticket, Show.id == Ticket.show_id)
        per_show = per_show.filter(Ticket.booked_at != None, Ticket.booked_at >= since)
        if theatre_id:
            per_show = per_show.filter(Ticket.theatre_id == int(theatre_id))
        per_show = per_show.group_by(Show.id).order_by(db.desc("count")).limit(20).all()

        per_show_out = [{"show_id": s[0], "name": s[1], "bookings": s[2]} for s in per_show]

        return {"total_bookings": total_bookings, "total_revenue": total_revenue, "top_shows": per_show_out}


class AdminStatsTimeseriesResource(Resource):
    @admin_required
    def get(self):
        # Return bookings per day for the window specified by since_days
        since_days = int(request.args.get("since_days", "30"))
        theatre_id = request.args.get("theatre_id")
        since = datetime.utcnow() - timedelta(days=since_days)

        # Group by date
        results = db.session.query(
            db.func.date(Ticket.booked_at).label("day"),
            db.func.count(Ticket.id).label("bookings"),
            db.func.sum(Ticket.price * Ticket.quantity).label("revenue"),
        )
        results = results.filter(Ticket.booked_at != None, Ticket.booked_at >= since)
        if theatre_id:
            results = results.filter(Ticket.theatre_id == int(theatre_id))
        results = results.group_by(db.func.date(Ticket.booked_at)).order_by(db.func.date(Ticket.booked_at)).all()

        out = [{"day": r[0], "bookings": int(r[1] or 0), "revenue": float(r[2] or 0.0)} for r in results]
        return {"timeseries": out}


class AdminSeatImportResource(Resource):
    @admin_required
    def post(self, theatre_id):
        """Import theatre seats from uploaded CSV (row_label,seat_number,seat_type,is_active)"""
        if 'file' not in request.files:
            return {"message": "No file provided"}, 400
        f = request.files['file']
        try:
            stream = io.StringIO(f.stream.read().decode('utf-8'))
            reader = csv.DictReader(stream)
            inserted = 0
            for row in reader:
                row_label = row.get('row_label') or row.get('row')
                seat_number = int(row.get('seat_number') or row.get('number'))
                seat_type = row.get('seat_type') or 'regular'
                is_active = row.get('is_active', 'true').lower() in ('1','true','yes')
                # Avoid duplicates
                exists = TheatreSeat.query.filter_by(theatre_id=theatre_id, row_label=row_label, seat_number=seat_number).first()
                if exists:
                    continue
                s = TheatreSeat(theatre_id=theatre_id, row_label=row_label, seat_number=seat_number, seat_type=seat_type, is_active=is_active)
                db.session.add(s)
                inserted += 1
            db.session.commit()
            # Invalidate theatre seat map cache so frontend picks up new layout
            try:
                from cache.seat_cache import seat_cache
                seat_cache.delete_theatre_seat_map(theatre_id)
            except Exception:
                pass
            return {"message": f"Imported {inserted} seats"}
        except Exception as e:
            db.session.rollback()
            return {"message": f"Import failed: {e}"}, 500


class AdminSeatExportResource(Resource):
    @admin_required
    def get(self, theatre_id):
        seats = TheatreSeat.query.filter_by(theatre_id=theatre_id).order_by(TheatreSeat.row_label, TheatreSeat.seat_number).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['row_label','seat_number','seat_type','is_active'])
        for s in seats:
            writer.writerow([s.row_label, s.seat_number, s.seat_type, '1' if s.is_active else '0'])
        output.seek(0)
        return (output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=theatre_{theatre_id}_seats.csv'
        })


class AdminBulkShowsImportResource(Resource):
    @admin_required
    def post(self):
        # Accept CSV upload with columns: name,start_time,end_time,theatre_id,ticket_price,capacity
        if 'file' not in request.files:
            return {"message": "No file provided"}, 400
        f = request.files['file']
        try:
            stream = io.StringIO(f.stream.read().decode('utf-8'))
            reader = csv.DictReader(stream)
            created = 0
            for row in reader:
                try:
                    show = Show(
                        name=row.get('name'),
                        start_time=datetime.fromisoformat(row.get('start_time')) if row.get('start_time') else None,
                        end_time=datetime.fromisoformat(row.get('end_time')) if row.get('end_time') else None,
                        theatre_id=int(row.get('theatre_id')) if row.get('theatre_id') else None,
                        ticket_price=float(row.get('ticket_price') or 0.0),
                        capacity=int(row.get('capacity') or 0),
                    )
                    db.session.add(show)
                    created += 1
                except Exception:
                    continue
            db.session.commit()
            return {"message": f"Created {created} shows"}
        except Exception as e:
            db.session.rollback()
            return {"message": f"Import failed: {e}"}, 500


class RecommendationsResource(Resource):
    def get(self):
        # Simple popularity-based recommendations: most booked shows in last 30 days
        limit = int(request.args.get("limit", "6"))
        since = datetime.utcnow() - timedelta(days=30)
        per_show = db.session.query(Show.id, Show.name, db.func.count(Ticket.id).label("count"))
        per_show = per_show.join(Ticket, Show.id == Ticket.show_id)
        per_show = per_show.filter(Ticket.booked_at != None, Ticket.booked_at >= since)
        per_show = per_show.group_by(Show.id).order_by(db.desc("count")).limit(limit).all()
        out = [{"id": s[0], "name": s[1], "bookings": s[2]} for s in per_show]
        return {"recommendations": out}
