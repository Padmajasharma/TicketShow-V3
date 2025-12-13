#!/usr/bin/env python3
"""Simple DB inspection script to help debug analytics results.

Run from the `Backend` folder:
    python3 scripts/inspect_db.py

It prints counts of shows, a sample of shows, ticket counts per show, and tickets missing `booked_at`.
"""
import os
import sys

# Ensure parent directory (project Backend/) is on sys.path so imports like `run` work
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from run import app as flask_app
from models import db, Show, Ticket, Theatre


def main():
    with flask_app.app_context():
        total_shows = Show.query.count()
        print(f"Total shows: {total_shows}")

        print('\nFirst 30 shows (id, name):')
        for s in Show.query.order_by(Show.id).limit(30).all():
            print(f"  {s.id}: {s.name}")

        print('\nTicket counts per show (show_id, cnt, revenue):')
        from sqlalchemy import text
        rows = db.session.execute(
            text("SELECT show_id, COUNT(*) AS cnt, SUM(price*quantity) AS revenue FROM ticket GROUP BY show_id ORDER BY cnt DESC LIMIT 50")
        ).fetchall()
        if not rows:
            print('  (no tickets found)')
        else:
            for r in rows:
                print(f"  show_id={r[0]} cnt={r[1]} revenue={r[2]}")

        null_booked = Ticket.query.filter(Ticket.booked_at == None).count()
        print(f"\nTickets with NULL booked_at: {null_booked}")

        recent_booked = db.session.execute(
            text("SELECT show_id, COUNT(*) as cnt FROM ticket WHERE booked_at IS NOT NULL AND booked_at >= datetime('now','-30 days') GROUP BY show_id ORDER BY cnt DESC")
        ).fetchall()
        print('\nTickets booked in last 30 days per show:')
        if not recent_booked:
            print('  (none)')
        else:
            for r in recent_booked:
                print(f"  show_id={r[0]} cnt={r[1]}")


if __name__ == '__main__':
    main()
