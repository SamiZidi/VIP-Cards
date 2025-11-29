from flask import Flask
from config import Config  
from extensions import db, migrate
from blueprints import register_blueprints
from services.schenduler_jobs import init_scheduler
from models import config

def load_token_from_db():
    row = config.query.filter_by(name="ACCESS_TOKEN").first()
    if row:
        return row.value
    return None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

   
    # Initialize CSRF protection
   

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    register_blueprints(app)

    with app.app_context():
         # load token once at startup
        app.config["FACEBOOK_ACCESS_TOKEN"] = load_token_from_db()
        init_scheduler(app)

    return app

app = create_app()


