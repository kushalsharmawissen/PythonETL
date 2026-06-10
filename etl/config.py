from pathlib import Path
from sqlalchemy.engine.url import URL

ROOT_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT_DIR / "sample_transactions.csv"

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username="user",
    password="password",
    host="127.0.0.1",
    port=3306,
    database="financial_etl",
)

BATCH_SIZE = 100
BASE_CURRENCY = "INR"
DEFAULT_TIMEZONE = "Asia/Kolkata"
