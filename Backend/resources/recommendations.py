from collections import Counter
from flask_restful import Resource
from flask import jsonify

from extensions import db
from models import Ticket, Show


class ShowRecommendationsResource(Resource):
    """Rule-based 'people who watched X also watched Y' recommendations.

    Simple algorithm:
    - Find users who bought tickets for show X
    - Gather other shows these users bought
    - Rank by co-occurrence count and return top-N
    """

    def get(self, show_id):
        try:
            # Users who bought tickets for this show
            user_ids = db.session.query(Ticket.user_id).filter(Ticket.show_id == show_id).distinct().all()
            user_ids = [u[0] for u in user_ids if u[0] is not None]

            if not user_ids:
                return jsonify([])

            # Other shows purchased by these users
            other_shows = (
                db.session.query(Ticket.show_id)
                .filter(Ticket.user_id.in_(user_ids), Ticket.show_id != show_id)
                .all()
            )
            other_show_ids = [s[0] for s in other_shows if s[0] is not None]

            counts = Counter(other_show_ids)
            top = counts.most_common(5)

            # Fetch show metadata
            recommendations = []
            for sid, score in top:
                show = Show.query.get(sid)
                if show:
                    recommendations.append({
                        'show_id': show.id,
                        'name': show.name,
                        'tags': show.tags,
                        'score': int(score),
                    })

            return {'recommendations': recommendations}

        except Exception as e:
            return {'message': 'Failed to generate recommendations', 'error': str(e)}, 500
