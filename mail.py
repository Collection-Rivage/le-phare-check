from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def send_welcome_email(user, password):
    """
    Envoie un email de bienvenue avec identifiants
    """
    app_url = current_app.config.get('APP_URL', 'https://le-phare-check.onrender.com')
    
    msg = Message(
        subject="Bienvenue sur Le Phare Check !",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email]
    )
    
    msg.body = f"""
Bonjour {user.username},

Votre compte Le Phare Check a été créé avec succès !

Voici vos identifiants :

Utilisateur : {user.username}
Mot de passe : {password}

Lien de connexion : {app_url}

Pensez à changer votre mot de passe dès votre première connexion.

Cordialement,
L'équipe Le Phare Collection Rivage
"""

    msg.html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f9f9f9; border-radius: 10px;">
        <h2 style="color: #1a3a52; text-align: center;">Le Phare Check</h2>
        <hr style="border: 1px solid #1a3a52;">
        
        <p>Bonjour <strong>{user.username}</strong>,</p>
        <p>Votre compte a été créé avec succès !</p>
        
        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <p><strong style="color: #1a3a52;">Identifiant :</strong> {user.username}</p>
            <p><strong style="color: #1a3a52;">Mot de passe :</strong> {password}</p>
        </div>
        
        <p style="text-align: center;">
            <a href="{app_url}" style="background: #1a3a52; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-size: 16px;">
                Accéder à l'application
            </a>
        </p>
        
        <p style="color: #666; font-size: 0.9em;">
            <small>Pour votre sécurité, changez votre mot de passe dès votre première connexion.</small>
        </p>
        
        <hr style="border: 1px solid #ddd; margin: 30px 0;">
        <p style="text-align: center; color: #666; font-size: 0.8em;">
            Le Phare Collection Rivage<br>
            Application de gestion technique
        </p>
    </div>
    """
    
    try:
        mail.send(msg)
        print(f"Email envoyé à {user.email}")
    except Exception as e:
        print(f"Échec envoi email à {user.email} : {e}")
