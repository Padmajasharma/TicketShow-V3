# backend/seed_theatre_seats.py
"""
Script to seed theatre seats for existing theatres.
Creates a standard cinema layout with rows A-J and seats 1-15 per row.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from models import Theatre, TheatreSeat

def seed_theatre_seats():
    """Create seats for all existing theatres"""

    theatres = Theatre.query.all()
    if not theatres:
        print("No theatres found. Please create theatres first.")
        return

    total_seats_created = 0

    for theatre in theatres:
        print(f"Creating seats for theatre: {theatre.name} (ID: {theatre.id})")

        # Check if seats already exist
        existing_seats = TheatreSeat.query.filter_by(theatre_id=theatre.id).count()
        if existing_seats > 0:
            print(f"  Theatre already has {existing_seats} seats. Skipping...")
            continue

        seats_created = 0

        # Create rows A-J with 15 seats each (standard cinema layout)
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

        for row in rows:
            for seat_num in range(1, 16):  # 1-15 seats per row
                # Determine seat type
                if row in ['I', 'J']:  # Back rows = premium
                    seat_type = 'premium'
                elif seat_num in [1, 15]:  # Aisle seats = regular
                    seat_type = 'regular'
                else:
                    seat_type = 'regular'

                seat = TheatreSeat(
                    theatre_id=theatre.id,
                    row_label=row,
                    seat_number=seat_num,
                    seat_type=seat_type,
                    is_active=True
                )

                db.session.add(seat)
                seats_created += 1

        try:
            db.session.commit()
            print(f"  Created {seats_created} seats for {theatre.name}")
            total_seats_created += seats_created
        except Exception as e:
            db.session.rollback()
            print(f"  Error creating seats for {theatre.name}: {e}")

    print(f"\nTotal seats created: {total_seats_created}")

if __name__ == "__main__":
    from run import app

    with app.app_context():
        seed_theatre_seats()