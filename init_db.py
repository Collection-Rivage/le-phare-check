from app import app
from models import db, User, TypeHebergement

with app.app_context():
    # 1. On efface tout et on recrée les tables proprement
    db.drop_all()
    db.create_all()
    
    # 2. On crée l'admin avec des paramètres simples
    # On met must_change_password=False pour que vous puissiez entrer directement
    admin = User(
        username='admin', 
        email='admin@lephare.com', 
        role='admin', 
        must_change_password=False
    )
    admin.set_password('admin123')
    
    # 3. On ajoute les types de base
    types = [
        TypeHebergement(nom='Cabane'), 
        TypeHebergement(nom='Mobil-home')
    ]
    
    db.session.add(admin)
    db.session.add_all(types)
    db.session.commit()
    
    print("------------------------------------------")
    print("✅ BASE DE DONNÉES RÉINITIALISÉE !")
    print("👤 Identifiant : admin")
    print("🔑 Mot de passe : admin123")
    print("------------------------------------------")