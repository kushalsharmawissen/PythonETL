from datetime import datetime

import pandas as pd

from etl.config import CSV_PATH
from etl.loader import (
    Session,
    create_tables,
    get_or_create_account,
    get_or_create_customer,
    get_or_create_merchant,
    insert_failed,
    insert_transaction,
)
from etl.models import Transaction
from etl.transform import cleanse_row, derive_fields


def load_csv():
    df = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)
    return df.fillna("")


def run():
    create_tables()
    df = load_csv()
    processed = 0
    failed = 0
    duplicate = 0

    with Session() as session:
        for index, row in df.iterrows():
            raw = row.to_dict()
            cleaned, errors = cleanse_row(raw)
            if errors:
                error = errors[0]
                insert_failed(session, raw, error["error_type"], error["error_field"], error["error_reason"])
                failed += 1
                continue

            if cleaned["status"] in {"FAILED", "PENDING"}:
                insert_failed(session, raw, "ROUTE_FILTER", "status", f"Record status is {cleaned['status']}.")
                failed += 1
                continue

            existing = session.get(Transaction, cleaned["transaction_id"])
            if existing:
                duplicate += 1
                continue

            derived = derive_fields(cleaned)
            customer, _ = get_or_create_customer(session, derived)
            account, _ = get_or_create_account(session, derived)
            merchant, _ = get_or_create_merchant(session, derived)
            derived["is_new_customer"] = "Y" if customer else "N"
            insert_transaction(session, derived, merchant.merchant_id)
            processed += 1

        session.commit()

    print(f"Processed rows: {processed}")
    print(f"Failed rows: {failed}")
    print(f"Duplicate transaction IDs skipped: {duplicate}")


if __name__ == "__main__":
    run()
