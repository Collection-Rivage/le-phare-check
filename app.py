from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Hebergement, Check, TypeHebergement, Incident
from mail import mail, send_alert_email
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ... (le code d'initialisation reste identique)

# ==================== ROUTES ====================

@app.route('/hebergements')
@login_required
def hebergements():
    hebergements_list = Hebergement.query.all()
    types = TypeHebergement.query.all()
    is_online = os.environ.get('RENDER') is not None
    return render_template('hebergements.html', hebergements=hebergements_list, types=types, is_online=is_online)

@app.route('/incident/<int:hebergement_id>', methods=['GET', 'POST'])
@login_required
def signaler_incident(hebergement_id):
    hebergement = Hebergement.query.get_or_404(hebergement_id)
    techniciens = User.query.filter(User.role.in_(['technicien', 'admin'])).all()
    
    if request.method == 'POST':
        type_incident = request.form.get('type_incident')
        description = request.form.get('description')
        assigne_a = request.form.get('assigne_a') or None
        
        incident = Incident(
            hebergement_id=hebergement_id,
            type_incident=type_incident,
            description=description,
            assigne_a=assigne_a,
            cree_par=current_user.id
        )
        db.session.add(incident)
        
        # Mettre à jour le statut de l'hébergement
        if type_incident == 'urgence':
            hebergement.statut = 'probleme'
        else:
            hebergement.statut = 'alerte'
        
        db.session.commit()
        flash('Incident signalé avec succès !', 'success')
        return redirect(url_for('hebergements'))
    
    is_online = os.environ.get('RENDER') is not None
    return render_template('incident.html', hebergement=hebergement, techniciens=techniciens, is_online=is_online)

# ... (le reste du code app.py reste identique)
