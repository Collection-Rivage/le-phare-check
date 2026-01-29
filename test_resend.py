# test_resend.py
import os
from dotenv import load_dotenv
import resend

# Charger les variables du fichier .env
load_dotenv()

# Configurer Resend
resend.api_key = os.getenv("RESEND_API_KEY")

try:
    # Envoyer un email de test
    response = resend.Emails.send({
        "from": "Le Phare <onboarding@resend.dev>",  # Sender temporaire
        "to": ["stephane@lephare-iledere.com"],  # Votre email de test
        "subject": "Test de configuration Resend",
        "html": "<strong>Si vous voyez ce message, l'envoi fonctionne !</strong>"
    })
    print("✅ SUCCÈS ! ID du message:", response["id"])
    print("📧 Vérifiez votre boîte email (et spams)")
except Exception as e:
    print("❌ Échec de l'envoi :", str(e))
    print("Vérifiez votre clé API et votre compte Resend")