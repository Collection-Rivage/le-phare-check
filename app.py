from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from markupsafe import Markup
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Hebergement, Check, TypeHebergement, Incident
from mail import send_welcome_email, send_assignment_email


from sqlalchemy.orm import selectinload, joinedload
from flask_migrate import Migrate
from sqlalchemy import func, or_, desc, select
from sqlalchemy.exc import IntegrityError, DBAPIError
from datetime import datetime
import os
import random
import string

app = Flask(__name__)
app.config.from_object(Config)

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
    """Charge les types frais à chaque appel"""
    return TypeHebergement.query.order_by(TypeHebergement.nom).all()

with app.app_context():
    db.create_all()
    
    # Init Types
    if TypeHebergement.query.count() == 0:
        types_data = [
            TypeHebergement(nom='Cabane', description='Cabanes bois'),
            TypeHebergement(nom='Mobil-home Staff', description='Staff'),
            TypeHebergement(nom='Mobil-home Standard', description='Clients'),
            TypeHebergement(nom='Espace Bien Être', description='Spa')
        ]
        db.session.add_all(types_data)
        db.session.commit()
    
    # Init Admin
    if User.query.filter_by(username='admin').first() is None:
        admin = User(username='admin', email='admin@lephare.com', role='admin', must_change_password=False)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# ===================== FONCTIONS HELPER =====================

def recalculer_statut_hebergement(hebergement_id):
    """Recalcule le statut d'un hébergement quand un incident est résolu"""
    heb = db.session.get(Hebergement, hebergement_id)
    if not heb:
        return
    
    incidents_ouverts = Incident.query.filter_by(
        hebergement_id=hebergement_id, 
        statut='ouvert'
    ).count()
    
    if incidents_ouverts > 0:
        return
    
    dernier_check = Check.query.filter_by(hebergement_id=hebergement_id)\
        .order_by(desc(Check.created_at))\
        .first()
    
    if dernier_check:
        if dernier_check.probleme_critique:
            heb.statut = 'probleme'
        elif all([dernier_check.electricite, dernier_check.plomberie, 
                 dernier_check.chauffage, dernier_check.proprete, 
                 dernier_check.equipements]):
            heb.statut = 'ok'
        else:
            heb.statut = 'alerte'
    else:
        heb.statut = 'ok'
    
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
            return redirect(url_for('change_password') if user.must_change_password else 'dashboard')
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

# ===================== DASHBOARD =====================

@app.route('/dashboard')
@login_required
def dashboard():
    total = Hebergement.query.count()
    stats = dict(db.session.query(
        Hebergement.statut, 
        func.count(Hebergement.id)
    ).group_by(Hebergement.statut).all())
    
    ok = stats.get('ok', 0)
    alerte = stats.get('alerte', 0)
    probleme = stats.get('probleme', 0)
    
    derniers_checks = Check.query.options(
        joinedload(Check.hebergement),
        joinedload(Check.technicien)
    ).order_by(desc(Check.created_at)).limit(10).all()
    
    return render_template(
        'dashboard.html', 
        total=total, 
        ok=ok, 
        alerte=alerte, 
        probleme=probleme, 
        taux_ok=round((ok/total)*100, 1) if total else 0, 
        derniers_checks=derniers_checks
    )

# ===================== HEBERGEMENTS =====================

