import os
import requests
import threading
from flask_mail import Mail

mail = Mail()

def send_async_email(payload):
    url = "https://api.brevo.com/v3/smtp/email"
    api_key = os.getenv("BREVO_API_KEY")
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": api_key
    }
    
    print(f"DEBUG MAIL: Tentative d'envoi via API Brevo...", flush=True)
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 201:
            print(f"📩 [MAIL SUCCESS] Email envoyé à {payload['to'][0]['email']}", flush=True)
        else:
            print(f"❌ [MAIL ERROR] Code {response.status_code} : {response.text}", flush=True)
    except Exception as e:
        print(f"❌ [MAIL ERROR] Erreur réseau : {str(e)}", flush=True)

def send_welcome_email(user, password):
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "stephane@lephare-iledere.com")
    app_url = os.getenv("APP_URL", "https://le-phare-check.onrender.com")

    # Design HTML Pro
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #eee; border-radius: 8px; overflow: hidden;">
        <div style="background-color: #1a3a52; padding: 20px; text-align: center; color: white;">
            <h1 style="margin: 0;">LE PHARE CHECK</h1>
        </div>
        <div style="padding: 30px; color: #333;">
            <p>Bonjour <strong>{user.username}</strong>,</p>
            <p>Stéphane, Responsable Technique, vous invite à rejoindre l'application.</p>
            <div style="background: #f4f7f9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Identifiant :</strong> {user.username}</p>
                <p><strong>Mot de passe :</strong> {password}</p>
            </div>
            <p style="background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107;">
                <strong>🔒 Sécurité :</strong> Vous devrez changer ce mot de passe lors de votre connexion.
            </p>
            <p style="text-align: center; margin-top: 20px;">
                <a href="{app_url}/login" style="background: #1a3a52; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px;">Se connecter</a>
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

    threading.Thread(target=send_async_email, args=(payload,)).start()
    return True

def send_assignment_email(incident, technician):
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "stephane@lephare-iledere.com")
    app_url = os.getenv("APP_URL", "https://le-phare-check.onrender.com")

    payload = {
        "sender": {"name": "Le Phare Check", "email": sender_email},
        "to": [{"email": technician.email}],
        "subject": f"🔔 Incident assigné : {incident.hebergement.emplacement}",
        "htmlContent": f"Un incident vous a été assigné : {incident.description}"
    }

    threading.Thread(target=send_async_email, args=(payload,)).start()
    return True