from app import app
from mail import mail as mail_extension
from flask_mail import Message

with app.app_context():
    print("SERVER:", app.config['MAIL_SERVER'])
    print("PORT:", app.config['MAIL_PORT'])
    print("USERNAME:", app.config['MAIL_USERNAME'])
    print("PASSWORD:", app.config['MAIL_PASSWORD'])

    msg = Message(
        subject="Test depuis app.py",
        recipients=["stephane@lephare-iledere.com"],
        body="Si tu reçois ce message, l'intégration Resend + Flask-Mail + app.py fonctionne."
    )

    try:
        mail_extension.send(msg)
        print("✅ Mail envoyé depuis l'app Flask")
    except Exception as e:
        print("❌ Erreur envoi depuis app.py :", repr(e))