from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def send_welcome_email(user, password):
    """Envoie un email de bienvenue HTML avec lien de connexion"""
    try:
        app_url = current_app.config.get('APP_URL', 'https://le-phare-check.onrender.com')
        
        # Version HTML avec .format() pour éviter les conflits d'accolades
        html_body = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .header {{ background-color: #2c3e50; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 40px 30px; }}
                .credentials {{ background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                .credential-item {{ margin: 10px 0; font-size: 16px; }}
                .label {{ font-weight: bold; color: #2c3e50; }}
                .password {{ font-family: monospace; background-color: #fff3cd; padding: 5px 10px; border-radius: 3px; font-size: 18px; color: #856404; }}
                .button {{ display: inline-block; background-color: #3498db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
                .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 14px; }}
                .footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; border-top: 1px solid #ecf0f1; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>LE PHARE CHECK - COLLECTION RIVAGE</h1>
                </div>
                
                <div class="content">
                    <h2>Bonjour {username},</h2>
                    <p>Stéphane Responsable technique vous invite à utiliser l'application Le Phare Check.</p>
                    
                    <div class="credentials">
                        <h3 style="margin-top: 0; color: #2c3e50;">Vos identifiants de connexion</h3>
                        <div class="credential-item">
                            <span class="label">Nom d'utilisateur :</span> {username}
                        </div>
                        <div class="credential-item">
                            <span class="label">Mot de passe temporaire :</span><br>
                            <span class="password">{password}</span>
                        </div>
                    </div>
                    
                    <center>
                        <a href="{app_url}/login" class="button">Se connecter à l'application</a>
                    </center>
                    
                    <div class="warning">
                        <strong>⚠️ Important :</strong> Pour des raisons de sécurité, vous devez changer votre mot de passe dès votre première connexion.
                    </div>
                </div>
                
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement par Le Phare Check.</p>
                </div>
            </div>
        </body>
        </html>
        """.format(app_url=app_url, username=user.username, password=password)
        
        # Version texte
        text_body = """Bonjour {username},

Stéphane Responsable technique vous invite à utiliser l'application Le Phare Check.

Vos identifiants :
- Utilisateur : {username}
- Mot de passe : {password}

Lien de connexion : {app_url}/login

Important : Changez votre mot de passe dès la première connexion.
""".format(app_url=app_url, username=user.username, password=password)
        
        msg = Message(
            subject="Bienvenue sur Le Phare Check - Vos identifiants",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user.email],
            body=text_body,
            html=html_body
        )
        
        mail.send(msg)
        print(f"✅ Email envoyé avec succès à {user.email}")
        return True
        
    except Exception as e:
        print(f"❌ ERREUR EMAIL : {str(e)}")
        import traceback
        traceback.print_exc()  # Affiche l'erreur complète dans le terminal
        return False

def send_assignment_email(incident, technicien):
    """Envoie un email HTML quand un incident est assigné"""
    try:
        app_url = current_app.config.get('APP_URL', 'https://le-phare-check.onrender.com')
        
        html_body = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .header {{ background-color: #e74c3c; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 40px 30px; }}
                .incident-box {{ background-color: #fdf2f2; border-left: 4px solid #e74c3c; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                .button {{ display: inline-block; background-color: #e74c3c; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
                .footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; border-top: 1px solid #ecf0f1; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Nouvel incident assigné</h1>
                </div>
                
                <div class="content">
                    <h2>Bonjour {username},</h2>
                    <p>Un nouvel incident vous a été assigné et nécessite votre intervention.</p>
                    
                    <div class="incident-box">
                        <h3 style="margin-top: 0; color: #e74c3c;">Détails de l'incident</h3>
                        <p><strong>Hébergement :</strong> {emplacement}</p>
                        <p><strong>Type :</strong> {type_incident}</p>
                        <p><strong>Description :</strong> {description}</p>
                    </div>
                    
                    <center>
                        <a href="{app_url}/problemes/{hebergement_id}" class="button">Voir l'incident</a>
                    </center>
                </div>
                
                <div class="footer">
                    <p>LE PHARE CHECK - COLLECTION RIVAGE</p>
                </div>
            </div>
        </body>
        </html>
        """.format(
            app_url=app_url,
            username=technicien.username,
            emplacement=incident.hebergement.emplacement,
            type_incident=incident.type_incident,
            description=incident.description,
            hebergement_id=incident.hebergement.id
        )
        
        text_body = f"""Bonjour {technicien.username},

Un nouvel incident vous a été assigné :
Hébergement : {incident.hebergement.emplacement}
Type : {incident.type_incident}

Lien : {app_url}/problemes/{incident.hebergement.id}
"""
        
        msg = Message(
            subject=f"🚨 Incident assigné - {incident.hebergement.emplacement}",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[technicien.email],
            body=text_body,
            html=html_body
        )
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"❌ Erreur email assignation : {str(e)}")
        return False