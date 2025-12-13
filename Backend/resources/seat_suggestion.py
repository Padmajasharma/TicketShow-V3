from flask_restful import Resource
from flask import request
import math

from extensions import db
from models import Show, TheatreSeat, Ticket
from cache.seat_cache import seat_cache


def _row_index_from_label(rows_sorted, label):
    try:
        return rows_sorted.index(label)
    except Exception:
        return 0


class SeatSuggestionResource(Resource):
    """Suggest a best seat for a user based on preference, availability and history."""

    def get(self, show_id):
        """Query params:
        - preference=center|aisle|front|any
        - count=1 (how many suggestions)
        """
        pref = request.args.get('preference', 'center')
        count = int(request.args.get('count', 1))

        show = Show.query.get(show_id)
        if not show:
            return {'message': 'Show not found'}, 404

        theatre_id = show.theatre_id

        # Try to get cached seat map
        seat_map = seat_cache.get_theatre_seat_map(theatre_id)
        seats = []
        if seat_map:
            seats = seat_map
        else:
            # Fallback to DB
            qs = TheatreSeat.query.filter_by(theatre_id=theatre_id, is_active=True).all()
            for s in qs:
                seats.append({'row': s.row_label, 'num': s.seat_number, 'seat_id': f"{s.row_label}{s.seat_number}"})

        # Build availability sets
        booked = set([t.seat_id for t in Ticket.query.filter_by(show_id=show_id).all() if t.seat_id])
        held = set([h['seat_id'] for h in seat_cache.get_active_holds(show_id)])

        # Rows sorted for center calculation
        rows = sorted(list({s['row'] for s in seats}))

        # Compute per-row seat counts
        row_seats = {}
        for s in seats:
            row_seats.setdefault(s['row'], []).append(s)

        candidate_scores = []
        for s in seats:
            seat_id = s.get('seat_id') or f"{s['row']}{s['num']}"
            if seat_id in booked or seat_id in held:
                continue

            # proximity to center score
            row = s['row']
            row_list = sorted(row_seats.get(row, []), key=lambda x: x['num'])
            nums = [x['num'] for x in row_list]
            if not nums:
                continue
            mid = (nums[0] + nums[-1]) / 2.0
            proximity = 1.0 / (1.0 + abs(s['num'] - mid))

            # row preference: center rows preferred
            row_idx = _row_index_from_label(rows, row)
            center_row_idx = (len(rows) - 1) / 2.0 if rows else 0
            row_proximity = 1.0 / (1.0 + abs(row_idx - center_row_idx))

            # historical popularity (how often this seat was bought across all shows)
            popularity = Ticket.query.filter(Ticket.seat_id == seat_id).count()
            pop_score = math.log(1 + popularity)

            score = 0.6 * proximity + 0.3 * row_proximity + 0.1 * pop_score

            # tweak by preference
            if pref == 'aisle':
                # prefer seats with low or high seat number (edges)
                if s['num'] == nums[0] or s['num'] == nums[-1]:
                    score *= 1.2
            elif pref == 'front':
                # prefer front-most rows (smallest row index)
                score *= (1.0 + (1.0 / (1 + row_idx)))

            candidate_scores.append((score, seat_id, s))

        candidate_scores.sort(reverse=True, key=lambda x: x[0])

        suggestions = [ {'seat_id': c[1], 'score': round(c[0], 3), 'row': c[2]['row'], 'num': c[2]['num']} for c in candidate_scores[:count] ]

        return {'suggestions': suggestions}
