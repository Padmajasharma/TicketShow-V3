# Example commands to run Postgres and Redis locally (macOS)

# Start Postgres (if using Homebrew)
brew services start postgresql
# Create DB (if not exists)
createdb ticketshow

# Start Redis (if using Homebrew)
brew services start redis

# Verify Postgres connection
psql -U postgres -d ticketshow -h localhost -c '\dt'

# Verify Redis connection
redis-cli ping

# Generate a Flask SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(48))"

# Example: Run backend with .env
export $(grep -v '^#' Backend/.env | xargs) && cd Backend && flask run

# Example: Run DB migrations (if you have shell access)
flask db upgrade

# Example: Seed shows (if you have shell access)
flask seed_shows
