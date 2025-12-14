# backend/run.py
import os
import base64
from io import BytesIO
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# If eventlet is available, monkey-patch the stdlib as early as possible
# to ensure compatibility with Flask-SocketIO. This must happen before
# importing modules that create threads or rely on blocking stdlib calls.
try:
    import eventlet
    eventlet.monkey_patch()
except Exception:
    # eventlet not installed or monkey-patch failed; we'll attempt a
    # graceful fallback later when starting the server.
    pass

from flask import Flask, jsonify, send_from_directory
from flask_restful import Api
from flask_cors import CORS
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for thread safety
import matplotlib.pyplot as plt

from config import Config
from extensions import init_extensions, init_celery, celery
from sockets import init_socketio
from resources import register_resources
from models import User, Role, Theatre, Show, ShowRating, Ticket  # ensure models imported
import tasks  # Import tasks to register with Celery
import click

app = Flask(__name__)
app.config.from_object(Config)

# Configure basic logging so `logger.exception` and other logs appear in server.log
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

# ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

api = Api(app)


# Enable CORS for frontend origins (development - allow all for flexibility)
CORS(app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])


# Remove after_request CORS header injection to avoid duplicate/multiple origins

init_extensions(app)
init_celery(app)
# Initialize optional subsystems based on feature flags
feature_flags = getattr(app.config, 'FEATURE_FLAGS', None) or app.config.get('FEATURE_FLAGS', {})
if feature_flags.get('websocket_updates', False):
    socketio = init_socketio(app)
else:
    socketio = None

# Initialize Redis cache with show capacities
def init_redis_cache():
    """Initialize Redis cache with current show capacities"""
    try:
        from models import Show
        from cache.seat_cache import seat_cache
        
        with app.app_context():
            shows = Show.query.all()
            for show in shows:
                seat_cache.set_show_capacity(show.id, show.capacity)
                print(f"Initialized cache for show {show.id}: capacity {show.capacity}")
    except Exception as e:
        print(f"Failed to initialize Redis cache: {e}")

# Skip Redis/cache initialization during migrations or when explicitly requested.
# This avoids querying the database for columns that may be added by migrations
# while the Alembic/Flask-Migrate command is running.

    # (Redis cache initialization moved to __main__ after migrations)

register_resources(api, app)


@app.route("/")
def home():
    return "Welcome to the homepage"


# Ensure CORS headers are always present (defensive for error responses)
@app.after_request
def add_cors_headers(response):
    response.headers.setdefault('Access-Control-Allow-Origin', '*')
    response.headers.setdefault('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.setdefault('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response

# Serve uploaded files
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    upload_folder = app.config.get('UPLOAD_FOLDER')
    return send_from_directory(upload_folder, filename)


# CLI: create admin
@app.cli.command("create_admin")
@click.argument("username")
@click.argument("password")
def create_admin(username, password):
    from extensions import db
    from models import Role, User

    with app.app_context():
        db.create_all()
        admin_role = Role.query.filter_by(name="admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator role")
            db.session.add(admin_role)
            db.session.commit()

        admin_user = User.query.filter_by(username=username).first()
        if not admin_user:
            admin_user = User(username=username, is_admin=True)
            admin_user.set_password(password)
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")


# Popularity graph endpoint
@app.route("/popularity_graph_image", methods=["GET"])
def popularity_graph_image():
    from models import Show

    shows = Show.query.all()
    show_names = [show.name for show in shows]
    ratings = [show.rating or 0 for show in shows]

    plt.figure(figsize=(9, 4))
    bars = plt.bar(show_names, ratings)

    plt.xlabel("Shows", fontsize=14)
    plt.ylabel("Ratings", fontsize=14)
    plt.title("Show Popularity Based on Ratings", fontsize=16)

    for bar, rating in zip(bars, ratings):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() - 0.5,
            str(rating),
            ha="center",
            fontsize=9,
        )

    plt.xticks(rotation=45, ha="right", fontsize=12)
    plt.subplots_adjust(bottom=0.2)

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format="png")
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode()
    plt.close()

    data_uri = "data:image/png;base64," + img_base64
    return jsonify(data_uri)

@app.cli.command("seed_shows")
def seed_shows():
    """Seed the database with a sample theatre and a few shows."""
    from extensions import db
    from datetime import datetime, timedelta

    with app.app_context():
        db.create_all()

        theatre = Theatre.query.first()
        if not theatre:
            theatre = Theatre(name="NovaSeat Main", place="City Center", capacity=150)
            db.session.add(theatre)
            db.session.commit()

        sample = [
            {
                "name": "Dune: Part Two",
                "tags": "movie, sci-fi",
                "ticket_price": 350.0,
            },
            {
                "name": "Inside Out 2",
                "tags": "movie, animation",
                "ticket_price": 300.0,
            },
            {
                "name": "Arijit Singh Live",
                "tags": "concert, music",
                "ticket_price": 800.0,
            },
            {
                "name": "Hamlet",
                "tags": "play, theatre",
                "ticket_price": 500.0,
            },
            {
                "name": "Tech Expo",
                "tags": "event, expo",
                "ticket_price": 200.0,
            },
        ]

        now = datetime.utcnow()
        created = 0
        for item in sample:
            exists = Show.query.filter_by(name=item["name"]).first()
            if exists:
                continue
            show = Show(
                name=item["name"],
                start_time=now + timedelta(days=1),
                end_time=now + timedelta(days=1, hours=2),
                tags=item["tags"],
                ticket_price=item["ticket_price"],
                image=None,
                theatre_id=theatre.id,
                capacity=int(theatre.capacity),
            )
            db.session.add(show)
            created += 1

        db.session.commit()
        print(f"Seeded {created} shows.")


if __name__ == "__main__":
    # Auto-run DB migrations on startup (before any DB/cache/Redis access)
    try:
        from extensions import db
        from flask_migrate import upgrade
        with app.app_context():
            upgrade()
        print("[INFO] Database migrations applied successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to apply migrations: {e}")

    # Now safe to initialize Redis cache, etc.
    if os.environ.get("SKIP_CACHE_INIT", "0") != "1":
        init_redis_cache()

    # If Socket.IO was initialized, run the app via Socket.IO's runner
    # which will use the configured async mode (eventlet by default).
    if socketio:
        try:
            import eventlet
            # Monkey-patch sockets/threads for eventlet compatibility
            try:
                eventlet.monkey_patch()
            except Exception:
                pass
        except Exception:
            pass
        # Disable the Flask reloader when running via Socket.IO to avoid
        # the reloader spawning a child process which attempts to bind the
        # same port again (causes "Address already in use").
        socketio.run(app, debug=True, host='0.0.0.0', port=5001, use_reloader=False)
    else:
        app.run(debug=True, host='0.0.0.0', port=5001)
