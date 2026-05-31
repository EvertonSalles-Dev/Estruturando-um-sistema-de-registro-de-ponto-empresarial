import customtkinter as ctk
from banco import conectar
import datetime
import os

from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def abrir_admin():

    janela = ctk.CTk()
    janela.title("Dashboard Empresarial")
    janela.geometry("1000x700")

    registros = []

    # =========================
    # 📊 PEGAR DADOS
    # =========================
    def pegar_dados():
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_users = cursor.fetchone()[0]

        hoje = datetime.date.today()
        cursor.execute("SELECT COUNT(*) FROM ponto WHERE data=?", (hoje,))
        total_hoje = cursor.fetchone()[0]

        cursor.execute("""
            SELECT tipo, COUNT(*) 
            FROM ponto 
            GROUP BY tipo
        """)
        dados = cursor.fetchall()

        conn.close()
        return total_users, total_hoje, dados

    # =========================
    # 🔄 ATUALIZAR DASHBOARD
    # =========================
    def atualizar():
        total_users, total_hoje, dados = pegar_dados()

        label_users.configure(text=f"👥 Usuarios: {total_users}")
        label_hoje.configure(text=f"📅 Hoje: {total_hoje}")

        atualizar_grafico(dados)

    # =========================
    # 📊 GRÁFICO
    # =========================
    def atualizar_grafico(dados):
        for widget in frame_grafico.winfo_children():
            widget.destroy()

        tipos = [d[0] for d in dados]
        valores = [d[1] for d in dados]

        fig = plt.Figure(figsize=(5, 3))
        ax = fig.add_subplot(111)

        ax.bar(tipos, valores)
        ax.set_title("Registros de Ponto")

        canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack()

    # =========================
    # 📋 VER REGISTROS
    # =========================
    def ver_registros():
        box.delete("0.0", "end")
        registros.clear()

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT usuario, tipo, hora, data, foto 
        FROM ponto 
        ORDER BY id DESC
        """)

        dados = cursor.fetchall()
        conn.close()

        for i, d in enumerate(dados):
            texto = f"{d[0]} | {d[1]} | {d[2]} | {d[3]}"
            box.insert("end", f"{i} - {texto}\n")
            registros.append(d)

    # =========================
    # 🖱️ SELECIONAR REGISTRO
    # =========================
    def selecionar_registro(event):
        try:
            linha = box.get("insert linestart", "insert lineend")
            indice = int(linha.split("-")[0].strip())

            registro = registros[indice]
            caminho_foto = registro[4]

            mostrar_foto(caminho_foto)

        except:
            pass

    # =========================
    # 🖼️ MOSTRAR FOTO
    # =========================
    def mostrar_foto(caminho):
        if not caminho or not os.path.exists(caminho):
            label_foto.configure(text="Sem imagem", image=None)
            return

        img = Image.open(caminho)
        img = img.resize((200, 200))

        img_ctk = ctk.CTkImage(light_image=img, size=(200, 200))

        label_foto.configure(image=img_ctk, text="")
        label_foto.image = img_ctk

    # =========================
    # 📄 RELATÓRIO PDF
    # =========================
    def gerar_relatorio():
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Image as RLImage
        from reportlab.lib.styles import getSampleStyleSheet

        doc = SimpleDocTemplate("relatorio_ponto.pdf")
        styles = getSampleStyleSheet()

        elementos = []

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT usuario, tipo, hora, data, foto FROM ponto")
        dados = cursor.fetchall()
        conn.close()

        for d in dados:
            texto = f"{d[0]} - {d[1]} - {d[2]} - {d[3]}"
            elementos.append(Paragraph(texto, styles["Normal"]))

            if d[4] and os.path.exists(d[4]):
                elementos.append(RLImage(d[4], width=100, height=100))

        doc.build(elementos)

    # =========================
    # 🎨 INTERFACE
    # =========================

    topo = ctk.CTkFrame(janela)
    topo.pack(fill="x", pady=10)

    label_users = ctk.CTkLabel(topo, text="👥 Usuarios: 0", font=("Arial", 18))
    label_users.pack(side="left", padx=20)

    label_hoje = ctk.CTkLabel(topo, text="📅 Hoje: 0", font=("Arial", 18))
    label_hoje.pack(side="left", padx=20)

    ctk.CTkButton(topo, text="🔄 Atualizar", command=atualizar).pack(side="right", padx=20)

    # 📊 gráfico
    frame_grafico = ctk.CTkFrame(janela)
    frame_grafico.pack(pady=10)

    # 📋 botões
    frame_btn = ctk.CTkFrame(janela)
    frame_btn.pack(pady=10)

    ctk.CTkButton(frame_btn, text="📋 Ver Registros", command=ver_registros).pack(side="left", padx=10)
    ctk.CTkButton(frame_btn, text="📄 Gerar Relatório", command=gerar_relatorio).pack(side="left", padx=10)

    # 📄 lista
    box = ctk.CTkTextbox(janela, width=900, height=250)
    box.pack(pady=10)

    box.bind("<ButtonRelease-1>", selecionar_registro)

    # 🖼️ foto
    label_foto = ctk.CTkLabel(janela, text="Foto do funcionário")
    label_foto.pack(pady=10)

    atualizar()

    janela.mainloop()