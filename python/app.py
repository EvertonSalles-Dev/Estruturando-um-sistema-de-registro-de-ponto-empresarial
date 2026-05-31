<<<<<<< HEAD
from flask import Flask, redirect
import sqlite3
import os
import base64
from datetime import datetime
from banco import criar_tabelas
from services.admin_service import buscar_resumo
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
 @app.route("/favicon.ico")
def favicon():
    # /vercel.svg is automatically served when included in the public/** directory.
    return redirect("/vercel.svg", code=307)

criar_tabelas()


@app.route("/recuperar", methods=["GET", "POST"])
def recuperar_senha():
    if request.method == "POST":
        email = request.form["email"]
        # Aqui você faria a lógica de enviar o link por email
        flash("Se o email existir, enviamos um link de recuperação.", "success")
        return redirect(url_for("recuperar_senha"))
    return render_template("recuperar_senha.html")

# ================= CONEXÃO =================
def conectar():
    return sqlite3.connect("database.db")
# ===== CORRIGIR BANCO AUTOMATICAMENTE =====
conn = conectar()
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE usuarios ADD COLUMN foto TEXT")
    print("Coluna foto criada!")
except:
    print("Coluna foto já existe")

conn.commit()
conn.close()
 
@app.context_processor
def inject_usuario():
    return dict(usuario=session.get("usuario"))

@app.route("/")
def home():
    return redirect("/login")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["usuario"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT tipo FROM usuarios WHERE usuario=? AND senha=?",
            (user, senha)
        )

        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            session["usuario"] = user

            if resultado[0] == "admin":
                return redirect("/admin")
            else:
                return redirect("/sistema")

        return render_template("login.html", erro="Usuario ou senha invalidos", usuario=user)

    return render_template("login.html")


# ================= CADASTRO =================
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        tipo = request.form.get("tipo")
        foto = request.files.get("foto")

        caminho_foto = None

        if foto and foto.filename != "":
            if not os.path.exists("static/perfil"):
                os.makedirs("static/perfil")

            nome_arquivo = f"{usuario}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            caminho_foto = os.path.join("static/perfil", nome_arquivo)
            foto.save(caminho_foto)

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO usuarios (usuario, senha, tipo, foto)
            VALUES (?, ?, ?, ?)
        """, (usuario, senha, tipo, caminho_foto))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("cadastro.html")


# ================= SISTEMA FUNCIONÁRIO =================
@app.route("/sistema", methods=["GET", "POST"])
def sistema():
    if "usuario" not in session:
        return redirect("/")

    usuario = session["usuario"]

    conn = conectar()
    cursor = conn.cursor()

    # pegar foto do usuario
    cursor.execute("SELECT foto FROM usuarios WHERE usuario=?", (usuario,))
    resultado = cursor.fetchone()
    foto_usuario = resultado[0] if resultado else None

    if request.method == "POST":
        tipo = request.form.get("tipo")
        foto = request.form.get("foto")

        if foto:
            if not os.path.exists("static/fotos"):
                os.makedirs("static/fotos")

            imagem_base64 = foto.split(",")[1]
            nome_arquivo = f"static/fotos/{usuario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            with open(nome_arquivo, "wb") as f:
                f.write(base64.b64decode(imagem_base64))

            cursor.execute("""
                INSERT INTO ponto (usuario, tipo, hora, data, foto)
                VALUES (?, ?, ?, ?, ?)
            """, (
                usuario,
                tipo,
                datetime.now().strftime("%H:%M:%S"),
                datetime.now().date(),
                nome_arquivo
            ))

            conn.commit()

        conn.close()
        return redirect("/sistema")

    conn.close()
    return render_template("sistema.html", foto_usuario=foto_usuario)

@app.route("/registrar/<tipo>")
def registrar_ponto(tipo):
    if "usuario" not in session:
        return redirect("/login")

    usuario = session["usuario"]

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ponto (usuario, tipo, hora, data)
        VALUES (?, ?, ?, ?)
    """, (
        usuario,
        tipo.capitalize(),  # "Entrada" ou "Saída"
        datetime.now().strftime("%H:%M:%S"),
        datetime.now().date()
    ))
    conn.commit()
    conn.close()

    return redirect("/sistema")