@app.route('/hebergements')
@login_required
def hebergements():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()
    statut = request.args.get('statut', '')
    type_id_str = request.args.get('type_id', '')
    
    type_id = None
    if type_id_str:
        try:
            type_id = int(type_id_str)
        except ValueError:
            type_id = None
    
    c_stats = db.session.query(
        Check.hebergement_id.label("hid"), 
        func.count(Check.id).label("cnt"), 
        func.max(Check.created_at).label("last")
    ).group_by(Check.hebergement_id).subquery()
    
    i_stats = db.session.query(
        Incident.hebergement_id.label("hid"), 
        func.count(Incident.id).label("cnt")
    ).filter(Incident.statut == 'ouvert').group_by(Incident.hebergement_id).subquery()
    
    query = db.session.query(
        Hebergement, 
        func.coalesce(c_stats.c.cnt, 0), 
        c_stats.c.last, 
        func.coalesce(i_stats.c.cnt, 0)
    ).outerjoin(c_stats, c_stats.c.hid == Hebergement.id
    ).outerjoin(i_stats, i_stats.c.hid == Hebergement.id
    ).options(
        selectinload(Hebergement.type_hebergement),
        selectinload(Hebergement.incidents)
    )
    
    if q:
        query = query.filter(
            or_(
                Hebergement.emplacement.ilike(f'%{q}%'),
                Hebergement.numero_chassis.ilike(f'%{q}%')
            )
        )
    
    if statut:
        query = query.filter(Hebergement.statut == statut)
    
    if type_id is not None:
        query = query.filter(Hebergement.type_id == type_id)
    
    query = query.order_by(
        Hebergement.type_id.asc(),
        func.length(Hebergement.emplacement).asc(),
        Hebergement.emplacement.asc()
    )
    
    h_list = query.paginate(page=page, per_page=30, error_out=False)
    
    return render_template(
        'hebergements.html', 
        hebergements=h_list, 
        types=get_types(),
        q=q,
        statut=statut,
        type_id=type_id_str
    )

@app.route('/hebergements/add', methods=['POST'])
@login_required
def add_hebergement():
    if current_user.role != 'admin':
        return redirect(url_for('hebergements'))
    h = Hebergement(
        emplacement=request.form.get('emplacement'),
        type_id=request.form.get('type_id'),
        numero_chassis=request.form.get('numero_chassis'),
        nb_personnes=request.form.get('nb_personnes'),
        compteur_eau=request.form.get('compteur_eau')
    )
    db.session.add(h)
    db.session.commit()
    flash('Ajouté', 'success')
    return redirect(url_for('hebergements'))

@app.route('/hebergements/edit/<int:id>', methods=['POST'])
@login_required
def edit_hebergement(id):
    if current_user.role != 'admin':
        return redirect(url_for('hebergements'))
    h = db.session.get(Hebergement, id)
    if not h:
        flash('Hébergement introuvable', 'danger')
        return redirect(url_for('hebergements'))
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
    if current_user.role != 'admin':
        return redirect(url_for('hebergements'))
    h = db.session.get(Hebergement, id)
    if not h:
        flash('Hébergement introuvable', 'danger')
        return redirect(url_for('hebergements'))
    db.session.delete(h)
    db.session.commit()
    flash('Supprimé', 'warning')
    return redirect(url_for('hebergements'))

# ===================== CHECKS =====================

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
        if c.probleme_critique:
            heb.statut = 'probleme'
        elif not all([c.electricite, c.plomberie, c.chauffage, c.proprete, c.equipements]):
            heb.statut = 'alerte'
        else:
            heb.statut = 'ok'
        db.session.commit()
        flash('Enregistré !', 'success')
        return redirect(url_for('dashboard'))
    return render_template('check.html', hebergement=heb)

@app.route('/historique')
@login_required
def historique():
    checks = Check.query.options(
        joinedload(Check.hebergement),
        joinedload(Check.technicien)
    ).order_by(desc(Check.created_at)).limit(50).all()
    return render_template('historique.html', checks=checks)

# ===================== INCIDENTS =====================

