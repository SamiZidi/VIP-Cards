from flask import jsonify, request, current_app
from . import api_bp
from models import Competition, User
from extensions import db
from datetime import datetime

# Simple admin-like check decorator for the API blueprint (reuse session if available)
def admin_required(f):
    from functools import wraps
    from flask import session, redirect, url_for
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# GET all competitions / POST new competition
@api_bp.route("/competitions", methods=["GET", "POST"])
@admin_required
def manage_competitions():
    if request.method == "GET":
        comps = Competition.query.order_by(Competition.start_date.desc()).all()
        results = []
        for c in comps:
            results.append({
                'id': c.id,
                'name': c.name,
                'start_date': c.start_date.isoformat(),
                'end_date': c.end_date.isoformat(),
                'registration_deadline': c.registration_deadline.isoformat(),
                'is_active': c.is_active,
                'participants_count': len(c.users),
                'winner_name': c.winner.full_name if c.winner else None
            })
        return jsonify({'success': True, 'competitions': results})

    if request.method == "POST":
        data = request.json
        try:
            new_comp = Competition(
                name=data['name'],
                start_date=datetime.fromisoformat(data['start_date']),
                end_date=datetime.fromisoformat(data['end_date']),
                registration_deadline=datetime.fromisoformat(data['registration_deadline']),
                is_active=data.get('is_active', True)
            )
            db.session.add(new_comp)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Competition created'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

# single competition GET / PUT / DELETE
@api_bp.route("/competitions/<int:comp_id>", methods=["GET", "PUT", "DELETE"])
@admin_required
def single_competition(comp_id):
    comp = Competition.query.get_or_404(comp_id)

    if request.method == "GET":
        return jsonify({
            'success': True,
            'competition': {
                'id': comp.id,
                'name': comp.name,
                'start_date': comp.start_date.isoformat(),
                'end_date': comp.end_date.isoformat(),
                'registration_deadline': comp.registration_deadline.isoformat(),
                'is_active': comp.is_active
            }
        })

    if request.method == "PUT":
        data = request.json
        try:
            comp.name = data['name']
            comp.start_date = datetime.fromisoformat(data['start_date'])
            comp.end_date = datetime.fromisoformat(data['end_date'])
            comp.registration_deadline = datetime.fromisoformat(data['registration_deadline'])
            comp.is_active = data['is_active']
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    if request.method == "DELETE":
        try:
            comp.users = []
            db.session.delete(comp)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

# participants list / add
@api_bp.route("/competitions/<int:comp_id>/participants", methods=["GET", "POST"])
@admin_required
def competition_participants(comp_id):
    comp = Competition.query.get_or_404(comp_id)

    if request.method == "GET":
        participants = sorted(comp.users, key=lambda u: u.likes_number or 0, reverse=True)
        results = []
        for u in participants:
            results.append({
                'id': u.id,
                'full_name': u.full_name,
                'id_qr_code': u.id_qr_code,
                'is_gold': u.is_gold,
                'likes_number': u.likes_number,
                'views_number': u.views_number,
                'url': u.url,
                'is_winner': (comp.winner_id == u.id)
            })
        return jsonify({'success': True, 'participants': results})

    if request.method == "POST":
        user_id = request.json.get('user_id')
        user = User.query.get(user_id)
        if user and user not in comp.users:
            comp.users.append(user)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'User not found or already added'}), 400

# remove participant
@api_bp.route("/competitions/<int:comp_id>/participants/<int:user_id>", methods=["DELETE"])
@admin_required
def remove_participant(comp_id, user_id):
    comp = Competition.query.get_or_404(comp_id)
    user = User.query.get(user_id)

    if user and user in comp.users:
        comp.users.remove(user)
        if comp.winner_id == user.id:
            comp.winner_id = None
            user.is_winner = False
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'User not in competition'}), 400