# ================= ADMIN =================
@app.route("/admin")
def admin():
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    # 🔥 RESUMO
    cursor.execute("""
        SELECT 
            u.usuario,
            u.foto,
            COALESCE(SUM(CASE WHEN p.tipo='Entrada' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN p.tipo='Saída' THEN 1 ELSE 0 END), 0)
        FROM usuarios u
        LEFT JOIN ponto p ON u.usuario = p.usuario
        GROUP BY u.usuario
    """)
    
    resumo = cursor.fetchall()

    # 📋 TABELA
    cursor.execute("""
        SELECT id, usuario, tipo, hora, data, foto
        FROM ponto
        ORDER BY data DESC, hora DESC
    """)
    dados = cursor.fetchall()

    conn.close()

    # 🚀 DADOS PARA GRÁFICOS
    nomes = [r[0] for r in resumo]
    entradas = [r[2] for r in resumo]
    saidas = [r[3] for r in resumo]

    return render_template(
        "admin.html",
        resumo=resumo,
        dados=dados,
        nomes=nomes,
        entradas=entradas,
        saidas=saidas
    )


# ================= EDITAR =================
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        hora = request.form.get("hora")
        data = request.form.get("data")

        cursor.execute("""
            UPDATE ponto
            SET hora = ?, data = ?
            WHERE id = ?
        """, (hora, data, id))

        conn.commit()
        conn.close()

        return redirect("/admin")

    cursor.execute("SELECT * FROM ponto WHERE id = ?", (id,))
    registro = cursor.fetchone()
    conn.close()

    return render_template("editar.html", registro=registro)


# ================= LOGOUT =================
if __name__ == "__main__":
    app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
    


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
@app.route("/perfil", methods=["GET", "POST"])
def   perfil():
    if "usuario" not in session:
        return redirect("/")

    usuario = session["usuario"]

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        foto = request.files.get("foto")

        if foto and foto.filename != "":
            if not os.path.exists("static/perfil"):
                os.makedirs("static/perfil")

            nome_arquivo = f"{usuario}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            caminho = os.path.join("static/perfil", nome_arquivo)

            foto.save(caminho)

            cursor.execute("UPDATE usuarios SET foto=? WHERE usuario=?", (caminho, usuario))
            conn.commit()

        conn.close()
        return redirect("/perfil")

    cursor.execute("SELECT foto FROM usuarios WHERE usuario=?", (usuario,))
    resultado = cursor.fetchone()
    foto_usuario = resultado[0] if resultado else None

    conn.close()

    return render_template("perfil.html", foto_usuario=foto_usuario)
if __name__ == "__main__":
    app.run(debug=True)
=======
from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import base64
from datetime import datetime
from banco import criar_tabelas

app = Flask(__name__)
app.secret_key = "123"

criar_tabelas()

# ================= CONEXÃO =================
def conectar():
    return sqlite3.connect("database.db")
# ===== CORRIGIR BANCO AUTOMATICAMENTE =====
conn = conectar()
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE usuarios ADD COLUMN foto TEXT")
    print("Coluna foto criada!")
except:
    print("Coluna foto já existe")

conn.commit()
conn.close()


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["usuario"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT tipo FROM usuarios WHERE usuario=? AND senha=?",
            (user, senha)
        )

        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            session["usuario"] = user

            if resultado[0] == "admin":
                return redirect("/admin")
            else:
                return redirect("/sistema")

        return render_template("login.html", erro="Usuário ou senha inválidos")

    return render_template("login.html")


