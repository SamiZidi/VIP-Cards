from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta
from extensions import db
from models import Competition, User
from sqlalchemy import and_

TUNIS_TZ = ZoneInfo("Africa/Tunis")
DURATION_COMPETITION = 1

def now_tunis():
    return datetime.now(TUNIS_TZ)


def update_likes(app):
    with app.app_context():
        try:
            now = now_tunis()
            active_competitions = Competition.query.options(
                db.joinedload(Competition.users)
            ).filter(
                Competition.is_active == True,
                Competition.start_date <= now,
                Competition.end_date >= now
            ).all()
            
            for comp in active_competitions:
                for user in comp.users:
                    try:
                        user.update_likes_number()
                    except Exception as e:
                        app.logger.error(f"Error updating likes for user {user.id}: {e}")
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error in update_likes: {e}")
        finally:
            db.session.remove()  # ✅ Clean up session


def create_monthly_competition(app):
    with app.app_context():
        try:
            now = now_tunis()
            existing = Competition.query.filter(
                Competition.is_active == True,
                Competition.registration_deadline >= now
            ).first()
            
            if existing:
                app.logger.info("Active competition exists. Skipping creation.")
                return
            
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            registration_deadline = start_date + relativedelta(months=DURATION_COMPETITION)
            end_date = start_date + relativedelta(months=DURATION_COMPETITION * 2)

            comp = Competition(
                name=now.strftime("Competition %B %Y"),
                start_date=start_date,
                end_date=end_date,
                registration_deadline=registration_deadline,
                is_active=True
            )
            db.session.add(comp)
            db.session.commit()
            app.logger.info(f"New competition created: {comp.name}")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating competition: {e}")
        finally:
            db.session.remove()  # ✅ Clean up session


def update_competitions(app):
    with app.app_context():
        try:
            now = now_tunis()
            competitions = Competition.query.options(
                db.joinedload(Competition.users)
            ).filter(
                Competition.is_active == True,
                Competition.start_date <= now,
                Competition.registration_deadline > now
            ).all()
            
            for comp in competitions:
                eligible_users = User.query.filter(
                    User.is_gold == True,
                    User.is_active == True,
                    User.date_wedding.isnot(None),
                    User.date_wedding >= comp.start_date,
                    User.date_wedding <= now,
                    User.date_wedding < comp.registration_deadline,
                    User.url.isnot(None),
                    User.url != '',
                    ~User.competitions.any(and_(
                        Competition.is_active == True,
                        Competition.start_date <= now,
                        Competition.registration_deadline > now    
                    ))  
                ).all()
                
                for user in eligible_users:
                    if user not in comp.users:
                        comp.users.append(user)
            
            db.session.commit()  # ✅ Single commit after all changes
            app.logger.info("Competitions updated with eligible users.")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating competitions: {e}")
        finally:
            db.session.remove()  # ✅ Clean up session


def close_competition(app):
    with app.app_context():
        try:
            now = now_tunis()
            competitions_to_close = Competition.query.options(
                db.joinedload(Competition.users)
            ).filter(
                Competition.is_active == True,
                Competition.end_date <= now
            ).all()
            
            for comp in competitions_to_close:
                # ✅ Fixed: Pass app parameter
                update_likes(app)
                
                users_sorted = sorted(
                    [u for u in comp.users if u.likes_number is not None],
                    key=lambda u: u.likes_number,
                    reverse=True
                )
                
                # Reset all users
                for u in comp.users:
                    u.is_winner = False
                
                # Set winner
                if users_sorted:
                    winner = users_sorted[0]
                    comp.winner_id = winner.id
                    winner.is_winner = True
                
                # Set ranks
                for idx, user in enumerate(users_sorted, start=1):
                    user.rank = idx
                
                comp.is_active = False
            
            db.session.commit()  # ✅ Single commit
            app.logger.info("Competitions closed and winners determined.")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error closing competitions: {e}")
        finally:
            db.session.remove()  # ✅ Clean up session