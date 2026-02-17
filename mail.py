# mail.py - Version Resend (marche à 100% en production)
import resend

# COLLE TA CLÉ RESEND ICI (celle qui commence par re_)
resend.api_key = 're_MK4pWNHu_3176dxmyuYA77kQDFz78Z6tY'

def send_welcome_email(user, password):
    app_url = "https://le-phare-check.onrender.com"
    
    try:
        resend.Emails.send({
            "from": "Le Phare Check <notifications@resend.dev>",
            "to": [user.email],
            "subject": "Bienvenue sur Le Phare Check - Vos identifiants",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                    .header {{ background-color: #2c3e50; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ padding: 40px 30px; }}
                    .credentials {{ background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .password {{ font-family: monospace; background-color: #fff3cd; padding: 8px 12px; border-radius: 5px; font-size: 18px; }}
                    .button {{ display: inline-block; background-color: #3498db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
                    .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 5px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>LE PHARE CHECK - COLLECTION RIVAGE</h1>
                    </div>
                    <div class="content">
                        <h2>Bonjour {user.username},</h2>
                        <p>Stéphane Responsable technique vous invite à utiliser l'application Le Phare Check.</p>
                        
                        <div class="credentials">
                            <p><strong>Nom d'utilisateur :</strong> {user.username}</p>
                            <p><strong>Mot de passe temporaire :</strong><br>
                                <span class="password">{password}</span>
                            </p>
                        </div>
                        
                        <center>
                            <a href="{app_url}/login" class="button">Se connecter</a>
                        </center>
                        
                        <div class="warning">
                            <strong>Important :</strong> Changez votre mot de passe dès la première connexion.
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
        })
        print(f"Email bienvenue envoyé à {user.email}")
        return True
    except Exception as e:
        print(f"Erreur Resend (bienvenue): {e}")
        return False

def send_assignment_email(incident, technicien):
    app_url = "https://le-phare-check.onrender.com"
    
    try:
        resend.Emails.send({
            "from": "Le Phare Check <notifications@resend.dev>",
            "to": [technicien.email],
            "subject": f"Incident assigné - {incident.hebergement.emplacement}",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; }}
                    .header {{ background-color: #e74c3c; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ padding: 40px 30px; }}
                    .incident-box {{ background-color: #fdf2f2; border-left: 4px solid #e74c3c; padding: 20px; margin: 20px 0; }}
                    .button {{ background-color: #e74c3c; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Nouvel incident assigné</h1>
                    </div>
                    <div class="content">
                        <h2>Bonjour {technicien.username},</h2>
                        <p>Un incident nécessite votre intervention :</p>
                        <div class="incident-box">
                            <p><strong>Hébergement :</strong> {incident.hebergement.emplacement}</p>
                            <p><strong>Type :</strong> {incident.type_incident}</p>
                            <p><strong>Description :</strong> {incident.description}</p>
                        </div>
                        <center>
                            <a href="{app_url}/problemes/{incident.hebergement.id}" class="button">Voir l'incident</a>
                        </center>
                    </div>
                </div>
            </body>
            </html>
            """
        })
        print(f"Email assignation envoyé à {technicien.email}")
        return True
    except Exception as e:
        print(f"Erreur Resend (assignation): {e}")
        return False