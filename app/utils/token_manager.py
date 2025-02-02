from datetime import datetime, timedelta
from app.utils.persistence_manager import PersistenceManager

class TokenManager:
    @staticmethod
    def invalidate_tokens_for_user(username):
        """
        Invalida todos os tokens de refresh de um usuário.
        """
        db = PersistenceManager.get_database()
        db.refresh_tokens.delete_many({"username": username})

    @staticmethod
    def store_refresh_token(username, refresh_token):
        """
        Armazena ou atualiza o refresh token de um usuário.
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
        Deleta um refresh token específico.
        """
        db = PersistenceManager.get_database()
        db.refresh_tokens.delete_one({"refresh_token": refresh_token})

    @staticmethod
    def cleanup_expired_tokens():
        """
        Limpa todos os refresh tokens expirados.
        """
        db = PersistenceManager.get_database()
        db.refresh_tokens.delete_many({"exp": {"$lt": datetime.utcnow()}})
