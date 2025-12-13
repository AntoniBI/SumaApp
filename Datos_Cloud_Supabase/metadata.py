
# import pandas as pd
# import psycopg2
# from psycopg2.extras import execute_values

# # ---------------------------
# # Parámetros de conexión
# # ---------------------------
# DB_USER = "postgres"
# DB_PASS = "Hi!7f*1mBI24Ae"
# DB_HOST = "localhost"
# DB_PORT = "5432"
# DB_NAME = "postgres"

# # Ruta del Excel (actualizada para el entorno del sandbox)
# EXCEL_FILE = r"C:\Users\antoni.mm\Downloads\Miembros de SUMA - Asistencia(1).xlsx"

# def main():
#     # ---------------------------
#     # 1. Leer Excel con dos filas de cabecera
#     # ---------------------------
#     df = pd.read_excel(EXCEL_FILE, header=[0,1])

#     # ---------------------------
#     # 2. Aplanar nombres de columnas
#     # ---------------------------
#     # Asegurarse de que los nombres de las columnas sean únicos y manejables
#     new_columns = []
#     for col in df.columns.to_flat_index():
#         # Convertir a string y limpiar espacios
#         col0 = str(col[0]).strip()
#         col1 = str(col[1]).strip()

#         # Si la primera parte es 'Unnamed', usar la segunda parte, sino la primera
#         if "Unnamed" in col0:
#             new_columns.append(col1)
#         else:
#             # Combinar ambas partes si no es 'Unnamed' y no es una columna personal
#             # Esto es para evitar nombres de columna como 'Nombre_Nombre' o 'email_email'
#             if col0 in ["Nombre", "Apellidos", "email", "Instrumento", "Información adicional"]:
#                 new_columns.append(col0)
#             else:
#                 new_columns.append(f"{col0}_{col1}")

#     df.columns = new_columns

#     # ---------------------------
#     # 3. Crear columna miembro (nombre completo)
#     # ---------------------------
#     df["Nombre"] = df["Nombre"].astype(str).str.strip()
#     df["Apellidos"] = df["Apellidos"].astype(str).str.strip()
#     df["miembro"] = df["Nombre"] + " " + df["Apellidos"]

#     # ---------------------------
#     # 4. Crear DataFrame con metadatos
#     # ---------------------------
#     # Ajusta los nombres según cómo quedaron tras aplanar columnas
#     # Se asume que las columnas 'email', 'Instrumento', 'Información adicional' no tienen sub-cabeceras 'Unnamed'
#     email_col = "email"
#     instrumento_col = "Instrumento"
#     info_col = "Información adicional"

#     df_meta = df[["miembro", "Nombre", "Apellidos", email_col, instrumento_col, info_col]].copy()
#     df_meta = df_meta.drop_duplicates(subset=["miembro"])

#     # ---------------------------
#     # 5. Conectar a PostgreSQL
#     # ---------------------------
#     conn = psycopg2.connect(
#         dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
#     )
#     cur = conn.cursor()

#     # ---------------------------
#     # 6. Crear tabla miembros
#     # ---------------------------
#     create_table_sql = """
#     CREATE TABLE IF NOT EXISTS miembros (
#         id SERIAL PRIMARY KEY,
#         miembro VARCHAR(255) UNIQUE,
#         nombre VARCHAR(255),
#         apellidos VARCHAR(255),
#         email VARCHAR(255),
#         instrumento VARCHAR(255),
#         informacion_adicional TEXT
#     );
#     """
#     cur.execute(create_table_sql)
#     conn.commit()

#     # ---------------------------
#     # 7. Insertar datos en miembros
#     # ---------------------------
#     datos = df_meta[["miembro", "Nombre", "Apellidos", email_col, instrumento_col, info_col]].values.tolist()
#     insert_sql = """
#     INSERT INTO miembros (miembro, nombre, apellidos, email, instrumento, informacion_adicional)
#     VALUES %s
#     ON CONFLICT (miembro) DO NOTHING;
#     """
#     execute_values(cur, insert_sql, datos)
#     conn.commit()

#     cur.close()
#     conn.close()

#     print("✅ Tabla 'miembros' creada y actualizada correctamente.")

