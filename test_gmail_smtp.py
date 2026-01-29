import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

load_dotenv()

app = Flask(__name__)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT') or 587)
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

with app.app_context():
    print("SERVER:", app.config['MAIL_SERVER'])
    print("PORT:", app.config['MAIL_PORT'])
    print("USERNAME:", app.config['MAIL_USERNAME'])

    msg = Message(
        subject="Test Gmail SMTP depuis Le Phare Check",
        recipients=[os.getenv('MAIL_USERNAME')],  # envoi vers ton propre Gmail
        body="Si tu reçois ce message, la config Gmail SMTP est OK."
    )

    try:
        mail.send(msg)
        print("✅ Mail envoyé avec succès via Gmail SMTP !")
    except Exception as e:
        print("❌ Erreur SMTP Gmail :", repr(e))