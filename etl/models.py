from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customer"

    customer_id = Column(String(30), primary_key=True)
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(150))
    customer_phone = Column(String(15))
    customer_segment = Column(String(30))
    customer_timezone = Column(String(50))
    rewards_points_earned = Column(Integer, nullable=False, default=0)
    rewards_tier = Column(String(20))
    effective_date = Column(Date, nullable=False)
    is_active = Column(String(1), nullable=False, default="Y")
    load_timestamp = Column(DateTime, nullable=False)

class Account(Base):
    __tablename__ = "account"

    account_id = Column(String(30), primary_key=True)
    account_type = Column(String(20))
    customer_id = Column(String(30), ForeignKey("customer.customer_id"))
    effective_date = Column(Date, nullable=False)
    is_active = Column(String(1), nullable=False, default="Y")
    load_timestamp = Column(DateTime, nullable=False)

class Merchant(Base):
    __tablename__ = "merchant"

    merchant_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_name = Column(String(150), nullable=False)
    merchant_city = Column(String(80), nullable=False)
    merchant_country = Column(String(3), nullable=False)
    category = Column(String(60))
    sub_category = Column(String(60))
    is_international = Column(String(1), nullable=False)
    load_timestamp = Column(DateTime, nullable=False)

class Transaction(Base):
    __tablename__ = "transaction"

    transaction_id = Column(String(50), primary_key=True)
    transaction_date = Column(Date, nullable=False)
    transaction_time = Column(String(8), nullable=False)
    transaction_channel = Column(String(30))
    channel_category = Column(String(20))
    currency = Column(String(5), nullable=False)
    amount_raw = Column(Numeric(18, 2), nullable=False)
    exchange_rate = Column(Numeric(10, 4), nullable=False)
    amount_base_currency = Column(Numeric(18, 2), nullable=False)
    amount_band = Column(String(15))
    is_high_value = Column(String(1))
    transaction_type = Column(String(10), nullable=False)
    payment_method = Column(String(30))
    is_recurring = Column(String(1))
    status = Column(String(10), nullable=False)
    is_international = Column(String(1))
    is_null_merchant = Column(String(1))
    is_weekend = Column(String(1))
    local_transaction_time = Column(DateTime)
    is_new_customer = Column(String(1))
    notes = Column(Text)
    customer_id = Column(String(30), ForeignKey("customer.customer_id"))
    account_id = Column(String(30), ForeignKey("account.account_id"))
    merchant_id = Column(BigInteger, ForeignKey("merchant.merchant_id"))
    load_timestamp = Column(DateTime, nullable=False)

class FailedTransaction(Base):
    __tablename__ = "failed_transactions"

    error_sk = Column(BigInteger, primary_key=True, autoincrement=True)
    transaction_id = Column(String(50))
    transaction_date = Column(Date)
    account_id = Column(String(30))
    customer_id = Column(String(30))
    amount_raw = Column(Numeric(18, 2))
    status = Column(String(10))
    error_type = Column(String(50), nullable=False)
    error_field = Column(String(60))
    error_reason = Column(String(255))
    raw_record = Column(Text, nullable=False)
    load_timestamp = Column(DateTime, nullable=False)
