# blueprints/__init__.py

from flask import Flask

# استيراد البلوب برينتس من الملفات الفرعية
from .user.routes import user_bp
from .admin.routes import admin_bp
from .api.routes import api_bp

def register_blueprints(app: Flask):
    """
    Function to register all blueprints with the main Flask app
    """
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
