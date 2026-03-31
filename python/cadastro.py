import customtkinter as ctk
from banco import conectar
from tkinter import messagebox

def abrir_cadastro():

    janela = ctk.CTk()
    janela.title("Cadastro de Usuario")
    janela.geometry("350x420")

    mostrar_senha = ctk.BooleanVar(value=False)

    def toggle_senha():
        if mostrar_senha.get():
            entry_senha.configure(show="")
            entry_confirmar.configure(show="")
        else:
            entry_senha.configure(show="*")
            entry_confirmar.configure(show="*")

    def cadastrar():
        user = entry_user.get().strip()
        senha = entry_senha.get().strip()
        confirmar = entry_confirmar.get().strip()

        # 🔒 Validações
        if not user or not senha or not confirmar:
            messagebox.showwarning("Atenção", "Preencha todos os campos!")
            return

        if len(senha) < 4:
            messagebox.showwarning("Atenção", "A senha deve ter pelo menos 4 caracteres!")
            return

        if senha != confirmar:
            messagebox.showerror("Erro", "As senhas não coincidem!")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO usuarios (usuario, senha, tipo) VALUES (?, ?, ?)",
                (user, senha, "funcionario")
            )

            conn.commit()
            conn.close()

            messagebox.showinfo("Sucesso", "Usuario cadastrado com sucesso!")
            janela.destroy()

        except:
            messagebox.showerror("Erro", "Usuario já existe!")

    # 🎨 Layout

    ctk.CTkLabel(janela, text="Criar Conta", font=("Arial", 20)).pack(pady=15)

    entry_user = ctk.CTkEntry(janela, placeholder_text="Usuario")
    entry_user.pack(pady=10)

    entry_senha = ctk.CTkEntry(janela, placeholder_text="Senha", show="*")
    entry_senha.pack(pady=10)

    entry_confirmar = ctk.CTkEntry(janela, placeholder_text="Confirmar Senha", show="*")
    entry_confirmar.pack(pady=10)

    # 👁️ Mostrar senha
    ctk.CTkCheckBox(
        janela,
        text="Mostrar senha",
        variable=mostrar_senha,
        command=toggle_senha
    ).pack(pady=5)

    # Botão cadastrar
    ctk.CTkButton(
        janela,
        text="Cadastrar",
        height=40,
        command=cadastrar
    ).pack(pady=20)

    # Botão voltar
    ctk.CTkButton(
        janela,
        text="Voltar",
        fg_color="gray",
        command=janela.destroy
    ).pack()

    janela.mainloop()