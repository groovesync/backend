import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key") 
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/groovesync")
    JWT_EXPIRATION_SECONDS = int(os.getenv("JWT_EXPIRATION_SECONDS", 86400))
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
