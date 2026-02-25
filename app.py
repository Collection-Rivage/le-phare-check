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

# ===================== ROUTES CONNEXION =====================

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

# ===================== DASHBOARD & HISTORIQUE =====================

@app.route('/dashboard')
@login_required
def dashboard():
    total = Hebergement.query.count()
    stats = dict(db.session.query(Hebergement.statut, func.count(Hebergement.id)).group_by(Hebergement.statut).all())
    ok = stats.get('ok', 0)
    derniers_checks = Check.query.options(joinedload(Check.hebergement), joinedload(Check.technicien)).order_by(desc(Check.created_at)).limit(10).all()
    return render_template('dashboard.html', total=total, ok=ok, alerte=stats.get('alerte', 0), probleme=stats.get('probleme', 0), taux_ok=round((ok/total)*100, 1) if total else 0, derniers_checks=derniers_checks)

@app.route('/historique')
@login_required
def historique():
    # 1. Récupération de tous les paramètres de recherche
    search_q = request.args.get('q', '').strip()
    filter_etat = request.args.get('etat', '')
    filter_type = request.args.get('type', '')
    filter_tech = request.args.get('tech', '')

    # 2. Construction de la requête de base
    query = Check.query.options(
        joinedload(Check.hebergement),
        joinedload(Check.technicien)
    )

    # 3. Application des filtres combinés
    # Filtre par mot-clé dans les observations
    if search_q:
        query = query.filter(Check.observations.ilike(f'%{search_q}%'))

    # Filtre par état global
    if filter_etat == 'critique':
        query = query.filter(Check.probleme_critique == True)
    elif filter_etat == 'alerte':
        query = query.filter(Check.probleme_critique == False, 
                             or_(Check.electricite==False, Check.plomberie==False, 
                                 Check.chauffage==False, Check.proprete==False, Check.equipements==False))

    # Filtre par type de défaut spécifique
    if filter_type:
        if filter_type == 'electricite': query = query.filter(Check.electricite == False)
        elif filter_type == 'plomberie': query = query.filter(Check.plomberie == False)
        elif filter_type == 'chauffage': query = query.filter(Check.chauffage == False)
        elif filter_type == 'proprete': query = query.filter(Check.proprete == False)
        elif filter_type == 'equipements': query = query.filter(Check.equipements == False)

    # Filtre par technicien
    if filter_tech:
        try:
            query = query.filter(Check.user_id == int(filter_tech))
        except ValueError: pass

    # 4. Exécution de la requête (trié par date décroissante)
    checks = query.order_by(desc(Check.created_at)).limit(100).all()
    
    # Liste des techniciens pour le menu déroulant
    techniciens = User.query.filter(User.role.in_(['technicien', 'admin'])).all()
    
    return render_template('historique.html', checks=checks, techniciens=techniciens)

# ===================== HEBERGEMENTS =====================

@app.route('/hebergements')
@login_required
def hebergements():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()
    statut = request.args.get('statut', '')
    type_id_str = request.args.get('type_id', '')
    
    c_stats = db.session.query(Check.hebergement_id.label("hid"), func.count(Check.id).label("cnt"), func.max(Check.created_at).label("last")).group_by(Check.hebergement_id).subquery()
    i_stats = db.session.query(Incident.hebergement_id.label("hid"), func.count(Incident.id).label("cnt")).filter(Incident.statut == 'ouvert').group_by(Incident.hebergement_id).subquery()
    
    query = db.session.query(Hebergement, func.coalesce(c_stats.c.cnt, 0), c_stats.c.last, func.coalesce(i_stats.c.cnt, 0)).outerjoin(c_stats, c_stats.c.hid == Hebergement.id).outerjoin(i_stats, i_stats.c.hid == Hebergement.id).options(selectinload(Hebergement.type_hebergement))
    
    if q: query = query.filter(or_(Hebergement.emplacement.ilike(f'%{q}%'), Hebergement.numero_chassis.ilike(f'%{q}%')))
    if statut: query = query.filter(Hebergement.statut == statut)
    if type_id_str: query = query.filter(Hebergement.type_id == int(type_id_str))
    
    query = query.order_by(func.length(Hebergement.emplacement).asc(), Hebergement.emplacement.asc())
    h_list = query.paginate(page=page, per_page=30, error_out=False)
    return render_template('hebergements.html', hebergements=h_list, types=get_types(), q=q, statut=statut, type_id=type_id_str)

@app.route('/hebergements/add', methods=['POST'])
@login_required
def add_hebergement():
    if current_user.role != 'admin': return redirect(url_for('hebergements'))
    h = Hebergement(emplacement=request.form.get('emplacement'), type_id=request.form.get('type_id'), numero_chassis=request.form.get('numero_chassis'), nb_personnes=request.form.get('nb_personnes'), compteur_eau=request.form.get('compteur_eau'))
    db.session.add(h)
    db.session.commit()
    flash('Ajouté', 'success')
    return redirect(url_for('hebergements'))

@app.route('/hebergements/edit/<int:id>', methods=['POST'])
@login_required
def edit_hebergement(id):
    if current_user.role != 'admin': return redirect(url_for('hebergements'))
    h = db.session.get(Hebergement, id)
    if not h: return redirect(url_for('hebergements'))
    h.emplacement = request.form.get('emplacement')
    h.type_id = request.form.get('type_id')
    h.numero_chassis = request.form.get('numero_chassis')
    h.nb_personnes = request.form.get('nb_personnes')
    h.compteur_eau = request.form.get('compteur_eau')
    db.session.commit()
    flash('Modifié', 'success')
    return redirect(url_for('hebergements'))

