from banco import conectar

def buscar_resumo():
    conn = conectar()
    cursor = conn.cursor()

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

    dados = cursor.fetchall()
    conn.close()

    return dados