# update likes for a competition
@api_bp.route("/competitions/<int:comp_id>/update_likes", methods=["POST"])
@admin_required
def update_competition_likes(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    try:
        for user in comp.users:
            user.update_likes_number()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Likes updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# set winner manually
@api_bp.route("/competitions/<int:comp_id>/winner", methods=["POST"])
@admin_required
def set_competition_winner(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)

    if user and user in comp.users:
        if comp.winner:
            comp.winner.is_winner = False
        comp.winner = user
        user.is_winner = True
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Invalid user'}), 400

# get user by qr code
@api_bp.route("/user/<qr_code_id>", methods=["GET"])
@admin_required
def get_user_by_qr(qr_code_id):
    if not qr_code_id.startswith("USER"):
        return jsonify({'success': False, 'error': 'Invalid QR code format'}), 400
    try:
        user = User.query.filter_by(id_qr_code=qr_code_id).first()
        if user:
            user_data = {
                'id': user.id,
                'id_qr_code': user.id_qr_code,
                'full_name': user.full_name,
                'phone_number': user.phone_number,
                'date_wedding': user.date_wedding.strftime('%Y-%m-%d') if user.date_wedding else None,
                'lieu_wedding': user.lieu_wedding,
                'url': user.url,
                'solde_to_pay': user.solde_to_pay,
                'avance_paid': user.avance_paid,
                'reduction': user.reduction,
                'slow_music': user.slow_music,
                'in_music': user.in_music,
                'special_music': user.special_music,
                'pnts': user.points,
                'note': user.note,
                'is_gold': user.is_gold,
                'is_active': user.is_active
            }
        else:
            user_data = {
                'id': None,
                'id_qr_code': qr_code_id,
                'full_name': None,
                'phone_number': None,
                'date_wedding': None,
                'lieu_wedding': None,
                'url': None,
                'solde_to_pay': 0,
                'avance_paid': 0,
                'reduction': 0,
                'slow_music': None,
                'in_music': None,
                'special_music': None,
                'pnts': 0,
                'note': None,
                'is_gold': True,
                'is_active': False
            }
        return jsonify({'success': True, 'user': user_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# save user (create/update)
@api_bp.route("/user/save", methods=["POST"])
@admin_required
def save_user():
    try:
        data = request.json
        user_id = data.get('user_id')

        if user_id:
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
        else:
            user = User(id_qr_code=data['id_qr_code'])
            db.session.add(user)

        user.full_name = data.get('full_name')
        user.phone_number = data.get('phone_number')
        user.lieu_wedding = data.get('lieu_wedding')
        user.url = data.get('url')
        user.solde_to_pay = data.get('solde_to_pay', 0)
        user.avance_paid = data.get('avance_paid', 0)
        user.reduction = data.get('reduction', 0)
        user.slow_music = data.get('slow_music')
        user.in_music = data.get('in_music')
        user.special_music = data.get('special_music')
        user.points = data.get('pnts', 0)
        user.note = data.get('note')
        user.is_gold = data.get('is_gold', True)
        user.is_active = data.get('is_active', False)

        date_wedding = data.get('date_wedding')
        if date_wedding:
            try:
                user.date_wedding = datetime.strptime(date_wedding, '%Y-%m-%d').date()
            except ValueError:
                user.date_wedding = None
        else:
            user.date_wedding = None

        db.session.commit()
        return jsonify({'success': True, 'user_id': user.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# get all users
@api_bp.route("/users", methods=["GET"])
@admin_required
def get_all_users():
    try:
        users = User.query.all()
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'id_qr_code': user.id_qr_code,
                'full_name': user.full_name,
                'phone_number': user.phone_number,
                'date_wedding': user.date_wedding.strftime('%Y-%m-%d') if user.date_wedding else None,
                'lieu_wedding': user.lieu_wedding,
                'url': user.url,
                'solde_to_pay': user.solde_to_pay,
                'avance_paid': user.avance_paid,
                'reduction': user.reduction,
                'slow_music': user.slow_music,
                'in_music': user.in_music,
                'special_music': user.special_music,
                'pnts': user.points,
                'note': user.note,
                'is_gold': user.is_gold,
                'is_active': user.is_active
            })
        return jsonify({'success': True, 'users': users_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# delete user
@api_bp.route("/user/delete/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# update user (public endpoint used by front-end forms)
@api_bp.route("/update_user/<qr_id>", methods=["POST"])
def update_user(qr_id):
    data = request.get_json()
    user = User.query.filter_by(id_qr_code=qr_id).first()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    user.slow_music = data.get("slow_music", user.slow_music)
    user.in_music = data.get("in_music", user.in_music)
    user.special_music = data.get("special_music", user.special_music)
    user.note = data.get("note", user.note)

    db.session.commit()
    return jsonify({"status": "success", "message": "Data updated"})
