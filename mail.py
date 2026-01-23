from flask_mail import Mail, Message
from flask import current_app
import os

mail = Mail()

def send_welcome_email(user, password):
    """Envoyer un email d'invitation quand un nouvel utilisateur est créé"""
    app_url = current_app.config.get('APP_URL', 'https://le-phare-check.onrender.com')
    
    msg = Message(
        subject="✅ Votre compte Le Phare Check a été créé",
        sender=("Le Phare Check", current_app.config['MAIL_DEFAULT_SENDER']),
        recipients=[user.email]
    )
    
    msg.body = f"""
Bonjour {user.username},

Votre compte sur l'application Le Phare Check a été créé avec succès !

📋 Vos identifiants de connexion :
👤 Nom d'utilisateur : {user.username}
🔑 Mot de passe temporaire : {password}

🌐 Lien de connexion : {app_url}

🔒 Pour votre sécurité, nous vous recommandons de changer ce mot de passe temporaire dès votre première connexion.

Cordialement,
L'équipe Le Phare Collection Rivage
"""

    msg.html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto; padding: 20px; background: #f8f9fa; border-radius: 10px;">
        <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.08);">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #1a3a52; margin: 0;">
                    <span style="color: #28a745;">✅</span> Bienvenue sur Le Phare Check
                </h1>
            </div>

            <p>Bonjour <strong>{user.username}</strong>,</p>
            <p>Votre compte sur l'application de gestion technique du Phare Collection Rivage a été créé avec succès.</p>

            <div style="background: #f8f9fa; padding: 20px; border-radius: 6px; margin: 25px 0;">
                <p style="margin: 0 0 10px 0;"><strong>📋 Vos identifiants de connexion :</strong></p>
                <p style="margin: 5px 0;"><strong>👤 Nom d'utilisateur :</strong> {user.username}</p>
                <p style="margin: 5px 0;"><strong>🔑 Mot de passe temporaire :</strong> <span style="font-family: monospace; font-weight: bold;">{password}</span></p>
            </div>

            <p style="text-align: center; margin: 30px 0;">
                <a href="{app_url}" style="background: #1a3a52; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                    🌐 Accéder à l'application
                </a>
            </p>

            <div style="color: #6c757d; font-size: 0.9em; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e9ecef;">
                <p style="margin: 5px 0;">
                    <strong>🔒 Conseil de sécurité :</strong> Nous vous recommandons de changer ce mot de passe temporaire dès votre première connexion.
                </p>
                <p style="margin: 15px 0 5px 0;">Cordialement,</p>
                <p style="margin: 0;">L'équipe Le Phare Collection Rivage</p>
            </div>
        </div>
    </div>
    """
    
    try:
        mail.send(msg)
        print(f"📩 Email d'invitation envoyé à {user.email}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email : {str(e)}")
        return False

def send_assignment_email(incident, technician):
    """Envoyer un email de notification quand un incident est assigné à un technicien"""
    app_url = current_app.config.get('APP_URL', 'https://le-phare-check.onrender.com')
    
    msg = Message(
        subject="🔔 Un incident vous a été assigné sur Le Phare Check",
        sender=("Le Phare Check", current_app.config['MAIL_DEFAULT_SENDER']),
        recipients=[technician.email]
    )
    
    msg.body = f"""
Bonjour {technician.username},

Un incident vous a été assigné sur l'application Le Phare Check.

📋 Détails de l'incident :
🏠 Hébergement concerné : {incident.hebergement.emplacement}
⚠️ Type d'incident : {incident.type_incident}
📝 Description : {incident.description}

🌐 Vous pouvez consulter et traiter cet incident depuis l'application : {app_url}

Cordialement,
L'équipe Le Phare Collection Rivage
"""

    msg.html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto; padding: 20px; background: #f8f9fa; border-radius: 10px;">
        <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.08);">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #dc3545; margin: 0;">
                    <span style="color: #dc3545;">🔔</span> Un incident vous a été assigné
                </h1>
            </div>

            <p>Bonjour <strong>{technician.username}</strong>,</p>
            <p>Un incident vous a été assigné sur l'application Le Phare Check.</p>

            <div style="background: #fff3cd; padding: 20px; border-radius: 6px; margin: 25px 0; border-left: 4px solid #ffc107;">
                <p style="margin: 0 0 15px 0;"><strong>📋 Détails de l'incident :</strong></p>
                <p style="margin: 5px 0;"><strong>🏠 Hébergement concerné :</strong> {incident.hebergement.emplacement}</p>
                <p style="margin: 5px 0;"><strong>⚠️ Type d'incident :</strong> {incident.type_incident.replace('urgence', 'Urgence').replace('probleme', 'Problème technique')}</p>
                <p style="margin: 5px 0;"><strong>📝 Description :</strong> {incident.description}</p>
            </div>

            <p style="text-align: center; margin: 30px 0;">
                <a href="{app_url}" style="background: #dc3545; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                    🚗 Accéder à l'application pour traiter l'incident
                </a>
            </p>

            <div style="color: #6c757d; font-size: 0.9em; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e9ecef;">
                <p style="margin: 0;">Cordialement,</p>
                <p style="margin: 0;">L'équipe Le Phare Collection Rivage</p>
            </div>
        </div>
    </div>
    """
    
    try:
        mail.send(msg)
        print(f"📩 Email d'assignation envoyé à {technician.email}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email d'assignation : {str(e)}")
        return False
