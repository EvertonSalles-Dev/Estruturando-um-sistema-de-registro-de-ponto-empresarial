from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
import os
import base64
from datetime import datetime
from banco import criar_tabelas

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me")

criar_tabelas()


def conectar():
    return sqlite3.connect("database.db")


@app.context_processor
def inject_usuario():
    return dict(usuario=session.get("usuario"))


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("usuario")
        senha = request.form.get("senha")

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tipo FROM usuarios WHERE usuario=? AND senha=?",
            (user, senha),
        )
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            session["usuario"] = user
            if resultado[0] == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for("sistema"))

        return render_template("login.html", erro="Usuário ou senha inválidos")

    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        tipo = request.form.get("tipo")
        foto = request.files.get("foto")

        caminho_foto = None
        if foto and foto.filename != "":
            os.makedirs("static/perfil", exist_ok=True)
            nome_arquivo = f"{usuario}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            caminho_foto = os.path.join("static/perfil", nome_arquivo)
            foto.save(caminho_foto)

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (usuario, senha, tipo, foto) VALUES (?, ?, ?, ?)",
            (usuario, senha, tipo, caminho_foto),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/sistema", methods=["GET", "POST"])
def sistema():
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario = session["usuario"]
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT foto FROM usuarios WHERE usuario=?", (usuario,))
    resultado = cursor.fetchone()
    foto_usuario = resultado[0] if resultado else None

    if request.method == "POST":
        tipo = request.form.get("tipo")
        foto = request.form.get("foto")

        if foto:
            os.makedirs("static/fotos", exist_ok=True)
            imagem_base64 = foto.split(",")[1]
            nome_arquivo = f"static/fotos/{usuario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            with open(nome_arquivo, "wb") as f:
                f.write(base64.b64decode(imagem_base64))

            cursor.execute(
                "INSERT INTO ponto (usuario, tipo, hora, data, foto) VALUES (?, ?, ?, ?, ?)",
                (
                    usuario,
                    tipo,
                    datetime.now().strftime("%H:%M:%S"),
                    datetime.now().strftime("%Y-%m-%d"),
                    nome_arquivo,
                ),
            )
            conn.commit()

        conn.close()
        return redirect(url_for("sistema"))

    conn.close()
    return render_template("sistema.html", foto_usuario=foto_usuario)


@app.route("/registrar/<tipo>")
def registrar_ponto(tipo):
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario = session["usuario"]
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ponto (usuario, tipo, hora, data) VALUES (?, ?, ?, ?)",
        (
            usuario,
            tipo.capitalize(),
            datetime.now().strftime("%H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d"),
        ),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("sistema"))


@app.route("/admin")
def admin():
    if "usuario" not in session:
        return redirect(url_for("login"))

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            u.usuario,
            u.foto,
            COALESCE(SUM(CASE WHEN p.tipo='Entrada' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN p.tipo='Saída' THEN 1 ELSE 0 END), 0)
        FROM usuarios u
        LEFT JOIN ponto p ON u.usuario = p.usuario
        GROUP BY u.usuario
        """
    )
    resumo = cursor.fetchall()
    cursor.execute(
        "SELECT id, usuario, tipo, hora, data, foto FROM ponto ORDER BY data DESC, hora DESC"
    )
    dados = cursor.fetchall()
    conn.close()

    nomes = [r[0] for r in resumo]
    entradas = [r[2] for r in resumo]
    saidas = [r[3] for r in resumo]

    return render_template(
        "admin.html",
        resumo=resumo,
        dados=dados,
        nomes=nomes,
        entradas=entradas,
        saidas=saidas,
    )


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        hora = request.form.get("hora")
        data = request.form.get("data")
        cursor.execute(
            "UPDATE ponto SET hora = ?, data = ? WHERE id = ?",
            (hora, data, id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("admin"))

    cursor.execute("SELECT * FROM ponto WHERE id = ?", (id,))
    registro = cursor.fetchone()
    conn.close()

    return render_template("editar.html", registro=registro)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario = session["usuario"]
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        foto = request.files.get("foto")
        if foto and foto.filename != "":
            os.makedirs("static/perfil", exist_ok=True)
            nome_arquivo = f"{usuario}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            caminho = os.path.join("static/perfil", nome_arquivo)
            foto.save(caminho)
            cursor.execute("UPDATE usuarios SET foto=? WHERE usuario=?", (caminho, usuario))
            conn.commit()

        conn.close()
        return redirect(url_for("perfil"))

    cursor.execute("SELECT foto FROM usuarios WHERE usuario=?", (usuario,))
    resultado = cursor.fetchone()
    foto_usuario = resultado[0] if resultado else None
    conn.close()

    return render_template("perfil.html", foto_usuario=foto_usuario)


@app.route("/recuperar", methods=["GET", "POST"])
def recuperar_senha():
    if request.method == "POST":
        email = request.form.get("email")
        flash("Se o email existir, enviamos um link de recuperação.", "success")
        return redirect(url_for("recuperar_senha"))
    return render_template("recuperar_senha.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