@app.route('/hebergements/delete/<int:id>')
@login_required
def delete_hebergement(id):
    if current_user.role != 'admin': return redirect(url_for('hebergements'))
    h = db.session.get(Hebergement, id)
    if h:
        db.session.delete(h)
        db.session.commit()
        flash('Supprimé', 'warning')
    return redirect(url_for('hebergements'))

# ===================== CHECKS & INCIDENTS =====================

@app.route('/check/<int:hebergement_id>', methods=['GET', 'POST'])
@login_required
def check(hebergement_id):
    heb = db.session.get(Hebergement, hebergement_id)
    if not heb: return redirect(url_for('hebergements'))
    
    if request.method == 'POST':
        # --- RÉCUPÉRATION DE LA SIGNATURE ---
        signature_data = request.form.get('signature_data')
        url_signature = None
        if signature_data:
            try:
                # Upload direct de la chaîne Base64 vers Cloudinary
                upload_result = cloudinary.uploader.upload(signature_data, folder="signatures")
                url_signature = upload_result.get('secure_url')
            except Exception as e:
                print(f"❌ Erreur Upload Signature : {e}")

        c = Check(
            hebergement_id=hebergement_id,
            user_id=current_user.id,
            electricite=request.form.get('electricite') == 'on',
            plomberie=request.form.get('plomberie') == 'on',
            chauffage=request.form.get('chauffage') == 'on',
            proprete=request.form.get('proprete') == 'on',
            equipements=request.form.get('equipements') == 'on',
            observations=request.form.get('observations'),
            probleme_critique=request.form.get('probleme_critique') == 'on',
            signature_url=url_signature # <-- ON ENREGISTRE L'URL ICI
        )
        db.session.add(c)
        # ... reste de la logique de statut ...
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('check.html', hebergement=heb)

@app.route('/incident/<int:hebergement_id>', methods=['GET', 'POST'])
@login_required
def signaler_incident(hebergement_id):
    heb = db.session.get(Hebergement, hebergement_id)
    if not heb: return redirect(url_for('hebergements'))
    techs = User.query.filter(User.role.in_(['technicien', 'admin'])).order_by(User.username).all()
    if request.method == 'POST':
        image_file = request.files.get('image')
        url_photo = None
        if image_file and image_file.filename != '':
            try:
                upload_result = cloudinary.uploader.upload(image_file)
                url_photo = upload_result['secure_url']
            except Exception as e: print(f"❌ Cloudinary error: {e}")
        
        assigne_a = request.form.get('assigne_a')
        tech_obj = db.session.get(User, int(assigne_a)) if assigne_a else None
        
        i = Incident(hebergement_id=hebergement_id, type_incident=request.form.get('type_incident'), 
                     description=request.form.get('description'), assigne_a=tech_obj.id if tech_obj else None,
                     cree_par=current_user.id, image_url=url_photo)
        db.session.add(i)
        heb.statut = 'probleme' if i.type_incident == 'urgence' else 'alerte'
        db.session.commit()
        if tech_obj: send_assignment_email(i, tech_obj)
        flash('Incident signalé !', 'success')
        return redirect(url_for('hebergements'))
    return render_template('incident.html', hebergement=heb, techniciens=techs)

@app.route('/incident/<int:incident_id>/resoudre', methods=['POST'])
@login_required
def resoudre_incident(incident_id):
    i = db.session.get(Incident, incident_id)
    if i:
        i.statut = 'resolu'
        i.date_resolution = datetime.utcnow()
        i.resolu_par_id = current_user.id
        db.session.commit()
        recalculer_statut_hebergement(i.hebergement_id)
        flash('Incident résolu !', 'success')
    return redirect(url_for('hebergements'))

@app.route('/problemes/<int:hebergement_id>')
@login_required
def voir_problemes(hebergement_id):
    heb = db.session.get(Hebergement, hebergement_id)
    incidents = Incident.query.filter_by(hebergement_id=hebergement_id, statut='ouvert').order_by(desc(Incident.created_at)).all()
    return render_template('problemes.html', hebergement=heb, incidents=incidents)

# ===================== TYPES & UTILISATEURS =====================

@app.route('/types')
@login_required
def types():
    return render_template('types.html', types=get_types())

@app.route('/types/add', methods=['POST'])
@login_required
def add_type():
    if current_user.role == 'admin':
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
    u = User(username=request.form.get('username'), email=request.form.get('email'), role=request.form.get('role'))
    pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    u.set_password(pwd)
    db.session.add(u)
    db.session.commit()
    send_welcome_email(u, pwd)
    flash(f'Utilisateur {u.username} créé !', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/edit/<int:id>', methods=['POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    u = db.session.get(User, id)
    if not u: return redirect(url_for('admin_users'))
    
    # Mise à jour du rôle
    u.role = request.form.get('role')
    
    # Mise à jour du mot de passe si rempli
    new_password = request.form.get('password')
    if new_password:
        u.set_password(new_password)
        u.must_change_password = True
        flash(f'Mot de passe de {u.username} réinitialisé', 'success')
    
    db.session.commit()
    flash('Utilisateur mis à jour', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:id>')
@login_required
def delete_user(id):
    if current_user.role != 'admin' or current_user.id == id: return redirect(url_for('admin_users'))
    u = db.session.get(User, id)
    if u:
        db.session.delete(u)
        db.session.commit()
        flash('Utilisateur supprimé', 'warning')
    return redirect(url_for('admin_users'))

@app.route('/api/status')
def api_status():
    return jsonify({'status': 'online' if os.environ.get("RENDER") else 'local'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