@app.route('/incident/<int:hebergement_id>', methods=['GET', 'POST'])
@login_required
def signaler_incident(hebergement_id):
    heb = db.session.get(Hebergement, hebergement_id)
    if not heb:
        flash('Hébergement non trouvé', 'danger')
        return redirect(url_for('hebergements'))
    
    # Vider le cache pour forcer la relecture depuis PostgreSQL
    db.session.expire_all()
    
    # Charger les techniciens frais
    techs = User.query.filter(
        User.role.in_(['technicien', 'admin'])
    ).order_by(User.username).all()
    
    # Liste des IDs valides
    valid_ids = {t.id for t in techs}
    
    if request.method == 'POST':
        type_incident = request.form.get('type_incident', '')
        description = request.form.get('description', '')
        
        # Récupération et validation stricte
        assigne_a_raw = request.form.get('assigne_a', '')
        assigne_a = None
        
        if assigne_a_raw and assigne_a_raw.strip():
            try:
                user_id = int(assigne_a_raw.strip())
                # Vérification dans la liste fraîche
                if user_id in valid_ids:
                    # Double vérification avec requête explicite
                    user_exists = db.session.execute(
                        select(User.id).where(User.id == user_id)
                    ).scalar_one_or_none()
                    
                    if user_exists:
                        assigne_a = user_id
                    else:
                        flash('Le technicien sélectionné n\'existe pas.', 'warning')
                else:
                    flash('Technicien invalide.', 'warning')
            except ValueError:
                flash('ID invalide.', 'warning')
        
        # CRÉATION
        i = Incident(
            hebergement_id=hebergement_id,
            type_incident=type_incident,
            description=description,
            assigne_a=assigne_a,
            cree_par=current_user.id
        )
        db.session.add(i)
        
        # Mise à jour statut
        if type_incident == 'urgence':
            heb.statut = 'probleme'
        else:
            heb.statut = 'alerte'
        
        # COMMIT avec gestion d'erreur
        try:
            db.session.commit()
            
            # Email si assigné
            if assigne_a:
                technicien = db.session.get(User, assigne_a)
                if technicien:
                    try:
                        send_assignment_email(i, technicien)
                    except Exception as e:
                        print(f"Erreur email: {e}")
            
            if assigne_a:
                flash('Incident signalé et assigné avec succès !', 'success')
            else:
                flash('Incident signalé (sans technicien assigné).', 'warning')
                
            return redirect(url_for('hebergements'))
            
        except (IntegrityError, DBAPIError) as e:
            db.session.rollback()
            
            # Recréation sans assignation
            i2 = Incident(
                hebergement_id=hebergement_id,
                type_incident=type_incident,
                description=description,
                assigne_a=None,
                cree_par=current_user.id
            )
            db.session.add(i2)
            
            heb2 = db.session.get(Hebergement, hebergement_id)
            if type_incident == 'urgence':
                heb2.statut = 'probleme'
            else:
                heb2.statut = 'alerte'
            
            db.session.commit()
            
            flash('Incident créé mais SANS technicien assigné (ID invalide en base).', 'warning')
            return redirect(url_for('hebergements'))
    
    return render_template('incident.html', hebergement=heb, techniciens=techs)

@app.route('/incident/<int:incident_id>/resoudre', methods=['POST'])
@login_required
def resoudre_incident(incident_id):
    incident = db.session.get(Incident, incident_id)
    
    if not incident:
        flash('Incident introuvable', 'danger')
        return redirect(url_for('hebergements'))
    
    if current_user.role != 'admin' and current_user.id != incident.assigne_a:
        flash('Vous ne pouvez pas résoudre cet incident', 'danger')
        return redirect(url_for('hebergements'))
    
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
    if not heb:
        flash('Hébergement non trouvé', 'danger')
        return redirect(url_for('hebergements'))
    
    incidents = Incident.query.options(
        joinedload(Incident.technicien)
    ).filter_by(
        hebergement_id=hebergement_id,
        statut='ouvert'
    ).order_by(desc(Incident.created_at)).all()
    
    return render_template('problemes.html', hebergement=heb, incidents=incidents)

# ===================== TYPES =====================

@app.route('/types')
@login_required
def types():
    return render_template('types.html', types=get_types())

@app.route('/types/add', methods=['POST'])
@login_required
def add_type():
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('types'))
    t = TypeHebergement(nom=request.form.get('nom'), description=request.form.get('description'))
    db.session.add(t)
    db.session.commit()
    flash('Type ajouté', 'success')
    return redirect(url_for('types'))

@app.route('/types/edit/<int:id>', methods=['POST'])
@login_required
def edit_type(id):
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('types'))
    t = db.session.get(TypeHebergement, id)
    if not t:
        flash('Type introuvable', 'danger')
        return redirect(url_for('types'))
    t.nom = request.form.get('nom')
    t.description = request.form.get('description')
    db.session.commit()
    flash('Type modifié', 'success')
    return redirect(url_for('types'))

@app.route('/types/delete/<int:id>')
@login_required
def delete_type(id):
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('types'))
    t = db.session.get(TypeHebergement, id)
    if not t:
        flash('Type introuvable', 'danger')
        return redirect(url_for('types'))
    if t.hebergements:
        flash('Type utilisé ! Impossible de supprimer.', 'danger')
    else:
        db.session.delete(t)
        db.session.commit()
        flash('Supprimé', 'warning')
    return redirect(url_for('types'))

