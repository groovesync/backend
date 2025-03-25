from app.utils.persistence_manager import PersistenceManager
from bson import ObjectId

class Favorite:
    def __init__(self, user_id, album_id):
        self.user_id = user_id
        self.album_id = album_id

    def save(self):
        db = PersistenceManager.get_database()
        if not self.is_valid_user(self.user_id):
            raise ValueError("Invalid user ID")

        favorite_data = {
            "userId": self.user_id,
            "albumId": self.album_id,
        }
        result = db.favorites.insert_one(favorite_data)
        return result.inserted_id

    @staticmethod
    def is_valid_user(user_id):
        db = PersistenceManager.get_database()
        return db.users.find_one({"spotify_id": user_id}) is not None
    
    @staticmethod
    def get_by_user(user_id):
        db = PersistenceManager.get_database()
        try:
            favorites = list(db.favorites.find({"userId": user_id}))
            for favorite in favorites:
                favorite["_id"] = str(favorite["_id"])
            return favorites
        except Exception as e:
            print(e)
            return []
    
    @staticmethod
    def is_favorite(user_id, album_id):
        db = PersistenceManager.get_database()
        favorite = db.favorites.find_one({"userId": user_id, "albumId": album_id})
        return favorite is not None
    
    @staticmethod
    def get_favorite_id(user_id, album_id):
        db = PersistenceManager.get_database()
        favorite = db.favorites.find_one({"userId": user_id, "albumId": album_id})
        if favorite:
            favorite["_id"] = str(favorite["_id"])
        return favorite
    
    @staticmethod
    def delete(favorite_id):
        db = PersistenceManager.get_database()
        try:
            object_id = ObjectId(favorite_id)
        except Exception as e:
            print(f"Erro converting favorite_id: {e}")
            return False

        result = db.favorites.delete_one({"_id": object_id})
        return result.deleted_count > 0