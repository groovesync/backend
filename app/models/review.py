from app.utils.persistence_manager import PersistenceManager
from datetime import datetime

class Review:
    def __init__(self, user_id, rate, album_id, text=None):
        self.user_id = user_id
        self.rate = rate
        self.album_id = album_id
        self.text = text
        self.timestamp = datetime.utcnow().date()

    def save(self):
        db = PersistenceManager.get_database()
        if not self.is_valid_user(self.user_id):
            raise ValueError("Invalid user ID")

        if not (0 <= self.rate <= 5):
            raise ValueError("Rate must be between 0 and 5")

        review_data = {
            "userId": self.user_id,
            "rate": self.rate,
            "albumId": self.album_id,
            "text": self.text,
            "timestamp": self.timestamp
        }
        result = db.reviews.insert_one(review_data)
        return result.inserted_id

    @staticmethod
    def is_valid_user(user_id):
        db = PersistenceManager.get_database()
        return db.users.find_one({"_id": user_id}) is not None

    @staticmethod
    def get_by_user(user_id, limit=1):
        db = PersistenceManager.get_database()
        return list(db.reviews.find({"userId": user_id}).sort("timestamp", -1).limit(limit))

    @staticmethod
    def update(review_id, rate=None, text=None):
        db = PersistenceManager.get_database()
        update_data = {}
        if rate is not None:
            if not (0 <= rate <= 5):
                raise ValueError("Rate must be between 0 and 5")
            update_data["rate"] = rate
        if text is not None:
            update_data["text"] = text

        result = db.reviews.update_one(
            {"_id": review_id},
            {"$set": update_data}
        )
        return result.matched_count > 0 and result.modified_count > 0

    @staticmethod
    def delete(review_id):
        db = PersistenceManager.get_database()
        result = db.reviews.delete_one({"_id": review_id})
        return result.deleted_count > 0

    @staticmethod
    def get_by_album(album_id):
        db = PersistenceManager.get_database()
        return list(db.reviews.find({"albumId": album_id}).sort("timestamp", -1))

