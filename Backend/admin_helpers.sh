#!/usr/bin/env bash
# Helper script to fetch an admin token and upload CSVs to the backend
# Usage:
#   ./admin_helpers.sh token USERNAME PASSWORD
#   ./admin_helpers.sh upload-shows PATH_TO_CSV
#   ./admin_helpers.sh upload-seats THEATRE_ID PATH_TO_CSV
#   ./admin_helpers.sh timeseries

API_HOST=${API_HOST:-http://127.0.0.1:5001}
TOKEN_FILE=".admin_token"

function fetch_token() {
  local username="$1"
  local password="$2"
  if [ -z "$username" ] || [ -z "$password" ]; then
    echo "Usage: $0 token USERNAME PASSWORD"
    return 1
  fi

  echo "Fetching token for $username..."
  resp=$(curl -s -X POST -H "Content-Type: application/json" -d "{\"username\":\"$username\",\"password\":\"$password\"}" "$API_HOST/login")
  token=$(echo "$resp" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null)
  if [ -z "$token" ]; then
    echo "Failed to retrieve token. Response:" >&2
    echo "$resp" >&2
    return 2
  fi
  echo "$token" > "$TOKEN_FILE"
  export ADMIN_TOKEN="$token"
  echo "Token saved to $TOKEN_FILE and exported as ADMIN_TOKEN"
}

function load_token() {
  if [ -z "$ADMIN_TOKEN" ] && [ -f "$TOKEN_FILE" ]; then
    export ADMIN_TOKEN=$(cat "$TOKEN_FILE")
  fi
}

function upload_shows() {
  local path="$1"
  if [ -z "$path" ] || [ ! -f "$path" ]; then
    echo "Path to CSV is required and must exist: $path" >&2
    return 1
  fi
  load_token
  if [ -z "$ADMIN_TOKEN" ]; then echo "No ADMIN_TOKEN set. Run: $0 token USERNAME PASSWORD" >&2; return 2; fi
  echo "Uploading shows from $path..."
  curl -v -X POST -H "Authorization: Bearer $ADMIN_TOKEN" -F file=@"$path" "$API_HOST/admin/shows/import"
}

function upload_seats() {
  local theatre_id="$1"
  local path="$2"
  if [ -z "$theatre_id" ] || [ -z "$path" ] || [ ! -f "$path" ]; then
    echo "Usage: $0 upload-seats THEATRE_ID PATH_TO_CSV" >&2
    return 1
  fi
  load_token
  if [ -z "$ADMIN_TOKEN" ]; then echo "No ADMIN_TOKEN set. Run: $0 token USERNAME PASSWORD" >&2; return 2; fi
  echo "Uploading seats for theatre $theatre_id from $path..."
  curl -v -X POST -H "Authorization: Bearer $ADMIN_TOKEN" -F file=@"$path" "$API_HOST/admin/theatres/$theatre_id/seats/import"
}

function timeseries() {
  load_token
  if [ -z "$ADMIN_TOKEN" ]; then echo "No ADMIN_TOKEN set. Run: $0 token USERNAME PASSWORD" >&2; return 2; fi
  curl -v -H "Authorization: Bearer $ADMIN_TOKEN" "$API_HOST/admin/stats/timeseries?since_days=30"
}

case "$1" in
  token)
    fetch_token "$2" "$3"
    ;;
  upload-shows)
    upload_shows "$2"
    ;;
  upload-seats)
    upload_seats "$2" "$3"
    ;;
  timeseries)
    timeseries
    ;;
  *)
    echo "Usage: $0 {token USERNAME PASSWORD|upload-shows PATH|upload-seats THEATRE_ID PATH|timeseries}"
    exit 1
    ;;
esac
