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


def init_db(db):
    from models import Role, AccountStatus
    try:
        roles = [Role(id=1, name="KIJ"), Role(id=2, name="SKIJ")]
        for role in roles:
            db.add(role)

        statuses = [AccountStatus(id=1, name="PENDING"), AccountStatus(id=2, name="ACTIVE"),
                    AccountStatus(id=3, name="REJECTED"), AccountStatus(id=4, name="DELETED")]
        for status in statuses:
            db.add(status)
        db.commit()
        db.flush()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
