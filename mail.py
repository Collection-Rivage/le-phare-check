# mail.py - VERSION DESIGN PRO & RESPONSIVE (Brevo)
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# 🔐 Clé API depuis les variables d'environnement Render
API_KEY = os.environ.get("BREVO_API_KEY")

if not API_KEY:
    print("⚠️ ERREUR : Variable BREVO_API_KEY manquante sur Render")
else:
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

def send_welcome_email(user, password):
    if not API_KEY: return False
    
    app_url = "https://le-phare-check.onrender.com"
    subject = f"Bienvenue sur Le Phare Check — {user.username}"
    
    # DESIGN MODERNE BIENVENUE
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bienvenue</title>
        <style>
            body {{ font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }}
            .container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
            .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 40px 20px; text-align: center; color: white; }}
            .header h1 {{ margin: 0; font-size: 28px; font-weight: 700; letter-spacing: 1px; }}
            .header p {{ margin: 10px 0 0; opacity: 0.9; font-size: 14px; }}
            .content {{ padding: 40px 30px; color: #333; line-height: 1.6; }}
            .greeting {{ font-size: 20px; font-weight: 600; color: #2c3e50; margin-bottom: 20px; }}
            .message {{ font-size: 16px; color: #555; margin-bottom: 30px; }}
            .credentials-box {{ background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 25px; margin: 25px 0; position: relative; }}
            .credentials-box::before {{ content: '🔑'; position: absolute; top: -15px; left: 20px; background: #fff; padding: 0 10px; font-size: 20px; }}
            .cred-row {{ margin: 12px 0; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #dee2e6; padding-bottom: 8px; }}
            .cred-row:last-child {{ border-bottom: none; }}
            .cred-label {{ font-weight: 600; color: #6c757d; font-size: 14px; }}
            .cred-value {{ font-family: 'Courier New', monospace; font-weight: bold; color: #2c3e50; background: #e9ecef; padding: 4px 8px; border-radius: 4px; }}
            .btn-container {{ text-align: center; margin: 35px 0; }}
            .btn {{ display: inline-block; background-color: #007bff; color: white; padding: 16px 40px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 16px; box-shadow: 0 4px 15px rgba(0,123,255,0.3); transition: transform 0.2s; }}
            .btn:hover {{ transform: translateY(-2px); background-color: #0056b3; }}
            .warning-box {{ background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 20px; border-radius: 4px; margin-top: 30px; }}
            .warning-title {{ color: #856404; font-weight: bold; display: block; margin-bottom: 5px; font-size: 16px; }}
            .warning-text {{ color: #856404; font-size: 14px; }}
            .footer {{ background-color: #f8f9fa; padding: 25px; text-align: center; font-size: 12px; color: #adb5bd; border-top: 1px solid #e9ecef; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>LE PHARE CHECK</h1>
                <p>Collection Rivage — Gestion Technique</p>
            </div>
            <div class="content">
                <div class="greeting">Bonjour {user.username},</div>
                <div class="message">
                    <strong>Stéphane, Responsable Technique du Phare</strong>, vous invite à utiliser l'application <strong>LE PHARE CHECK</strong> pour la gestion quotidienne des hébergements.
                </div>
                
                <div class="credentials-box">
                    <div class="cred-row">
                        <span class="cred-label">Nom d'utilisateur</span>
                        <span class="cred-value">{user.username}</span>
                    </div>
                    <div class="cred-row">
                        <span class="cred-label">Mot de passe temporaire</span>
                        <span class="cred-value">{password}</span>
                    </div>
                </div>
                
                <div class="btn-container">
                    <a href="{app_url}/login" class="btn">Accéder à l'application</a>
                </div>
                
                <div class="warning-box">
                    <span class="warning-title">⚠️ Sécurité Importante</span>
                    <span class="warning-text">Pour protéger vos données, vous devez impérativement <strong>changer votre mot de passe</strong> dès votre première connexion.</span>
                </div>
            </div>
            <div class="footer">
                <p>Cet email a été envoyé automatiquement par Le Phare Check.<br>© 2025 Collection Rivage</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender={"name": "Stéphane - Le Phare", "email": "stephane@lephare-iledere.com"},
            to=[{"email": user.email, "name": user.username}],
            subject=subject,
            html_content=html_content
        )
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Email bienvenue envoyé à {user.email}")
        return True
    except ApiException as e:
        print(f"❌ Erreur Brevo : {e}")
        return False

def send_assignment_email(incident, technicien):
    if not API_KEY: return False
    
    app_url = "https://le-phare-check.onrender.com"
    
    # Détection du niveau d'urgence pour adapter les couleurs
    is_urgent = incident.type_incident == 'urgence'
    title_text = "URGENCE CRITIQUE" if is_urgent else "NOUVEL INCIDENT"
    header_gradient = "linear-gradient(135deg, #dc3545 0%, #a71d2a 100%)" if is_urgent else "linear-gradient(135deg, #fd7e14 0%, #d35400 100%)"
    btn_color = "#dc3545" if is_urgent else "#fd7e14"
    
    subject = f"🚨 {title_text} : {incident.hebergement.emplacement}"
    
    # Formatage date
    date_str = "À l'instant"
    if hasattr(incident, 'created_at') and incident.created_at:
        date_str = incident.created_at.strftime('%d/%m/%Y à %H:%M')

    # DESIGN MODERNE INCIDENT
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Incident Assigné</title>
        <style>
            body {{ font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
            .header {{ background: {header_gradient}; padding: 40px 20px; text-align: center; color: white; }}
            .header h1 {{ margin: 0; font-size: 26px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; }}
            .header-icon {{ font-size: 40px; margin-bottom: 10px; display: block; }}
            .content {{ padding: 40px 30px; color: #333; }}
            .greeting {{ font-size: 18px; font-weight: 600; color: #2c3e50; margin-bottom: 15px; }}
            .intro {{ font-size: 16px; color: #555; margin-bottom: 25px; }}
            .incident-card {{ background-color: #fff5f5; border: 1px solid #ffcccc; border-radius: 8px; padding: 25px; margin: 25px 0; }}
            .card-title {{ color: #dc3545; font-weight: bold; font-size: 14px; text-transform: uppercase; margin-bottom: 15px; display: block; border-bottom: 2px solid #ffcccc; padding-bottom: 10px; }}
            .detail-item {{ margin: 12px 0; display: flex; align-items: flex-start; }}
            .detail-icon {{ width: 25px; margin-right: 10px; text-align: center; font-size: 18px; }}
            .detail-text {{ font-size: 15px; color: #444; }}
            .detail-text strong {{ color: #2c3e50; }}
            .btn-container {{ text-align: center; margin: 35px 0; }}
            .btn {{ display: inline-block; background-color: {btn_color}; color: white; padding: 16px 40px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 16px; box-shadow: 0 4px 15px rgba(220,53,69,0.3); transition: transform 0.2s; }}
            .btn:hover {{ transform: translateY(-2px); filter: brightness(110%); }}
            .footer {{ background-color: #f8f9fa; padding: 25px; text-align: center; font-size: 12px; color: #adb5bd; border-top: 1px solid #e9ecef; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <span class="header-icon">🚨</span>
                <h1>{title_text}</h1>
            </div>
            <div class="content">
                <div class="greeting">Bonjour {technicien.username},</div>
                <div class="intro">Un nouvel incident a été signalé et vous a été assigné. Votre intervention est requise :</div>
                
                <div class="incident-card">
                    <span class="card-title">Détails de l'intervention</span>
                    
                    <div class="detail-item">
                        <span class="detail-icon">📍</span>
                        <div class="detail-text"><strong>Lieu :</strong><br>{incident.hebergement.emplacement}</div>
                    </div>
                    
                    <div class="detail-item">
                        <span class="detail-icon">⚠️</span>
                        <div class="detail-text"><strong>Type :</strong> {incident.type_incident.capitalize()}</div>
                    </div>
                    
                    <div class="detail-item">
                        <span class="detail-icon">📝</span>
                        <div class="detail-text"><strong>Description :</strong><br>{incident.description}</div>
                    </div>
                    
                    <div class="detail-item">
                        <span class="detail-icon">🕒</span>
                        <div class="detail-text"><strong>Signalé le :</strong> {date_str}</div>
                    </div>
                </div>
                
                <div class="btn-container">
                    <a href="{app_url}/problemes/{incident.hebergement.id}" class="btn">Voir l'incident & Agir</a>
                </div>
                
                <p style="text-align: center; font-size: 13px; color: #6c757d; margin-top: 20px;">
                    Si vous ne pouvez pas traiter cet incident, merci de prévenir Stéphane immédiatement.
                </p>
            </div>
            <div class="footer">
                <p>Le Phare Check - Collection Rivage<br>Service Technique</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender={"name": "Le Phare - Alertes", "email": "stephane@lephare-iledere.com"},
            to=[{"email": technicien.email, "name": technicien.username}],
            subject=subject,
            html_content=html_content
        )
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Email incident envoyé à {technicien.email}")
        return True
    except ApiException as e:
        print(f"❌ Erreur Brevo : {e}")
        return False
