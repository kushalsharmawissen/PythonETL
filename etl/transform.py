from datetime import datetime, time
from decimal import Decimal

import pytz

from etl.config import BASE_CURRENCY, DEFAULT_TIMEZONE
from etl.utils import (
    parse_date,
    parse_decimal,
    parse_int,
    parse_time,
    strip_value,
    to_upper,
    title_case,
    validate_country,
    validate_currency,
    validate_email,
    normalize_phone,
    validate_timezone,
)

CHANNEL_MAP = {
    "WEB": "DIGITAL",
    "MOBILE": "DIGITAL",
    "ATM": "PHYSICAL",
    "BRANCH": "PHYSICAL",
    "POS": "PHYSICAL",
    "CALL_CENTER": "OTHER",
    "PHONE": "OTHER",
}

TRANSACTION_TYPE_MAP = {
    "PAYMENT": "PAYMENT",
    "REFUND": "REFUND",
    "REVERSAL": "REVERSAL",
    "TRANSFER": "TRANSFER",
}

STATUS_MAP = {
    "SUCCESS": "SUCCESS",
    "FAILED": "FAILED",
    "PENDING": "PENDING",
}

PAYMENT_METHOD_MAP = {
    "CREDIT_CARD": "CREDIT_CARD",
    "DEBIT_CARD": "DEBIT_CARD",
    "NET_BANKING": "NET_BANKING",
    "UPI": "UPI",
    "WALLET": "WALLET",
    "CHEQUE": "CHEQUE",
    "CASH": "CASH",
}

ACCOUNT_TYPE_MAP = {
    "SAVINGS": "SAVINGS",
    "CURRENT": "CURRENT",
    "LOAN": "LOAN",
    "CREDIT": "CREDIT",
}

CUSTOMER_SEGMENT_MAP = {
    "RETAIL": "RETAIL",
    "CORPORATE": "CORPORATE",
    "WEALTH": "WEALTH",
    "NRI": "NRI",
    "HNI": "HNI",
}

RECURRING_MAP = {
    "Y": "Y",
    "YES": "Y",
    "N": "N",
    "NO": "N",
}

DEFAULT_DIMENSION_VALUE = "UNKNOWN"


def normalize_enum(value, mapping, default=None):
    if not value:
        return default
    candidate = to_upper(value).replace(" ", "_")
    return mapping.get(candidate, default)


def bucket_amount(value):
    if value is None:
        return "UNKNOWN"
    if value < Decimal("1000"):
        return "LOW"
    if value < Decimal("10000"):
        return "MEDIUM"
    if value < Decimal("100000"):
        return "HIGH"
    return "VERY_HIGH"


def compute_rewards_tier(points):
    if points is None:
        return "NONE"
    if points >= 10000:
        return "PLATINUM"
    if points >= 5000:
        return "GOLD"
    if points >= 1000:
        return "SILVER"
    return "BRONZE"


def compute_local_timestamp(date_obj, time_str, timezone_str):
    if not date_obj or not time_str:
        return None
    naive = datetime.strptime(f"{date_obj.isoformat()} {time_str}", "%Y-%m-%d %H:%M:%S")
    utc = pytz.utc.localize(naive)
    target_tz = pytz.timezone(validate_timezone(timezone_str))
    return utc.astimezone(target_tz)


