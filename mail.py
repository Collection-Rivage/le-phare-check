import smtplib
import threading
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_async_email(smtp_config, msg_data):
    """Envoi direct via smtplib avec support SSL/TLS automatique"""
    try:
        message = MIMEMultipart()
        message["From"] = smtp_config['sender']
        message["To"] = msg_data['to']
        message["Subject"] = msg_data['subject']
        message.attach(MIMEText(msg_data['body'], "plain"))

        # Log de debug pour voir quel port est utilisé
        print(f"DEBUG: Tentative via port {smtp_config['port']}")

        # Si on utilise le port 465, on doit utiliser SMTP_SSL
        if smtp_config['port'] == 465:
            server = smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port'], timeout=15)
        else:
            server = smtplib.SMTP(smtp_config['server'], smtp_config['port'], timeout=15)
            server.starttls()

        server.login(smtp_config['user'], smtp_config['password'])
        server.sendmail(smtp_config['sender'], msg_data['to'], message.as_string())
        server.quit()
        
        print(f"📩 [MAIL SUCCESS] Email envoyé à {msg_data['to']}")
    except Exception as e:
        print(f"❌ [MAIL ERROR] Erreur sur Render : {str(e)}")

def send_welcome_email(user, password):
    smtp_config = {
        'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        'port': int(os.getenv('MAIL_PORT', 465)),
        'user': os.getenv('MAIL_USERNAME'),
        'password': os.getenv('MAIL_PASSWORD'),
        'sender': os.getenv('MAIL_DEFAULT_SENDER')
    }

    msg_data = {
        'to': user.email,
        'subject': "✅ Bienvenue sur Le Phare Check",
        'body': f"Bonjour {user.username},\n\nVotre compte est prêt.\nIdentifiants : {user.username} / {password}"
    }

    threading.Thread(target=send_async_email, args=(smtp_config, msg_data)).start()
    return True

def send_assignment_email(incident, technician):
    smtp_config = {
        'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        'port': int(os.getenv('MAIL_PORT', 465)),
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