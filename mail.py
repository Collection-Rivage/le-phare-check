from flask_mail import Mail, Message
from flask import current_app

# L'objet mail sera initialisé dans app.py
mail = Mail()

def send_welcome_email(user, password):
    """Envoie le mail de bienvenue lors de la création d'un compte"""
    msg = Message(
        subject="✅ Votre compte Le Phare Check",
        recipients=[user.email],
        body=f"""Bonjour {user.username},

Votre compte sur l'application Le Phare Check a été créé avec succès !

👤 Utilisateur : {user.username}
🔑 Mot de passe : {password}

Lien : {current_app.config.get('APP_URL', 'https://le-phare-check.onrender.com')}
""",
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    try:
        mail.send(msg)
        print(f"📩 Mail de bienvenue envoyé à {user.email}")
        return True
    except Exception as e:
        print(f"❌ Erreur envoi bienvenue : {e}")
        return False

def send_assignment_email(incident, technician):
    """Envoie une notification au technicien quand un incident lui est assigné"""
    msg = Message(
        subject="🔔 Nouvel incident assigné - Le Phare Check",
        recipients=[technician.email],
        body=f"""Bonjour {technician.username},

Un incident vous a été assigné :
🏠 Lieu : {incident.hebergement.emplacement}
⚠️ Problème : {incident.description}

Merci de vous connecter pour traiter l'incident.""",
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    try:
        mail.send(msg)
        print(f"📩 Mail d'assignation envoyé à {technician.email}")
        return True
    except Exception as e:
        print(f"❌ Erreur envoi assignation : {e}")
        return False