# ================= CADASTRO =================
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        tipo = request.form.get("tipo")
        foto = request.files.get("foto")

        caminho_foto = None

        if foto and foto.filename != "":
            if not os.path.exists("static/perfil"):
                os.makedirs("static/perfil")

            nome_arquivo = f"{usuario}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            caminho_foto = os.path.join("static/perfil", nome_arquivo)
            foto.save(caminho_foto)

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO usuarios (usuario, senha, tipo, foto)
            VALUES (?, ?, ?, ?)
        """, (usuario, senha, tipo, caminho_foto))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("cadastro.html")


# ================= SISTEMA FUNCIONÁRIO =================
@app.route("/sistema", methods=["GET", "POST"])
def sistema():
    if "usuario" not in session:
        return redirect("/")

    usuario = session["usuario"]

    conn = conectar()
    cursor = conn.cursor()

    # pegar foto do usuário
    cursor.execute("SELECT foto FROM usuarios WHERE usuario=?", (usuario,))
    resultado = cursor.fetchone()
    foto_usuario = resultado[0] if resultado else None

    if request.method == "POST":
        tipo = request.form.get("tipo")
        foto = request.form.get("foto")

        if foto:
            if not os.path.exists("static/fotos"):
                os.makedirs("static/fotos")

            imagem_base64 = foto.split(",")[1]
            nome_arquivo = f"static/fotos/{usuario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            with open(nome_arquivo, "wb") as f:
                f.write(base64.b64decode(imagem_base64))

            cursor.execute("""
                INSERT INTO ponto (usuario, tipo, hora, data, foto)
                VALUES (?, ?, ?, ?, ?)
            """, (
                usuario,
                tipo,
                datetime.now().strftime("%H:%M:%S"),
                datetime.now().date(),
                nome_arquivo
            ))

            conn.commit()

        conn.close()
        return redirect("/sistema")

    conn.close()
    return render_template("sistema.html", foto_usuario=foto_usuario)


# ================= ADMIN =================
@app.route("/admin")
def admin():
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    # 🔥 RESUMO CORRETO (SEM BUG)
    cursor.execute("""
        SELECT 
            u.usuario,
            u.foto,
            COALESCE(SUM(CASE WHEN p.tipo='Entrada' THEN 1 END),0),
            COALESCE(SUM(CASE WHEN p.tipo='Saída' THEN 1 END),0)
        FROM usuarios u
        LEFT JOIN ponto p ON u.usuario = p.usuario
        GROUP BY u.usuario
    """)
    resumo = cursor.fetchall()

    # 📋 TABELA
    cursor.execute("""
        SELECT id, usuario, tipo, hora, data, foto
        FROM ponto
        ORDER BY data DESC, hora DESC
    """)
    dados = cursor.fetchall()

    conn.close()

    return render_template("admin.html", resumo=resumo, dados=dados)


# ================= EDITAR =================
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        hora = request.form.get("hora")
        data = request.form.get("data")

        cursor.execute("""
            UPDATE ponto
            SET hora = ?, data = ?
            WHERE id = ?
        """, (hora, data, id))

        conn.commit()
        conn.close()

        return redirect("/admin")

    cursor.execute("SELECT * FROM ponto WHERE id = ?", (id,))
    registro = cursor.fetchone()
    conn.close()

    return render_template("editar.html", registro=registro)


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
@app.route("/perfil", methods=["GET", "POST"])
def   perfil():
    if "usuario" not in session:
        return redirect("/")

    usuario = session["usuario"]

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        foto = request.files.get("foto")

        if foto and foto.filename != "":
            if not os.path.exists("static/perfil"):
                os.makedirs("static/perfil")

            nome_arquivo = f"{usuario}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            caminho = os.path.join("static/perfil", nome_arquivo)

            foto.save(caminho)

            cursor.execute("UPDATE usuarios SET foto=? WHERE usuario=?", (caminho, usuario))
            conn.commit()

        conn.close()
        return redirect("/perfil")

    cursor.execute("SELECT foto FROM usuarios WHERE usuario=?", (usuario,))
    resultado = cursor.fetchone()
    foto_usuario = resultado[0] if resultado else None

    conn.close()

    return render_template("perfil.html", foto_usuario=foto_usuario)
    >>>>>>> 611eec2f5e68649bd93f3732da5a1bbaf1a8d10e
    
