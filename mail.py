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
    
    # Détection du niveau d'urgence pour adapter les couleurs et le texte
    is_urgent = incident.type_incident.lower() == 'urgence'
    
    if is_urgent:
        title_text = "URGENCE CRITIQUE"
        header_color = "#dc2626" # Rouge vif
        header_gradient = "linear-gradient(135deg, #dc2626 0%, #991b1b 100%)"
        btn_color = "#dc2626"
        icon = "🚨"
        border_color = "#fecaca"
        bg_card = "#fef2f2"
    else:
        title_text = "NOUVEL INCIDENT"
        header_color = "#ea580c" # Orange
        header_gradient = "linear-gradient(135deg, #ea580c 0%, #9a3412 100%)"
        btn_color = "#ea580c"
        icon = "⚠️"
        border_color = "#ffedd5"
        bg_card = "#fff7ed"

    subject = f"{icon} {title_text} : {incident.hebergement.emplacement}"
    
    # Formatage de la date
    date_str = "À l'instant"
    if hasattr(incident, 'created_at') and incident.created_at:
        date_str = incident.created_at.strftime('%d/%m/%Y à %H:%M')

    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>{title_text}</title>
        <style>
            /* Reset styles */
            body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
            table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
            img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
            table {{ border-collapse: collapse !important; }}
            body {{ height: 100% !important; margin: 0 !important; padding: 0 !important; width: 100% !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6; }}
            
            /* Mobile styles */
            @media screen and (max-width: 600px) {{
                .email-container {{ width: 100% !important; }}
                .fluid-img {{ width: 100% !important; max-width: 100% !important; height: auto !important; }}
                .stack-column {{ display: block !important; width: 100% !important; max-width: 100% !important; direction: ltr !important; }}
                .center-on-mobile {{ text-align: center !important; }}
                .padding-mobile {{ padding: 20px !important; }}
            }}
        </style>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f3f4f6;">
        
        <!-- Hidden preheader -->
        <div style="display: none; font-size: 1px; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;">
            Un nouvel incident vous a été assigné : {incident.hebergement.emplacement}. Intervention requise.
        </div>

        <center style="width: 100%; background-color: #f3f4f6;">
            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f3f4f6;">
                <tr>
                    <td align="center" valign="top" style="padding: 40px 10px;">
                        
                        <!-- Main Container -->
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" class="email-container" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                            
                            <!-- Header Banner -->
                            <tr>
                                <td style="background: {header_gradient}; padding: 40px 30px; text-align: center;">
                                    <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                        {icon} {title_text}
                                    </h1>
                                    <p style="margin: 10px 0 0 0; color: rgba(255,255,255,0.9); font-size: 16px; font-weight: 500;">
                                        Intervention requise immédiatement
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Content Body -->
                            <tr>
                                <td class="padding-mobile" style="padding: 40px 30px;">
                                    
                                    <!-- Greeting -->
                                    <p style="margin: 0 0 20px 0; font-size: 18px; color: #1f2937; font-weight: 600;">
                                        Bonjour {technicien.username},
                                    </p>
                                    <p style="margin: 0 0 30px 0; font-size: 16px; color: #4b5563; line-height: 1.6;">
                                        Un nouvel incident a été signalé sur le site et vous a été assigné. Veuillez prendre connaissance des détails ci-dessous :
                                    </p>
                                    
                                    <!-- Incident Details Card -->
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: {bg_card}; border-left: 5px solid {header_color}; border-radius: 8px; margin-bottom: 30px;">
                                        <tr>
                                            <td style="padding: 25px;">
                                                <h3 style="margin: 0 0 20px 0; color: {header_color}; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700;">
                                                    📋 Détails de l'intervention
                                                </h3>
                                                
                                                <!-- Location -->
                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-bottom: 15px;">
                                                    <tr>
                                                        <td width="30" valign="top" style="font-size: 18px; padding-right: 10px;">📍</td>
                                                        <td valign="top">
                                                            <span style="display: block; font-size: 12px; color: #6b7280; text-transform: uppercase; font-weight: 600;">Lieu</span>
                                                            <span style="font-size: 16px; color: #111827; font-weight: 700;">{incident.hebergement.emplacement}</span>
                                                        </td>
                                                    </tr>
                                                </table>
                                                
                                                <!-- Type -->
                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-bottom: 15px;">
                                                    <tr>
                                                        <td width="30" valign="top" style="font-size: 18px; padding-right: 10px;">⚠️</td>
                                                        <td valign="top">
                                                            <span style="display: block; font-size: 12px; color: #6b7280; text-transform: uppercase; font-weight: 600;">Type</span>
                                                            <span style="font-size: 16px; color: #111827; font-weight: 600;">{incident.type_incident.capitalize()}</span>
                                                        </td>
                                                    </tr>
                                                </table>
                                                
                                                <!-- Description -->
                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-bottom: 15px;">
                                                    <tr>
                                                        <td width="30" valign="top" style="font-size: 18px; padding-right: 10px;">📝</td>
                                                        <td valign="top">
                                                            <span style="display: block; font-size: 12px; color: #6b7280; text-transform: uppercase; font-weight: 600;">Description</span>
                                                            <span style="font-size: 15px; color: #374151; line-height: 1.5;">{incident.description}</span>
                                                        </td>
                                                    </tr>
                                                </table>
                                                
                                                <!-- Date -->
                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                                    <tr>
                                                        <td width="30" valign="top" style="font-size: 18px; padding-right: 10px;">🕒</td>
                                                        <td valign="top">
                                                            <span style="display: block; font-size: 12px; color: #6b7280; text-transform: uppercase; font-weight: 600;">Signalé le</span>
                                                            <span style="font-size: 14px; color: #6b7280;">{date_str}</span>
                                                        </td>
                                                    </tr>
                                                </table>
                                                
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Call to Action Button -->
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                        <tr>
                                            <td align="center" style="padding-bottom: 20px;">
                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                                    <tr>
                                                        <td style="border-radius: 50px; background-color: {btn_color}; text-align: center;">
                                                            <a href="{app_url}/problemes/{incident.hebergement.id}" target="_blank" style="display: inline-block; padding: 16px 40px; font-size: 16px; font-weight: 700; color: #ffffff; text-decoration: none; border-radius: 50px; border: 1px solid {btn_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                                                Voir l'incident & Agir ➔
                                                            </a>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="margin: 0; font-size: 13px; color: #9ca3af; text-align: center; font-style: italic;">
                                        Si vous ne pouvez pas traiter cet incident, merci de prévenir Stéphane Responsable Technique immédiatement.
                                    </p>
                                    
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #f9fafb; padding: 25px 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                                    <p style="margin: 0 0 5px 0; font-size: 12px; color: #6b7280; font-weight: 600; text-transform: uppercase;">
                                        Le Phare Check — Collection Rivage
                                    </p>
                                    <p style="margin: 0; font-size: 11px; color: #9ca3af;">
                                        Service Technique & Maintenance
                                    </p>
                                </td>
                            </tr>
                            
                        </table>
                        <!-- End Main Container -->
                        
                        <!-- Spacer -->
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                            <tr>
                                <td height="40" style="font-size: 40px; line-height: 40px;">&nbsp;</td>
                            </tr>
                        </table>
                        
                    </td>
                </tr>
            </table>
        </center>
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
