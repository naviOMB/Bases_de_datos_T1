import psycopg2
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
import secrets
import string

def generar_usuario(unicos):
    while True:
        uid = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(10))
        if uid not in unicos:
            unicos.add(uid)
            return uid

def generar_password():
    return ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%&") for _ in range(12))

load_dotenv() # Uso de load_dotenv para cargar las variables de entorno desde el archivo .env

DB_NAME = os.getenv("DB_NAME") 
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Crear la base de datos si no existe
try:
    conn = psycopg2.connect( # Conexión a la base de datos
        dbname="postgres",
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True # Cada instrucción de SQL se ejecuta de inmediato
    cur = conn.cursor() # Intermediario entre python y la base de datos

    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    exists = cur.fetchone()
    if not exists:
        cur.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Base de datos '{DB_NAME}' creada.")
    else:
        print(f"ℹLa base de datos '{DB_NAME}' ya existe.")

    cur.close() # Desconexión
    conn.close()

except Exception as e:
    print(f"Error creando la base de datos: {e}")
    exit()



# Conexión a la base de datos
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()

    # Crear tablas desde archivo SQL
    with open("Creacion_Tablas.sql", "r", encoding="UTF-8", errors="replace") as sql_file:
        cur.execute(sql_file.read())
    conn.commit()

    # Leer CSV
    df = pd.read_csv("registros.csv", sep=",", encoding="latin1")

    # Poblar Topico
    topico_set = set()
    for fila in df['Nombre_Topico']:
        if pd.notna(fila):
            topicos = [t.strip() for t in fila.split('|') if t.strip()]
            topico_set.update(topicos)

    # Insertar en la tabla y construir el mapa
    topico_map = {}
    for topico in sorted(topico_set):
        cur.execute("SELECT ID_Topico FROM Topico WHERE Nombre_Topico = %s;", (topico,))
        result = cur.fetchone()
        if result is None:
            cur.execute("""
                INSERT INTO Topico (Nombre_Topico)
                VALUES (%s)
                RETURNING ID_Topico;
            """, (topico,))
            result = cur.fetchone()
        topico_map[topico] = result[0]

    # Poblar Autor con USERID y PASSWORD únicos
    autores_insertados = set()
    autor_userids = set()
    for _, row in df.iterrows():
        for autor_str in row['Autores'].split(','):
            rut, nombre, email = [x.strip() for x in autor_str.split('|')]
            if rut not in autores_insertados:
                userid = generar_usuario(autor_userids)
                password = generar_password()
                cur.execute("""
                    INSERT INTO Autor (RUT_Autor, Nombre_Autor, Email_Autor, USERID_Autor, PASSWORD_Autor)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (rut, nombre, email, userid, password))
                autores_insertados.add(rut)

    # Poblar Revisor con USERID y PASSWORD únicos
    revisores_insertados = set()
    revisor_userids = set()
    for _, row in df.iterrows():
        for rev_str in row['Revisores'].split(','):
            rut, nombre, email = [x.strip() for x in rev_str.split('|')]
            if rut not in revisores_insertados:
                userid = generar_usuario(revisor_userids)
                password = generar_password()
                cur.execute("""
                    INSERT INTO Revisor (RUT_Revisor, Nombre_Revisor, Email_Revisor, USERID_Revisor, PASSWORD_Revisor)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (rut, nombre, email, userid, password))
                revisores_insertados.add(rut)

    # Poblar Articulo
    articulo_map = {}
    for _, row in df[['Titulo', 'Resumen']].drop_duplicates().iterrows():
        cur.execute("""
            INSERT INTO Articulo (Nombre_Articulo, Resumen_Articulo)
            VALUES (%s, %s)
            RETURNING ID_Articulo;
        """, (row['Titulo'], row['Resumen']))
        articulo_id = cur.fetchone()[0]
        articulo_map[(row['Titulo'], row['Resumen'])] = articulo_id

    # Poblar Publicacion
    for _, row in df.iterrows():
        autores = [a.strip() for a in row['Autores'].split(',')]
        articulo_id = articulo_map[(row['Titulo'], row['Resumen'])]
        for idx, autor_str in enumerate(autores):
            partes = autor_str.strip().split('|')
            if len(partes) < 1:
                continue
            rut = partes[0].strip()
            es_contacto = (idx == 0)
            cur.execute("""
                INSERT INTO Publicacion (ID_Articulo, RUT_Autor, Fecha_Publicacion, ES_Contacto)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (articulo_id, rut, row['Fecha_Envio'], es_contacto))

    # Poblar Topico_Articulo
    for _, row in df.iterrows():
        articulo_id = articulo_map[(row['Titulo'], row['Resumen'])]
        topicos = [t.strip() for t in row['Nombre_Topico'].split('|') if t.strip()]
        for topico in topicos:
            id_topico = topico_map.get(topico)
            if id_topico:
                cur.execute("""
                    INSERT INTO Topico_Articulo (ID_Articulo, ID_Topico)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING;
                """, (articulo_id, id_topico))

    # Poblar Topico_ESP 
    for _, row in df.iterrows():
        articulo_id = articulo_map[(row['Titulo'], row['Resumen'])]
        topicos = [t.strip() for t in row['Nombre_Topico'].split('|') if t.strip()]
        for rev_str in row['Revisores'].split(','):
            rut, *_ = [x.strip() for x in rev_str.split('|')]
            for topico in topicos:
                cur.execute("""
                    INSERT INTO Topico_ESP (RUT_Revisor, ID_Topico)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING;
                """, (rut, topico_map[topico]))

    # Poblar Revision 
    for _, row in df.iterrows():
        articulo_id = articulo_map[(row['Titulo'], row['Resumen'])]
        revisores = [x.strip() for x in row['Revisores'].split(',')]
        valoraciones = [int(v.strip()) for v in row['Valoraciones'].split('|')]
        comentarios = [c.strip()[:100] for c in row['Comentarios'].split('|')]
        for idx, rev_str in enumerate(revisores):
            rut, *_ = [x.strip() for x in rev_str.split('|')]
            valoracion = valoraciones[idx] if idx < len(valoraciones) else None
            comentario = comentarios[idx] if idx < len(comentarios) else None
            cur.execute("""
                INSERT INTO Revision (ID_Articulo, RUT_Revisor, Fecha_Revision, VALORACION_REVISION, COMENTARIO_REVISION)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (articulo_id, rut, row['Fecha_Revision'], valoracion, comentario))
            
    conn.commit()

except Exception as e:
    print(f"Error en la ejecución: {e}")

finally:
    if 'cur' in locals(): cur.close()
    if 'conn' in locals(): conn.close()