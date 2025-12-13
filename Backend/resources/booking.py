# backend/resources/booking.py
"""
Booking Resource with proper Redis locking, DB transactions, caching, and Celery tasks.

Flow:
1. Redis atomic seat reservation - Prevent race conditions with Lua scripts
2. DB validation inside transaction - Ensure data consistency
3. Write booking, update DB - Create tickets and update capacity
4. Update Redis cache - Invalidate/update cached data
5. Enqueue Celery task - Send confirmation email asynchronously
"""
import logging
from datetime import datetime

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db, cache
from models import User, Show, ShowRating, Ticket, TheatreSeat, Booking
from cache.seat_cache import seat_cache
from payments import payment_simulator
from utils.audit import log_action


class BookShowsResource(Resource):
    @jwt_required()
    def post(self, show_id):
        """
        Book tickets for a show with full transactional safety.
        
        Steps:
        1. Redis check & atomic lock
        2. DB validation inside transaction
        3. Write booking, update DB
        4. Update Redis cache
        5. Enqueue Celery task
        """
        data = request.get_json()
        selected_seats = data.get("seats", [])  # Array of {row, num} objects
        reservation_id = data.get("reservation_id")
        number_of_tickets = len(selected_seats) if selected_seats else int(data.get("number_of_tickets", 0))
        user_rating = data.get("rating")
        current_user_username = get_jwt_identity()
        
        # Basic validation before acquiring lock
        if number_of_tickets <= 0:
            return {"message": "No seats selected"}, 400
        
        if not selected_seats:
            return {"message": "Seat selection is required"}, 400
        
        current_user = User.query.filter_by(username=current_user_username).first()
        if not current_user:
            return {"message": "User not found"}, 404

        # Extract idempotency key (supports header or JSON field)
        idempotency_key = request.headers.get('Idempotency-Key') or data.get('idempotency_key')

        # If idempotency key provided, check for an existing booking
        if idempotency_key:
            existing_booking = Booking.query.filter_by(idempotency_key=idempotency_key, user_id=current_user.id, show_id=show_id).first()
            if existing_booking:
                # If booking already confirmed and has tickets, return booking details
                if existing_booking.status == 'confirmed':
                    tickets = Ticket.query.filter_by(booking_id=existing_booking.id).all()
                    return {
                        "message": "Booking already completed",
                        "booking_id": existing_booking.id,
                        "tickets": [{"id": t.id, "seat_id": t.seat_id} for t in tickets]
                    }, 200
                # If booking exists but not yet confirmed, and tickets already created, return current state
                tickets = Ticket.query.filter_by(booking_id=existing_booking.id).all()
                if tickets:
                    return {
                        "message": "Booking in progress or previously created",
                        "booking_id": existing_booking.id,
                        "tickets": [{"id": t.id, "seat_id": t.seat_id} for t in tickets]
                    }, 200

        # ============================================================
        # STEP 1: If a reservation_id (seat-level hold) is provided, validate it; otherwise fall back to count-based atomic reservation
        if reservation_id:
            # Validate reservation belongs to current user and covers selected seats
            try:
                reservation_key = f"reservation:{reservation_id}"
                res_exists = seat_cache.redis.exists(reservation_key)
                if not res_exists:
                    return {"message": "Reservation not found or expired"}, 404

                owner = seat_cache.redis.hget(reservation_key, 'user_id')
                seats_csv = seat_cache.redis.hget(reservation_key, 'seats') or ''
                reserved_seats = seats_csv.split(',') if seats_csv else []

                # Normalize selected seat ids
                seat_ids = [f"{s['row']}{s['num']}" for s in selected_seats]

                if str(owner) != str(current_user_username):
                    return {"message": "Reservation does not belong to current user"}, 403

                if set(reserved_seats) != set(seat_ids):
                    return {"message": "Selected seats do not match reservation"}, 400

                # We rely on per-seat holds; skip the capacity count reservation
            except Exception as e:
                logging.error(f"Reservation validation failed: {e}")
                return {"message": "Reservation validation failed"}, 500
        else:
            # No reservation id provided - fall back to count-based reservation
            # Log that we're attempting a count-based reservation
            try:
                log_action(current_user.id, show_id, None, 'seat_reservation_attempt', {'count': number_of_tickets})
            except Exception:
                pass
            reservation_result = seat_cache.reserve_seats_atomic(show_id, number_of_tickets)

            if not reservation_result['success']:
                error_msg = reservation_result['error']
                if error_msg == 'INSUFFICIENT_CAPACITY':
                    return {"message": "Not enough available tickets"}, 400
                elif error_msg == 'LOCK_ACQUISITION_FAILED':
                    return {"message": "Show is currently busy. Please try again."}, 409
                else:
                    return {"message": "Booking service temporarily unavailable"}, 503

            reservation_id = reservation_result['reservation_id']

        # Prepare container for created tickets so we can reference IDs later
        tickets_created = []

        try:
            # ============================================================
            # STEP 2: DB validation inside transaction
            # ============================================================
            try:
                # Start explicit transaction
                show = Show.query.with_for_update().get(show_id)
                if not show:
                    # Release reservation if show not found
                    try:
                        if reservation_id:
                            released = seat_cache.release_seat_hold(reservation_id)
                            if not released:
                                seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                        else:
                            seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                    except Exception:
                        seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                    return {"message": "Show not found"}, 404

                # Double-check capacity with DB lock held (belt and suspenders)
                if show.capacity < number_of_tickets:
                    seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                    return {"message": "Not enough available tickets"}, 400

                # ============================================================
                # STEP 3: Write booking, update DB
                # ============================================================

                # Handle rating if provided
                if user_rating:
                    user_rating = int(user_rating)
                    if user_rating < 1 or user_rating > 5:
                        db.session.rollback()
                        try:
                            if reservation_id:
                                released = seat_cache.release_seat_hold(reservation_id)
                                if not released:
                                    seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                            else:
                                seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                        except Exception:
                            seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                        return {
                            "message": "Invalid rating value. It should be between 1 and 5.",
                        }, 400

                    existing_rating = ShowRating.query.filter_by(
                        user_id=current_user.id,
                        show_id=show.id,
                    ).first()

                    if existing_rating:
                        existing_rating.rating = user_rating
                    else:
                        new_rating = ShowRating(
                            user_id=current_user.id,
                            show_id=show.id,
                            rating=user_rating,
                        )
                        db.session.add(new_rating)

                    # Recalculate average rating
                    ratings = ShowRating.query.filter_by(show_id=show.id).all()
                    total_ratings = sum(r.rating for r in ratings)
                    average_rating = total_ratings / len(ratings) if ratings else 0
                    show.rating = average_rating

                # Validate and lock selected seats
                seat_ids = []
                for seat in selected_seats:
                    seat_id = f"{seat['row']}{seat['num']}"
                    seat_ids.append(seat_id)
                    
                    # Check if seat exists in theatre layout
                    theatre_seat = TheatreSeat.query.filter_by(
                        theatre_id=show.theatre_id,
                        row_label=seat['row'],
                        seat_number=seat['num'],
                        is_active=True
                    ).first()
                    
                    if not theatre_seat:
                        db.session.rollback()
                        try:
                            if reservation_id:
                                released = seat_cache.release_seat_hold(reservation_id)
                                if not released:
                                    seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                            else:
                                seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                        except Exception:
                            seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                        return {"message": f"Seat {seat_id} does not exist or is not available"}, 400
                
                # Check for already booked seats for this show
                existing_bookings = Ticket.query.filter(
                    Ticket.show_id == show.id,
                    Ticket.seat_id.in_(seat_ids)
                ).all()
                
                if existing_bookings:
                    booked_seats = [ticket.seat_id for ticket in existing_bookings]
                    db.session.rollback()
                    try:
                        if reservation_id:
                            released = seat_cache.release_seat_hold(reservation_id)
                            if not released:
                                seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                        else:
                            seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                    except Exception:
                        seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                    return {"message": f"Seats already booked: {', '.join(booked_seats)}"}, 400

                # Calculate total and run payment simulation before creating DB records
                total_price = number_of_tickets * show.ticket_price

                payment_info = data.get('payment', {}) or {}
                try:
                    payment_result = payment_simulator.simulate_charge(int(total_price * 100), payment_info, idempotency_key)
                except Exception as e:
                    logging.error(f"Payment simulation failed: {e}")
                    payment_result = {'status': 'failure', 'transaction_id': None, 'reason': 'simulation_error'}

                if not payment_result or payment_result.get('status') != 'success':
                    # Log payment failure
                    try:
                        log_action(current_user.id, show_id, None, 'payment_failed', {'reason': payment_result.get('reason') if payment_result else 'unknown'})
                    except Exception:
                        pass
                    # Release reservation/holds on payment failure
                    try:
                        if reservation_id:
                            released = seat_cache.release_seat_hold(reservation_id)
                            if not released:
                                seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                        else:
                            seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                    except Exception:
                        try:
                            seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                        except Exception:
                            pass

                    reason = payment_result.get('reason') if payment_result else 'payment_failed'
                    return {"message": "Payment failed", "reason": reason}, 402

                # Payment succeeded — create Booking and Tickets
                # Log payment started/succeeded
                try:
                    log_action(current_user.id, show.id, None, 'payment_started', {'transaction_id': payment_result.get('transaction_id')})
                except Exception:
                    pass
                booking = None
                if idempotency_key:
                    try:
                        booking = Booking(idempotency_key=idempotency_key, user_id=current_user.id, show_id=show.id, reservation_id=str(reservation_id) if reservation_id else None, status='reserved')
                        db.session.add(booking)
                    except Exception:
                        booking = None

                for seat in selected_seats:
                    seat_id = f"{seat['row']}{seat['num']}"
                    ticket = Ticket(
                        theatre_id=show.theatre_id,
                        price=show.ticket_price,
                        quantity=1,
                        user_id=current_user.id,
                        show_id=show.id,
                        seat_row=seat['row'],
                        seat_number=seat['num'],
                        seat_id=seat_id,
                    )
                    ticket.booked_at = datetime.utcnow()
                    if booking:
                        ticket.booking = booking
                    db.session.add(ticket)
                    tickets_created.append(ticket)

                # Update show capacity and mark booking confirmed
                show.capacity -= number_of_tickets
                try:
                    if booking:
                        booking.status = 'confirmed'
                        booking.confirmed_at = datetime.utcnow()
                except Exception:
                    pass

                db.session.commit()

                # After commit, collect created ticket IDs from session objects
                try:
                    ticket_ids = [t.id for t in tickets_created] if tickets_created else []
                except Exception:
                    try:
                        created_tickets = Ticket.query.filter_by(user_id=current_user.id, show_id=show.id).order_by(Ticket.id.desc()).limit(number_of_tickets).all()
                        ticket_ids = [t.id for t in created_tickets]
                    except Exception:
                        ticket_ids = None

                logging.info(f"Booking successful: User {current_user.id} booked {number_of_tickets} tickets for Show {show_id}")
                try:
                    # Log booking confirmed
                    log_action(current_user.id, show.id, None, 'booking_confirmed', {'booking_id': booking.id if booking else None, 'ticket_ids': ticket_ids})
                except Exception:
                    pass

            except Exception as e:
                # Rollback on any error and log full traceback for debugging
                db.session.rollback()
                logging.exception("Booking transaction failed")
                try:
                    if reservation_id:
                        released = seat_cache.release_seat_hold(reservation_id)
                        if not released:
                            seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                    else:
                        seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                except Exception:
                    seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                return {"message": "Booking failed due to a database error"}, 500

            # ============================================================
            # STEP 4: Confirm booking in Redis cache
            # ============================================================
            # If a seat-level reservation was used, confirm the seat hold; otherwise use the count-based confirm
            try:
                if reservation_id and 'seats' in locals() and isinstance(reserved_seats, list):
                    # seat-level hold flow
                    booking_confirmed = seat_cache.confirm_seat_hold(reservation_id, current_user.id, show_id)
                else:
                    booking_confirmed = seat_cache.confirm_booking(
                        reservation_id, current_user.id, show_id, number_of_tickets
                    )
                if not booking_confirmed:
                    logging.warning(f"Failed to confirm booking in Redis cache for reservation {reservation_id}")
            except Exception as e:
                logging.error(f"Error confirming booking in cache: {e}")

            # Update capacity in cache
            seat_cache.set_show_capacity(show_id, show.capacity)

            # Invalidate any cached show data
            cache.delete(f"show_{show_id}")
            cache.delete("all_shows")

            logging.info(f"Cache updated for show {show_id}, new capacity: {show.capacity}")

            # ============================================================
            # STEP 5: Enqueue Celery task
            # ============================================================
            try:
                from tasks.emails import send_booking_confirmation
                # Collect created ticket IDs to attach PDFs (query recent tickets)
                try:
                    created_tickets = Ticket.query.filter_by(user_id=current_user.id, show_id=show.id).order_by(Ticket.id.desc()).limit(number_of_tickets).all()
                    ticket_ids = [t.id for t in created_tickets]
                except Exception:
                    ticket_ids = None

                send_booking_confirmation.delay(
                    current_user.id,
                    show.id,
                    number_of_tickets,
                    total_price,
                    ticket_ids
                )
                logging.info(f"Booking confirmation email task enqueued for user {current_user.id}")
                try:
                    log_action(current_user.id, show.id, None, 'email_enqueued', {'ticket_ids': ticket_ids})
                except Exception:
                    pass
            except Exception as e:
                # Don't fail the booking if email task fails
                logging.warning(f"Failed to enqueue email task: {e}")

            response_body = {
                "message": f"Successfully booked {number_of_tickets} tickets for {show.name}",
                "success": True,
                "booking": {
                    "show_name": show.name,
                    "tickets": number_of_tickets,
                    "total_price": total_price
                }
            }
            if booking:
                response_body['booking']['booking_id'] = booking.id
            # include ticket ids when available
            if 'ticket_ids' in locals() and ticket_ids:
                response_body['booking']['ticket_ids'] = ticket_ids

            return response_body, 201

        except Exception as e:
            # Log full traceback to help diagnose DB errors
            logging.exception("Booking process failed")
            if 'reservation_id' in locals():
                try:
                    if reservation_id:
                        released = seat_cache.release_seat_hold(reservation_id)
                        if not released:
                            seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                    else:
                        seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
                except Exception:
                    seat_cache.release_lock_and_restore(show_id, reservation_id, number_of_tickets)
            return {"message": "Booking failed"}, 500

    def _book_without_lock(self, show_id, number_of_tickets, user_rating, current_user):
        """
        Fallback booking method when Redis is unavailable.
        Uses database-level locking only.
        """
        try:
            show = Show.query.with_for_update().get(show_id)
            if not show:
                return {"message": "Show not found"}, 404

            if show.capacity < number_of_tickets:
                return {"message": "Not enough available tickets"}, 400

            # Handle rating
            if user_rating:
                user_rating = int(user_rating)
                if user_rating < 1 or user_rating > 5:
                    db.session.rollback()
                    return {"message": "Invalid rating value"}, 400

                existing_rating = ShowRating.query.filter_by(
                    user_id=current_user.id,
                    show_id=show.id,
                ).first()

                if existing_rating:
                    existing_rating.rating = user_rating
                else:
                    new_rating = ShowRating(
                        user_id=current_user.id,
                        show_id=show.id,
                        rating=user_rating,
                    )
                    db.session.add(new_rating)

                ratings = ShowRating.query.filter_by(show_id=show.id).all()
                total_ratings = sum(r.rating for r in ratings)
                average_rating = total_ratings / len(ratings) if ratings else 0
                show.rating = average_rating

            # Create tickets
            total_price = number_of_tickets * show.ticket_price
            for _ in range(number_of_tickets):
                ticket = Ticket(
                    theatre_id=show.theatre_id,
                    price=show.ticket_price,
                    quantity=1,
                    user_id=current_user.id,
                    show_id=show.id,
                )
                ticket.booked_at = datetime.utcnow()
                db.session.add(ticket)

            show.capacity -= number_of_tickets
            db.session.commit()

            # Try to enqueue email task
            try:
                from tasks.emails import send_booking_confirmation
                # Fallback: no per-seat tickets list, try to pass whatever we have
                try:
                    created_tickets = Ticket.query.filter_by(user_id=current_user.id, show_id=show.id).order_by(Ticket.id.desc()).limit(number_of_tickets).all()
                    ticket_ids = [t.id for t in created_tickets]
                except Exception:
                    ticket_ids = None
                send_booking_confirmation.delay(
                    current_user.id,
                    show.id,
                    number_of_tickets,
                    total_price,
                    ticket_ids
                )
            except Exception:
                pass

            return {
                "message": f"Successfully booked {number_of_tickets} tickets for {show.name}",
                "success": True,
                "booking": {
                    "show_name": show.name,
                    "tickets": number_of_tickets,
                    "total_price": total_price
                }
            }, 201

        except Exception as e:
            db.session.rollback()
            logging.error(f"Fallback booking failed: {e}")
            return {"message": "Booking failed"}, 500
