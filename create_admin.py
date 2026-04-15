from app import app, db, UserAuth

with app.app_context():
    if not UserAuth.query.filter_by(username="admin").first():
        admin = UserAuth(username="admin")
        admin.set_password("123")
        db.session.add(admin)
        db.session.commit()
        print("Usuário admin criado.")
    else:
        print("Usuário admin já existe.")