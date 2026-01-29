import smtplib
import threading
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

# Initialisation pour ne pas casser app.py
from flask_mail import Mail
mail = Mail()

def send_async_email(smtp_config, msg_data):
    """Envoi direct via smtplib (plus rapide et stable sur Render)"""
    try:
        message = MIMEMultipart()
        message["From"] = smtp_config['sender']
        message["To"] = msg_data['to']
        message["Subject"] = msg_data['subject']
        message.attach(MIMEText(msg_data['body'], "plain"))

        with smtplib.SMTP(smtp_config['server'], smtp_config['port'], timeout=15) as server:
            server.starttls()
            server.login(smtp_config['user'], smtp_config['password'])
            server.sendmail(smtp_config['sender'], msg_data['to'], message.as_string())
        
        print(f"📩 [MAIL SUCCESS] Envoyé à {msg_data['to']}")
    except Exception as e:
        print(f"❌ [MAIL ERROR] Échec : {str(e)}")

def send_welcome_email(user, password):
    # Récupération des données depuis les variables Render (image)
    smtp_config = {
        'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        'port': int(os.getenv('MAIL_PORT', 587)),
        'user': os.getenv('MAIL_USERNAME'),
        'password': os.getenv('MAIL_PASSWORD'),
        'sender': os.getenv('MAIL_DEFAULT_SENDER') # Attention au R final
    }

    msg_data = {
        'to': user.email,
        'subject': "✅ Votre compte Le Phare Check",
        'body': f"Bonjour {user.username},\n\nVotre compte a été créé.\nUtilisateur : {user.username}\nMot de passe : {password}"
    }

    threading.Thread(target=send_async_email, args=(smtp_config, msg_data)).start()
    return True

def send_assignment_email(incident, technician):
    smtp_config = {
        'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        'port': int(os.getenv('MAIL_PORT', 587)),
        'user': os.getenv('MAIL_USERNAME'),
        'password': os.getenv('MAIL_PASSWORD'),
        'sender': os.getenv('MAIL_DEFAULT_SENDER')
    }

    msg_data = {
        'to': technician.email,
        'subject': "🔔 Nouvel incident assigné",
        'body': f"Bonjour {technician.username},\n\nUn incident vous a été assigné à {incident.hebergement.emplacement}."
    }

    threading.Thread(target=send_async_email, args=(smtp_config, msg_data)).start()
    return True