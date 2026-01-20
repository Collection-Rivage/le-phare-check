from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def send_alert_email(check, hebergement, technicien):
    """Envoie un email d'alerte en cas de problème"""
    
    # Liste des problèmes détectés
    problemes = []
    if not check.electricite:
        problemes.append("Électricité")
    if not check.plomberie:
        problemes.append("Plomberie")
    if not check.chauffage:
        problemes.append("Chauffage")
    if not check.proprete:
        problemes.append("Propreté")
    if not check.equipements:
        problemes.append("Équipements")
    
    if not problemes and not check.probleme_critique:
        return  # Pas d'email si tout va bien
    
    # Construction du message
    sujet = f"🚨 Alerte - {hebergement.nom}"
    
    corps = f"""
    Alerte Le Phare Check
    =====================
    
    Hébergement : {hebergement.nom} ({hebergement.type})
    Zone : {hebergement.zone or 'N/A'}
    Technicien : {technicien.username}
    Date : {check.created_at.strftime('%d/%m/%Y %H:%M')}
    
    Problèmes détectés :
    {chr(10).join(['❌ ' + p for p in problemes])}
    
    {"⚠️ PROBLÈME CRITIQUE SIGNALÉ" if check.probleme_critique else ""}
    
    Observations :
    {check.observations or 'Aucune observation'}
    
    ---
    Le Phare Collection Rivage
    """
    
    msg = Message(
        sujet,
        recipients=[current_app.config.get('MAIL_DEFAULT_SENDER')],  # À adapter
        body=corps
    )
    
    mail.send(msg)
