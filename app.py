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

# ===================== INITIALISATION =====================
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
    # Initialisation des types
    if TypeHebergement.query.count() == 0:
        types_defaut = [
            TypeHebergement(nom='Cabane', description='Cabanes en bois'),
            TypeHebergement(nom='Mobil-home Staff', description='Hébergements personnel'),
            TypeHebergement(nom='Mobil-home Standard', description='Hébergements clients'),
            TypeHebergement(nom='Espace Bien Être', description='Spa/Sauna')
        ]
        db.session.add_all(types_defaut)
        db.session.commit()
    # Initialisation admin
    if User.query.filter_by(username='admin').first() is None:
        admin = User(username='admin', email='admin@lephare.com', role='admin', must_change_password=False)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# ===================== ROUTES CONNEXION =====================

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
            flash('Mot de passe mis à jour avec succès !', 'success')
            return redirect(url_for('dashboard'))
    return render_template('change_password.html')

# ===================== DASHBOARD & HEBERGEMENTS =====================

@app.route('/dashboard')
@login_required
def dashboard():
    total = Hebergement.query.count()
    stats = dict(db.session.query(Hebergement.statut, func.count(Hebergement.id)).group_by(Hebergement.statut).all())
    ok = stats.get('ok', 0)
    alerte = stats.get('alerte', 0)
    probleme = stats.get('probleme', 0)
    taux_ok = round((ok / total) * 100, 1) if total else 0
    derniers_checks = Check.query.options(selectinload(Check.hebergement), selectinload(Check.technicien)).order_by(Check.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', total=total, ok=ok, alerte=alerte, probleme=probleme, taux_ok=taux_ok, derniers_checks=derniers_checks)

@app.route('/hebergements')
@login_required
def hebergements():
    page = request.args.get('page', 1, type=int)
    c_stats = db.session.query(Check.hebergement_id.label("hid"), func.count(Check.id).label("cnt"), func.max(Check.created_at).label("last")).group_by(Check.hebergement_id).subquery()
    i_stats = db.session.query(Incident.hebergement_id.label("hid"), func.count(Incident.id).label("cnt")).group_by(Incident.hebergement_id).subquery()
    query = db.session.query(Hebergement, func.coalesce(c_stats.c.cnt, 0), c_stats.c.last, func.coalesce(i_stats.c.cnt, 0)).outerjoin(c_stats, c_stats.c.hid == Hebergement.id).outerjoin(i_stats, i_stats.c.hid == Hebergement.id).options(selectinload(Hebergement.type_hebergement)).order_by(Hebergement.emplacement.asc())
    h_list = query.paginate(page=page, per_page=20, error_out=False)
    return render_template('hebergements.html', hebergements=h_list, types=TypeHebergement.query.all())

@app.route('/hebergements/add', methods=['POST'])
@login_required
def add_hebergement():
    if current_user.role != 'admin': return redirect(url_for('hebergements'))
    h = Hebergement(emplacement=request.form.get('emplacement'), type_id=request.form.get('type_id'), numero_chassis=request.form.get('numero_chassis'), nb_personnes=request.form.get('nb_personnes'), compteur_eau=request.form.get('compteur_eau'))
    db.session.add(h); db.session.commit(); flash('Ajouté', 'success')
    return redirect(url_for('hebergements'))

@app.route('/hebergements/edit/<int:id>', methods=['POST'])
@login_required
def edit_hebergement(id):
    if current_user.role != 'admin': return redirect(url_for('hebergements'))
    h = db.session.get(Hebergement, id)
    h.emplacement = request.form.get('emplacement'); h.type_id = request.form.get('type_id')
    h.numero_chassis = request.form.get('numero_chassis'); h.nb_personnes = request.form.get('nb_personnes')
    h.compteur_eau = request.form.get('compteur_eau'); db.session.commit(); flash('Modifié', 'success')
    return redirect(url_for('hebergements'))

@app.route('/hebergements/delete/<int:id>')
@login_required
def delete_hebergement(id):
    if current_user.role != 'admin': return redirect(url_for('hebergements'))
    h = db.session.get(Hebergement, id)
    if h: db.session.delete(h); db.session.commit(); flash('Supprimé', 'warning')
    return redirect(url_for('hebergements'))

# ===================== OPÉRATIONS =====================

@app.route('/check/<int:hebergement_id>', methods=['GET', 'POST'])
@login_required
def check(hebergement_id):
    heb = db.session.get(Hebergement, hebergement_id)
    if request.method == 'POST':
        c = Check(hebergement_id=hebergement_id, user_id=current_user.id, electricite=request.form.get('electricite')=='on', plomberie=request.form.get('plomberie')=='on', chauffage=request.form.get('chauffage')=='on', proprete=request.form.get('proprete')=='on', equipements=request.form.get('equipements')=='on', observations=request.form.get('observations'), probleme_critique=request.form.get('probleme_critique')=='on')
        db.session.add(c)
        if c.probleme_critique: heb.statut = 'probleme'
        elif not all([c.electricite, c.plomberie, c.chauffage, c.proprete, c.equipements]): heb.statut = 'alerte'
        else: heb.statut = 'ok'
        db.session.commit(); flash('Check enregistré !', 'success')
        return redirect(url_for('dashboard'))
    return render_template('check.html', hebergement=heb)

@app.route('/historique')
@login_required
def historique():
    checks = Check.query.order_by(Check.created_at.desc()).all()
    return render_template('historique.html', checks=checks)

@app.route('/incident/<int:hebergement_id>', methods=['GET', 'POST'])
@login_required
def signaler_incident(hebergement_id):
    heb = db.session.get(Hebergement, hebergement_id)
    techniciens = User.query.filter(User.role.in_(['technicien', 'admin'])).all()
    if request.method == 'POST':
        i = Incident(hebergement_id=hebergement_id, type_incident=request.form.get('type_incident'), description=request.form.get('description'), assigne_a=request.form.get('assigne_a') or None, cree_par=current_user.id)
        db.session.add(i)
        heb.statut = 'probleme' if request.form.get('type_incident') == 'urgence' else 'alerte'
        db.session.commit()
        if i.assigne_a:
            tech = db.session.get(User, i.assigne_a)
            send_assignment_email(i, tech)
        flash('Incident signalé !', 'success')
        return redirect(url_for('hebergements'))
    return render_template('incident.html', hebergement=heb, techniciens=techniciens)

# ===================== GESTION TYPES =====================

@app.route('/types')
@login_required
def types():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    return render_template('types.html', types=TypeHebergement.query.all())

@app.route('/types/add', methods=['POST'])
@login_required
def add_type():
    if current_user.role != 'admin': return redirect(url_for('types'))
    t = TypeHebergement(nom=request.form.get('nom'), description=request.form.get('description'))
    db.session.add(t); db.session.commit(); flash('Type ajouté', 'success')
    return redirect(url_for('types'))

@app.route('/types/edit/<int:id>', methods=['POST'])
@login_required
def edit_type(id):
    if current_user.role != 'admin': return redirect(url_for('types'))
    t = db.session.get(TypeHebergement, id)
    if t:
        t.nom = request.form.get('nom'); t.description = request.form.get('description')
        db.session.commit(); flash('Type modifié', 'success')
    return redirect(url_for('types'))

@app.route('/types/delete/<int:id>')
@login_required
def delete_type(id):
    if current_user.role != 'admin': return redirect(url_for('types'))
    t = db.session.get(TypeHebergement, id)
    if t and t.hebergements: flash('Utilisé par des hébergements !', 'danger')
    elif t: db.session.delete(t); db.session.commit(); flash('Supprimé', 'warning')
    return redirect(url_for('types'))

# ===================== GESTION UTILISATEURS =====================

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
    if User.query.filter(or_(User.username==username, User.email==email)).first():
        flash('Existe déjà', 'danger')
    else:
        pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        u = User(username=username, email=email, role=role, must_change_password=True)
        u.set_password(pwd)
        db.session.add(u); db.session.commit()
        send_welcome_email(u, pwd) # On envoie le mot de passe en clair au mail
        flash(f'Créé avec succès !', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/edit/<int:id>', methods=['POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin': return redirect(url_for('admin_users'))
    u = db.session.get(User, id)
    if u:
        u.role = request.form.get('role')
        if request.form.get('password'):
            u.set_password(request.form.get('password'))
            u.must_change_password = True
        db.session.commit(); flash('Mis à jour', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:id>')
@login_required
def delete_user(id):
    if current_user.role == 'admin' and id != current_user.id:
        u = db.session.get(User, id)
        if u: db.session.delete(u); db.session.commit(); flash('Supprimé', 'warning')
    return redirect(url_for('admin_users'))

# ===================== DEBUG =====================

@app.route('/debug-reset-admin')
def debug_reset_admin():
    u = User.query.filter_by(username='admin').first()
    if u: db.session.delete(u); db.session.commit()
    a = User(username='admin', email='admin@lephare.com', role='admin', must_change_password=False)
    a.set_password('admin123')
    db.session.add(a); db.session.commit()
    return "✅ Admin réinitialisé !"

@app.route('/api/status')
def api_status():
    return jsonify({'status': 'online' if os.environ.get('RENDER') else 'local'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)