# if __name__ == "__main__":
#     main()

import pandas as pd
import psycopg2
import os
from psycopg2.extras import execute_values
from dotenv import load_dotenv
load_dotenv()

# ---------------------------
# Parámetros de conexión
# ---------------------------
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Ruta del Excel (actualizada para el entorno del sandbox)
EXCEL_FILE = r"/home/antonim/proyectos/test/Datos_Cloud_Supabase/Miembros de SUMA - Asistencia.xlsx"

def main():
    # ---------------------------
    # 1. Leer Excel con dos filas de cabecera
    # ---------------------------
    df = pd.read_excel(EXCEL_FILE, header=[0,1])

    # ---------------------------
    # 2. Aplanar nombres de columnas
    # ---------------------------
    # Asegurarse de que los nombres de las columnas sean únicos y manejables
    new_columns = []
    for col in df.columns.to_flat_index():
        # Convertir a string y limpiar espacios
        col0 = str(col[0]).strip()
        col1 = str(col[1]).strip()

        # Si la primera parte es 'Unnamed', usar la segunda parte, sino la primera
        if "Unnamed" in col0:
            new_columns.append(col1)
        else:
            # Combinar ambas partes si no es 'Unnamed' y no es una columna personal
            # Esto es para evitar nombres de columna como 'Nombre_Nombre' o 'email_email'
            if col0 in ["Nombre", "Apellidos", "email", "Instrumento", "Información adicional"]:
                new_columns.append(col0)
            else:
                new_columns.append(f"{col0}_{col1}")

    df.columns = new_columns

    # ---------------------------
    # 3. Crear columna miembro (nombre completo) y normalizarla
    # ---------------------------
    df["Nombre"] = df["Nombre"].astype(str).str.strip().str.lower()
    df["Apellidos"] = df["Apellidos"].astype(str).str.strip().str.lower()
    df["miembro"] = df["Nombre"] + " " + df["Apellidos"]

    # ---------------------------
    # 4. Crear DataFrame con metadatos
    # ---------------------------
    # Ajusta los nombres según cómo quedaron tras aplanar columnas
    # Se asume que las columnas 'email', 'Instrumento', 'Información adicional' no tienen sub-cabeceras 'Unnamed'
    email_col = "email"
    instrumento_col = "Instrumento"
    info_col = "Información adicional"

    df_meta = df[["miembro", "Nombre", "Apellidos", email_col, instrumento_col, info_col]].copy()
    df_meta = df_meta.drop_duplicates(subset=["miembro"])

    # ---------------------------
    # 5. Conectar a PostgreSQL
    # ---------------------------
    conn = psycopg2.connect(
        dbname=DBNAME, user=USER, password=PASSWORD, host=HOST, port=PORT
    )
    cur = conn.cursor()

    # ---------------------------
    # 6. Crear tabla miembros
    # ---------------------------
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS miembros (
        id SERIAL PRIMARY KEY,
        miembro VARCHAR(255) UNIQUE,
        nombre VARCHAR(255),
        apellidos VARCHAR(255),
        email VARCHAR(255),
        instrumento VARCHAR(255),
        informacion_adicional TEXT
    );
    """
    cur.execute(create_table_sql)
    conn.commit()

    # ---------------------------
    # 7. Insertar o Actualizar datos en miembros (UPSERT)
    # ---------------------------
    datos = df_meta[["miembro", "Nombre", "Apellidos", email_col, instrumento_col, info_col]].values.tolist()
    insert_sql = """
    INSERT INTO miembros (miembro, nombre, apellidos, email, instrumento, informacion_adicional)
    VALUES %s
    ON CONFLICT (miembro) DO UPDATE SET
        nombre = EXCLUDED.nombre,
        apellidos = EXCLUDED.apellidos,
        email = EXCLUDED.email,
        instrumento = EXCLUDED.instrumento,
        informacion_adicional = EXCLUDED.informacion_adicional;
    """
    execute_values(cur, insert_sql, datos)
    conn.commit()

    cur.close()
    conn.close()

    print("Tabla 'miembros' creada y actualizada correctamente (UPSERT).")

if __name__ == "__main__":
    main()
