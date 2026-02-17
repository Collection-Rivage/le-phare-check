# mail.py - Version Brevo (Solution de secours fiable)
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# === COLLE TA CLÉ BREVO ICI (celle qui commence par xkeysib-) ===
API_KEY = "xsmtpsib-2b4db7b15ad4e38ed80adc16700aeb1fb7ae39f69bf73b0dfa9b5ef0d172943b-ddu71NUUzMNGJWmq" 

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = API_KEY
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

def send_welcome_email(user, password):
    app_url = "https://le-phare-check.onrender.com"
    
    subject = f"Bienvenue sur Le Phare Check - {user.username}"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background:#f4f4f4; padding:20px;">
        <div style="max-width:600px; margin:0 auto; background:white; border-radius:10px; overflow:hidden;">
            <div style="background:#2c3e50; color:white; padding:30px; text-align:center;">
                <h1>LE PHARE CHECK</h1>
            </div>
            <div style="padding:40px 30px;">
                <h2>Bonjour {user.username},</h2>
                <p>Stéphane vous invite à utiliser l'application.</p>
                
                <div style="background:#f8f9fa; border-left:4px solid #3498db; padding:20px; margin:25px 0;">
                    <p><strong>Utilisateur :</strong> {user.username}</p>
                    <p><strong>Mot de passe :</strong> <span style="background:#fff3cd; padding:5px 10px; border-radius:3px; font-family:monospace;">{password}</span></p>
                </div>
                
                <center>
                    <a href="{app_url}/login" style="background:#3498db; color:white; padding:15px 30px; text-decoration:none; border-radius:5px; font-weight:bold;">Se connecter</a>
                </center>
            </div>
        </div>
    </body>
    </html>
    """

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        sender={"name": "Le Phare Check", "email": "stephane@lephare-iledere.com"},
        to=[{"email": user.email, "name": user.username}],
        subject=subject,
        html_content=html_content
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Email Brevo envoyé à {user.email} (ID: {api_response.message_id})")
        return True
    except ApiException as e:
        print(f"❌ Erreur Brevo : {e}")
        return False

def send_assignment_email(incident, technicien):
    app_url = "https://le-phare-check.onrender.com"
    
    subject = f"Incident assigné : {incident.hebergement.emplacement}"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Bonjour {technicien.username},</h2>
        <p>Un incident vous a été assigné :</p>
        <ul>
            <li><strong>Lieu :</strong> {incident.hebergement.emplacement}</li>
            <li><strong>Type :</strong> {incident.type_incident}</li>
            <li><strong>Description :</strong> {incident.description}</li>
        </ul>
        <a href="{app_url}/problemes/{incident.hebergement.id}" style="background:#e74c3c; color:white; padding:10px 20px; text-decoration:none;">Voir l'incident</a>
    </body>
    </html>
    """

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        sender={"name": "Le Phare Check Alertes", "email": "stephane@lephare-iledere.com"},
        to=[{"email": technicien.email, "name": technicien.username}],
        subject=subject,
        html_content=html_content
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Email incident envoyé à {technicien.email}")
        return True
    except ApiException as e:
        print(f"❌ Erreur Brevo incident : {e}")
        return False
