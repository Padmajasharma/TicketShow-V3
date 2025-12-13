from flask import request
from flask_restful import Resource
from datetime import datetime, timedelta
from extensions import db
from models import Ticket, Show, Theatre


class AnalyticsSalesResource(Resource):
    def get(self):
        """Return sales grouped by movie or by city.

        Query params:
        - group_by: 'movie' (default), 'city', or a category like 'concert', 'play', 'event', 'theatre'
        - since_days: integer days window (default 30)
        - start: ISO date YYYY-MM-DD (optional)
        - end: ISO date YYYY-MM-DD (optional)
        """
        group_by_raw = request.args.get('group_by', 'movie')
        # normalize group_by to handle plural/capitalized forms from the UI
        gb = (group_by_raw or 'movie').strip().lower()
        # map common plural/alias forms to canonical values expected below
        _map = {
            'movies': 'movie',
            'movie': 'movie',
            'concerts': 'concert',
            'concert': 'concert',
            'plays': 'play',
            'play': 'play',
            'events': 'event',
            'event': 'event',
            'theatres': 'theatre',
            'theaters': 'theatre',
            'theatre': 'theatre',
            'theater': 'theatre',
            'cities': 'city',
            'city': 'city',
            'place': 'city'
        }
        group_by = _map.get(gb, gb)
        start_param = request.args.get('start')
        end_param = request.args.get('end')
        since_days = int(request.args.get('since_days', '30'))
        include_unconfirmed = request.args.get('include_unconfirmed', '0').lower() in ('1', 'true', 'yes')
        # If group_by contains a category name (concert, play, event, theatre), treat that as a tag filter
        category = None
        if group_by in ('concert', 'play', 'event', 'theatre'):
            category = group_by

        # Parse start/end if provided, otherwise compute 'since' from since_days
        try:
            if start_param:
                start = datetime.strptime(start_param, '%Y-%m-%d')
            else:
                start = None
            if end_param:
                # treat end as inclusive end of day
                end = datetime.strptime(end_param, '%Y-%m-%d')
                end = end.replace(hour=23, minute=59, second=59)
            else:
                end = None
        except Exception:
            # fallback to since_days if parsing fails
            start = None
            end = None

        if not start and not end:
            # when since_days==0 we treat it as "no date filter" (all time)
            if since_days == 0:
                since = None
            else:
                since = datetime.utcnow() - timedelta(days=since_days)
        else:
            # Use start/end to filter
            since = start

        q = db.session.query(Ticket)
        if since is not None and end is not None:
            q = q.filter(Ticket.booked_at != None, Ticket.booked_at >= since, Ticket.booked_at <= end)
        elif since is not None:
            q = q.filter(Ticket.booked_at != None, Ticket.booked_at >= since)
        else:
            # default: last since_days
            q = q.filter(Ticket.booked_at != None, Ticket.booked_at >= datetime.utcnow() - timedelta(days=since_days))

        if group_by == 'city' or group_by == 'place':
            # Aggregate tickets first (applying date/unconfirmed rules), then join through Show -> Theatre
            ticket_agg = db.session.query(
                Ticket.show_id.label('show_id'),
                db.func.count(Ticket.id).label('bookings'),
                db.func.sum(Ticket.price * Ticket.quantity).label('revenue')
            )

            # If category filter is provided, join Show and filter by tags
            if category:
                tag_term = category
                ticket_agg = ticket_agg.join(Show, Show.id == Ticket.show_id).filter(Show.tags.ilike(f"%{tag_term}%"))

            # Decide whether to apply date filtering. If include_unconfirmed is True or since_days==0
            # with no explicit start/end, we skip the booked_at filter (include all tickets).
            apply_date_filter = True
            if include_unconfirmed:
                apply_date_filter = False
            elif since_days == 0 and not start_param and not end_param:
                apply_date_filter = False

            if apply_date_filter:
                if since is not None and end is not None:
                    ticket_agg = ticket_agg.filter(Ticket.booked_at != None, Ticket.booked_at >= since, Ticket.booked_at <= end)
                elif since is not None:
                    ticket_agg = ticket_agg.filter(Ticket.booked_at != None, Ticket.booked_at >= since)
                else:
                    ticket_agg = ticket_agg.filter(Ticket.booked_at != None, Ticket.booked_at >= datetime.utcnow() - timedelta(days=since_days))

            ticket_agg = ticket_agg.group_by(Ticket.show_id).subquery()

            results = db.session.query(
                Theatre.place.label('city'),
                db.func.coalesce(db.func.sum(ticket_agg.c.bookings), 0).label('bookings'),
                db.func.coalesce(db.func.sum(ticket_agg.c.revenue), 0.0).label('revenue')
            ).join(Show, Show.theatre_id == Theatre.id).outerjoin(ticket_agg, ticket_agg.c.show_id == Show.id)
            results = results.group_by(Theatre.place).order_by(db.desc('revenue')).all()
            out = [{'city': r[0], 'bookings': int(r[1] or 0), 'revenue': float(r[2] or 0.0)} for r in results]
            return {'group_by': group_by, 'since_days': since_days, 'data': out}

        # default: group by movie/show
        # Build a tickets aggregation subquery that applies the date filters, then left-join to Show
        ticket_agg = db.session.query(
            Ticket.show_id.label('show_id'),
            db.func.count(Ticket.id).label('bookings'),
            db.func.sum(Ticket.price * Ticket.quantity).label('revenue')
        )

        # If category filter is provided, join Show and filter by tags
        if category:
            tag_term = category
            ticket_agg = ticket_agg.join(Show, Show.id == Ticket.show_id).filter(Show.tags.ilike(f"%{tag_term}%"))

        # Decide whether to apply date filtering. If include_unconfirmed is True or since_days==0
        # with no explicit start/end, we skip the booked_at filter (include all tickets).
        apply_date_filter = True
        if include_unconfirmed:
            apply_date_filter = False
        elif since_days == 0 and not start_param and not end_param:
            apply_date_filter = False

        if apply_date_filter:
            if since is not None and end is not None:
                ticket_agg = ticket_agg.filter(Ticket.booked_at != None, Ticket.booked_at >= since, Ticket.booked_at <= end)
            elif since is not None:
                ticket_agg = ticket_agg.filter(Ticket.booked_at != None, Ticket.booked_at >= since)
            else:
                ticket_agg = ticket_agg.filter(Ticket.booked_at != None, Ticket.booked_at >= datetime.utcnow() - timedelta(days=since_days))

        ticket_agg = ticket_agg.group_by(Ticket.show_id).subquery()

        results = db.session.query(
            Show.id.label('show_id'),
            Show.name.label('name'),
            db.func.coalesce(ticket_agg.c.bookings, 0).label('bookings'),
            db.func.coalesce(ticket_agg.c.revenue, 0.0).label('revenue')
        ).outerjoin(ticket_agg, ticket_agg.c.show_id == Show.id)
        # If a category was requested via group_by (concert/play/event/theatre), filter shows to that category
        if category:
            results = results.filter(Show.tags.ilike(f"%{category}%"))
        results = results.order_by(db.desc('revenue')).all()

        out = [{'show_id': r[0], 'name': r[1], 'bookings': int(r[2] or 0), 'revenue': float(r[3] or 0.0)} for r in results]
        return {'group_by': group_by, 'since_days': since_days, 'data': out}
