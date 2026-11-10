from datetime import datetime

from _decimal import Decimal

from zatomis import Request, Response, JSONResponse, TextResponse, MethodNotAllowedError, NotFoundError, \
    BadRequestError, NopeResponse

from models import User, UserApplication, Log, Transaction, Subscription, TransactionStatus
from utils import get_db, generate_secret_key, is_float, get_time_stamp
from extensions import SessionLocal
from zatomis.response import ForbiddenError, InternalError


def index_view(request: Request):
    db = SessionLocal()

    try:
        log = Log(text=request.data, sender=request.sender)
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(e)
        return InternalError()
    finally:
        db.close()
    return 200, "OK"


def test_view(request: Request):
    return NopeResponse()


def account_view(request: Request):
    db = SessionLocal()

    try:
        if not isinstance(request.data, dict):
            return BadRequestError()

        if request.method == "POST":
            if "application_text" not in request.data or "username" not in request.data:
                return BadRequestError()

            if db.query(User).filter(User.username == request.data["username"]).first():
                return ForbiddenError()

            user = User(username=request.data["username"], role_id=1, secret_key=generate_secret_key(),
                        account_status_id=1)
            db.add(user)
            db.commit()

            application = UserApplication(username=request.data["username"], node_adr=request.sender,
                                          text=request.data["application_text"], user_id=user.id)
            db.add(application)
            db.commit()

            return JSONResponse(data=user.to_json(is_secret_key=True), status=202)
        elif request.method == "GET":
            if not isinstance(request.data, dict) or "secret_key" not in request.data:
                return BadRequestError()

            user = db.query(User).filter(User.secret_key == request.data["secret_key"]).first()
            if user is None:
                return NotFoundError()

            return JSONResponse(user.to_json(is_secret_key=True), status=200)

            """
            if "username" not in request.data:
                return BadRequestError()

            application = db.query(UserApplication).filter(UserApplication.username == request.data["username"] and UserApplication.node_adr == request.sender).first()
            if not application:
                return NotFoundError()
            if not application.approved:
                return Response("Wait...", 202)

            new_user = User(username=application.username, role_id=1)
            SessionLocal.add(new_user)

            for application in db.query(UserApplication).filter(UserApplication.username == request.data["username"]):
                SessionLocal.remove(application)
            SessionLocal.commit()

            return 200, new_user.to_json()
            """
        else:
            return MethodNotAllowedError()
    except Exception as e:
        db.rollback()
        print(e)
        return InternalError()
    finally:
        db.close()


def status_view(request: Request):
    db = SessionLocal()

    try:
        if not isinstance(request.data, dict) or "secret_key" not in request:
            return BadRequestError()

        user = db.query(User).filter(User.secret_key == request.data["secret_key"]).first()
        if user is None:
            return NotFoundError()

        return Response({"status": user.account_status.name})
    except Exception as e:
        db.rollback()
        return InternalError()
    finally:
        db.close()


def profile_view(request: Request):
    db = SessionLocal()

    try:
        if not isinstance(request.data, dict) or "secret_key" not in request:
            return BadRequestError()

        user = db.query(User).filter(User.secret_key == request.data["secret_key"]).first()
        if user is None:
            return NotFoundError()

        return JSONResponse(user.to_json())
    except Exception as e:
        db.rollback()
        return InternalError()
    finally:
        db.close()


def balance_view(request: Request):
    db = SessionLocal()

    try:
        if not isinstance(request.data, dict) or "secret_key" not in request:
            return BadRequestError()

        user = db.query(User).filter(User.secret_key == request.data["secret_key"]).first()
        if user is None:
            return NotFoundError()

        return Response(float(user.grubles))
    except Exception as e:
        db.rollback()
        return InternalError()
    finally:
        db.close()


def payment_view(request: Request):
    db = SessionLocal()

    if request.method == "COMMIT":
        try:
            if not isinstance(request.data, dict) or "secret_key" not in request.data:
                return BadRequestError()

            user = db.query(User).filter(User.secret_key == request.data["secret_key"]).first()
            if user is None:
                return NotFoundError()

            if "transactions" in request.data:
                for transaction_id in request.data["transactions"]:
                    if not isinstance(transaction_id, int):
                        continue
                    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
                    if transaction is None:
                        continue

                    transaction.accepted = True

            if "subscriptions" in request.data:
                for subscription_id in request.data["subscriptions"]:
                    if not isinstance(subscription_id, int):
                        continue
                    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
                    if subscription is None:
                        continue

                    subscription.accepted = True

            db.commit()
        except Exception as e:
            db.rollback()
        finally:
            db.close()
    elif request.method == "GET":
        try:
            if not isinstance(request.data, dict) or "secret_key" not in request:
                return BadRequestError()

            user = db.query(User).filter(User.secret_key == request.data["secret_key"]).first()
            if user is None:
                return NotFoundError()

            transactions = db.query(Transaction).filter(
                Transaction.user_id == user.id and not Transaction.accepted).all()
            subscriptions = db.query(Subscription).filter(
                Subscription.user_id == user.id and not Subscription.accepted).all()

            return JSONResponse({"balance": user.grubles, "transactions": transactions, "subscriptions": subscriptions})
        except Exception as e:
            db.rollback()
            return InternalError()
        finally:
            db.close()
    else:
        return MethodNotAllowedError()


def transfer_view(request: Request):
    if request.method != "POST":
        return MethodNotAllowedError()

    db = SessionLocal()

    try:
        if not isinstance(request.data, dict) or "secret_key" not in request.data or "username" not in request.data \
                or "amount" not in request.data or not is_float(request.data["amount"]):
            return BadRequestError()

        user1 = db.query(User).filter(User.secret_key == request.data["secret_key"]).first()
        if user1 is None:
            return NotFoundError()

        user2 = db.query(User).filter(User.username == request.data["username"]).first()
        if user2 is None:
            return NotFoundError()

        amount = Decimal(request.data["amount"])
        if user1.grubles < amount:
            return ForbiddenError()

        time_stamp = get_time_stamp()

        transaction1 = Transaction(text=f"Перевод на счёт {user2.username}", amount=-amount, date=time_stamp,
                                   user_id=user1.id)
        transaction2 = Transaction(text=f"Получено от {user1.username}", amount=amount, date=time_stamp,
                                   user_id=user2.id)
        db.add(transaction1)
        db.add(transaction2)

        user1.grubles -= amount
        user2.grubles += amount

        db.commit()

        return JSONResponse(
            {"balance": float(user1.grubles), "transactions": [transaction1.to_json()]})  # TextResponse("OK")
    except Exception as e:
        db.rollback()
        print(e)
        return InternalError()
    finally:
        db.close()
