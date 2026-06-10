import re
from decimal import Decimal, InvalidOperation
from datetime import datetime

import pycountry
import pytz
from dateutil import parser

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\d{10}$")
DEFAULT_TIMEZONE = "Asia/Kolkata"


def strip_value(value):
    if value is None:
        return None
    text = str(value).strip()
    return text if text != "" else None


def to_upper(value):
    text = strip_value(value)
    return text.upper() if text else None


def title_case(value):
    text = strip_value(value)
    return text.title() if text else None


def parse_date(value):
    text = strip_value(value)
    if not text:
        return None
    try:
        return parser.parse(text, dayfirst=False).date()
    except Exception:
        return None


def parse_time(value):
    text = strip_value(value)
    if not text:
        return None
    try:
        return parser.parse(text).time().strftime("%H:%M:%S")
    except Exception:
        return None


def parse_decimal(value):
    text = strip_value(value)
    if not text:
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def parse_int(value):
    text = strip_value(value)
    if not text:
        return None
    try:
        return int(Decimal(text))
    except Exception:
        return None


def validate_email(value):
    text = strip_value(value)
    if not text:
        return None
    candidate = text.lower()
    return candidate if EMAIL_RE.match(candidate) else None


def normalize_phone(value):
    text = strip_value(value)
    if not text:
        return None
    digits = re.sub(r"[^0-9]", "", text)
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    return digits if PHONE_RE.match(digits) else None


def validate_currency(value):
    text = to_upper(value)
    if not text:
        return None
    try:
        if pycountry.currencies.get(alpha_3=text):
            return text
    except Exception:
        pass
    return None


def validate_country(value):
    text = to_upper(value)
    if not text:
        return None
    try:
        if pycountry.countries.get(alpha_2=text):
            return text
    except Exception:
        pass
    return None


def validate_timezone(value):
    text = strip_value(value)
    if not text:
        return DEFAULT_TIMEZONE
    if text in pytz.all_timezones:
        return text
    return DEFAULT_TIMEZONE


def raw_record_from_dict(raw):
    return ",".join(str(raw.get(key, "")) for key in raw.keys())
