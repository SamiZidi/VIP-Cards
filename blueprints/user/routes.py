from flask import render_template
from . import user_bp
from models import User
from services.competition_service import now_tunis
from extensions import db


@user_bp.route("/")
def home():
    return render_template("user/not_active.html")

@user_bp.route("/AbX9TqVrKmN<qr_id>4FjHsW2GyUeRc", methods=["GET"])
def user_home(qr_id):
    user = User.query.filter_by(id_qr_code=qr_id).first()
    # not found or not active
    if not user or not getattr(user, "date_wedding", None)  or not getattr(user, "is_active", False) :      
        return render_template("user/not_active.html")
    # before wedding
    if user.date_wedding > now_tunis().date():
        return render_template("user/befor_wedding.html", user=user)
        
    # gold user and active
    if  getattr(user, "is_gold", False):
        # in competition
        active_comp = next((c for c in user.competitions if c.is_active), None)
        if active_comp:
            sorted_users = sorted(active_comp.users, key=lambda u: u.likes_number or 0, reverse=True)
            for idx, u in enumerate(sorted_users, start=1):
                u.rank = idx
            db.session.commit()
            return render_template("user/competition.html", user=user, competition=active_comp)
        # after competition
        else:
            return render_template("user/finished_event.html", user=user)
    # platinum user and active
    if not getattr(user, "is_gold", True) and user.date_wedding <= now_tunis().date():
        return render_template("user/finished_event.html", user=user)
             
    return render_template("user/not_active.html")


@user_bp.route("/AbX9TqVrKmN<qr_id>4FjHsW2GyUeRk", methods=["GET"])
def dashboard(qr_id):

    user = User.query.filter_by(id_qr_code=qr_id).first()
    if not user:
        return render_template("user/not_active.html"), 404

    if not getattr(user, "is_active", False):
        return render_template("user/not_active.html")

    return render_template("user/user_dashboard.html", user=user)