def cleanse_row(raw):
    errors = []
    cleaned = {}

    cleaned["transaction_id"] = strip_value(raw.get("transaction_id"))
    if not cleaned["transaction_id"]:
        errors.append({"error_type": "MISSING_VALUE", "error_field": "transaction_id", "error_reason": "Transaction ID is required."})

    cleaned["transaction_date"] = parse_date(raw.get("transaction_date"))
    if not cleaned["transaction_date"]:
        errors.append({"error_type": "INVALID_VALUE", "error_field": "transaction_date", "error_reason": "Invalid or missing transaction date."})

    cleaned["transaction_time"] = parse_time(raw.get("transaction_time")) or "00:00:00"
    cleaned["transaction_channel"] = strip_value(raw.get("transaction_channel")) or DEFAULT_DIMENSION_VALUE
    cleaned["channel_category"] = CHANNEL_MAP.get(cleaned["transaction_channel"], "OTHER")
    cleaned["currency"] = validate_currency(raw.get("currency")) or BASE_CURRENCY
    if not validate_currency(raw.get("currency")):
        errors.append({"error_type": "INVALID_VALUE", "error_field": "currency", "error_reason": "Unsupported currency code; defaulting to base currency."})

    cleaned["amount_raw"] = parse_decimal(raw.get("amount_raw"))
    if cleaned["amount_raw"] is None or cleaned["amount_raw"] <= 0:
        errors.append({"error_type": "INVALID_VALUE", "error_field": "amount_raw", "error_reason": "Amount must be a positive decimal."})

    cleaned["exchange_rate"] = parse_decimal(raw.get("exchange_rate")) or Decimal("1.0000")
    cleaned["transaction_type"] = normalize_enum(raw.get("transaction_type"), TRANSACTION_TYPE_MAP, default="PAYMENT")
    cleaned["payment_method"] = normalize_enum(raw.get("payment_method"), PAYMENT_METHOD_MAP, default="OTHER")
    cleaned["is_recurring"] = RECURRING_MAP.get(to_upper(raw.get("is_recurring")), "N")
    cleaned["status"] = normalize_enum(raw.get("status"), STATUS_MAP, default="PENDING")
    cleaned["merchant_name"] = title_case(raw.get("merchant_name")) or DEFAULT_DIMENSION_VALUE
    cleaned["merchant_city"] = title_case(raw.get("merchant_city")) or DEFAULT_DIMENSION_VALUE
    cleaned["merchant_country"] = validate_country(raw.get("merchant_country")) or "IN"
    cleaned["category"] = title_case(raw.get("category")) or DEFAULT_DIMENSION_VALUE
    cleaned["sub_category"] = title_case(raw.get("sub_category")) or DEFAULT_DIMENSION_VALUE
    cleaned["notes"] = strip_value(raw.get("notes")) or ""
    cleaned["customer_id"] = strip_value(raw.get("customer_id")) or DEFAULT_DIMENSION_VALUE
    cleaned["customer_name"] = title_case(raw.get("customer_name")) or DEFAULT_DIMENSION_VALUE
    cleaned["customer_email"] = validate_email(raw.get("customer_email"))
    if raw.get("customer_email") and not cleaned["customer_email"]:
        errors.append({"error_type": "INVALID_VALUE", "error_field": "customer_email", "error_reason": "Customer email is not valid."})

    cleaned["customer_phone"] = normalize_phone(raw.get("customer_phone"))
    if raw.get("customer_phone") and not cleaned["customer_phone"]:
        errors.append({"error_type": "INVALID_VALUE", "error_field": "customer_phone", "error_reason": "Customer phone is not valid."})

    cleaned["customer_segment"] = normalize_enum(raw.get("customer_segment"), CUSTOMER_SEGMENT_MAP, default="RETAIL")
    cleaned["customer_timezone"] = validate_timezone(raw.get("customer_timezone"))
    cleaned["rewards_points_earned"] = parse_int(raw.get("rewards_points_earned")) or 0
    cleaned["account_id"] = strip_value(raw.get("account_id")) or DEFAULT_DIMENSION_VALUE
    cleaned["account_type"] = normalize_enum(raw.get("account_type"), ACCOUNT_TYPE_MAP, default="SAVINGS")
    cleaned["balance_before"] = parse_decimal(raw.get("balance_before")) or Decimal("0.00")
    cleaned["balance_after"] = parse_decimal(raw.get("balance_after")) or Decimal("0.00")
    cleaned["location_latitude"] = parse_decimal(raw.get("location_latitude"))
    cleaned["location_longitude"] = parse_decimal(raw.get("location_longitude"))

    return cleaned, errors


def derive_fields(cleaned):
    derived = dict(cleaned)
    derived["transaction_month"] = cleaned["transaction_date"].month if cleaned["transaction_date"] else None
    quarter = ((derived["transaction_month"] - 1) // 3) + 1 if derived["transaction_month"] else None
    derived["transaction_quarter"] = f"Q{quarter}" if quarter else None
    derived["amount_base_currency"] = (cleaned["amount_raw"] * cleaned["exchange_rate"]).quantize(Decimal("0.01"))
    derived["amount_band"] = bucket_amount(derived["amount_base_currency"])
    derived["is_high_value"] = "Y" if derived["amount_base_currency"] and derived["amount_base_currency"] > Decimal("100000") else "N"
    derived["is_international"] = "Y" if cleaned["merchant_country"] and cleaned["merchant_country"] != "IN" else "N"
    derived["is_null_merchant"] = "Y" if cleaned["merchant_name"] == DEFAULT_DIMENSION_VALUE else "N"
    derived["is_weekend"] = "Y" if cleaned["transaction_date"] and cleaned["transaction_date"].weekday() in (5, 6) else "N"
    derived["local_transaction_time"] = compute_local_timestamp(
        cleaned["transaction_date"], cleaned["transaction_time"], cleaned["customer_timezone"],
    )
    derived["rewards_tier"] = compute_rewards_tier(cleaned["rewards_points_earned"])
    derived["load_timestamp"] = datetime.utcnow()
    return derived
