# Financial ETL Pipeline

This repository contains a Python ETL pipeline that ingests a flat financial CSV file, applies cleansing rules, computes derived fields, routes records into tables, and writes data into a MySQL database via SQLAlchemy.

## Files created

- `docker-compose.yaml` — spins up a MySQL 8.0 instance.
- `sample_transactions.csv` — sample source CSV with valid and invalid rows.
- `requirements.txt` — project dependencies.
- `setup_env.bat` — creates the local `uv` environment and installs dependencies.
- `etl/` — Python ETL package.

## Getting started

1. Start MySQL:

```bash
docker-compose up -d
```

2. Install dependencies:

```bash
.\setup_env.bat
```

3. Run the pipeline:

```bash
uv run python -m etl.main
```

## Notes

- The pipeline reads `sample_transactions.csv` by default.
- The pipeline writes to the `financial_etl` database on MySQL.
- You can modify `etl/config.py` to point to a different CSV path or database URL.
