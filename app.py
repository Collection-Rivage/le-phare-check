import os
import random
import string
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from sqlalchemy import func, or_, desc, select
from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy.orm import selectinload, joinedload

import cloudinary
import cloudinary.uploader

from config import Config
from models import db, User, Hebergement, Check, TypeHebergement, Incident
from mail import send_welcome_email, send_assignment_email

app = Flask(__name__)
app.config.from_object(Config)

# Config Cloudinary
cloudinary.config(
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
  api_key = os.environ.get('CLOUDINARY_API_KEY'),
  api_secret = os.environ.get('CLOUDINARY_API_SECRET')
)

# ===================== INITIALISATION =====================
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.context_processor
def inject_globals():
    return {"is_online": os.environ.get("RENDER") is not None}

def get_types():
    return TypeHebergement.query.order_by(TypeHebergement.nom).all()

with app.app_context():
    db.create_all()
    if TypeHebergement.query.count() == 0:
        types_data = [
            TypeHebergement(nom='Cabane', description='Cabanes bois'),
            TypeHebergement(nom='Mobil-home Staff', description='Staff'),
            TypeHebergement(nom='Mobil-home Standard', description='Clients'),
            TypeHebergement(nom='Espace Bien Être', description='Spa')
        ]
        db.session.add_all(types_data)
        db.session.commit()
    
    if User.query.filter_by(username='admin').first() is None:
        admin = User(username='admin', email='admin@lephare.com', role='admin', must_change_password=False)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# ===================== FONCTIONS HELPER =====================

def recalculer_statut_hebergement(hebergement_id):
    heb = db.session.get(Hebergement, hebergement_id)
    if not heb: return
    incidents_ouverts = Incident.query.filter_by(hebergement_id=hebergement_id, statut='ouvert').count()
    if incidents_ouverts > 0: return
    dernier_check = Check.query.filter_by(hebergement_id=hebergement_id).order_by(desc(Check.created_at)).first()
    if dernier_check:
        if dernier_check.probleme_critique: heb.statut = 'probleme'
        elif all([dernier_check.electricite, dernier_check.plomberie, dernier_check.chauffage, dernier_check.proprete, dernier_check.equipements]):
            heb.statut = 'ok'
        else: heb.statut = 'alerte'
    else: heb.statut = 'ok'
    db.session.commit()

# ===================== ROUTES =====================

