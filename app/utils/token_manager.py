from datetime import datetime, timedelta
from app.utils.persistence_manager import PersistenceManager

class TokenManager:
    @staticmethod
    def invalidate_tokens_for_user(username):
        """
        Invalidates all refresh tokens for a user.
        """
        db = PersistenceManager.get_database()
        db.refresh_tokens.delete_many({"username": username})

    @staticmethod
    def store_refresh_token(username, refresh_token):
        """
        Stores or updates the refresh token for a user.
        """
        db = PersistenceManager.get_database()
        db.refresh_tokens.update_one(
            {"username": username},
            {"$set": {"refresh_token": refresh_token,
                      "exp": datetime.utcnow() + timedelta(days=7)}},
            upsert=True
        )

    @staticmethod
    def delete_refresh_token(refresh_token):
        """
        Deletes a specific refresh token.
        """
        db = PersistenceManager.get_database()
        db.refresh_tokens.delete_one({"refresh_token": refresh_token})

    @staticmethod
    def cleanup_expired_tokens():
        """
        Cleans up all expired refresh tokens.
        """
        db = PersistenceManager.get_database()
        db.refresh_tokens.delete_many({"exp": {"$lt": datetime.utcnow()}})

