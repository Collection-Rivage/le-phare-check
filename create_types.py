from app import app
from models import db, TypeHebergement

with app.app_context():
    types = TypeHebergement.query.all()
    print("Types existants avant :", [t.nom for t in types])

    # On supprime tout et on recrée (optionnel mais propre)
    for t in types:
        db.session.delete(t)
    db.session.commit()

    types_defaut = [
        TypeHebergement(nom='Cabane'),
        TypeHebergement(nom='Mobil-home Staff'),
        TypeHebergement(nom='Mobil-home Standard'),
        TypeHebergement(nom='Espace Bien Être'),
    ]
    db.session.add_all(types_defaut)
    db.session.commit()

    types = TypeHebergement.query.all()
    print("Types existants après :", [t.nom for t in types])