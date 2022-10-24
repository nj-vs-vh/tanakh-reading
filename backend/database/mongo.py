from backend.database.interface import DatabaseInterface


class MongoDatabase(DatabaseInterface):
    @classmethod
    def from_config(cls) -> "MongoDatabase":
        return MongoDatabase()
