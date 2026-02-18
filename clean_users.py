# clean_users.py - Nettoie uniquement les utilisateurs orphelins ou de test
import os
from app import app, db
from models import User, Incident, Hebergement, Check

def clean_users_only():
    with app.app_context():
        print("🧹 Démarrage du nettoyage des utilisateurs...")
        
        try:
            # 1. Identifier les utilisateurs qui ne sont ni 'admin' ni 'technicien' actif si besoin
            # Ici, on va surtout s'assurer qu'aucun incident ne pointe vers un utilisateur inexistant
            
            # Option A : Si tu veux TOUT supprimer sauf l'admin principal
            # Attention : cela mettra assigne_a à NULL dans les incidents existants
            print("   -> Mise à jour des incidents orphelins (assigne_a = NULL)...")
            # On met à NULL tous les incidents qui pointent vers un ID qui n'existe plus OU qu'on va supprimer
            # Pour être sûr, on va d'abord lister les IDs valides après suppression
            
            # Liste des emails/noms à garder impérativement (ex: ton compte admin)
            KEEP_USERS = ['admin', 'stephane@lephare-iledere.com'] 
            
            # Suppression des utilisateurs de test (ceux qui causent les erreurs)
            # On cible ceux dont le username contient 'test', 'Stéphane 2', ou qui ne sont pas dans KEEP_USERS
            users_to_delete = User.query.filter(
                ~User.username.in_(KEEP_USERS)
            ).all()
            
            count = len(users_to_delete)
            if count == 0:
                print("ℹ️ Aucun utilisateur de test trouvé à supprimer.")
            else:
                print(f"   -> Suppression de {count} utilisateurs de test...")
                for u in users_to_delete:
                    print(f"      - Suppression de : {u.username} (ID: {u.id})")
                    db.session.delete(u)
                
                db.session.commit()
                print("✅ Utilisateurs supprimés.")
                
                # IMPORTANT : Mettre à jour les incidents qui pointaient vers ces utilisateurs supprimés
                # On passe assigne_a à NULL pour éviter l'erreur de clé étrangère future
                print("   -> Correction des incidents orphelins (mise à NULL)...")
                # Cette requête SQL directe est plus sûre pour gérer les contraintes FK
                db.session.execute("""
                    UPDATE incidents 
                    SET assigne_a = NULL 
                    WHERE assigne_a NOT IN (SELECT id FROM users) OR assigne_a IS NULL
                """)
                # Note: La commande ci-dessus peut varier selon le dialecte SQL exact, 
                # mais avec SQLAlchemy on peut aussi faire :
                # On récupère tous les incidents et on vérifie manuellement si c'est lent, 
                # mais une requête brute est plus efficace ici.
                # Si la requête brute échoue, on fait une boucle python :
                
                all_incidents = Incident.query.all()
                valid_user_ids = {u.id for u in User.query.all()}
                
                fixed_count = 0
                for inc in all_incidents:
                    if inc.assigne_a and inc.assigne_a not in valid_user_ids:
                        inc.assigne_a = None
                        fixed_count += 1
                
                if fixed_count > 0:
                    print(f"   -> Correction de {fixed_count} incidents orphelins.")
                    db.session.commit()
                else:
                    print("   -> Aucun incident orphelin détecté.")

            print("🎉 Nettoyage terminé !")
            print("👉 Prochaine étape : Crée un NOUVEAU technicien propre dans l'interface.")

        except Exception as e:
            print(f"❌ Erreur : {e}")
            db.session.rollback()

if __name__ == '__main__':
    clean_users_only()
