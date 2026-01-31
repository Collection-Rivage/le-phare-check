import os
import requests
import threading
from flask_mail import Mail # Pour ne pas casser app.py

# On garde l'objet pour la compatibilité
mail = Mail()

def send_async_email(payload):
    """Envoi via l'API Brevo (Port 443 Web - Impossible à bloquer)"""
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": os.getenv("BREVO_API_KEY")
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 201:
            print(f"📩 [MAIL SUCCESS] Via API Brevo !")
        else:
            print(f"❌ [MAIL ERROR] Code {response.status_code} : {response.text}")
    except Exception as e:
        print(f"❌ [MAIL ERROR] Erreur réseau API : {str(e)}")

def send_welcome_email(user, password):
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "stephane@lephare-iledere.com")
    
    payload = {
        "sender": {"name": "Le Phare Check", "email": sender_email},
        "to": [{"email": user.email}],
        "subject": "✅ Votre compte Le Phare Check",
        "htmlContent": f"""
            <h3>Bienvenue {user.username}</h3>
            <p>Votre compte est prêt.</p>
            <p>Identifiants : <b>{user.username}</b> / <b>{password}</b></p>
        """
    }

    threading.Thread(target=send_async_email, args=(payload,)).start()
    return True

def send_assignment_email(incident, technician):
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "stephane@lephare-iledere.com")

    payload = {
        "sender": {"name": "Le Phare Check", "email": sender_email},
        "to": [{"email": technician.email}],
        "subject": "🔔 Nouvel incident assigné",
        "htmlContent": f"<p>Bonjour, un incident vous attend à l'hébergement {incident.hebergement.emplacement}.</p>"
    }

    threading.Thread(target=send_async_email, args=(payload,)).start()
    return True
    print(f"📝 [MAIL] Préparation mail de bienvenue pour {user.email}", flush=True)
    
    smtp_config = {
        'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        'user': os.getenv('MAIL_USERNAME'),
        'password': os.getenv('MAIL_PASSWORD'), # Sans espaces
        'sender': os.getenv('MAIL_DEFAULT_SENDER')
    }

    msg_data = {
        'to': user.email,
        'subject': "✅ Votre compte Le Phare Check",
        'body': f"Bonjour {user.username},\n\nVotre compte est prêt.\nIdentifiants : {user.username} / {password}"
    }

    # On lance la tâche de fond
    threading.Thread(target=send_async_email, args=(smtp_config, msg_data)).start()
    return True

def send_assignment_email(incident, technician):
    """Prépare le mail d'assignation et lance le thread"""
    print(f"📝 [MAIL] Préparation mail d'assignation pour {technician.email}", flush=True)
    
    smtp_config = {
        'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        'user': os.getenv('MAIL_USERNAME'),
        'password': os.getenv('MAIL_PASSWORD'),
        'sender': os.getenv('MAIL_DEFAULT_SENDER')
    }

    msg_data = {
        'to': technician.email,
        'subject': "🔔 Nouvel incident assigné",
        'body': f"Bonjour {technician.username}, un incident vous a été assigné à l'hébergement {incident.hebergement.emplacement}."
    }

    threading.Thread(target=send_async_email, args=(smtp_config, msg_data)).start()
    return True