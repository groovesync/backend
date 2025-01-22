from pymongo import MongoClient
from flask import current_app


class PersistenceManager:
    _client = None
    _db = None

    @staticmethod
    def get_database():
        if not PersistenceManager._client:
            PersistenceManager._client = MongoClient(current_app.config['MONGO_URI'])
            PersistenceManager._db = PersistenceManager._client.get_database()
        return PersistenceManager._db

    @staticmethod
    def close_connection():
        if PersistenceManager._client:
            PersistenceManager._client.close()
            PersistenceManager._client = None
            PersistenceManager._db = None
