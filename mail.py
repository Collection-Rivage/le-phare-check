# mail.py - VERSION PROFESSIONNELLE & SÉCURISÉE
import resend
import os

# 🔐 Clé API via variable d'environnement (NE JAMAIS POUSSER SUR GITHUB !)
resend.api_key = os.getenv("RESEND_API_KEY")  # ← Configure dans Render > Environment

def send_welcome_email(user, password):
    try:
        resend.Emails.send({
            "from": "Le Phare Check <contact@lephare-iledere.com>",  # ← Utilise ton domaine une fois vérifié
            "to": [user.email],
            "subject": "Bienvenue sur Le Phare Check — Vos identifiants",
            "html": f"""
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
                    @media (max-width: 600px) {{
                        .container {{ margin: 10px; }}
                        .button {{ width: 100%; text-align: center; }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>LE PHARE CHECK</h1>
                        <p>Collection Rivage — Gestion des hébergements</p>
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
                            <a href="https://le-phare-check.onrender.com/login" class="button">Se connecter à l’application</a>
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
        })
        print(f"✅ Email bienvenue envoyé à {user.email}")
        return True
    except Exception as e:
        print(f"❌ Erreur Resend (bienvenue): {e}")
        return False

def send_assignment_email(incident, technicien):
    try:
        resend.Emails.send({
            "from": "Le Phare Check <contact@lephare-iledere.com>",
            "to": [technicien.email],
            "subject": f"🚨 Incident assigné — {incident.hebergement.emplacement}",
            "html": f"""
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
                    .button {{ display: inline-block; background-color: #e74c3c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 15px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; border-top: 1px solid #ecf0f1; }}
                    @media (max-width: 600px) {{
                        .container {{ margin: 10px; }}
                        .button {{ width: 100%; text-align: center; }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚨 Nouvel incident assigné</h1>
                    </div>
                    <div class="content">
                        <h2>Bonjour {technicien.username},</h2>
                        <p>Un nouvel incident vous a été assigné et nécessite votre intervention.</p>
                        
                        <div class="incident-box">
                            <p><strong>Hébergement :</strong> {incident.hebergement.emplacement}</p>
                            <p><strong>Type :</strong> {incident.type_incident}</p>
                            <p><strong>Description :</strong> {incident.description}</p>
                        </div>
                        
                        <center>
                            <a href="https://le-phare-check.onrender.com/problemes/{incident.hebergement.id}" class="button">Voir l'incident</a>
                        </center>
                    </div>
                    <div class="footer">
                        <p>Cet email a été envoyé automatiquement par Le Phare Check.</p>
                        <p>© 2025 Collection Rivage — Tous droits réservés</p>
                    </div>
                </div>
            </body>
            </html>
            """
        })
        print(f"✅ Email assignation envoyé à {technicien.email}")
        return True
    except Exception as e:
        print(f"❌ Erreur Resend (assignation): {e}")
        return False
