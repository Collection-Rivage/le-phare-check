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
            print(f"📩 [MAIL SUCCESS] Email envoyé avec succès !")
        else:
            print(f"❌ [MAIL ERROR] {response.status_code} : {response.text}")
    except Exception as e:
        print(f"❌ [MAIL ERROR] Erreur réseau API : {str(e)}")

def send_welcome_email(user, password):
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "stephane@lephare-iledere.com")
    app_url = os.getenv("APP_URL", "https://le-phare-check.onrender.com")
    
    # Design HTML de l'email
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden;">
        <div style="background-color: #1a3a52; padding: 20px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 24px;">Le Phare Check</h1>
        </div>
        <div style="padding: 30px; line-height: 1.6; color: #333;">
            <h2 style="color: #1a3a52;">Bienvenue {user.username} !</h2>
            <p>Ton compte sur l'application de gestion technique de la <strong>Collection Rivage</strong> vient d'être créé.</p>
            
            <div style="background-color: #f8f9fa; border-left: 4px solid #1a3a52; padding: 15px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>👤 Identifiant :</strong> {user.username}</p>
                <p style="margin: 5px 0;"><strong>🔑 Mot de passe :</strong> <span style="color: #d9534f; font-weight: bold;">{password}</span></p>
            </div>

            <p style="text-align: center; margin-top: 30px;">
                <a href="{app_url}" style="background-color: #1a3a52; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                    Accéder à l'application
                </a>
            </p>
            
            <p style="font-size: 12px; color: #777; margin-top: 30px; border-top: 1px solid #eee; padding-top: 15px;">
                ⚠️ Par mesure de sécurité, nous te conseillons de modifier ton mot de passe dès ta première connexion dans l'onglet profil.
            </p>
        </div>
        <div style="background-color: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; color: #888;">
            &copy; 2025 Le Phare - Collection Rivage
        </div>
    </div>
    """

    payload = {
        "sender": {"name": "Le Phare Check", "email": sender_email},
        "to": [{"email": user.email}],
        "subject": "✅ Ton compte Le Phare Check est prêt",
        "htmlContent": html_content
    }

    threading.Thread(target=send_async_email, args=(payload,)).start()
    return True

def send_assignment_email(incident, technician):
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "stephane@lephare-iledere.com")
    app_url = os.getenv("APP_URL", "https://le-phare-check.onrender.com")

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden;">
        <div style="background-color: #d9534f; padding: 20px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 24px;">🔔 Nouvel Incident Assigné</h1>
        </div>
        <div style="padding: 30px; line-height: 1.6; color: #333;">
            <p>Bonjour <strong>{technician.username}</strong>,</p>
            <p>Un nouvel incident nécessite ton intervention immédiate.</p>
            
            <div style="background-color: #fff4f4; border-left: 4px solid #d9534f; padding: 15px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>🏠 Hébergement :</strong> {incident.hebergement.emplacement}</p>
                <p style="margin: 5px 0;"><strong>⚠️ Type :</strong> {incident.type_incident}</p>
                <p style="margin: 5px 0;"><strong>📝 Description :</strong> {incident.description}</p>
            </div>

            <p style="text-align: center; margin-top: 30px;">
                <a href="{app_url}" style="background-color: #d9534f; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                    Voir l'incident sur l'application
                </a>
            </p>
        </div>
        <div style="background-color: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; color: #888;">
            Service technique Le Phare - Collection Rivage
        </div>
    </div>
    """

    payload = {
        "sender": {"name": "Le Phare Check", "email": sender_email},
        "to": [{"email": technician.email}],
        "subject": "🔔 Incident à traiter - " + incident.hebergement.emplacement,
        "htmlContent": html_content
    }

    threading.Thread(target=send_async_email, args=(payload,)).start()
    return True