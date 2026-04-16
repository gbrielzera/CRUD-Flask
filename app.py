from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Usuario {self.nome}>"
    
class UserAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
with app.app_context():
    db.create_all()

    if not UserAuth.query.filter_by(username="admin").first():
        admin = UserAuth(username="admin")
        admin.set_password("123")
        db.session.add(admin)
        db.session.commit()
    
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Faça login para acessar esta página.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/logout")
def logout():
    session.clear()
    flash("Logout realizado com sucesso.")
    return redirect(url_for("login"))

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("listar_usuarios"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = UserAuth.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash("Usuário ou senha inválidos")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        flash("Login realizado com sucesso!")
        return redirect(url_for("listar_usuarios"))

    return render_template("login.html")


@app.route("/formulario", methods=["GET", "POST"])
@login_required
def formulario():
    erro = None

    if request.method == "POST":
        nome = request.form["nome"]

        if nome.strip() == "":
            flash("Por favor digite um nome!")
            return redirect(url_for("formulario"))

        novo_usuario = Usuario(nome = nome)
        db.session.add(novo_usuario)
        db.session.commit()

        flash("Nome salvo com sucesso!")
        return redirect(url_for("listar_usuarios"))

    return render_template("formulario.html", erro=erro)

@app.route("/usuarios")
@login_required
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template("usuarios.html", usuarios=usuarios)

@app.route("/deletar/<int:id>", methods=["POST"])
@login_required
def deletar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()

    flash("Usuário excluído com sucesso!")
    return redirect(url_for("listar_usuarios"))

@app.route("/confirmar_delecao/<int:id>")
@login_required
def confirmar_delecao(id):
    usuario = Usuario.query.get_or_404(id)
    return render_template("confirmar_delecao.html", usuario=usuario)

@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    if request.method == "POST":
        nome = request.form["nome"]

        if nome.strip() == "":
            flash("O nome não pode ficar vazio!")
            return redirect(url_for("editar_usuario", id=id))
        
        usuario.nome = nome
        db.session.commit()
        
        flash("Usuário atualizado com sucesso!")
        return redirect(url_for("listar_usuarios"))
    
    return render_template("editar.html", usuario=usuario)


@app.route("/resultado/<nome>")
@login_required
def resultado(nome):
    return render_template("resultado.html", nome=nome)

if __name__ == "__main__":
    app.run()