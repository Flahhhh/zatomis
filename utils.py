import secrets
import time
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
    return int(time.time() * 1000)
