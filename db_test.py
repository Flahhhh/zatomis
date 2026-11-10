from models import AccountStatus, Role, Log, User, UserApplication
from extensions import SessionLocal
db = SessionLocal()


"""
status = AccountStatus(id=1, name="PENDING")
db.add(status)
status = AccountStatus(id=2, name="ACTIVE")
db.add(status)
status = AccountStatus(id=3, name="REJECTED")
db.add(status)
status = AccountStatus(id=4, name="DELETED")
db.add(status)
db.commit()



role = Role(id=1, name="KIJ")
db.add(role)
role = Role(id=2, name="SKIJ")
db.add(role)
role = Role(id=11, name="Predictor-Corrector")
db.add(role)
db.commit()

print([(role.id, role.name) for role in db.query(Role).all()])
"""

#print([(log.id, log.date, log.time, log.text, log.sender) for log in db.query(Log).all()])
#print(len([(log.id, log.date, log.time, log.text, log.sender) for log in db.query(Log).all()]))
print([(account.id, account.name) for account in db.query(AccountStatus).all()])
print([(user.id, user.username, user.account_status_id) for user in db.query(User).all()])
print([(application.id, application.username, application.user_id) for application in db.query(UserApplication).all()])


for user in db.query(User).all():
    user.account_status_id = 2

db.commit()

db.close()