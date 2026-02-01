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

# Initialisation automatique
with app.app_context():
    db.create_all()
    if TypeHebergement.query.count() == 0:
        t1 = TypeHebergement(nom='Cabane', description='En bois'); t2 = TypeHebergement(nom='Mobil-home Staff', description='Staff')
        t3 = TypeHebergement(nom='Mobil-home Standard', description='Clients'); t4 = TypeHebergement(nom='Espace Bien Être', description='Spa')
        db.session.add_all([t1, t2, t3, t4]); db.session.commit()
    
    if User.query.filter_by(username='admin').first() is None:
        admin = User(username='admin', email='admin@lephare.com', role='admin', must_change_password=False)
        admin.set_password('admin123'); db.session.add(admin); db.session.commit()

    if Hebergement.query.count() == 0:
        type_cabane = TypeHebergement.query.filter_by(nom='Cabane').first()
        type_staff = TypeHebergement.query.filter_by(nom='Mobil-home Staff').first()
        type_be = TypeHebergement.query.filter_by(nom='Espace Bien Être').first()
        compteurs = ['devant_droite', 'devant_gauche', 'arriere_droite', 'arriere_gauche', 'devant_milieu', 'arriere_milieu']
        h_list = []
        for i in range(1, 190): h_list.append(Hebergement(emplacement=str(i), type_id=type_cabane.id, numero_chassis=f"CAB-2024-{str(i).zfill(3)}", nb_personnes=2, compteur_eau=compteurs[i%6]))
        for i in range(1, 29): h_list.append(Hebergement(emplacement=f"STAFF-{str(i).zfill(2)}", type_id=type_staff.id, numero_chassis=f"MHS-2024-{str(i).zfill(2)}", nb_personnes=2, compteur_eau=compteurs[i%6]))
        h_list.append(Hebergement(emplacement='BIEN-ETRE-01', type_id=type_be.id, nb_personnes=10))
        db.session.add_all(h_list); db.session.commit()

# ===================== ROUTES =====================

@app.route('/')
@login_required
def index():
    return redirect(url_for('change_password') if current_user.must_change_password else 'dashboard')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('change_password') if user.must_change_password else 'dashboard')
        flash('Identifiants incorrects', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout(): logout_user(); return redirect(url_for('login'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        new_pwd = request.form.get('new_password')
        if new_pwd != request.form.get('confirm_password'): flash('Erreur de confirmation', 'danger')
        else:
            current_user.set_password(new_pwd); current_user.must_change_password = False
            db.session.commit(); flash('Mot de passe mis à jour !', 'success')
            return redirect(url_for('dashboard'))
    return render_template('change_password.html')

@app.route('/dashboard')
@login_required
def dashboard():
    total = Hebergement.query.count()
    stats = dict(db.session.query(Hebergement.statut, func.count(Hebergement.id)).group_by(Hebergement.statut).all())
    ok, alerte, probleme = stats.get('ok', 0), stats.get('alerte', 0), stats.get('probleme', 0)
    derniers_checks = Check.query.options(selectinload(Check.hebergement), selectinload(Check.technicien)).order_by(Check.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', total=total, ok=ok, alerte=alerte, probleme=probleme, taux_ok=round((ok/total)*100,1) if total else 0, derniers_checks=derniers_checks)

@app.route('/hebergements')
@login_required
def hebergements():
    page = request.args.get('page', 1, type=int)
    c_stats = db.session.query(Check.hebergement_id.label("hid"), func.count(Check.id).label("cnt"), func.max(Check.created_at).label("last")).group_by(Check.hebergement_id).subquery()
    i_stats = db.session.query(Incident.hebergement_id.label("hid"), func.count(Incident.id).label("cnt")).group_by(Incident.hebergement_id).subquery()
    query = db.session.query(Hebergement, func.coalesce(c_stats.c.cnt, 0), c_stats.c.last, func.coalesce(i_stats.c.cnt, 0)).outerjoin(c_stats, c_stats.c.hid == Hebergement.id).outerjoin(i_stats, i_stats.c.hid == Hebergement.id).options(selectinload(Hebergement.type_hebergement)).order_by(Hebergement.emplacement.asc())
    h_list = query.paginate(page=page, per_page=20, error_out=False)
    return render_template('hebergements.html', hebergements=h_list, types=TypeHebergement.query.all())

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
        db.session.commit(); flash('Check enregistré !', 'success'); return redirect(url_for('dashboard'))
    return render_template('check.html', hebergement=heb)

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    return render_template('admin_users.html', users=User.query.order_by(User.created_at.desc()).all())

@app.route('/admin/users/add', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    username, email, role = request.form.get('username'), request.form.get('email'), request.form.get('role')
    if User.query.filter(or_(User.username==username, User.email==email)).first(): flash('Existe déjà', 'danger')
    else:
        pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        u = User(username=username, email=email, role=role, must_change_password=True); u.set_password(pwd)
        db.session.add(u); db.session.commit()
        send_welcome_email(u, pwd)
        flash(f'Utilisateur créé ! Mot de passe envoyé : {pwd}', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/edit/<int:id>', methods=['POST'])
@login_required
def edit_user(id):
    u = db.session.get(User, id)
    if u and current_user.role == 'admin':
        u.role = request.form.get('role')
        if request.form.get('password'): u.set_password(request.form.get('password')); u.must_change_password = True
        db.session.commit(); flash('Mis à jour', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:id>')
@login_required
def delete_user(id):
    if current_user.role == 'admin' and id != current_user.id:
        u = db.session.get(User, id); db.session.delete(u); db.session.commit(); flash('Supprimé', 'warning')
    return redirect(url_for('admin_users'))

@app.route('/types')
@login_required
def types():
    return render_template('types.html', types=TypeHebergement.query.all())

@app.route('/historique')
@login_required
def historique():
    checks = Check.query.options(selectinload(Check.hebergement), selectinload(Check.technicien)).order_by(Check.created_at.desc()).all()
    return render_template('historique.html', checks=checks)

@app.route('/debug-reset-admin')
def debug_reset_admin():
    u = User.query.filter_by(username='admin').first()
    if u: db.session.delete(u); db.session.commit()
    a = User(username='admin', email='admin@lephare.com', role='admin', must_change_password=False); a.set_password('admin123')
    db.session.add(a); db.session.commit(); return "✅ OK"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)