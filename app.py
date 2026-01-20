from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Hebergement, Check
from mail import mail, send_alert_email
import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialisation des extensions
db.init_app(app)
mail.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Création des tables et données initiales
with app.app_context():
    db.create_all()
    
    # Créer un utilisateur admin par défaut si aucun utilisateur existe
    if User.query.count() == 0:
        admin = User(username='admin', email='admin@lephare.com', role='admin')
        admin.set_password('admin123')  # À changer en production !
        db.session.add(admin)
        db.session.commit()
        print("✅ Utilisateur admin créé : admin / admin123")


# ==================== ROUTES ====================

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants incorrects', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    total_hebergements = Hebergement.query.count()
    hebergements_ok = Hebergement.query.filter_by(statut='ok').count()
    hebergements_alerte = Hebergement.query.filter_by(statut='alerte').count()
    hebergements_probleme = Hebergement.query.filter_by(statut='probleme').count()
    
    derniers_checks = Check.query.order_by(Check.created_at.desc()).limit(5).all()
    
    # Détection du mode (local/online)
    is_online = os.environ.get('RENDER') is not None
    
    return render_template('dashboard.html', 
                         total=total_hebergements,
                         ok=hebergements_ok,
                         alerte=hebergements_alerte,
                         probleme=hebergements_probleme,
                         derniers_checks=derniers_checks,
                         is_online=is_online)


@app.route('/hebergements')
@login_required
def hebergements():
    hebergements_list = Hebergement.query.all()
    is_online = os.environ.get('RENDER') is not None
    return render_template('hebergements.html', hebergements=hebergements_list, is_online=is_online)


@app.route('/hebergements/add', methods=['POST'])
@login_required
def add_hebergement():
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('hebergements'))
    
    nom = request.form.get('nom')
    type_heb = request.form.get('type')
    zone = request.form.get('zone')
    capacite = request.form.get('capacite')
    
    nouvel_heb = Hebergement(nom=nom, type=type_heb, zone=zone, capacite=capacite)
    db.session.add(nouvel_heb)
    db.session.commit()
    
    flash(f'Hébergement "{nom}" ajouté avec succès', 'success')
    return redirect(url_for('hebergements'))


@app.route('/check/<int:hebergement_id>', methods=['GET', 'POST'])
@login_required
def check(hebergement_id):
    hebergement = Hebergement.query.get_or_404(hebergement_id)
    is_online = os.environ.get('RENDER') is not None
    
    if request.method == 'POST':
        nouveau_check = Check(
            hebergement_id=hebergement_id,
            user_id=current_user.id,
            electricite=request.form.get('electricite') == 'on',
            plomberie=request.form.get('plomberie') == 'on',
            chauffage=request.form.get('chauffage') == 'on',
            proprete=request.form.get('proprete') == 'on',
            equipements=request.form.get('equipements') == 'on',
            observations=request.form.get('observations'),
            probleme_critique=request.form.get('probleme_critique') == 'on'
        )
        
        db.session.add(nouveau_check)
        
        # Mise à jour du statut de l'hébergement
        if nouveau_check.probleme_critique:
            hebergement.statut = 'probleme'
        elif not all([nouveau_check.electricite, nouveau_check.plomberie, 
                     nouveau_check.chauffage, nouveau_check.proprete, 
                     nouveau_check.equipements]):
            hebergement.statut = 'alerte'
        else:
            hebergement.statut = 'ok'
        
        db.session.commit()
        
        # Envoi de l'email si problème
        if hebergement.statut != 'ok':
            try:
                send_alert_email(nouveau_check, hebergement, current_user)
            except Exception as e:
                print(f"Erreur envoi email : {e}")
        
        flash('Check enregistré avec succès', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('check.html', hebergement=hebergement, is_online=is_online)


@app.route('/historique')
@login_required
def historique():
    checks = Check.query.order_by(Check.created_at.desc()).all()
    is_online = os.environ.get('RENDER') is not None
    return render_template('historique.html', checks=checks, is_online=is_online)


# ==================== API ====================

@app.route('/api/status')
def api_status():
    is_online = os.environ.get('RENDER') is not None
    return jsonify({
        'status': 'online' if is_online else 'local',
        'app': 'Le Phare Check'
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
