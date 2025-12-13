Admin helpers and quick guide

This folder contains helper scripts to make admin testing easier.

Files:
- `admin_helpers.sh` — Bash helper to fetch an admin token and upload CSVs.
- `shows_sample.csv` — Sample shows CSV (already present).
- `seats_sample.csv` — Sample seats CSV (already present).

Quick start:

1. Make the script executable:

```bash
cd Backend
chmod +x admin_helpers.sh
```

2. Fetch a token and save it locally (replace credentials):

```bash
./admin_helpers.sh token admin admin123
```

3. Upload sample shows:

```bash
./admin_helpers.sh upload-shows shows_sample.csv
```

4. Upload sample seats for theatre 1:

```bash
./admin_helpers.sh upload-seats 1 seats_sample.csv
```

5. Call timeseries stats:

```bash
./admin_helpers.sh timeseries
```

If you prefer direct curl commands, ensure you export the token as `ADMIN_TOKEN` before using `-H "Authorization: Bearer $ADMIN_TOKEN"`.
