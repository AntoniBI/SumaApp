# import pandas as pd
# import psycopg2
# from psycopg2.extras import execute_values
# import unicodedata

# # ---------------------------
# # Parámetros de conexión
# # ---------------------------
# DB_USER = "postgres"
# DB_PASS = "Hi!7f*1mBI24Ae"
# DB_HOST = "localhost"
# DB_PORT = "5432"
# DB_NAME = "postgres"

# # Ruta del Excel
# EXCEL_FILE = r"C:\Users\antoni.mm\Downloads\Miembros de SUMA - Asistencia(1).xlsx"

# # ---------------------------
# # Función para clasificar eventos
# # ---------------------------
# def tipo_evento(nombre):
#     nombre_norm = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('utf-8').lower()

#     ensayo_keywords = ["assaig", "parcial"]
#     actuacion_keywords = ["acte", "concert", "presentacio", "certamen", "entra",
#                           "moros i cristians", "alardo", "fira",
#                           "processo", "disfresses", "mati", "entrada", "festes", "barri", "falles", "mic", "sant", "sants", "desperta","acompanyament","mig", "any", "pasacarrer", "local"]
#     otros_keywords = ["assemblea", "dinar", "soterrar", "esmorzar", "sopar"]

#     if any(k in nombre_norm for k in ensayo_keywords):
#         return "Ensayo"
#     elif any(k in nombre_norm for k in actuacion_keywords):
#         return "Actuación"
#     elif any(k in nombre_norm for k in otros_keywords):
#         return "Otros"
#     else:
#         return "desconocido"

# def main():
#     df = pd.read_excel(EXCEL_FILE, header=[0, 1])

#     personal_cols = ["Nombre", "Apellidos", "email", "Instrumento", "Información adicional"]

#     event_data_for_display = []

#     for col_idx, col_tuple in enumerate(df.columns.to_flat_index()):
#         col0 = str(col_tuple[0]).strip()
#         col1 = str(col_tuple[1]).strip()

#         if col0 not in personal_cols:
#             try:
#                 fecha = pd.to_datetime(col1, dayfirst=True, errors='coerce').date()
#             except:
#                 fecha = None
            
#             if pd.notna(fecha):
#                 event_data_for_display.append({
#                     "evento": col0,
#                     "fecha": str(fecha)
#                 })

#     df_events = pd.DataFrame(event_data_for_display)

#     # ⚠️ YA NO ELIMINAMOS DUPLICADOS
#     df_events['tipo'] = df_events['evento'].apply(tipo_evento)

#     print("Eventos identificados en el Excel y su clasificación:")
#     print(df_events.to_markdown(index=False))
#     print(f"Total de eventos (incluyendo repetidos): {len(df_events)}")

#     try:
#         conn = psycopg2.connect(
#             dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
#         )
#         cur = conn.cursor()

#         create_eventos_sql = """
#         CREATE TABLE IF NOT EXISTS eventos (
#             id SERIAL PRIMARY KEY,
#             evento VARCHAR(255),
#             tipo VARCHAR(50)
#         );
#         """
#         cur.execute(create_eventos_sql)
#         conn.commit()

#         datos_eventos = df_events[["evento", "tipo"]].values.tolist()
#         insert_eventos_sql = """
#         INSERT INTO eventos (evento, tipo)
#         VALUES %s;
#         """
#         execute_values(cur, insert_eventos_sql, datos_eventos)
#         conn.commit()

#         cur.close()
#         conn.close()

#         print("✅ Todos los eventos del Excel fueron insertados en la tabla 'eventos'.")
#     except Exception as e:
#         print(f"⚠️ Error al conectar o insertar en PostgreSQL: {e}")

# if __name__ == "__main__":
#     main()


import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import unicodedata
from dotenv import load_dotenv
import os
load_dotenv()

# ---------------------------
# Parámetros de conexión
# ---------------------------
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Ruta del Excel
EXCEL_FILE = r"/home/antonim/proyectos/test/Datos_Cloud_Supabase/Miembros de SUMA - Asistencia.xlsx"

# ---------------------------
# Función para clasificar eventos
# ---------------------------
def tipo_evento(nombre):
    nombre_norm = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('utf-8').lower()

    ensayo_keywords = ["assaig", "parcial","ensayo"]
    actuacion_keywords = ["acte", "concert", "presentacio", "certamen", "entra",
                          "moros i cristians", "alardo", "fira",
                          "processo", "disfresses", "mati", "entrada", "festes", "barri", "falles", "mic",
                          "sant", "sants", "desperta", "acompanyament", "mig", "any", "pasacarrer", "local","deu"]
    otros_keywords = ["assemblea", "dinar", "soterrar", "esmorzar", "sopar"]

    if any(k in nombre_norm for k in ensayo_keywords):
        return "Ensayo"
    elif any(k in nombre_norm for k in actuacion_keywords):
        return "Actuación"
    elif any(k in nombre_norm for k in otros_keywords):
        return "Otros"
    else:
        return "desconocido"

def main():
    # ---------------------------
    # 1. Leer Excel
    # ---------------------------
    df = pd.read_excel(EXCEL_FILE, header=[0, 1])
    personal_cols = ["Nombre", "Apellidos", "email", "Instrumento", "Información adicional"]

    event_data_for_display = []

    for col_idx, col_tuple in enumerate(df.columns.to_flat_index()):
        col0 = str(col_tuple[0]).strip()
        col1 = str(col_tuple[1]).strip()

        if col0 not in personal_cols:
            try:
                fecha = pd.to_datetime(col1, dayfirst=True, errors='coerce').date()
            except:
                fecha = None
            
            if pd.notna(fecha):
                event_data_for_display.append({
                    "evento": col0,
                    "fecha": str(fecha)
                })

    df_events = pd.DataFrame(event_data_for_display)

    # Clasificar todos los eventos (no eliminamos duplicados)
    df_events['tipo'] = df_events['evento'].apply(tipo_evento)

    print("Eventos identificados en el Excel y su clasificación:")
    print(df_events.to_markdown(index=False))
    print(f"Total de eventos (incluyendo repetidos): {len(df_events)}")

    # ---------------------------
    # 2. Insertar en PostgreSQL
    # ---------------------------
    try:
        conn = psycopg2.connect(
            dbname=DBNAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cur = conn.cursor()

        create_eventos_sql = """
        CREATE TABLE IF NOT EXISTS eventos (
            id SERIAL PRIMARY KEY,
            evento VARCHAR(255),
            fecha DATE,
            tipo VARCHAR(50)
        );
        """
        cur.execute(create_eventos_sql)
        conn.commit()

        datos_eventos = df_events[["evento", "fecha", "tipo"]].values.tolist()
        insert_eventos_sql = """
        INSERT INTO eventos (evento, fecha, tipo)
        VALUES %s;
        """
        execute_values(cur, insert_eventos_sql, datos_eventos)
        conn.commit()

        cur.close()
        conn.close()

        print("✅ Todos los eventos del Excel fueron insertados en la tabla 'eventos' con fecha y tipo.")
    except Exception as e:
        print(f"⚠️ Error al conectar o insertar en PostgreSQL: {e}")

if __name__ == "__main__":
    main()
