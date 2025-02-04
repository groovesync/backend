import bcrypt
from app.utils.persistence_manager import PersistenceManager

class User:
    def __init__(self, username=None, password=None, spotify_id=None):
        self.username = username
        self.password = password
        self.spotify_id = spotify_id

    def save(self):
        db = PersistenceManager.get_database()
        if db.users.find_one({"username": self.username}):
            return False

        hashed_password = None
        if self.password:
            hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt())

        db.users.insert_one({
            "username": self.username,
            "password": hashed_password.decode('utf-8') if hashed_password else None,
            "spotify_id": self.spotify_id,
        })
        return True

    @staticmethod
    def find_user_by_spotify_id(spotify_id):
        db = PersistenceManager.get_database()
        return db.users.find_one({"spotify_id": spotify_id})

    @staticmethod
    def find_user_by_username(username):
        db = PersistenceManager.get_database()
        return db.users.find_one({"username": username})

    @staticmethod
    def find_user_by_credentials(username, password):
        db = PersistenceManager.get_database()
        user = db.users.find_one({"username": username})
        if not user or not user.get('password'):
            return None

        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return user

        return None

    @staticmethod
    def delete_user(username):
        db = PersistenceManager.get_database()
        result = db.users.delete_one({"username": username})
        return result.deleted_count > 0

    @staticmethod
    def update_password(username, new_password):
        db = PersistenceManager.get_database()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        result = db.users.update_one(
            {"username": username},
            {"$set": {"password": hashed_password}}
        )
        return result.matched_count > 0 and result.modified_count > 0

    @staticmethod
    def update_spotify_token(username, spotify_id):
        db = PersistenceManager.get_database()
        result = db.users.update_one(
            {"username": username},
            {"$set": {"spotify_id": spotify_id}}
        )
        return result.matched_count > 0 and result.modified_count > 0
