from flask_mail import Mail, Message
from flask import current_app

# Extension Flask-Mail, initialisée dans app.py
mail = Mail()


def _debug_config():
    """Affiche la config mail utilisée (utile dans les logs Render)."""
    print("=== [MAIL CONFIG] ===")
    print("MAIL_SERVER        :", current_app.config.get("MAIL_SERVER"))
    print("MAIL_PORT          :", current_app.config.get("MAIL_PORT"))
    print("MAIL_USE_TLS       :", current_app.config.get("MAIL_USE_TLS"))
    print("MAIL_USE_SSL       :", current_app.config.get("MAIL_USE_SSL"))
    print("MAIL_USERNAME      :", current_app.config.get("MAIL_USERNAME"))
    print("MAIL_DEFAULT_SENDER:", current_app.config.get("MAIL_DEFAULT_SENDER"))
    print("APP_URL            :", current_app.config.get("APP_URL"))
    print("=====================")


def send_welcome_email(user, password):
    """Envoie le mail de bienvenue lors de la création d'un compte."""

    print(f"[MAIL] Préparation mail de bienvenue pour {user.email}")
    _debug_config()

    base_url = current_app.config.get("APP_URL", "https://le-phare-check.onrender.com")
    # URL vers la page de login
    login_url = f"{base_url.rstrip('/')}/login"

    subject = "Invitation à utiliser l’application Le Phare Check ✅"

    # Texte brut (fallback si HTML non supporté)
    body_text = f"""Bonjour {user.username},

Stéphane, Responsable Technique, vous invite à utiliser l’application Le Phare Check.

Votre compte a été créé et vous permet d’accéder à l’outil de suivi technique du Phare Collection Rivage.

Voici vos identifiants de connexion :

  • Utilisateur : {user.username}
  • Mot de passe temporaire : {password}

Page de connexion : {login_url}

IMPORTANT :
Pour votre sécurité, vous devez changer ce mot de passe temporaire dès votre première connexion,
depuis votre profil utilisateur.

À bientôt,
L'équipe Le Phare Collection Rivage
"""

    # HTML
    body_html = f"""
    <div style="font-family: Arial, sans-serif; background-color:#f5f7fb; padding:20px;">
      <div style="max-width:600px; margin:0 auto; background:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        
        <!-- En-tête -->
        <div style="background:linear-gradient(135deg,#0d3b66,#1d7fbf); color:#ffffff; padding:20px 24px;">
          <h1 style="margin:0; font-size:22px;">
            Le Phare Check
          </h1>
          <p style="margin:4px 0 0; font-size:14px; opacity:0.9;">
            Application de suivi technique du Phare Collection Rivage
          </p>
        </div>

        <!-- Contenu -->
        <div style="padding:24px;">
          <p style="font-size:16px; margin:0 0 16px 0;">
            Bonjour <strong>{user.username}</strong>,
          </p>

          <p style="margin:0 0 10px 0; font-size:14px; color:#444;">
            <strong>Stéphane, Responsable Technique, vous invite à utiliser l’application Le Phare Check.</strong>
          </p>

          <p style="margin:0 0 16px 0; font-size:14px; color:#444;">
            Votre compte a été créé et vous permet d’accéder à l’outil de suivi technique du
            <strong>Phare Collection Rivage</strong>.
          </p>

          <div style="background:#f5f7fb; border-radius:6px; padding:16px; margin:16px 0;">
            <p style="margin:0 0 10px 0; font-weight:bold; color:#0d3b66;">
              Vos identifiants de connexion :
            </p>
            <p style="margin:4px 0; font-size:14px;">
              👤 <strong>Utilisateur :</strong> {user.username}
            </p>
            <p style="margin:4px 0; font-size:14px;">
              🔑 <strong>Mot de passe temporaire :</strong> 
              <span style="font-family:monospace; background:#e9ecef; padding:2px 6px; border-radius:4px;">
                {password}
              </span>
            </p>
          </div>

          <p style="margin:0 0 16px 0; font-size:14px; color:#444;">
            Cliquez sur le bouton ci-dessous pour accéder à la page de connexion de l’application :
          </p>

          <p style="text-align:center; margin:24px 0;">
            <a href="{login_url}" 
               style="display:inline-block; background:#0d3b66; color:#ffffff; text-decoration:none; 
                      padding:12px 24px; border-radius:4px; font-size:15px; font-weight:bold;">
              🌐 Se connecter à Le Phare Check
            </a>
          </p>

          <div style="background:#fff3cd; border-left:4px solid #ffc107; padding:12px 16px; border-radius:4px; margin-top:16px;">
            <p style="margin:0; font-size:13px; color:#856404;">
              🔒 <strong>IMPORTANT :</strong> pour votre sécurité,
              <span style="text-decoration:underline;">vous devez changer ce mot de passe temporaire dès votre première connexion</span>,
              depuis votre profil utilisateur (menu en haut à droite).
            </p>
          </div>

          <p style="margin:18px 0 0 0; font-size:13px; color:#666;">
            À très bientôt,<br>
            <strong>L'équipe Le Phare Collection Rivage</strong><br>
            (et Stéphane, Responsable Technique)
          </p>
        </div>

        <!-- Pied -->
        <div style="background:#f1f3f7; padding:12px 24px; text-align:center; font-size:11px; color:#777;">
          Cet email a été envoyé automatiquement, merci de ne pas y répondre.
        </div>
      </div>
    </div>
    """

    msg = Message(
        subject=subject,
        recipients=[user.email],
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        body=body_text,
        html=body_html,
    )

    try:
        print(f"DEBUG: Tentative d'envoi à {user.email}...")
        mail.send(msg)
        print(f"📩 Mail de bienvenue envoyé à {user.email}")
        return True
    except Exception as e:
        print(f"❌ [MAIL ERROR] Erreur : {e!r}")
        return False


