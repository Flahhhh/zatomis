import os

from sqlalchemy import inspect
from sqlalchemy.orm import create_session
from sqlalchemy_utils import database_exists, create_database
import asyncio

from extensions import DATABASE_URL, engine
from models import Base
from utils import init_db
from zatomis import Zatomis

from urls import routes

async def main():
    app = Zatomis()
    app.setup_routes(routes)
    await app.run()

if __name__ == "__main__":
    if not engine.url.database or not os.path.exists(engine.url.database) or os.path.getsize(engine.url.database) == 0:
        print("База данных пуста или отсутствует. Создание структуры таблиц...")
        Base.metadata.create_all(engine)
        session = create_session(bind=engine, autocommit=False, autoflush=False)
        init_db(session)
        session.close()

        print("База данных успешно создана и заполнена с нуля!")

    asyncio.run(main())
