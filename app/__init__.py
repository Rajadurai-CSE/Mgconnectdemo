from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MongoDB
mongo = PyMongo()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configure the app
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "default-dev-key")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/mgconnecttndeemo")
    
    # Initialize extensions
    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Import and register blueprints
    from app.routes.auth import auth
    from app.routes.migrants import migrants
    from app.routes.employers import employers
    from app.routes.ngos import ngos
    from app.routes.government import government
    from app.routes.main import main
    from app.routes.education import education
    from app.routes.admin import admin

    app.register_blueprint(auth)
    app.register_blueprint(migrants)
    app.register_blueprint(employers)
    app.register_blueprint(ngos)
    app.register_blueprint(government)
    app.register_blueprint(education)
    app.register_blueprint(admin)
    app.register_blueprint(main)

    return app
