import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'
    
    # Configuration de la base de données
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Convertir pour utiliser pg8000 (compatible Windows)
        if database_url.startswith('postgresql://'):
            SQLALCHEMY_DATABASE_URI = database_url.replace('postgresql://', 'postgresql+pg8000://', 1)
        else:
            SQLALCHEMY_DATABASE_URI = database_url
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///lephare.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Options de connexion simplifiées
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # 📧 CONFIGURATION EMAIL AVEC RESEND (remplace Brevo/Gmail)
    MAIL_SERVER = 'smtp.resend.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'resend'  # Toujours 'resend' avec Resend
    MAIL_PASSWORD = os.environ.get('RESEND_API_KEY')  # Clé API Resend
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'stephane@lephare-iledere.com'