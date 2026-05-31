import sqlite3


def conectar():
    return sqlite3.connect("database.db")


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            senha TEXT,
            tipo TEXT,
            foto TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ponto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            tipo TEXT,
            hora TEXT,
            data TEXT,
            foto TEXT
        )
        """
    )

    cursor.execute("SELECT * FROM usuarios WHERE usuario='admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO usuarios (usuario, senha, tipo) VALUES (?, ?, ?)",
            ("admin", "123", "admin"),
        )

    conn.commit()
    conn.close()
   