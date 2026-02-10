from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='technicien')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    must_change_password = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Hebergement(db.Model):
    __tablename__ = 'hebergements'
    id = db.Column(db.Integer, primary_key=True)
    emplacement = db.Column(db.String(50), unique=True, nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('type_hebergement.id'))
    numero_chassis = db.Column(db.String(100))
    nb_personnes = db.Column(db.Integer)
    compteur_eau = db.Column(db.String(50))
    statut = db.Column(db.String(20), default='ok')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TypeHebergement(db.Model):
    __tablename__ = 'type_hebergement'
    id = db.Column(db.Integer, primary_key=True)
    # 🔥 SUPPRESSION DE unique=True pour permettre les doublons de nom
    nom = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    hebergements = db.relationship('Hebergement', backref='type_hebergement', lazy=True)
    
    # Pour afficher proprement dans les listes (nom + description)
    def __repr__(self):
        if self.description:
            return f"{self.nom} ({self.description})"
        return self.nom

class Check(db.Model):
    __tablename__ = 'checks'
    id = db.Column(db.Integer, primary_key=True)
    hebergement_id = db.Column(db.Integer, db.ForeignKey('hebergements.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    electricite = db.Column(db.Boolean, default=True)
    plomberie = db.Column(db.Boolean, default=True)
    chauffage = db.Column(db.Boolean, default=True)
    proprete = db.Column(db.Boolean, default=True)
    equipements = db.Column(db.Boolean, default=True)
    observations = db.Column(db.Text)
    probleme_critique = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    hebergement = db.relationship('Hebergement', backref='checks')
    technicien = db.relationship('User', backref='checks')

class Incident(db.Model):
    __tablename__ = 'incidents'
    id = db.Column(db.Integer, primary_key=True)
    hebergement_id = db.Column(db.Integer, db.ForeignKey('hebergements.id'), nullable=False)
    type_incident = db.Column(db.String(50))
    description = db.Column(db.Text)
    statut = db.Column(db.String(20), default='ouvert')
    assigne_a = db.Column(db.Integer, db.ForeignKey('user.id'))
    cree_par = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_resolution = db.Column(db.DateTime, nullable=True)
    resolu_par_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    hebergement = db.relationship('Hebergement', backref='incidents')
    technicien = db.relationship('User', foreign_keys=[assigne_a], backref='incidents_assignes')
    resolu_par = db.relationship('User', foreign_keys=[resolu_par_id], backref='incidents_resolus')