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
            print(f"📩 [MAIL SUCCESS] Email envoyé !")
        else:
            print(f"❌ [MAIL ERROR] {response.status_code}")
    except Exception as e:
        print(f"❌ [MAIL ERROR] Erreur : {str(e)}")

def send_welcome_email(user, password_clair):
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "stephane@lephare-iledere.com")
    app_url = os.getenv("APP_URL", "https://le-phare-check.onrender.com")

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden;">
        <div style="background-color: #1a3a52; padding: 30px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 26px;">LE PHARE CHECK</h1>
            <p style="margin: 5px 0; opacity: 0.8;">Collection Rivage</p>
        </div>
        <div style="padding: 40px 30px; line-height: 1.6; color: #333; background-color: white;">
            <p>Bonjour <strong>{user.username}</strong>,</p>
            <p><strong>Stéphane, Responsable Technique</strong>, vous invite sur l'application.</p>
            <div style="background-color: #f4f7f9; border-radius: 8px; padding: 20px; margin: 25px 0; border: 1px solid #d1d9e0;">
                <p style="margin: 5px 0;"><strong>👤 Identifiant :</strong> {user.username}</p>
                <p style="margin: 5px 0;"><strong>🔑 Mot de passe :</strong> <span style="font-weight: bold; color: #1a3a52;">{password_clair}</span></p>
            </div>
            <p style="background-color: #fff3cd; padding: 15px; border-radius: 4px; color: #856404;">
                🔒 Vous devrez <strong>obligatoirement changer ce mot de passe</strong> lors de votre première connexion.
            </p>
            <p style="text-align: center; margin-top: 35px;">
                <a href="{app_url}/login" style="background-color: #1a3a52; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Se connecter à l'application</a>
            </p>
        </div>
    </div>
    """

    payload = {
        "sender": {"name": "Le Phare Check", "email": sender_email},
        "to": [{"email": user.email}],
        "subject": "Invitation : Stéphane vous invite sur l'application Le Phare Check",
        "htmlContent": html_content
    }

    threading.Thread(target=send_async_email, args=(payload,)).start()
    return True

def send_assignment_email(incident, technician):
    # Logique identique pour les incidents
    return True