def send_assignment_email(incident, technician):
    """Envoie une notification au technicien quand un incident lui est assigné."""
    print(f"[MAIL] Préparation mail d'assignation pour {technician.email}")
    _debug_config()

    app_url = current_app.config.get("APP_URL", "https://le-phare-check.onrender.com")

    subject = "🔔 Nouvel incident assigné - Le Phare Check"

    body_text = f"""Bonjour {technician.username},

Un incident vous a été assigné sur Le Phare Check.

Détails :

🏠 Hébergement : {incident.hebergement.emplacement}
⚠️ Type d'incident : {incident.type_incident}
📝 Description : {incident.description}

Merci de vous connecter pour traiter cet incident :
{app_url}

Cordialement,
L'équipe Le Phare Collection Rivage
"""

    body_html = f"""
    <div style="font-family: Arial, sans-serif; background-color:#f5f7fb; padding:20px;">
      <div style="max-width:600px; margin:0 auto; background:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        
        <div style="background:#dc3545; color:#ffffff; padding:20px 24px;">
          <h1 style="margin:0; font-size:20px;">
            🔔 Nouvel incident assigné
          </h1>
        </div>

        <div style="padding:24px;">
          <p>Bonjour <strong>{technician.username}</strong>,</p>
          <p>Un incident vous a été assigné sur l'application <strong>Le Phare Check</strong>.</p>

          <div style="background:#fff3cd; border-left:4px solid #ffc107; padding:12px 16px; border-radius:4px; margin:16px 0;">
            <p style="margin:0 0 8px 0; font-weight:bold;">Détails de l'incident :</p>
            <p style="margin:4px 0;">🏠 <strong>Hébergement :</strong> {incident.hebergement.emplacement}</p>
            <p style="margin:4px 0;">⚠️ <strong>Type :</strong> {incident.type_incident}</p>
            <p style="margin:4px 0;">📝 <strong>Description :</strong> {incident.description}</p>
          </div>

          <p style="margin:0 0 16px 0;">
            Merci de vous connecter à l'application pour traiter cet incident.
          </p>

          <p style="text-align:center; margin:24px 0;">
            <a href="{app_url}" 
               style="display:inline-block; background:#dc3545; color:#ffffff; text-decoration:none; 
                      padding:12px 24px; border-radius:4px; font-size:15px; font-weight:bold;">
              🚧 Accéder à l'incident
            </a>
          </p>

          <p style="margin:18px 0 0 0; font-size:13px; color:#666;">
            Cordialement,<br>
            <strong>L'équipe Le Phare Collection Rivage</strong>
          </p>
        </div>

        <div style="background:#f1f3f7; padding:12px 24px; text-align:center; font-size:11px; color:#777;">
          Cet email a été envoyé automatiquement, merci de ne pas y répondre.
        </div>
      </div>
    </div>
    """

    msg = Message(
        subject=subject,
        recipients=[technician.email],
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        body=body_text,
        html=body_html,
    )

    try:
        print(f"DEBUG: Tentative d'envoi d'assignation à {technician.email}...")
        mail.send(msg)
        print(f"📩 Mail d'assignation envoyé à {technician.email}")
        return True
    except Exception as e:
        print(f"❌ [MAIL ERROR] Erreur assignation : {e!r}")
        return False