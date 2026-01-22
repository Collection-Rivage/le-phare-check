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
    role = db.Column(db.String(20), default='technicien')  # admin, technicien, accueil, direction
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    checks = db.relationship('Check', backref='technicien', lazy=True)
    incidents_assignes = db.relationship('Incident', foreign_keys='Incident.assigne_a', backref='technicien')
    incidents_crees = db.relationship('Incident', foreign_keys='Incident.cree_par', backref='createur')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class TypeHebergement(db.Model):
    __tablename__ = 'types_hebergement'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Hebergement(db.Model):
    __tablename__ = 'hebergements'
    id = db.Column(db.Integer, primary_key=True)
    emplacement = db.Column(db.String(50), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('types_hebergement.id'), nullable=False)
    numero_chassis = db.Column(db.String(100))
    nb_personnes = db.Column(db.Integer)
    compteur_eau = db.Column(db.String(50))
    statut = db.Column(db.String(20), default='ok')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    checks = db.relationship('Check', backref='hebergement', lazy=True)
    incidents = db.relationship('Incident', backref='hebergement', lazy=True)
    type_hebergement = db.relationship('TypeHebergement', backref='hebergements')

class Check(db.Model):
    __tablename__ = 'checks'
    id = db.Column(db.Integer, primary_key=True)
    hebergement_id = db.Column(db.Integer, db.ForeignKey('hebergements.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    electricite = db.Column(db.Boolean, default=True)
    plomberie = db.Column(db.Boolean, default=True)
    chauffage = db.Column(db.Boolean, default=True)
    proprete = db.Column(db.Boolean, default=True)
    equipements = db.Column(db.Boolean, default=True)
    observations = db.Column(db.Text)
    probleme_critique = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Incident(db.Model):
    __tablename__ = 'incidents'
    id = db.Column(db.Integer, primary_key=True)
    hebergement_id = db.Column(db.Integer, db.ForeignKey('hebergements.id'), nullable=False)
    type_incident = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    assigne_a = db.Column(db.Integer, db.ForeignKey('users.id'))
    statut = db.Column(db.String(20), default='nouveau')
    cree_par = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cree_le = db.Column(db.DateTime, default=datetime.utcnow)
