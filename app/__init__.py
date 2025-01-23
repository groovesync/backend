from flask import Flask
from app.routes import auth, user
from app.utils.persistence_manager import PersistenceManager

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    @app.teardown_appcontext
    def close_db_connection(exception):
        PersistenceManager.close_connection()
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)

    return app
