# mail.py - VERSION FINALE BREVO (Sécurisée & Design Pro)
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# 🔐 Clé API récupérée depuis les variables d'environnement de Render
# Assure-toi que BREVO_API_KEY est bien défini dans Render > Environment
API_KEY = os.environ.get("BREVO_API_KEY")

if not API_KEY:
    print("⚠️ ERREUR CRITIQUE : La variable BREVO_API_KEY n'est pas configurée sur Render !")
else:
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

def send_welcome_email(user, password):
    if not API_KEY: return False
    
    app_url = "https://le-phare-check.onrender.com"
    subject = f"Bienvenue sur Le Phare Check — {user.username}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f7fa; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #2c3e50, #1a252c); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; line-height: 1.6; color: #333; }}
            .credentials {{ background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 20px; margin: 20px 0; border-radius: 8px; }}
            .password {{ font-family: 'Courier New', Courier, monospace; background-color: #fff3cd; padding: 8px 12px; border-radius: 5px; font-size: 16px; color: #856404; font-weight: bold; }}
            .button {{ display: inline-block; background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 15px 0; }}
            .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 8px; margin-top: 20px; font-size: 14px; }}
            .footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; border-top: 1px solid #ecf0f1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin:0;">LE PHARE CHECK</h1>
                <p style="margin:5px 0 0 0; opacity: 0.9;">Collection Rivage</p>
            </div>
            <div class="content">
                <h2>Bonjour {user.username},</h2>
                <p><strong>Stéphane, Responsable Technique du Phare, vous invite à utiliser l'application LE PHARE CHECK.</strong></p>
                
                <div class="credentials">
                    <p><strong>Nom d'utilisateur :</strong> {user.username}</p>
                    <p><strong>Mot de passe temporaire :</strong><br>
                        <span class="password">{password}</span>
                    </p>
                </div>
                
                <center>
                    <a href="{app_url}/login" class="button">Se connecter à l'application</a>
                </center>
                
                <div class="warning">
                    <strong>⚠️ Important :</strong> Pour des raisons de sécurité, vous devez <strong>changer votre mot de passe dès la première connexion</strong>.
                </div>
            </div>
            <div class="footer">
                <p>Cet email a été envoyé automatiquement par Le Phare Check.</p>
                <p>© 2025 Collection Rivage — Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender={"name": "Stéphane - Le Phare", "email": "stephane@lephare-iledere.com"}, # Change par contact@... si validé chez Brevo
            to=[{"email": user.email, "name": user.username}],
            subject=subject,
            html_content=html_content
        )
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Email bienvenue envoyé à {user.email} (ID: {api_response.message_id})")
        return True
    except ApiException as e:
        print(f"❌ Erreur Brevo (bienvenue) : {e}")
        return False

def send_assignment_email(incident, technicien):
    if not API_KEY: return False
    
    app_url = "https://le-phare-check.onrender.com"
    urgency_text = "URGENCE CRITIQUE" if incident.type_incident == 'urgence' else "NOUVEL INCIDENT"
    
    subject = f"🚨 {urgency_text} — {incident.hebergement.emplacement}"
    
    # Formatage date sécurisé
    date_str = "À l'instant"
    if hasattr(incident, 'created_at') and incident.created_at:
        date_str = incident.created_at.strftime('%d/%m/%Y à %H:%M')

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f7fa; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; line-height: 1.6; color: #333; }}
            .incident-box {{ background-color: #fdf2f2; border-left: 4px solid #e74c3c; padding: 20px; margin: 20px 0; border-radius: 8px; }}
            .detail-row {{ margin: 10px 0; }}
            .button {{ display: inline-block; background-color: #e74c3c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 15px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; border-top: 1px solid #ecf0f1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin:0;">🚨 {urgency_text}</h1>
            </div>
            <div class="content">
                <h2>Bonjour {technicien.username},</h2>
                <p>Un nouvel incident vous a été assigné et nécessite votre intervention.</p>
                
                <div class="incident-box">
                    <div class="detail-row"><strong>📍 Hébergement :</strong> {incident.hebergement.emplacement}</div>
                    <div class="detail-row"><strong>⚠️ Type :</strong> {incident.type_incident.capitalize()}</div>
                    <div class="detail-row"><strong>📝 Description :</strong> {incident.description}</div>
                    <div class="detail-row"><strong>🕒 Date :</strong> {date_str}</div>
                </div>
                
                <center>
                    <a href="{app_url}/problemes/{incident.hebergement.id}" class="button">Voir l'incident</a>
                </center>
            </div>
            <div class="footer">
                <p>Le Phare Check - Collection Rivage</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender={"name": "Le Phare - Alertes", "email": "stephane@lephare-iledere.com"}, # Change par contact@... si validé
            to=[{"email": technicien.email, "name": technicien.username}],
            subject=subject,
            html_content=html_content
        )
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Email assignation envoyé à {technicien.email}")
        return True
    except ApiException as e:
        print(f"❌ Erreur Brevo (assignation) : {e}")
        return False
