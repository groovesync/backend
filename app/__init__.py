from flask import Flask
from flask_cors import CORS
from app.utils.persistence_manager import PersistenceManager
from app.config import config_dict, Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import os

limiter = Limiter(get_remote_address, default_limits=["100 per minute"])

def create_app():
    app = Flask(__name__)

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_dict.get(env, Config))
    app.config.from_object(Config)

    limiter.init_app(app)

    with app.app_context():  
        from app.routes import auth, user, spotify, review 

        app.register_blueprint(auth.bp)
        app.register_blueprint(user.bp)
        app.register_blueprint(spotify.bp)
        app.register_blueprint(review.bp)
        
    @app.teardown_appcontext
    def close_db_connection(exception):
        if hasattr(PersistenceManager, "close_connection"):
            PersistenceManager.close_connection()

    return app

  