import os
import requests
import threading
from flask_mail import Mail

# On garde l'objet pour la compatibilité avec app.py
mail = Mail()

def send_async_email(payload):
    """Envoi via l'API Brevo (Port 443 Web - Garanti sans blocage)"""
    url = "https://api.brevo.com/v3/smtp/email"
    api_key = os.getenv("BREVO_API_KEY")
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": api_key
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 201:
            print(f"📩 [MAIL SUCCESS] Email envoyé via API Brevo !")
        else:
            print(f"❌ [MAIL ERROR] Code {response.status_code} : {response.text}")
    except Exception as e:
        print(f"❌ [MAIL ERROR] Erreur réseau API : {str(e)}")

def send_welcome_email(user, password_en_clair):
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "stephane@lephare-iledere.com")
    app_url = os.getenv("APP_URL", "https://le-phare-check.onrender.com")

    html_content = f"""
    <div style="font-family: Arial; max-width: 600px; margin: 0 auto; border: 1px solid #eee; border-radius: 12px; overflow: hidden;">
        <div style="background-color: #1a3a52; padding: 25px; text-align: center; color: white;">
            <h1>LE PHARE CHECK</h1>
        </div>
        <div style="padding: 30px;">
            <p>Bonjour <strong>{user.username}</strong>,</p>
            <p>Stéphane vous invite sur l'application <strong>Le Phare Check</strong>.</p>
            <div style="background: #f4f7f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Identifiant :</strong> {user.username}</p>
                <p><strong>Mot de passe :</strong> {password_en_clair}</p>
            </div>
            <p style="color: #d9534f;"><strong>⚠️ Obligatoire :</strong> Changez votre mot de passe dès la première connexion.</p>
            <p style="text-align: center; margin-top: 30px;">
                <a href="{app_url}/login" style="background: #1a3a52; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px;">Se connecter</a>
            </p>
        </div>
    </div>
    """

    payload = {
        "sender": {"name": "Le Phare Check", "email": sender_email},
        "to": [{"email": user.email}],
        "subject": "Invitation sur Le Phare Check",
        "htmlContent": html_content
    }

    # Envoi en arrière-plan
    threading.Thread(target=send_async_email, args=(payload,)).start()
    return True

def send_assignment_email(incident, technician):
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "stephane@lephare-iledere.com")
    payload = {
        "sender": {"name": "Le Phare Check", "email": sender_email},
        "to": [{"email": technician.email}],
        "subject": f"🔔 Incident assigné : {incident.hebergement.emplacement}",
        "htmlContent": f"Un incident vous a été assigné : {incident.description}"
    }
    threading.Thread(target=send_async_email, args=(payload,)).start()
    return True