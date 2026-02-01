import os
import requests
import threading
from flask_mail import Mail
from flask import current_app

mail = Mail()

def send_async_email(payload):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": os.getenv("BREVO_API_KEY")
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 201:
            print(f"📩 [MAIL SUCCESS] Invitation envoyée avec succès !")
        else:
            print(f"❌ [MAIL ERROR] {response.status_code} : {response.text}")
    except Exception as e:
        print(f"❌ [MAIL ERROR] Erreur réseau : {str(e)}")

def send_welcome_email(user, raw_password):
    """
    Envoie le mail de bienvenue. 
    IMPORTANT : raw_password est le mot de passe en CLAIR généré dans app.py
    """
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "stephane@lephare-iledere.com")
    app_url = os.getenv("APP_URL", "https://le-phare-check.onrender.com")

    html_content = f"""
    <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333333; border: 1px solid #eeeeee; border-radius: 8px;">
        <div style="background-color: #1a3a52; padding: 25px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="color: #ffffff; margin: 0; font-size: 24px; letter-spacing: 1px;">LE PHARE CHECK</h1>
        </div>
        
        <div style="padding: 40px 30px;">
            <p style="font-size: 16px; margin-bottom: 25px;">Bonjour <strong>{user.username}</strong>,</p>
            
            <p style="font-size: 15px; line-height: 1.6;">
                <strong>Stéphane, Responsable Technique</strong>, a le plaisir de vous inviter sur l'application <strong>Le Phare Check</strong>, votre nouvel outil de gestion technique pour la Collection Rivage.
            </p>

            <div style="background-color: #f4f7f9; border-radius: 6px; padding: 20px; margin: 30px 0; border: 1px solid #e1e8ed;">
                <p style="margin: 0 0 10px 0; font-weight: bold; color: #1a3a52;">Vos accès provisoires :</p>
                <p style="margin: 5px 0;"><strong>Identifiant :</strong> {user.username}</p>
                <p style="margin: 5px 0;"><strong>Mot de passe :</strong> <span style="font-family: monospace; font-size: 16px; background: #ffffff; padding: 2px 8px; border: 1px solid #cbd5e0; border-radius: 4px;">{raw_password}</span></p>
            </div>

            <div style="background-color: #fffaf0; border-left: 4px solid #ed8936; padding: 15px; margin-bottom: 30px;">
                <p style="margin: 0; color: #7b341e; font-size: 14px;">
                    <strong>🔒 Sécurité :</strong> Pour valider votre accès, vous devrez choisir votre propre mot de passe lors de votre première connexion.
                </p>
            </div>

            <div style="text-align: center;">
                <a href="{app_url}/login" style="background-color: #1a3a52; color: #ffffff; padding: 14px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 16px;">
                    Se connecter maintenant
                </a>
            </div>
        </div>

        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #718096; border-radius: 0 0 8px 8px;">
            Cordialement,<br>
            <strong>Service Technique - Le Phare</strong><br>
            Collection Rivage
        </div>
    </div>
    """

    payload = {
        "sender": {{"name": "Le Phare Check", "email": sender_email}},
        "to": [{{"email": user.email}}],
        "subject": "Invitation : Stéphane vous invite sur Le Phare Check",
        "htmlContent": html_content
    }

    threading.Thread(target=send_async_email, args=(payload,)).start()
    return True

# Fonction d'assignation également améliorée
def send_assignment_email(incident, technician):
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "stephane@lephare-iledere.com")
    app_url = os.getenv("APP_URL", "https://le-phare-check.onrender.com")

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px;">
        <div style="background-color: #e53e3e; padding: 20px; text-align: center; color: white; border-radius: 8px 8px 0 0;">
            <h2 style="margin: 0;">🔔 Incident assigné</h2>
        </div>
        <div style="padding: 30px;">
            <p>Bonjour <strong>{technician.username}</strong>,</p>
            <p>Un incident vient de vous être assigné :</p>
            <div style="background-color: #fff5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Lieu :</strong> {incident.hebergement.emplacement}</p>
                <p><strong>Description :</strong> {incident.description}</p>
            </div>
            <a href="{app_url}/login" style="background-color: #e53e3e; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Traiter l'incident</a>
        </div>
    </div>
    """
    payload = {{
        "sender": {{"name": "Le Phare Check", "email": sender_email}},
        "to": [{{"email": technician.email}}],
        "subject": f"🔔 ALERTE : Incident à {incident.hebergement.emplacement}",
        "htmlContent": html_content
    }}
    threading.Thread(target=send_async_email, args=(payload,)).start()
    return True