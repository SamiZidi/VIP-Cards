from datetime import datetime
from decimal import Decimal
from services.facebook_likes import get_video_likes_from_url
from extensions import db
from flask import current_app as app

# many - to - many relationship between User and Competition
user_competition = db.Table(
    'user_competition',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('competition_id', db.Integer, db.ForeignKey('competitions.id'), primary_key=True)
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    id_qr_code = db.Column(db.String(120), unique=True, nullable=False)
    is_gold = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=False)

    full_name = db.Column(db.String(80), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    date_wedding = db.Column(db.Date, nullable=True)
    lieu_wedding = db.Column(db.String(120), nullable=True)
    url = db.Column(db.String(200), nullable=True)

    solde_to_pay = db.Column(db.Numeric(10, 2), default=Decimal('0.00'))
    avance_paid = db.Column(db.Numeric(10, 2), default=Decimal('0.00'))
    reduction = db.Column(db.Numeric(10, 2), default=Decimal('0.00'))

    slow_music = db.Column(db.String(500), nullable=True)
    in_music = db.Column(db.String(500), nullable=True)
    special_music = db.Column(db.String(500), nullable=True)
    points = db.Column('pnts', db.Integer, default=0)
    note = db.Column(db.String(5000), nullable=True)

    is_winner = db.Column(db.Boolean, default=False)
    rank = db.Column(db.Integer, default=0)  
    likes_number = db.Column(db.Integer, default=0)
    views_number = db.Column(db.Integer, default=0)

    # competition relationship
    competitions = db.relationship(
        'Competition',
        secondary=user_competition,
        back_populates='users'
    )

    @property
    def remaining_to_pay(self):
        return self.solde_to_pay - self.avance_paid - self.reduction

    def __repr__(self):
        return f'<User {self.id_qr_code} - {self.full_name}>'
    
    def update_likes_number(self):
        if not self.url:
            app.logger.info(f"User {self.id_qr_code} has no URL set.")
            return
        
        likes, views = get_video_likes_from_url(self.url, app.config["FACEBOOK_ACCESS_TOKEN"])
        
        # update likes_number if valid
        # update likes_number if valid
        if isinstance(likes, int):
            self.likes_number = likes
        else:
            app.logger.info(f"Error updating likes for user {self.id_qr_code}: {likes}")

        # update views_number if valid
        if isinstance(views, int):
            self.views_number = views
        else:
            app.logger.info(f"Error updating views for user {self.id_qr_code}: {views}")

        # commit the changes to DB only once
        db.session.commit()
        
       

class Competition(db.Model):
    __tablename__ = 'competitions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    registration_deadline = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    # winner of the competition (foreign key to User)
    winner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # relationship to the winner User (convenience)
    winner = db.relationship('User', foreign_keys=[winner_id], backref='won_competitions', uselist=False)

    #  Users participating in the competition
    users = db.relationship(
        'User',
        secondary=user_competition,
        back_populates='competitions'
    )

    def __repr__(self):
        return f'<Competition {self.name}>'

class config(db.Model):
    __tablename__ = 'config'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    value = db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return f'<Config {self.name}: {self.value}>'