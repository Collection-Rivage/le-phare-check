from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from markupsafe import Markup
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Hebergement, Check, TypeHebergement, Incident
from mail import mail, send_welcome_email, send_assignment_email

from sqlalchemy.orm import selectinload
from sqlalchemy import case, cast, Integer, func, or_
import os
import random
import string

app = Flask(__name__)
app.config.from_object(Config)

# Initialisations
db.init_app(app)
mail.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.context_processor
def inject_globals():
    return {"is_online": os.environ.get("RENDER") is not None}

with app.app_context():
    db.create_all()

# ===================== ROUTES DE CONNEXION =====================

@app.route('/')
@login_required
def index():
    if current_user.must_change_password:
        return redirect(url_for('change_password'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            if user.must_change_password:
                return redirect(url_for('change_password'))
            return redirect(url_for('dashboard'))
        flash('Identifiants incorrects', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        new_pwd = request.form.get('new_password')
        confirm_pwd = request.form.get('confirm_password')
        if new_pwd != confirm_pwd:
            flash('Les mots de passe ne correspondent pas.', 'danger')
        elif len(new_pwd) < 6:
            flash('Le mot de passe doit faire au moins 6 caractères.', 'danger')
        else:
            current_user.set_password(new_pwd)
            current_user.must_change_password = False
            db.session.commit()
            flash('Mot de passe mis à jour !', 'success')
            return redirect(url_for('dashboard'))
    return render_template('change_password.html')

# ===================== DASHBOARD & HEBERGEMENTS =====================

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.must_change_password:
        return redirect(url_for('change_password'))
    total = Hebergement.query.count()
    stats = dict(db.session.query(Hebergement.statut, func.count(Hebergement.id)).group_by(Hebergement.statut).all())
    ok, alerte, probleme = stats.get('ok', 0), stats.get('alerte', 0), stats.get('probleme', 0)
    taux_ok = round((ok / total) * 100, 1) if total else 0
    derniers_checks = Check.query.options(selectinload(Check.hebergement), selectinload(Check.technicien)).order_by(Check.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', total=total, ok=ok, alerte=alerte, probleme=probleme, taux_ok=taux_ok, derniers_checks=derniers_checks)

@app.route('/hebergements')
@login_required
def hebergements():
    page = request.args.get('page', 1, type=int)
    query = Hebergement.query.order_by(Hebergement.emplacement.asc())
    hebergements_list = query.paginate(page=page, per_page=20, error_out=False)
    types = TypeHebergement.query.all()
    return render_template('hebergements.html', hebergements=hebergements_list, types=types)

@app.route('/hebergements/add', methods=['POST'])
@login_required
def add_hebergement():
    if current_user.role != 'admin': return redirect(url_for('hebergements'))
    nouvel_heb = Hebergement(
        emplacement=request.form.get('emplacement'),
        type_id=request.form.get('type_id'),
        numero_chassis=request.form.get('numero_chassis'),
        nb_personnes=request.form.get('nb_personnes'),
        compteur_eau=request.form.get('compteur_eau')
    )
    db.session.add(nouvel_heb)
    db.session.commit()
    flash('Hébergement ajouté', 'success')
    return redirect(url_for('hebergements'))

@app.route('/hebergements/edit/<int:id>', methods=['POST'])
@login_required
def edit_hebergement(id):
    if current_user.role != 'admin': return redirect(url_for('hebergements'))
    heb = Hebergement.query.get_or_404(id)
    heb.emplacement = request.form.get('emplacement')
    heb.type_id = request.form.get('type_id')
    heb.numero_chassis = request.form.get('numero_chassis')
    heb.nb_personnes = request.form.get('nb_personnes')
    heb.compteur_eau = request.form.get('compteur_eau')
    db.session.commit()
    flash('Hébergement modifié', 'success')
    return redirect(url_for('hebergements'))

# ===================== CHECKS & INCIDENTS =====================

@app.route('/check/<int:hebergement_id>', methods=['GET', 'POST'])
@login_required
def check(hebergement_id):
    hebergement = Hebergement.query.get_or_404(hebergement_id)
    if request.method == 'POST':
        nouveau_check = Check(
            hebergement_id=hebergement_id, user_id=current_user.id,
            electricite=request.form.get('electricite') == 'on',
            plomberie=request.form.get('plomberie') == 'on',
            chauffage=request.form.get('chauffage') == 'on',
            proprete=request.form.get('proprete') == 'on',
            equipements=request.form.get('equipements') == 'on',
            observations=request.form.get('observations'),
            probleme_critique=request.form.get('probleme_critique') == 'on'
        )
        db.session.add(nouveau_check)
        if nouveau_check.probleme_critique: hebergement.statut = 'probleme'
        elif not all([nouveau_check.electricite, nouveau_check.plomberie, nouveau_check.chauffage, nouveau_check.proprete, nouveau_check.equipements]):
            hebergement.statut = 'alerte'
        else: hebergement.statut = 'ok'
        db.session.commit()
        flash('Check enregistré !', 'success')
        return redirect(url_for('dashboard'))
    return render_template('check.html', hebergement=hebergement)

@app.route('/historique')
@login_required
def historique():
    checks = Check.query.order_by(Check.created_at.desc()).all()
    return render_template('historique.html', checks=checks)

@app.route('/incident/<int:hebergement_id>', methods=['GET', 'POST'])
@login_required
def signaler_incident(hebergement_id):
    hebergement = Hebergement.query.get_or_404(hebergement_id)
    techniciens = User.query.filter(User.role.in_(['technicien', 'admin'])).all()
    if request.method == 'POST':
        incident = Incident(
            hebergement_id=hebergement_id, type_incident=request.form.get('type_incident'),
            description=request.form.get('description'), assigne_a=request.form.get('assigne_a') or None,
            cree_par=current_user.id
        )
        db.session.add(incident)
        hebergement.statut = 'probleme' if request.form.get('type_incident') == 'urgence' else 'alerte'
        db.session.commit()
        if incident.assigne_a:
            tech = db.session.get(User, incident.assigne_a)
            send_assignment_email(incident, tech)
        flash('Incident signalé !', 'success')
        return redirect(url_for('hebergements'))
    return render_template('incident.html', hebergement=hebergement, techniciens=techniciens)

# ===================== GESTION DES TYPES =====================

@app.route('/types')
@login_required
def types():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    all_types = TypeHebergement.query.all()
    return render_template('types.html', types=all_types)

@app.route('/types/add', methods=['POST'])
@login_required
def add_type():
    if current_user.role != 'admin': return redirect(url_for('types'))
    nouveau = TypeHebergement(nom=request.form.get('nom'), description=request.form.get('description'))
    db.session.add(nouveau)
    db.session.commit()
    return redirect(url_for('types'))

# ===================== ADMINISTRATION UTILISATEURS =====================

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/add', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    username, email, role = request.form.get('username'), request.form.get('email'), request.form.get('role')
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        flash('Utilisateur déjà existant', 'danger')
    else:
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        user = User(username=username, email=email, role=role, must_change_password=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        send_welcome_email(user, password)
        flash(f'Utilisateur {username} créé et invité par mail !', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:id>')
@login_required
def delete_user(id):
    if current_user.role != 'admin' or id == current_user.id: return redirect(url_for('admin_users'))
    user = db.session.get(User, id)
    db.session.delete(user)
    db.session.commit()
    flash('Utilisateur supprimé', 'warning')
    return redirect(url_for('admin_users'))

@app.route('/api/status')
def api_status():
    return jsonify({'status': 'online' if os.environ.get('RENDER') else 'local'})

@app.route('/debug-reset-admin')
def debug_reset_admin():
    user = User.query.filter_by(username='admin').first()
    if user:
        db.session.delete(user)
        db.session.commit()
    
    new_admin = User(
        username='admin', 
        email='admin@lephare.com', 
        role='admin', 
        must_change_password=False
    )
    new_admin.set_password('admin123')
    db.session.add(new_admin)
    db.session.commit()
    return "✅ L'admin sur Render a été réinitialisé ! Identifiant: admin | MDP: admin123"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)