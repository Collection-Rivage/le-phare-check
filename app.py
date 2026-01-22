from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Hebergement, Check, TypeHebergement, Incident
from mail import mail, send_welcome_email
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
    return User.query.get(int(user_id))


# ===================== INITIALISATION =====================
with app.app_context():
    db.create_all()
    
    if User.query.count() == 0:
        admin = User(username='admin', email='admin@lephare.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin créé")
    
    if TypeHebergement.query.count() == 0:
        types_defaut = [
            TypeHebergement(nom='Cabane'),
            TypeHebergement(nom='Mobil-home Staff'),
            TypeHebergement(nom='Mobil-home Standard'),
            TypeHebergement(nom='Espace Bien Être'),
        ]
        db.session.add_all(types_defaut)
        db.session.commit()
        print("Types créés")
    
    if Hebergement.query.count() == 0:
        print("Création des 218 hébergements...")
        type_cabane = TypeHebergement.query.filter_by(nom='Cabane').first()
        type_mh_staff = TypeHebergement.query.filter_by(nom='Mobil-home Staff').first()
        type_bien_etre = TypeHebergement.query.filter_by(nom='Espace Bien Être').first()
        
        h = []
        compteurs = ['devant_droite', 'devant_gauche', 'arriere_droite', 'arriere_gauche', 'devant_milieu', 'arriere_milieu']
        
        for i in range(1, 190):
            h.append(Hebergement(
                emplacement=str(i),
                type_id=type_cabane.id,
                numero_chassis=f"CAB-2024-{str(i).zfill(3)}",
                nb_personnes=4 if i % 3 == 0 else 2,
                compteur_eau=compteurs[i % 6]
            ))
        
        for i in range(1, 29):
            h.append(Hebergement(
                emplacement=f"STAFF-{str(i).zfill(2)}",
                type_id=type_mh_staff.id,
                numero_chassis=f"MHS-2024-{str(i).zfill(3)}",
                nb_personnes=2,
                compteur_eau=compteurs[i % 6]
            ))
        
        h.append(Hebergement(
            emplacement='BIEN-ETRE-01',
            type_id=type_bien_etre.id,
            numero_chassis='EBE-2024-001',
            nb_personnes=10,
            compteur_eau='devant_milieu'
        ))
        
        db.session.add_all(h)
        db.session.commit()
        print("218 hébergements créés !")


# ===================== ROUTES =====================

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('dashboard'))
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
    total = Hebergement.query.count()
    ok = Hebergement.query.filter_by(statut='ok').count()
    alerte = Hebergement.query.filter_by(statut='alerte').count()
    probleme = Hebergement.query.filter_by(statut='probleme').count()
    derniers_checks = Check.query.order_by(Check.created_at.desc()).limit(5).all()
    is_online = os.environ.get('RENDER') is not None
    return render_template('dashboard.html', total=total, ok=ok, alerte=alerte, probleme=probleme,
                         derniers_checks=derniers_checks, is_online=is_online)

@app.route('/hebergements')
@login_required
def hebergements():
    hebergements_list = Hebergement.query.all()
    types = TypeHebergement.query.all()
    is_online = os.environ.get('RENDER') is not None
    return render_template('hebergements.html', hebergements=hebergements_list, types=types, is_online=is_online)

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
        
        if nouveau_check.probleme_critique:
            hebergement.statut = 'probleme'
        elif not all([nouveau_check.electricite, nouveau_check.plomberie, nouveau_check.chauffage, nouveau_check.proprete, nouveau_check.equipements]):
            hebergement.statut = 'alerte'
        else:
            hebergement.statut = 'ok'
        
        db.session.commit()
        flash('Check enregistré !', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('check.html', hebergement=hebergement, is_online=is_online)

@app.route('/historique')
@login_required
def historique():
    checks = Check.query.order_by(Check.created_at.desc()).all()
    is_online = os.environ.get('RENDER') is not None
    return render_template('historique.html', checks=checks, is_online=is_online)

@app.route('/types')
@login_required
def types():
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('dashboard'))
    types = TypeHebergement.query.all()
    is_online = os.environ.get('RENDER') is not None
    return render_template('types.html', types=types, is_online=is_online)

@app.route('/incident/<int:hebergement_id>', methods=['GET', 'POST'])
@login_required
def signaler_incident(hebergement_id):
    hebergement = Hebergement.query.get_or_404(hebergement_id)
    techniciens = User.query.filter(User.role.in_(['technicien', 'admin'])).all()
    
    if request.method == 'POST':
        incident = Incident(
            hebergement_id=hebergement_id,
            type_incident=request.form.get('type_incident'),
            description=request.form.get('description'),
            assigne_a=request.form.get('assigne_a') or None,
            cree_par=current_user.id
        )
        db.session.add(incident)
        hebergement.statut = 'probleme' if request.form.get('type_incident') == 'urgence' else 'alerte'
        db.session.commit()
        flash('Incident signalé !', 'success')
        return redirect(url_for('hebergements'))
    
    is_online = os.environ.get('RENDER') is not None
    return render_template('incident.html', hebergement=hebergement, techniciens=techniciens, is_online=is_online)

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('dashboard'))
    users = User.query.order_by(User.created_at.desc()).all()
    is_online = os.environ.get('RENDER') is not None
    return render_template('admin_users.html', users=users, is_online=is_online)

@app.route('/admin/users/add', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('admin_users'))
    
    username = request.form.get('username')
    email = request.form.get('email')
    password_input = request.form.get('password')
    role = request.form.get('role')
    
    if User.query.filter_by(username=username).first():
        flash('Nom d’utilisateur déjà pris', 'danger')
    elif User.query.filter_by(email=email).first():
        flash('Email déjà utilisé', 'danger')
    else:
        password = password_input or ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        send_welcome_email(user, password)
        flash(f'Utilisateur {username} créé et email envoyé !', 'success')
    return redirect(url_for('admin_users'))

@app.route('/api/status')
def api_status():
    is_online = os.environ.get('RENDER') is not None
    return jsonify({'status': 'online' if is_online else 'local'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
