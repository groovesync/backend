import bcrypt
from app.utils.persistence_manager import PersistenceManager
import difflib

class User:
    def __init__(self, username=None, password=None, spotify_id=None, followers=None, following=None):
        self.username = username
        self.password = password
        self.spotify_id = spotify_id
        self.followers = followers if followers is not None else []
        self.following = following if following is not None else []

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
            "followers": self.followers,
            "following": self.following
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
    
    @staticmethod
    def search_users(q=None):
        db = PersistenceManager.get_database()
        all_users = list(db["users"].find())
        results = difflib.get_close_matches(q, [user["username"] for user in all_users], cutoff=0.6)
        
        matched_users = [
            {
                "username": user["username"],
                "spotify_id": user["spotify_id"]
            }
                for user in all_users if user["username"] in results
        ]
        
        return {
            "users": matched_users
        }

    @staticmethod
    def get_all_users():
        db = PersistenceManager.get_database()
        users = list(db["users"].find())

        return {
            "users": [
                {
                    "username": user["name"],
                    "spotify_id": user["spotify_id"]
                } for user in users
            ]
            }

    @staticmethod
    def find_user_by_id(user_id):
        db = PersistenceManager.get_database()
        return db.users.find_one({"_id": user_id})

    @staticmethod
    def update_followers(user_id, follower_id, action):
        db = PersistenceManager.get_database()
        if action == "add":
            db.users.update_one({"user_id": user_id}, {"$addToSet": {"followers": follower_id}})
        elif action == "remove":
            db.users.update_one({"user_id": user_id}, {"$pull": {"followers": follower_id}})

    @staticmethod
    def update_following(user_id, following_id, action):
        db = PersistenceManager.get_database()
        if action == "add":
            db.users.update_one({"user_id": user_id}, {"$addToSet": {"following": following_id}})
        elif action == "remove":
            db.users.update_one({"user_id": user_id}, {"$pull": {"following": following_id}})

