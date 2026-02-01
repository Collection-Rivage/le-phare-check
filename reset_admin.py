from app import app
from models import db, User, TypeHebergement

with app.app_context():
    # 1. On recrée les tables
    db.drop_all()
    db.create_all()
    
    # 2. On crée l'admin
    admin = User(
        username='admin', 
        email='admin@lephare.com', 
        role='admin', 
        must_change_password=False
    )
    admin.set_password('admin123')
    
    # 3. On ajoute les types de base (pour pas que le site soit vide)
    types = [TypeHebergement(nom='Cabane'), TypeHebergement(nom='Mobil-home')]
    
    db.session.add(admin)
    db.session.add_all(types)
    db.session.commit()
    
    print("--- RÉINITIALISATION RÉUSSIE ---")
    print("Identifiant : admin")
    print("Mot de passe : admin123")