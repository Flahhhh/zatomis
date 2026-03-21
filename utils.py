import secrets
from datetime import datetime

from extensions import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_secret_key(key_size=12):
    return secrets.token_urlsafe(key_size)


def is_float(s: str):
    try:
        float(s)
        return True
    except Exception as e:
        return False


def get_time_stamp():
    dt_obj = datetime(2026, 3, 20)
    return int(dt_obj.timestamp() * 1000)
