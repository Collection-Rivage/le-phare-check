# mail.py - VERSION DESIGN PRO & RESPONSIVE (Brevo + Photos)
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
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
            .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 40px 20px; text-align: center; color: white; }}
            .header h1 {{ margin: 0; font-size: 28px; font-weight: 700; }}
            .content {{ padding: 40px 30px; color: #333; line-height: 1.6; }}
            .credentials-box {{ background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 25px; margin: 25px 0; }}
            .cred-value {{ font-family: 'Courier New', monospace; font-weight: bold; color: #2c3e50; background: #e9ecef; padding: 4px 8px; border-radius: 4px; }}
            .btn-container {{ text-align: center; margin: 35px 0; }}
            .btn {{ display: inline-block; background-color: #007bff; color: white; padding: 16px 40px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 16px; }}
            .warning-box {{ background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 20px; border-radius: 4px; color: #856404; }}
            .footer {{ background-color: #f8f9fa; padding: 25px; text-align: center; font-size: 12px; color: #adb5bd; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>LE PHARE CHECK</h1>
                <p>Collection Rivage — Gestion Technique</p>
            </div>
            <div class="content">
                <div style="font-size: 20px; font-weight: 600; color: #2c3e50; margin-bottom: 20px;">Bonjour {user.username},</div>
                <p><strong>Stéphane, Responsable Technique du Phare</strong>, vous invite à utiliser l'application <strong>LE PHARE CHECK</strong>.</p>
                <div class="credentials-box">
                    <p><strong>Utilisateur :</strong> <span class="cred-value">{user.username}</span></p>
                    <p><strong>Mot de passe :</strong> <span class="cred-value">{password}</span></p>
                </div>
                <div class="btn-container">
                    <a href="{app_url}/login" class="btn">Accéder à l'application</a>
                </div>
                <div class="warning-box">
                    <strong>⚠️ Sécurité :</strong> Vous devez impérativement changer votre mot de passe dès votre première connexion.
                </div>
            </div>
            <div class="footer">© 2025 Collection Rivage</div>
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
        api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Email bienvenue envoyé à {user.email}")
        return True
    except ApiException as e:
        print(f"❌ Erreur Brevo : {e}")
        return False

def send_assignment_email(incident, technicien):
    if not API_KEY: return False
    app_url = "https://le-phare-check.onrender.com"
    is_urgent = incident.type_incident.lower() == 'urgence'
    
    title_text = "URGENCE CRITIQUE" if is_urgent else "NOUVEL INCIDENT"
    header_gradient = "linear-gradient(135deg, #dc2626 0%, #991b1b 100%)" if is_urgent else "linear-gradient(135deg, #ea580c 0%, #9a3412 100%)"
    btn_color = "#dc2626" if is_urgent else "#ea580c"
    icon = "🚨" if is_urgent else "⚠️"
    bg_card = "#fef2f2" if is_urgent else "#fff7ed"
    header_color = "#dc2626" if is_urgent else "#ea580c"

    # --- LOGIQUE PHOTO ---
    image_section = ""
    if incident.image_url:
        image_section = f"""
        <tr>
            <td align="center" style="padding: 10px 30px 30px 30px;">
                <p style="text-align: left; font-size: 14px; color: #6b7280; font-weight: 600; text-transform: uppercase;">📸 Photo jointe :</p>
                <img src="{incident.image_url}" width="100%" style="max-width: 500px; border-radius: 12px; border: 1px solid #e5e7eb; display: block;" alt="Photo Incident">
            </td>
        </tr>
        """

    subject = f"{icon} {title_text} : {incident.hebergement.emplacement}"
    date_str = incident.created_at.strftime('%d/%m/%Y à %H:%M') if incident.created_at else "À l'instant"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ margin: 0; padding: 0; background-color: #f3f4f6; font-family: sans-serif; }}
            .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body style="background-color: #f3f4f6; padding: 20px;">
        <div class="container">
            <div style="background: {header_gradient}; padding: 40px 20px; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 26px; text-transform: uppercase;">{icon} {title_text}</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Intervention requise sur le site</p>
            </div>
            
            <div style="padding: 30px;">
                <p style="font-size: 18px; font-weight: bold; color: #1f2937;">Bonjour {technicien.username},</p>
                <p style="color: #4b5563; line-height: 1.6;">Un nouvel incident a été signalé. Voici les détails :</p>
                
                <div style="background-color: {bg_card}; border-left: 5px solid {header_color}; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>📍 Lieu :</strong> {incident.hebergement.emplacement}</p>
                    <p style="margin: 5px 0;"><strong>⚠️ Type :</strong> {incident.type_incident.capitalize()}</p>
                    <p style="margin: 5px 0;"><strong>📝 Description :</strong> {incident.description}</p>
                    <p style="margin: 5px 0; color: #6b7280; font-size: 14px;"><strong>🕒 Signalé le :</strong> {date_str}</p>
                </div>
            </div>

            <!-- SECTION PHOTO SI EXISTE -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                {image_section}
            </table>

            <div style="text-align: center; padding-bottom: 40px;">
                <a href="{app_url}/problemes/{incident.hebergement.id}" style="background-color: {btn_color}; color: white; padding: 16px 40px; text-decoration: none; border-radius: 50px; font-weight: bold; display: inline-block;">Voir l'incident & Agir ➔</a>
            </div>
            
            <div style="background-color: #f9fafb; padding: 20px; text-align: center; color: #9ca3af; font-size: 12px; border-top: 1px solid #e5e7eb;">
                Le Phare Check — Collection Rivage
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
        api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Email incident envoyé à {technicien.email}")
        return True
    except ApiException as e:
        print(f"❌ Erreur Brevo : {e}")
        return False
