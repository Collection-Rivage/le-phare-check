from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='technicien')  # admin, technicien
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    checks = db.relationship('Check', backref='technicien', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class TypeHebergement(db.Model):
    __tablename__ = 'types_hebergement'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TypeHebergement {self.nom}>'


class Hebergement(db.Model):
    __tablename__ = 'hebergements'
    
    id = db.Column(db.Integer, primary_key=True)
    emplacement = db.Column(db.String(50), nullable=False)  # Ex: A12, B5
    type_id = db.Column(db.Integer, db.ForeignKey('types_hebergement.id'), nullable=False)
    numero_chassis = db.Column(db.String(100))
    nb_personnes = db.Column(db.Integer)
    compteur_eau = db.Column(db.String(50))  # devant_droite, devant_gauche, etc.
    statut = db.Column(db.String(20), default='ok')  # ok, alerte, probleme
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    checks = db.relationship('Check', backref='hebergement', lazy=True)
    type_hebergement = db.relationship('TypeHebergement', backref='hebergements')
    
    def __repr__(self):
        return f'<Hebergement {self.emplacement}>'


class Check(db.Model):
    __tablename__ = 'checks'
    
    id = db.Column(db.Integer, primary_key=True)
    hebergement_id = db.Column(db.Integer, db.ForeignKey('hebergements.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Checklist
    electricite = db.Column(db.Boolean, default=True)
    plomberie = db.Column(db.Boolean, default=True)
    chauffage = db.Column(db.Boolean, default=True)
    proprete = db.Column(db.Boolean, default=True)
    equipements = db.Column(db.Boolean, default=True)
    
    # Observations
    observations = db.Column(db.Text)
    probleme_critique = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Check {self.id} - {self.hebergement.emplacement}>'
