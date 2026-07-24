#app/database/models.py
from app.modules.core.database import db
from flask_login import UserMixin
from app.modules.core.database import db


class Eu2016(db.Model):
    __tablename__ = 'Eu_2016'

    # The first argument of Column is the exact name in the database
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    carimbo = db.Column('Carimbo de data/hora', db.DateTime)
    peso = db.Column('Peso', db.Float)
    gordura = db.Column('Gordura', db.Float)
    musculo = db.Column('Musculo', db.Float)
    basal = db.Column('basal', db.Float)
    idade = db.Column('Idade', db.Float)
    viceral = db.Column('viceral', db.Float)
    
    # Foreign key referencing the users table (not null)
    fk_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationship to easily access user data from the record
    user = db.relationship('User', backref=db.backref('eu2016_records', lazy=True))

    def __repr__(self):
        return f"<Record {self.id} - {self.carimbo}>"


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
