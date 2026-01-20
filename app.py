from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Hebergement, Check, TypeHebergement
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
    
    # Créer un utilisateur admin par défaut
    if User.query.count() == 0:
        admin = User(username='admin', email='admin@lephare.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Utilisateur admin créé : admin / admin123")
    
    # Créer des types par défaut
    if TypeHebergement.query.count() == 0:
        types_defaut = [
            TypeHebergement(nom='Cabane', description='Cabane sur pilotis'),
            TypeHebergement(nom='Mobil-home Staff', description='Mobil-home pour le personnel'),
            TypeHebergement(nom='Mobil-home Standard', description='Mobil-home standard'),
        ]
        db.session.add_all(types_defaut)
        db.session.commit()
        print("✅ Types d'hébergement créés")


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
    types = TypeHebergement.query.all()
    is_online = os.environ.get('RENDER') is not None
    return render_template('hebergements.html', hebergements=hebergements_list, types=types, is_online=is_online)


@app.route('/hebergements/add', methods=['POST'])
@login_required
def add_hebergement():
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('hebergements'))
    
    emplacement = request.form.get('emplacement')
    type_id = request.form.get('type_id')
    numero_chassis = request.form.get('numero_chassis')
    nb_personnes = request.form.get('nb_personnes')
    compteur_eau = request.form.get('compteur_eau')
    
    nouvel_heb = Hebergement(
        emplacement=emplacement,
        type_id=type_id,
        numero_chassis=numero_chassis,
        nb_personnes=nb_personnes,
        compteur_eau=compteur_eau
    )
    db.session.add(nouvel_heb)
    db.session.commit()
    
    flash(f'Hébergement "{emplacement}" ajouté avec succès', 'success')
    return redirect(url_for('hebergements'))


@app.route('/hebergements/edit/<int:id>', methods=['POST'])
@login_required
def edit_hebergement(id):
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('hebergements'))
    
    heb = Hebergement.query.get_or_404(id)
    heb.emplacement = request.form.get('emplacement')
    heb.type_id = request.form.get('type_id')
    heb.numero_chassis = request.form.get('numero_chassis')
    heb.nb_personnes = request.form.get('nb_personnes')
    heb.compteur_eau = request.form.get('compteur_eau')
    
    db.session.commit()
    flash(f'Hébergement "{heb.emplacement}" modifié avec succès', 'success')
    return redirect(url_for('hebergements'))


@app.route('/hebergements/delete/<int:id>')
@login_required
def delete_hebergement(id):
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('hebergements'))
    
    heb = Hebergement.query.get_or_404(id)
    emplacement = heb.emplacement
    db.session.delete(heb)
    db.session.commit()
    
    flash(f'Hébergement "{emplacement}" supprimé', 'warning')
    return redirect(url_for('hebergements'))


# ==================== GESTION DES TYPES ====================

@app.route('/types')
@login_required
def types_hebergement():
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('dashboard'))
    
    types = TypeHebergement.query.all()
    is_online = os.environ.get('RENDER') is not None
    return render_template('types.html', types=types, is_online=is_online)


@app.route('/types/add', methods=['POST'])
@login_required
def add_type():
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('types_hebergement'))
    
    nom = request.form.get('nom')
    description = request.form.get('description')
    
    nouveau_type = TypeHebergement(nom=nom, description=description)
    db.session.add(nouveau_type)
    db.session.commit()
    
    flash(f'Type "{nom}" ajouté avec succès', 'success')
    return redirect(url_for('types_hebergement'))


@app.route('/types/edit/<int:id>', methods=['POST'])
@login_required
def edit_type(id):
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('types_hebergement'))
    
    type_heb = TypeHebergement.query.get_or_404(id)
    type_heb.nom = request.form.get('nom')
    type_heb.description = request.form.get('description')
    
    db.session.commit()
    flash(f'Type "{type_heb.nom}" modifié avec succès', 'success')
    return redirect(url_for('types_hebergement'))


@app.route('/types/delete/<int:id>')
@login_required
def delete_type(id):
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('types_hebergement'))
    
    type_heb = TypeHebergement.query.get_or_404(id)
    
    # Vérifier qu'aucun hébergement n'utilise ce type
    if len(type_heb.hebergements) > 0:
        flash(f'Impossible de supprimer : {len(type_heb.hebergements)} hébergement(s) utilisent ce type', 'danger')
        return redirect(url_for('types_hebergement'))
    
    nom = type_heb.nom
    db.session.delete(type_heb)
    db.session.commit()
    
    flash(f'Type "{nom}" supprimé', 'warning')
    return redirect(url_for('types_hebergement'))


# ==================== CHECKS ====================

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
        elif not (nouveau_check.electricite and nouveau_check.plomberie and 
                 nouveau_check.chauffage and nouveau_check.proprete and 
                 nouveau_check.equipements):
            hebergement.statut = 'alerte'
        else:
            hebergement.statut = 'ok'
        
        db.session.commit()
        
        # Envoi de l'email si problème (désactivé temporairement)
        # if hebergement.statut != 'ok':
        #     try:
        #         send_alert_email(nouveau_check, hebergement, current_user)
        #     except Exception as e:
        #         print(f"Erreur envoi email : {e}")
        
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
