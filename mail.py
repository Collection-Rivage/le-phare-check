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
            print(f"📩 [MAIL SUCCESS] Invitation envoyée !")
        else:
            print(f"❌ [MAIL ERROR] {response.status_code} : {response.text}")
    except Exception as e:
        print(f"❌ [MAIL ERROR] Erreur réseau API : {str(e)}")

def send_welcome_email(user, password):
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "stephane@lephare-iledere.com")
    app_url = os.getenv("APP_URL", "https://le-phare-check.onrender.com")
    
    html_content = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
        <!-- Header -->
        <div style="background-color: #1a3a52; padding: 30px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 26px; letter-spacing: 1px;">LE PHARE CHECK</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.8; font-size: 14px;">Gestion Technique - Collection Rivage</p>
        </div>

        <!-- Body -->
        <div style="padding: 40px 30px; line-height: 1.6; color: #333; background-color: white;">
            <p style="font-size: 18px; margin-bottom: 20px;">Bonjour <strong>{user.username}</strong>,</p>
            
            <p style="font-size: 16px;">
                <strong>Stéphane, Responsable Technique</strong>, vous invite à utiliser l'application <strong>Le Phare Check</strong> pour la gestion des contrôles et des incidents.
            </p>
            
            <div style="margin: 30px 0; background-color: #f4f7f9; border-radius: 8px; padding: 25px; border: 1px solid #d1d9e0;">
                <p style="margin: 0 0 15px 0; font-weight: bold; color: #1a3a52; text-decoration: underline;">Vos accès personnels :</p>
                <p style="margin: 8px 0;"><strong>👤 Identifiant :</strong> {user.username}</p>
                <p style="margin: 8px 0;"><strong>🔑 Mot de passe :</strong> <span style="font-family: monospace; background: #eee; padding: 2px 6px; border-radius: 4px; font-size: 16px;">{password}</span></p>
            </div>

            <!-- Warning Securité -->
            <div style="background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 15px; margin: 25px 0; border-radius: 4px;">
                <p style="margin: 0; color: #856404; font-weight: bold;">
                    🔒 Action requise :
                </p>
                <p style="margin: 5px 0 0 0; color: #856404;">
                    Pour garantir la sécurité de votre compte, vous devez <strong>obligatoirement modifier ce mot de passe</strong> dès votre première connexion dans l'onglet "Profil".
                </p>
            </div>

            <p style="text-align: center; margin-top: 40px;">
                <a href="{app_url}" style="background-color: #1a3a52; color: white; padding: 15px 35px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; font-size: 16px;">
                    Se connecter à l'application
                </a>
            </p>
        </div>

        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 13px; color: #6c757d; border-top: 1px solid #eeeeee;">
            Cordialement,<br>
            <strong>Le Service Technique - Le Phare</strong><br>
            Collection Rivage
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

# Gardez send_assignment_email identique ou faites le push quand même
def send_assignment_email(incident, technician):
    # (Votre code actuel pour les incidents reste ici)
    return True