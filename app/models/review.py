from app.utils.persistence_manager import PersistenceManager
from datetime import datetime
from bson.objectid import ObjectId
from bson.errors import InvalidId

class Review:
    def __init__(self, user_id, rate, album_id, text=None):
        self.user_id = user_id
        self.rate = rate
        self.album_id = album_id
        self.text = text
        self.timestamp = datetime.utcnow()

    def save(self):
        db = PersistenceManager.get_database()
        if not self.is_valid_user(self.user_id):
            raise ValueError("Invalid or non-existent user ID")

        if not isinstance(self.rate, (int, float)) or not (0 <= self.rate <= 5):
            raise ValueError("Rate must be a number between 0 and 5")

        review_data = {
            "userId": ObjectId(self.user_id),
            "rate": self.rate,
            "albumId": self.album_id,
            "text": self.text,
            "timestamp": self.timestamp
        }
        result = db.reviews.insert_one(review_data)
        return result.inserted_id

    @staticmethod
    def is_valid_user(user_id):
        try:
            db = PersistenceManager.get_database()
            return db.users.find_one({"_id": ObjectId(user_id)}) is not None
        except (InvalidId, TypeError):
            return False

    @staticmethod
    def get_by_user(user_id, limit=1):
        db = PersistenceManager.get_database()
        try:
            oid = ObjectId(user_id)
            return list(db.reviews.find({"userId": oid}).sort("timestamp", -1).limit(limit))
        except (InvalidId, TypeError):
            return []

    @staticmethod
    def update(review_id, rate=None, text=None):
        db = PersistenceManager.get_database()
        update_data = {}
        if rate is not None:
            if not isinstance(rate, (int, float)) or not (0 <= rate <= 5):
                raise ValueError("Rate must be a number between 0 and 5")
            update_data["rate"] = rate
        if text is not None:
            update_data["text"] = text

        if not update_data:
            return False 

        try:
            result = db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {"$set": update_data}
            )
            return result.matched_count > 0 and result.modified_count > 0
        except (InvalidId, TypeError):
            return False

    @staticmethod
    def delete(review_id):
        db = PersistenceManager.get_database()
        try:
            result = db.reviews.delete_one({"_id": ObjectId(review_id)})
            return result.deleted_count > 0
        except (InvalidId, TypeError):
            return False

    @staticmethod
    def get_by_album(album_id):
        db = PersistenceManager.get_database()
        return list(db.reviews.find({"albumId": album_id}).sort("timestamp", -1))