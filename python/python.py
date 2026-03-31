ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
from login import app
from sistema import abrir_sistema 
from banco import conectar

conn = conectar()
cursor = conn.cursor()

cursor.execute(
    "INSERT INTO usuarios (usuario, senha, tipo) VALUES (?, ?, ?)",
    ("admin", "123", "admin")
)

conn.commit()
conn.close()
