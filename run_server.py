import logging

from backend.database.mongo import MongoDatabase
from backend.server import BackendApp

if __name__ == "__init__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(name)s: %(message)s")
    app = BackendApp(db=MongoDatabase.from_config())
    app.run()
