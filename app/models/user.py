import bcrypt
from werkzeug.security import generate_password_hash
from app.utils.persistence_manager import PersistenceManager


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def save(self):
        db = PersistenceManager.get_database()

        if db.users.find_one({"username": self.username}):
            return False

        hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt())

        db.users.insert_one({
            "username": self.username,
            "password": hashed_password.decode('utf-8'),
        })
        return True

    @staticmethod
    def find_user_by_credentials(username, password):
        db = PersistenceManager.get_database()

        user = db.users.find_one({"username": username})

        if not user:
            return False

        return bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))

    @staticmethod
    def delete_user(username):
        db = PersistenceManager.get_database()
        result = db.users.delete_one({"username": username})
        return result.deleted_count > 0

    @staticmethod
    def update_password(username, new_password):
        db = PersistenceManager.get_database()
        hashed_password = generate_password_hash(new_password)
        result = db.users.update_one(
            {"username": username},
            {"$set": {"password": hashed_password}}
        )
        return result.matched_count > 0 and result.modified_count > 0
