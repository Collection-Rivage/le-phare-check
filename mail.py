import smtplib
import threading
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_async_email(smtp_config, msg_data):
    """Envoi direct via SSL (Port 465)"""
    try:
        message = MIMEMultipart()
        message["From"] = smtp_config['sender']
        message["To"] = msg_data['to']
        message["Subject"] = msg_data['subject']
        message.attach(MIMEText(msg_data['body'], "plain"))

        print(f"DEBUG: Tentative SSL via Port 465 vers {msg_data['to']}...")

        # Connexion SSL directe (plus stable sur Render)
        server = smtplib.SMTP_SSL(smtp_config['server'], 465, timeout=15)
        server.login(smtp_config['user'], smtp_config['password'])
        server.sendmail(smtp_config['sender'], msg_data['to'], message.as_string())
        server.quit()
        
        print(f"📩 [MAIL SUCCESS] Email envoyé avec succès !")
    except Exception as e:
        print(f"❌ [MAIL ERROR] Échec : {str(e)}")

def send_welcome_email(user, password):
    smtp_config = {
        'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        'user': os.getenv('MAIL_USERNAME'),
        'password': os.getenv('MAIL_PASSWORD'), # SANS ESPACES
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
        'user': os.getenv('MAIL_USERNAME'),
        'password': os.getenv('MAIL_PASSWORD'),
        'sender': os.getenv('MAIL_DEFAULT_SENDER')
    }
    msg_data = {
        'to': technician.email,
        'subject': "🔔 Nouvel incident assigné",
        'body': f"Bonjour {technician.username}, un incident vous a été assigné."
    }
    threading.Thread(target=send_async_email, args=(smtp_config, msg_data)).start()
    return True