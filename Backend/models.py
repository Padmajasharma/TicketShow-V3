# backend/models.py
from flask_security import UserMixin, RoleMixin
from datetime import datetime
from extensions import db, bcrypt

roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id")),
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    is_admin = db.Column(db.Boolean(), default=False)

    roles = db.relationship(
        "Role",
        secondary=roles_users,
        backref=db.backref("users", lazy="dynamic"),
    )
    tickets_purchased = db.relationship("Ticket", backref="purchased_by", lazy=True)

    def set_password(self, password: str):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password, password)

    def get_roles(self):
        return [role.name for role in self.roles]


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"<Role {self.name}>"


class Theatre(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    shows = db.relationship(
        "Show",
        backref="theatre",
        lazy=True,
        cascade="all, delete-orphan",
    )


class Screen(db.Model):
    """A physical screen inside a theatre (auditorium). A theatre can have multiple screens."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatre.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Screen 1"
    capacity = db.Column(db.Integer, nullable=False, default=0)

    theatre = db.relationship('Theatre', backref=db.backref('screens', lazy='dynamic'))



class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    image = db.Column(db.String(255))
    rating = db.Column(db.Float, nullable=True)
    tags = db.Column(db.String(200))
    ticket_price = db.Column(db.Float)
    capacity = db.Column(db.Integer, nullable=False, default=1)
    theatre_id = db.Column(db.Integer, db.ForeignKey("theatre.id"), nullable=True)
    screen_id = db.Column(db.Integer, db.ForeignKey('screen.id'), nullable=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=True)
    
    # TMDB metadata fields
    tmdb_id = db.Column(db.Integer, nullable=True)
    overview = db.Column(db.Text, nullable=True)  # Movie description
    runtime = db.Column(db.Integer, nullable=True)  # Duration in minutes
    release_date = db.Column(db.String(20), nullable=True)  # YYYY-MM-DD
    tmdb_rating = db.Column(db.Float, nullable=True)  # TMDB vote_average
    backdrop = db.Column(db.String(255), nullable=True)  # Backdrop image URL

    tickets = db.relationship(
        "Ticket",
        backref="event",
        # Use lazy='select' instead of 'joined' to avoid automatic JOINs that
        # can fail at startup if Ticket schema has pending migrations.
        lazy="select",
        primaryjoin="Show.id == Ticket.show_id",
    )
    ratings = db.relationship("ShowRating", backref="show", lazy="dynamic")

    # optional relationship pointers
    screen = db.relationship('Screen', backref=db.backref('shows', lazy='dynamic'))
    movie = db.relationship('Movie', backref=db.backref('shows', lazy='dynamic'))

    __table_args__ = (
        db.Index('ix_show_start_time', 'start_time'),
    )


class ShowRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey("show.id"), nullable=False)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    theatre_id = db.Column(
        db.Integer,
        db.ForeignKey("theatre.id", ondelete="CASCADE"),
        nullable=True,
    )
    screen_id = db.Column(db.Integer, db.ForeignKey('screen.id'), nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)  # Default to 1 for individual seats
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    show_id = db.Column(db.Integer, db.ForeignKey("show.id"))
    # Seat-specific fields for individual seat tracking
    seat_row = db.Column(db.String(10), nullable=True)      # "A", "B", "C"
    seat_number = db.Column(db.Integer, nullable=True)      # 1, 2, 3...
    seat_id = db.Column(db.String(20), nullable=True)       # "A1", "B2", "C15"
    # Booking metadata
    status = db.Column(db.String(20), nullable=False, default='confirmed')  # confirmed | cancelled
    booked_at = db.Column(db.DateTime, nullable=True)
    ticket_pdf = db.Column(db.String(255), nullable=True)
    # Link to Booking where applicable
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=True)

    __table_args__ = (
        db.Index('ix_ticket_booked_at', 'booked_at'),
        db.Index('ix_ticket_show_id', 'show_id'),
    )


class Booking(db.Model):
    """Persistent Booking entity to support idempotency and two-phase flow."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idempotency_key = db.Column(db.String(128), unique=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    reservation_id = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='reserved')  # reserved | confirmed | cancelled
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('bookings', lazy='dynamic'))
    show = db.relationship('Show', backref=db.backref('bookings', lazy='dynamic'))
    tickets = db.relationship('Ticket', backref='booking', lazy='select')


class TheatreSeat(db.Model):
    """Defines the seating layout for each theatre"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    theatre_id = db.Column(db.Integer, db.ForeignKey("theatre.id"), nullable=True)
    screen_id = db.Column(db.Integer, db.ForeignKey('screen.id'), nullable=True)
    row_label = db.Column(db.String(10), nullable=False)    # "A", "B", "C"
    seat_number = db.Column(db.Integer, nullable=False)     # 1, 2, 3...
    seat_type = db.Column(db.String(20), nullable=False, default='regular')  # 'regular', 'premium', 'wheelchair'
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Composite unique constraint to prevent duplicate seats per screen (or per theatre if screen not used)
    __table_args__ = (
        db.UniqueConstraint('screen_id', 'row_label', 'seat_number', name='unique_screen_seat'),
    )

    theatre = db.relationship("Theatre", backref="seats")
    screen = db.relationship('Screen', backref=db.backref('seats', lazy='dynamic'))


class Movie(db.Model):
    """Represents a movie (separate from Show). Allows same movie to run in multiple cities/theatres/screens."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    tmdb_id = db.Column(db.Integer, nullable=True, index=True)
    overview = db.Column(db.Text, nullable=True)
    runtime = db.Column(db.Integer, nullable=True)
    release_date = db.Column(db.String(20), nullable=True)
    tmdb_rating = db.Column(db.Float, nullable=True)
    backdrop = db.Column(db.String(255), nullable=True)

    __table_args__ = (
        db.Index('ix_movie_title', 'title'),
    )


class AuditLog(db.Model):
    """Simple audit log for booking-related events to support observability."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=True)
    action = db.Column(db.String(64), nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('audit_logs', lazy='dynamic'))
    show = db.relationship('Show', backref=db.backref('audit_logs', lazy='dynamic'))
    ticket = db.relationship('Ticket', backref=db.backref('audit_logs', lazy='dynamic'))

    __table_args__ = (
        db.Index('ix_audit_action_created', 'action', 'created_at'),
    )


class Offer(db.Model):
    """Represents a promotional offer or coupon code."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    discount_type = db.Column(db.String(20), nullable=False, default='percent')  # 'percent' or 'amount'
    discount_value = db.Column(db.Float, nullable=False, default=0.0)  # percentage (0-100) or absolute amount
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=True)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatre.id'), nullable=True)
    active = db.Column(db.Boolean, default=True)
    starts_at = db.Column(db.DateTime, nullable=True)
    ends_at = db.Column(db.DateTime, nullable=True)
    usage_limit = db.Column(db.Integer, nullable=True)  # optional global usage cap
    used_count = db.Column(db.Integer, nullable=False, default=0)

    show = db.relationship('Show', backref=db.backref('offers', lazy='dynamic'))
    theatre = db.relationship('Theatre', backref=db.backref('offers', lazy='dynamic'))