@app.route('/')
@login_required
def index():
    if current_user.must_change_password: return redirect(url_for('change_password'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('change_password') if user.must_change_password else url_for('dashboard'))
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
        if new_pwd != request.form.get('confirm_password'):
            flash('Les mots de passe ne correspondent pas.', 'danger')
        elif len(new_pwd) < 6:
            flash('Trop court (min 6)', 'danger')
        else:
            current_user.set_password(new_pwd)
            current_user.must_change_password = False
            db.session.commit()
            flash('Mot de passe mis à jour !', 'success')
            return redirect(url_for('dashboard'))
    return render_template('change_password.html')

@app.route('/dashboard')
@login_required
def dashboard():
    total = Hebergement.query.count()
    stats = dict(db.session.query(Hebergement.statut, func.count(Hebergement.id)).group_by(Hebergement.statut).all())
    ok = stats.get('ok', 0)
    derniers_checks = Check.query.options(joinedload(Check.hebergement), joinedload(Check.technicien)).order_by(desc(Check.created_at)).limit(10).all()
    return render_template('dashboard.html', total=total, ok=ok, alerte=stats.get('alerte', 0), probleme=stats.get('probleme', 0), taux_ok=round((ok/total)*100, 1) if total else 0, derniers_checks=derniers_checks)

@app.route('/hebergements')
@login_required
def hebergements():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()
    statut = request.args.get('statut', '')
    type_id_str = request.args.get('type_id', '')
    query = db.session.query(Hebergement).options(selectinload(Hebergement.type_hebergement))
    if q: query = query.filter(or_(Hebergement.emplacement.ilike(f'%{q}%'), Hebergement.numero_chassis.ilike(f'%{q}%')))
    if statut: query = query.filter(Hebergement.statut == statut)
    if type_id_str: query = query.filter(Hebergement.type_id == int(type_id_str))
    
    # Tri par emplacement (1, 2, 10...)
    query = query.order_by(func.length(Hebergement.emplacement).asc(), Hebergement.emplacement.asc())
    h_list = query.paginate(page=page, per_page=30, error_out=False)
    return render_template('hebergements.html', hebergements=h_list, types=get_types(), q=q, statut=statut, type_id=type_id_str)

@app.route('/check/<int:hebergement_id>', methods=['GET', 'POST'])
@login_required
def check(hebergement_id):
    heb = db.session.get(Hebergement, hebergement_id)
    if not heb:
        flash('Hébergement introuvable', 'danger')
        return redirect(url_for('hebergements'))
    if request.method == 'POST':
        c = Check(
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
        db.session.add(c)
        heb.statut = 'probleme' if c.probleme_critique else ('ok' if all([c.electricite, c.plomberie, c.chauffage, c.proprete, c.equipements]) else 'alerte')
        db.session.commit()
        flash('Contrôle enregistré !', 'success')
        return redirect(url_for('dashboard'))
    return render_template('check.html', hebergement=heb)

@app.route('/incident/<int:hebergement_id>', methods=['GET', 'POST'])
@login_required
def signaler_incident(hebergement_id):
    heb = db.session.get(Hebergement, hebergement_id)
    if not heb:
        flash('Hébergement non trouvé', 'danger')
        return redirect(url_for('hebergements'))
    
    techs = User.query.filter(User.role.in_(['technicien', 'admin'])).order_by(User.username).all()
    
    if request.method == 'POST':
        type_incident = request.form.get('type_incident', '')
        description = request.form.get('description', '')
        assigne_a_raw = request.form.get('assigne_a', '').strip()
        
        # --- UPLOAD CLOUDINARY ---
        image_file = request.files.get('image')
        url_photo = None
        if image_file and image_file.filename != '':
            try:
                upload_result = cloudinary.uploader.upload(image_file)
                url_photo = upload_result['secure_url']
            except Exception as e:
                print(f"❌ Erreur Cloudinary : {e}")

        assigne_a = None
        technicien_obj = None
        if assigne_a_raw:
            try:
                user_id = int(assigne_a_raw)
                technicien_obj = db.session.get(User, user_id)
                if technicien_obj: assigne_a = user_id
            except ValueError: pass

        i = Incident(
            hebergement_id=hebergement_id,
            type_incident=type_incident,
            description=description,
            assigne_a=assigne_a,
            cree_par=current_user.id,
            image_url=url_photo
        )
        db.session.add(i)
        heb.statut = 'probleme' if type_incident == 'urgence' else 'alerte'
        
        try:
            db.session.commit()
            if assigne_a and technicien_obj:
                send_assignment_email(i, technicien_obj)
            flash('Incident signalé !', 'success')
            return redirect(url_for('hebergements'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')
    
    return render_template('incident.html', hebergement=heb, techniciens=techs)

@app.route('/incident/<int:incident_id>/resoudre', methods=['POST'])
@login_required
def resoudre_incident(incident_id):
    incident = db.session.get(Incident, incident_id)
    if not incident: return redirect(url_for('hebergements'))
    incident.statut = 'resolu'
    incident.date_resolution = datetime.utcnow()
    incident.resolu_par_id = current_user.id
    db.session.commit()
    recalculer_statut_hebergement(incident.hebergement_id)
    flash('Incident résolu !', 'success')
    return redirect(url_for('hebergements'))

@app.route('/problemes/<int:hebergement_id>')
@login_required
def voir_problemes(hebergement_id):
    heb = db.session.get(Hebergement, hebergement_id)
    incidents = Incident.query.filter_by(hebergement_id=hebergement_id, statut='ouvert').order_by(desc(Incident.created_at)).all()
    return render_template('problemes.html', hebergement=heb, incidents=incidents)

@app.route('/historique')
@login_required
def historique():
    checks = Check.query.options(joinedload(Check.hebergement), joinedload(Check.technicien)).order_by(desc(Check.created_at)).limit(50).all()
    return render_template('historique.html', checks=checks)

@app.route('/types')
@login_required
def types():
    return render_template('types.html', types=get_types())

@app.route('/types/add', methods=['POST'])
@login_required
def add_type():
    if current_user.role != 'admin': return redirect(url_for('types'))
    t = TypeHebergement(nom=request.form.get('nom'), description=request.form.get('description'))
    db.session.add(t)
    db.session.commit()
    flash('Type ajouté', 'success')
    return redirect(url_for('types'))

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    users = User.query.order_by(desc(User.created_at)).all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/add', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    username = request.form.get('username')
    email = request.form.get('email')
    password_en_clair = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    u = User(username=username, email=email, role=request.form.get('role'), must_change_password=True)
    u.set_password(password_en_clair)
    db.session.add(u)
    db.session.commit()
    send_welcome_email(u, password_en_clair)
    flash(f'Utilisateur {username} créé !', 'success')
    return redirect(url_for('admin_users'))

@app.route('/api/status')
def api_status():
    return jsonify({'status': 'online' if os.environ.get("RENDER") else 'local'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
