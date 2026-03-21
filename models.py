from enum import Enum

from sqlalchemy import Column, Integer, BigInteger, String, Text, text, ForeignKey, Boolean, Double, DECIMAL, \
    Date, Time, func
from sqlalchemy.orm import declarative_base, relationship

from extensions import engine

Base = declarative_base()


class Permission(Base):
    __tablename__ = 'permission'
    name = Column(String(255), primary_key=True)

    def __repr__(self):
        return self.name


class PermissionRole(Base):
    __tablename__ = 'permission_role'
    permission_id = Column(String(255), ForeignKey('permission.name'), primary_key=True)
    role_id = Column(Integer, ForeignKey('role.id'), primary_key=True)

    permission = relationship("Permission", backref="roles")
    role = relationship("Role", backref="permissions")


class PermissionUser(Base):
    __tablename__ = 'permission_user'
    permission_id = Column(String(255), ForeignKey('permission.name'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    permission = relationship("Permission", backref="users")
    user = relationship("User", backref="permissions")


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    is_admin = Column(Boolean, default=False)

    def __repr__(self):
        return self.name


class AccountStatus(Base):
    __tablename__ = "account_status"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))  # 1 -> Pending; 2 -> Active; 3 -> Rejected; 4 -> Deleted


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), default="")
    name = Column(String(255), default="")
    second_name = Column(String(255), default="")
    last_name = Column(String(255), default="")
    secret_key = Column(String(255))
    grubles = Column(DECIMAL(20, 10), default=0)

    account_status_id = Column(Integer, ForeignKey("account_status.id"))
    account_status = relationship("AccountStatus", backref="users")

    role_id = Column(Integer, ForeignKey('role.id'))
    role = relationship("Role", backref="users")

    applications = relationship("UserApplication", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")

    def get_permissions(self):
        return []

    def to_json(self, is_secret_key=False):
        r = {
            "user_id": self.id,
            "username": self.username,
            "grubles": float(self.grubles),
            "name": self.name,
            "second_name": self.second_name,
            "last_name": self.last_name,
            "role": self.role.name,
            "permissions": self.get_permissions(),
            "status": self.account_status.name
        }

        if is_secret_key:
            r["secret_key"] = self.secret_key

        return r

    def __repr__(self):
        return f"{self.username}_{self.id}"


class TransactionStatus(Enum):
    SUCCESSFUL = 0
    ERROR = 1
    DENIED = 2


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True)
    text = Column(String(255))
    date = Column(BigInteger)
    amount = Column(Double)
    status = Column(Integer, default=TransactionStatus.SUCCESSFUL.value)
    accepted = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="transactions")

    def to_json(self):
        return {"id": self.id, "text": self.text, "date": self.date, "amount": self.amount, "userId": self.user_id}


class SubscriptionStatus(Enum):
    SUCCESSFUL = 0
    ERROR = 1
    DENIED = 2


class Subscription(Base):
    __tablename__ = "subscription"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    expiringDate = Column(BigInteger)
    price = Column(Double)
    status = Column(Integer, default=SubscriptionStatus.SUCCESSFUL)
    accepted = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="subscriptions")


class Log(Base):
    __tablename__ = "log"

    id = Column(BigInteger, primary_key=True)
    date = Column(Date, default=func.current_date())
    time = Column(Time, default=func.current_time())
    text = Column(String(255))
    sender = Column(String(255))


class TGChat(Base):
    __tablename__ = "tg_chat"

    id = Column(BigInteger, primary_key=True)
    messages = relationship("TGMessage", back_populates="chat")

    def __repr__(self):
        return f"chat_{self.chat_id}"


class TGMessage(Base):
    __tablename__ = 'tg_message'

    id = Column(Integer, primary_key=True)
    # chat_id = Column(BigInteger)
    message_id = Column(Integer)

    text = Column(Text)
    role_name = Column(String(255))

    # chat = relationship("TGChats")
    chat_id = Column(BigInteger, ForeignKey('tg_chat.id'))
    chat = relationship("TGChat", back_populates="messages")

    def __repr__(self):
        return f"message_{self.id}"


class UserApplication(Base):
    __tablename__ = "user_application"

    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    node_adr = Column(String(255))
    text = Column(String(500))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="applications")

    approved = Column(Boolean, default=False)

    def __repr__(self):
        return f"application_{self.id}"


Base.metadata.create_all(engine)