# ===================== UTILISATEURS =====================

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('dashboard'))
    users = User.query.order_by(desc(User.created_at)).all()
    return render_template('admin_users.html', users=users)

    @app.route('/admin/users/add', methods=['POST'])
@login_required
def add_user():
    """Création d'un utilisateur"""
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('dashboard'))
    
    username = request.form.get('username')
    email = request.form.get('email')
    role = request.form.get('role')
    
    # Vérifications
    if not username or not email:
        flash('Nom d\'utilisateur et email requis', 'danger')
        return redirect(url_for('admin_users'))
    
    # Vérifier si existe déjà
    if User.query.filter(or_(User.username == username, User.email.ilike(email))).first():
        flash('Utilisateur existe déjà', 'danger')
        return redirect(url_for('admin_users'))
    
    # Création
    password_en_clair = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    u = User(username=username, email=email, role=role, must_change_password=True)
    u.set_password(password_en_clair)
    db.session.add(u)
    db.session.commit()
    
    # Tentative d'envoi email (sans bloquer l'affichage)
    try:
        send_welcome_email(u, password_en_clair)
        flash(f'✅ Utilisateur {username} créé et email envoyé !', 'success')
    except Exception as e:
        print(f"Erreur email: {e}")
        # On affiche quand même que l'utilisateur est créé, même si le mail échoue
        flash(f'✅ Utilisateur {username} créé !', 'success')
        flash(f'⚠️ Erreur envoi email (vérifiez la config Resend). Mot de passe : {password_en_clair}', 'warning')
    
    return redirect(url_for('admin_users'))
   
@app.route('/admin/users/edit/<int:id>', methods=['POST'])
@login_required
def edit_user(id):
    """Modification d'un utilisateur"""
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('dashboard'))
    
    u = db.session.get(User, id)
    if not u:
        flash('Utilisateur introuvable', 'danger')
        return redirect(url_for('admin_users'))
    
    # Empêcher de modifier son propre rôle
    if id == current_user.id and request.form.get('role') != current_user.role:
        flash('Vous ne pouvez pas modifier votre propre rôle', 'danger')
        return redirect(url_for('admin_users'))
    
    u.role = request.form.get('role')
    if request.form.get('password'):
        u.set_password(request.form.get('password'))
        u.must_change_password = True
        flash('Mot de passe réinitialisé', 'success')
    
    db.session.commit()
    flash('Mis à jour', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:id>')
@login_required
def delete_user(id):
    """Suppression d'un utilisateur avec vérifications"""
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('admin_users'))
    
    # Empêcher de se supprimer soi-même
    if id == current_user.id:
        flash('Vous ne pouvez pas vous supprimer vous-même !', 'danger')
        return redirect(url_for('admin_users'))
    
    # Vérifier que l'utilisateur existe
    u = db.session.get(User, id)
    if not u:
        flash('Utilisateur introuvable', 'danger')
        return redirect(url_for('admin_users'))
    
    try:
        db.session.delete(u)
        db.session.commit()
        flash('Supprimé', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'danger')
    
    return redirect(url_for('admin_users'))

@app.route('/api/status')
def api_status():
    return jsonify({'status': 'online' if os.environ.get("RENDER") else 'local'})
    
# --- ROUTE TEMPORAIRE POUR DÉBLOQUER RESEND ---
@app.route('/debloquer-resend')
def debloquer_resend():
    try:
        import resend
        # On utilise TA clé API déjà définie dans mail.py ou on la remet ici si besoin
        # Assure-toi que resend.api_key est bien défini au début de app.py ou importe-le
        
        # Si tu as déjà importé resend dans app.py, sinon ajoute : import resend
        
        info = resend.Emails.send({
            "from": "stephane@lephare-iledere.com",  # TON EMAIL EXACT
            "to": ["stephane@lephare-iledere.com"],  # TON EMAIL EXACT
            "subject": "TEST DEBLOCAGE RESEND",
            "html": "<h1>Si tu reçois ça, c'est gagné !</h1><p>Ton compte Resend est maintenant actif.</p>"
        })
        return f"✅ Mail envoyé avec succès ! ID: {info['id']}"
    except Exception as e:
        return f"❌ Erreur : {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
