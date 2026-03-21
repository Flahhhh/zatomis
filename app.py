import asyncio

from zatomis import Zatomis

from urls import routes

async def main():
    app = Zatomis()
    app.setup_routes(routes)
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
