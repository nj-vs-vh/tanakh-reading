import os

IS_PROD = os.getenv("IS_PROD") is not None

PORT = int(os.getenv("PORT", "8081"))

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "torah-reading-data")

PEPPER = os.getenv("PEPPER", "no-pepper").encode("utf-8")

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "local-admin-token")

STATIC_DIR = os.getenv("STATIC_DIR")
