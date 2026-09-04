# app/database/models.py
#https://chat.deepseek.com/share/3d22sunus1b9kev5m2

from app.modules.core.database import db
from flask_login import UserMixin
from sqlalchemy import Computed

class Eu2016(db.Model):
    __tablename__ = 'Eu_2016'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    carimbo = db.Column('Carimbo de data/hora', db.DateTime)
    peso = db.Column('Peso', db.Float)
    gordura = db.Column('Gordura', db.Float)
    musculo = db.Column('Musculo', db.Float)
    basal = db.Column('basal', db.Float)
    idade = db.Column('Idade', db.Float)
    viceral = db.Column('viceral', db.Float)

    # Declarada como coluna gerada/computada pelo servidor (banco de dados)
    str_comb = db.Column('str_comb', db.String(10), Computed('PERSISTED'))
    
    fk_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    usuario = db.relationship('User', backref=db.backref('registros_eu2016', lazy=True))

    def __repr__(self):
        return f"<Record {self.id} - {self.carimbo}>"


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)


class RecordVape(db.Model):
    __tablename__ = 'record_vape'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    puff_count = db.Column(db.Integer, nullable=False)
    recorded_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('vape_records', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<RecordVape {self.id} - Puffs: {self.puff_count}>"
