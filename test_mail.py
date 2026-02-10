import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()

# Test de connexion SMTP
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(
        os.getenv('MAIL_USERNAME'), 
        os.getenv('MAIL_PASSWORD')
    )
    print("✅ Connexion SMTP réussie !")
    
    # Test d'envoi
    msg = MIMEText("Ceci est un test")
    msg['Subject'] = "Test LePhare"
    msg['From'] = os.getenv('MAIL_USERNAME')
    msg['To'] = os.getenv('MAIL_USERNAME')
    
    server.send_message(msg)
    print("✅ Email de test envoyé !")
    server.quit()
    
except Exception as e:
    print(f"❌ Erreur : {e}")
    print(f"Username : {os.getenv('MAIL_USERNAME')}")
    print(f"Password : {'*' * len(os.getenv('MAIL_PASSWORD', ''))} (longueur: {len(os.getenv('MAIL_PASSWORD', ''))})")