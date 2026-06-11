from datetime import datetime, date, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from etl.config import DATABASE_URL
from etl.models import (
    Account,
    Customer,
    FailedTransaction,
    Merchant,
    Transaction,
    Base,
)
from etl.utils import raw_record_from_dict

engine = create_engine(DATABASE_URL, echo=False, future=True)
Session = sessionmaker(bind=engine, future=True)


def create_tables():
    Base.metadata.create_all(engine)


def insert_failed(session, raw, error_type, error_field, error_reason):
    load_timestamp = datetime.now(timezone.utc)
    failed = FailedTransaction(
        transaction_id=raw.get("transaction_id"),
        transaction_date=raw.get("transaction_date"),
        account_id=raw.get("account_id"),
        customer_id=raw.get("customer_id"),
        amount_raw=raw.get("amount_raw"),
        status=raw.get("status"),
        error_type=error_type,
        error_field=error_field,
        error_reason=error_reason,
        raw_record=raw_record_from_dict(raw),
        load_timestamp=load_timestamp,
    )
    session.add(failed)


def get_or_create_customer(session, cleaned):
    existing = session.get(Customer, cleaned["customer_id"])
    now = datetime.now(timezone.utc)

    if existing:
        changed = (
            existing.customer_name != cleaned["customer_name"]
            or existing.customer_email != cleaned["customer_email"]
            or existing.customer_phone != cleaned["customer_phone"]
            or existing.customer_segment != cleaned["customer_segment"]
            or existing.customer_timezone != cleaned["customer_timezone"]
            or existing.rewards_points_earned != cleaned["rewards_points_earned"]
        )
        if changed:
            existing.customer_name = cleaned["customer_name"]
            existing.customer_email = cleaned["customer_email"]
            existing.customer_phone = cleaned["customer_phone"]
            existing.customer_segment = cleaned["customer_segment"]
            existing.customer_timezone = cleaned["customer_timezone"]
            existing.rewards_points_earned = cleaned["rewards_points_earned"]
            existing.rewards_tier = cleaned["rewards_tier"]
            existing.effective_date = date.today()
            existing.is_active = "Y"
            existing.load_timestamp = now
            session.flush()
            return existing, True
        return existing, False

    customer = Customer(
        customer_id=cleaned["customer_id"],
        customer_name=cleaned["customer_name"],
        customer_email=cleaned["customer_email"],
        customer_phone=cleaned["customer_phone"],
        customer_segment=cleaned["customer_segment"],
        customer_timezone=cleaned["customer_timezone"],
        rewards_points_earned=cleaned["rewards_points_earned"],
        rewards_tier=cleaned["rewards_tier"],
        effective_date=date.today(),
        is_active="Y",
        load_timestamp=now,
    )
    session.add(customer)
    session.flush()
    return customer, True


def get_or_create_account(session, cleaned):
    existing = session.get(Account, cleaned["account_id"])
    now = datetime.now(timezone.utc)

    if existing:
        changed = existing.account_type != cleaned["account_type"]
        if changed:
            existing.account_type = cleaned["account_type"]
            existing.customer_id = cleaned["customer_id"]
            existing.effective_date = date.today()
            existing.is_active = "Y"
            existing.load_timestamp = now
            session.flush()
            return existing, True
        return existing, False

    account = Account(
        account_id=cleaned["account_id"],
        account_type=cleaned["account_type"],
        customer_id=cleaned["customer_id"],
        effective_date=date.today(),
        is_active="Y",
        load_timestamp=now,
    )
    session.add(account)
    session.flush()
    return account, True


def get_or_create_merchant(session, cleaned):
    stmt = select(Merchant).where(
        Merchant.merchant_name == cleaned["merchant_name"],
        Merchant.merchant_city == cleaned["merchant_city"],
        Merchant.merchant_country == cleaned["merchant_country"],
    )
    merchant = session.execute(stmt).scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if merchant:
        return merchant, False

    merchant = Merchant(
        merchant_name=cleaned["merchant_name"],
        merchant_city=cleaned["merchant_city"],
        merchant_country=cleaned["merchant_country"],
        category=cleaned["category"],
        sub_category=cleaned["sub_category"],
        is_international=cleaned["is_international"],
        load_timestamp=now,
    )
    session.add(merchant)
    session.flush()
    return merchant, True


def insert_transaction(session, derived, merchant_id):
    transaction = Transaction(
        transaction_id=derived["transaction_id"],
        transaction_date=derived["transaction_date"],
        transaction_time=derived["transaction_time"],
        transaction_channel=derived["transaction_channel"],
        channel_category=derived["channel_category"],
        currency=derived["currency"],
        amount_raw=derived["amount_raw"],
        exchange_rate=derived["exchange_rate"],
        amount_base_currency=derived["amount_base_currency"],
        amount_band=derived["amount_band"],
        is_high_value=derived["is_high_value"],
        transaction_type=derived["transaction_type"],
        payment_method=derived["payment_method"],
        is_recurring=derived["is_recurring"],
        status=derived["status"],
        is_international=derived["is_international"],
        is_null_merchant=derived["is_null_merchant"],
        is_weekend=derived["is_weekend"],
        local_transaction_time=derived["local_transaction_time"],
        is_new_customer=derived.get("is_new_customer", "N"),
        notes=derived["notes"],
        customer_id=derived["customer_id"],
        account_id=derived["account_id"],
        merchant_id=merchant_id,
        load_timestamp=derived["load_timestamp"],
    )
    session.add(transaction)
