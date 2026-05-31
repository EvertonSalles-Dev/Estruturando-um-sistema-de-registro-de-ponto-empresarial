from banco import criar_tabelas
from login import abrir_login
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

criar_tabelas()
abrir_login()