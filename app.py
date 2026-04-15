from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

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

@app.route("/")
def home():
    nome = "Gabriel"
    return render_template("index.html", nome_usuario=nome)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/formulario", methods=["GET", "POST"])
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
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template("usuarios.html", usuarios=usuarios)

@app.route("/deletar/<int:id>", methods=["POST"])
def deletar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()

    flash("Usuário excluído com sucesso!")
    return redirect(url_for("listar_usuarios"))

@app.route("/confirmar_delecao/<int:id>")
def confirmar_delecao(id):
    usuario = Usuario.query.get_or_404(id)
    return render_template("confirmar_delecao.html", usuario=usuario)

@app.route("/editar/<int:id>", methods=["GET", "POST"])
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
def resultado(nome):
    return render_template("resultado.html", nome=nome)

if __name__ == "__main__":
    app.run(debug=True)