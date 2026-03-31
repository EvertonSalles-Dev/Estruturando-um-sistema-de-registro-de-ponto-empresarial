import customtkinter as ctk
from tkinter import messagebox
from banco import conectar
from cadastro import abrir_cadastro

tentativas = 3

def abrir_login():
    global tentativas

    app = ctk.CTk()
    app.title("Login")
    app.geometry("350x350")

    # FUNÇÃO LOGIN
    def login():
        global tentativas

        user = entry_user.get().strip()
        senha = entry_senha.get().strip()

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT usuario, tipo FROM usuarios WHERE usuario=? AND senha=?",
            (user, senha)
        )

        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            usuario, tipo = resultado

            app.withdraw()  

            if tipo == "admin":
                from admin import abrir_admin
                abrir_admin()
            else:
                from sistema import abrir_sistema
                abrir_sistema(usuario)

        else:
            tentativas -= 1
            messagebox.showerror("Erro", f"Tentativas restantes: {tentativas}")

    # FUNÇÃO ESQUECI SENHA 👇
    def esqueci_senha():
        messagebox.showinfo("Recuperação", "Fale com o administrador!")

    # CAMPOS
    entry_user = ctk.CTkEntry(app, placeholder_text="Usuario")
    entry_user.pack(pady=10)

    entry_senha = ctk.CTkEntry(app, placeholder_text="Senha", show="*")
    entry_senha.pack(pady=10)

    # BOTÕES
    ctk.CTkButton(app, text="Entrar", command=login).pack(pady=10)
    ctk.CTkButton(app, text="Esqueci a senha", command=esqueci_senha).pack(pady=5)
    ctk.CTkButton(app, text="Cadastrar", command=abrir_cadastro).pack(pady=5)

    app.mainloop()
    app.protocol("WM_DELETE_WINDOW", lambda: (app.destroy()))