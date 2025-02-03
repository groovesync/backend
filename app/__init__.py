from flask import Flask
from app.routes import auth, user
from app.utils.persistence_manager import PersistenceManager
from app.config import config_dict, Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

limiter = Limiter(get_remote_address, default_limits=["5 per minute"])

def create_app():
    app = Flask(__name__)


    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_dict.get(env, Config))
    app.config.from_object(Config)

    limiter.init_app(app)

    @app.teardown_appcontext
    def close_db_connection(exception):
        if hasattr(PersistenceManager, "close_connection"):
            PersistenceManager.close_connection()

    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)

    return app
