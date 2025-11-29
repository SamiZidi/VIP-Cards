from flask import Blueprint

user_bp = Blueprint("user_bp", __name__)

# import routes to register them with the blueprint
from . import routes  # noqa: F401
