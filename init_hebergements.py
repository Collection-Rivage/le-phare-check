"""
Script d'initialisation des hébergements
À exécuter UNE SEULE FOIS pour créer tous les hébergements
"""

from app import app, db
from models import Hebergement, TypeHebergement

def init_hebergements():
    with app.app_context():
        # Récupérer les types
        type_cabane = TypeHebergement.query.filter_by(nom='Cabane').first()
        type_mh_staff = TypeHebergement.query.filter_by(nom='Mobil-home Staff').first()
        
        # Créer le type "Espace Bien Être" s'il n'existe pas
        type_bien_etre = TypeHebergement.query.filter_by(nom='Espace Bien Être').first()
        if not type_bien_etre:
            type_bien_etre = TypeHebergement(
                nom='Espace Bien Être',
                description='Espace détente et bien-être'
            )
            db.session.add(type_bien_etre)
            db.session.commit()
        
        print("🏗️  Création des hébergements...")
        
        # Compteurs
        created = 0
        
        # CABANES (189)
        print("📦 Création des 189 Cabanes...")
        zones = ['A', 'B', 'C', 'D', 'E', 'F']
        compteurs = ['devant_droite', 'devant_gauche', 'arriere_droite', 'arriere_gauche']
        
        for i in range(1, 190):
            zone = zones[(i - 1) // 32]  # Répartition par zones
            numero = ((i - 1) % 32) + 1
            emplacement = f"{zone}{numero}"
            
            # Vérifier si existe déjà
            existe = Hebergement.query.filter_by(emplacement=emplacement).first()
            if not existe:
                cabane = Hebergement(
                    emplacement=emplacement,
                    type_id=type_cabane.id,
                    numero_chassis=f"CAB-2024-{str(i).zfill(3)}",
                    nb_personnes=4 if i % 3 == 0 else 2,  # Alternance 2-4 personnes
                    compteur_eau=compteurs[i % 4]
                )
                db.session.add(cabane)
                created += 1
        
        # MOBIL HOMES STAFF (28)
        print("📦 Création des 28 Mobil Homes Staff...")
        for i in range(1, 29):
            emplacement = f"STAFF-{str(i).zfill(2)}"
            
            existe = Hebergement.query.filter_by(emplacement=emplacement).first()
            if not existe:
                mh_staff = Hebergement(
                    emplacement=emplacement,
                    type_id=type_mh_staff.id,
                    numero_chassis=f"MHS-2024-{str(i).zfill(3)}",
                    nb_personnes=2,
                    compteur_eau=compteurs[i % 4]
                )
                db.session.add(mh_staff)
                created += 1
        
        # ESPACE BIEN ÊTRE (1)
        print("📦 Création de l'Espace Bien Être...")
        existe = Hebergement.query.filter_by(emplacement='BIEN-ETRE-01').first()
        if not existe:
            bien_etre = Hebergement(
                emplacement='BIEN-ETRE-01',
                type_id=type_bien_etre.id,
                numero_chassis='EBE-2024-001',
                nb_personnes=10,
                compteur_eau='devant_milieu'
            )
            db.session.add(bien_etre)
            created += 1
        
        # Sauvegarder tout
        db.session.commit()
        
        print(f"✅ {created} hébergements créés avec succès !")
        print(f"📊 Total dans la base : {Hebergement.query.count()}")

if __name__ == '__main__':
    print("🚀 Initialisation des hébergements Le Phare Collection Rivage")
    init_hebergements()
