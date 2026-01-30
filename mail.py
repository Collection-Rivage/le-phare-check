import smtplib
import threading
import os
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_mail import Mail

mail = Mail()

def send_async_email(smtp_config, msg_data):
    """Envoi direct via smtplib en forçant l'IPv4 pour éviter Errno 101"""
    try:
        # Création du message
        message = MIMEMultipart()
        message["From"] = smtp_config['sender']
        message["To"] = msg_data['to']
        message["Subject"] = msg_data['subject']
        message.attach(MIMEText(msg_data['body'], "plain"))

        print(f"DEBUG: Tentative d'envoi à {msg_data['to']} via Port {smtp_config['port']}...")

        # FORCE IPV4 : On résout l'adresse de Gmail manuellement pour éviter IPv6
        gmail_ip = socket.gethostbyname(smtp_config['server'])
        
        # Connexion au serveur
        server = smtplib.SMTP(gmail_ip, smtp_config['port'], timeout=20)
        server.set_debuglevel(1) # Pour voir les détails dans les logs Render
        server.starttls()
        server.login(smtp_config['user'], smtp_config['password'])
        server.sendmail(smtp_config['sender'], msg_data['to'], message.as_string())
        server.quit()
        
        print(f"📩 [MAIL SUCCESS] Enfin envoyé à {msg_data['to']} !")
    except Exception as e:
        print(f"❌ [MAIL ERROR] Échec sur Render : {str(e)}")

def send_welcome_email(user, password):
    # On récupère les réglages
    smtp_config = {
        'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        'port': int(os.getenv('MAIL_PORT', 587)),
        'user': os.getenv('MAIL_USERNAME'),
        'password': os.getenv('MAIL_PASSWORD'),
        'sender': os.getenv('MAIL_DEFAULT_SENDER')
    }

    msg_data = {
        'to': user.email,
        'subject': "✅ Bienvenue sur Le Phare Check",
        'body': f"Bonjour {user.username},\n\nVotre compte est prêt.\nUtilisateur : {user.username}\nMot de passe : {password}"
    }

    # Lancement du Thread
    threading.Thread(target=send_async_email, args=(smtp_config, msg_data)).start()
    return True

def send_assignment_email(incident, technician):
    # Même logique pour les incidents
    smtp_config = {
        'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        'port': int(os.getenv('MAIL_PORT', 587)),
        'user': os.getenv('MAIL_USERNAME'),
        'password': os.getenv('MAIL_PASSWORD'),
        'sender': os.getenv('MAIL_DEFAULT_SENDER')
    }
    msg_data = {
        'to': technician.email,
        'subject': "🔔 Incident assigné",
        'body': f"Bonjour {technician.username}, un incident vous attend à {incident.hebergement.emplacement}."
    }
    threading.Thread(target=send_async_email, args=(smtp_config, msg_data)).start()
    return True