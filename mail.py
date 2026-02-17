import resend

# TA CLÉ RESEND
resend.api_key = "re_MK4pWNHu_3176dxmyuYA77kQDFz78Z6tY"  # Mets ta vraie clé ici

def send_welcome_email(user, password):
    app_url = "https://le-phare-check.onrender.com"
    
    # DEBUG : Affiche ce qu'on essaie d'envoyer dans les logs Render
    print(f"🚀 TENTATIVE ENVOI À : {user.email}")
    print(f"📩 DEPUIS : Le Phare Check <hello@resend.dev>")
    
    try:
        info = resend.Emails.send({
            "from": "Le Phare Check <hello@resend.dev>",  # ON CHANGE POUR hello@
            "to": [user.email],
            "subject": "Bienvenue sur Le Phare Check",
            "html": f"<h1>Bonjour {user.username}</h1><p>Mot de passe : {password}</p>"
        })
        print(f"✅ SUCCÈS RESSEND : {info}")
        return True
    except Exception as e:
        print(f"❌ ERREUR RESSEND : {str(e)}")
        return False

def send_assignment_email(incident, technicien):
    app_url = "https://le-phare-check.onrender.com"
    
    print(f"🚀 TENTATIVE ENVOI INCIDENT À : {technicien.email}")
    
    try:
        info = resend.Emails.send({
            "from": "Le Phare Check <hello@resend.dev>", # ON CHANGE POUR hello@
            "to": [technicien.email],
            "subject": f"Incident : {incident.hebergement.emplacement}",
            "html": f"<h1>Incident</h1><p>{incident.description}</p>"
        })
        print(f"✅ SUCCÈS RESSEND : {info}")
        return True
    except Exception as e:
        print(f"❌ ERREUR RESSEND : {str(e)}")
        return False
