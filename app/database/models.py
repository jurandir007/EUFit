from app.modules.core.database import db


class Eu2016(db.Model):
    __tablename__ = 'Eu_2016'

    # O primeiro argumento da Column é o nome exato no banco (o 'key')
    carimbo = db.Column('Carimbo de data/hora', db.DateTime, primary_key=True)
    peso = db.Column('Peso', db.Float)
    gordura = db.Column('Gordura', db.Float)
    musculo = db.Column('Musculo', db.Float)
    basal = db.Column('basal', db.Float)
    idade = db.Column('Idade', db.Float)
    viceral = db.Column('viceral', db.Float)

    def __repr__(self):
        return f"<Registro {self.carimbo}>"