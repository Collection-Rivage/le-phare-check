import smtplib
import threading
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_mail import Mail

# Cet objet permet à app.py de ne pas crasher à l'importation
mail = Mail()

def send_async_email(smtp_config, msg_data):
    """Fonction d'envoi en arrière-plan avec logs détaillés"""
    print(f"🚀 [MAIL] Démarrage de l'envoi pour {msg_data['to']}...", flush=True)
    
    try:
        # 1. Création du message
        message = MIMEMultipart()
        message["From"] = smtp_config['sender']
        message["To"] = msg_data['to']
        message["Subject"] = msg_data['subject']
        message.attach(MIMEText(msg_data['body'], "plain"))

        # 2. Connexion SSL au Port 465
        print(f"📡 [MAIL] Connexion à {smtp_config['server']} sur le port 465...", flush=True)
        
        # On utilise un timeout de 20 secondes pour ne pas rester bloqué
        with smtplib.SMTP_SSL(smtp_config['server'], 465, timeout=20) as server:
            print(f"🔑 [MAIL] Authentification pour {smtp_config['user']}...", flush=True)
            server.login(smtp_config['user'], smtp_config['password'])
            
            print(f"📤 [MAIL] Envoi en cours...", flush=True)
            server.sendmail(smtp_config['sender'], msg_data['to'], message.as_string())
            
        print(f"✅ [MAIL SUCCESS] Email bien envoyé à {msg_data['to']} !", flush=True)
        
    except smtplib.SMTPAuthenticationError:
        print(f"❌ [MAIL ERROR] Identifiants incorrects. Vérifiez le mot de passe d'application (16 lettres).", flush=True, file=sys.stderr)
    except Exception as e:
        print(f"❌ [MAIL ERROR] Détails de l'erreur : {str(e)}", flush=True, file=sys.stderr)

def send_welcome_email(user, password):
    """Prépare le mail de bienvenue et lance le thread"""
    print(f"📝 [MAIL] Préparation mail de bienvenue pour {user.email}", flush=True)
    
    smtp_config = {
        'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        'user': os.getenv('MAIL_USERNAME'),
        'password': os.getenv('MAIL_PASSWORD'), # Sans espaces
        'sender': os.getenv('MAIL_DEFAULT_SENDER')
    }

    msg_data = {
        'to': user.email,
        'subject': "✅ Votre compte Le Phare Check",
        'body': f"Bonjour {user.username},\n\nVotre compte est prêt.\nIdentifiants : {user.username} / {password}"
    }

    # On lance la tâche de fond
    threading.Thread(target=send_async_email, args=(smtp_config, msg_data)).start()
    return True

def send_assignment_email(incident, technician):
    """Prépare le mail d'assignation et lance le thread"""
    print(f"📝 [MAIL] Préparation mail d'assignation pour {technician.email}", flush=True)
    
    smtp_config = {
        'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        'user': os.getenv('MAIL_USERNAME'),
        'password': os.getenv('MAIL_PASSWORD'),
        'sender': os.getenv('MAIL_DEFAULT_SENDER')
    }

    msg_data = {
        'to': technician.email,
        'subject': "🔔 Nouvel incident assigné",
        'body': f"Bonjour {technician.username}, un incident vous a été assigné à l'hébergement {incident.hebergement.emplacement}."
    }

    threading.Thread(target=send_async_email, args=(smtp_config, msg_data)).start()
    return True