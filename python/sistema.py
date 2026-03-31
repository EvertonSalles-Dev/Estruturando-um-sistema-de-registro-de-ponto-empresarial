import customtkinter as ctk
import datetime
import os
import cv2

from banco import conectar
from tkinter import messagebox


def abrir_sistema(usuario):

    janela = ctk.CTk()
    janela.title("Registro de Ponto")
    janela.geometry("400x550")

    # =========================
    # 📸 CAMERA COM PREVIEW
    # =========================
    def tirar_foto(usuario):
        try:
            cam = cv2.VideoCapture(0)

            if not cam.isOpened():
                messagebox.showerror("Erro", "Não foi possível acessar a câmera")
                return None

            while True:
                ret, frame = cam.read()

                if not ret:
                    messagebox.showerror("Erro", "Falha ao capturar imagem")
                    break

                # Mostra a câmera ao vivo
                cv2.imshow(
                    "Pressione ESPAÇO para tirar foto | ESC para cancelar",
                    frame
                )

                key = cv2.waitKey(1)

                # ESC cancela
                if key == 27:
                    cam.release()
                    cv2.destroyAllWindows()
                    return None

                # ESPAÇO captura
                elif key == 32:
                    if not os.path.exists("fotos"):
                        os.makedirs("fotos")

                    nome_arquivo = f"fotos/{usuario}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

                    cv2.imwrite(nome_arquivo, frame)

                    cam.release()
                    cv2.destroyAllWindows()

                    return nome_arquivo

            cam.release()
            cv2.destroyAllWindows()

        except Exception as e:
            print("Erro câmera:", e)
            return None

    # =========================
    # ⏱️ REGISTRAR PONTO
    # =========================
    def registrar(tipo):
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        data = datetime.date.today()

        foto = tirar_foto(usuario)

        if foto is None:
            messagebox.showwarning("Cancelado", "Registro cancelado (sem foto)")
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO ponto (usuario, tipo, hora, data, foto)
        VALUES (?, ?, ?, ?, ?)
        """, (usuario, tipo, hora, data, foto))

        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", f"{tipo} registrado com foto!")

        atualizar_status()

    # =========================
    # 📋 HISTÓRICO DO DIA
    # =========================
    def atualizar_status():
        conn = conectar()
        cursor = conn.cursor()

        hoje = datetime.date.today()

        cursor.execute("""
        SELECT tipo, hora FROM ponto
        WHERE usuario=? AND data=?
        ORDER BY id DESC
        """, (usuario, hoje))

        registros = cursor.fetchall()
        conn.close()

        box_status.configure(state="normal")
        box_status.delete("0.0", "end")

        if not registros:
            box_status.insert("end", "Nenhum registro hoje.")
        else:
            for r in registros:
                box_status.insert("end", f"{r[0]} - {r[1]}\n")

        box_status.configure(state="disabled")

    # =========================
    # 🎨 INTERFACE
    # =========================

    ctk.CTkLabel(
        janela,
        text=f"Bem-vindo, {usuario}",
        font=("Arial", 20)
    ).pack(pady=10)

    # BOTÕES
    ctk.CTkButton(
        janela,
        text="🟢 Entrada",
        height=40,
        command=lambda: registrar("Entrada")
    ).pack(pady=5)

    ctk.CTkButton(
        janela,
        text="🍽️ Saída Almoço",
        height=40,
        command=lambda: registrar("Saída Almoço")
    ).pack(pady=5)

    ctk.CTkButton(
        janela,
        text="🔙 Volta Almoço",
        height=40,
        command=lambda: registrar("Volta Almoço")
    ).pack(pady=5)

    ctk.CTkButton(
        janela,
        text="🔴 Saída",
        height=40,
        command=lambda: registrar("Saída")
    ).pack(pady=5)

    # HISTÓRICO
    ctk.CTkLabel(janela, text="Registros de Hoje").pack(pady=10)

    box_status = ctk.CTkTextbox(janela, width=320, height=180)
    box_status.pack()

    # BOTÃO SAIR
    ctk.CTkButton(
        janela,
        text="Sair",
        fg_color="red",
        command=janela.destroy
    ).pack(pady=20)

    atualizar_status()

    janela.mainloop()
    cursor.execute("SELECT foto FROM usuarios WHERE usuario=?", (usuario,))
resultado = cursor.fetchone()
foto_usuario = resultado[0] if resultado else None