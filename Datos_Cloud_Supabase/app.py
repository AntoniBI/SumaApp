# import streamlit as st
# import pandas as pd
# import psycopg2
# from psycopg2.extras import execute_values
# import os
# from dotenv import load_dotenv
# import unicodedata

# # Load environment variables
# load_dotenv()

# # Database credentials
# USER = os.getenv("user")
# PASSWORD = os.getenv("password")
# HOST = os.getenv("host")
# PORT = os.getenv("port")
# DBNAME = os.getenv("dbname")

# def get_db_connection():
#     try:
#         conn = psycopg2.connect(
#             dbname=DBNAME, user=USER, password=PASSWORD, host=HOST, port=PORT
#         )
#         return conn
#     except Exception as e:
#         st.error(f"Error connecting to database: {e}")
#         return None

# # ---------------------------
# # Logic from metadata.py
# # ---------------------------
# def process_metadata(df, conn):
#     st.info("Processing Metadata...")
    
#     # 2. Aplanar nombres de columnas
#     new_columns = []
#     for col in df.columns.to_flat_index():
#         col0 = str(col[0]).strip()
#         col1 = str(col[1]).strip()
#         if "Unnamed" in col0:
#             new_columns.append(col1)
#         else:
#             if col0 in ["Nombre", "Apellidos", "email", "Instrumento", "Información adicional"]:
#                 new_columns.append(col0)
#             else:
#                 new_columns.append(f"{col0}_{col1}")
    
#     df_meta_proc = df.copy()
#     df_meta_proc.columns = new_columns

#     # 3. Crear columna miembro
#     df_meta_proc["Nombre"] = df_meta_proc["Nombre"].astype(str).str.strip().str.lower()
#     df_meta_proc["Apellidos"] = df_meta_proc["Apellidos"].astype(str).str.strip().str.lower()
#     df_meta_proc["miembro"] = df_meta_proc["Nombre"] + " " + df_meta_proc["Apellidos"]

#     # 4. Crear DataFrame con metadatos
#     email_col = "email"
#     instrumento_col = "Instrumento"
#     info_col = "Información adicional"
    
#     # Ensure columns exist
#     for col in [email_col, instrumento_col, info_col]:
#         if col not in df_meta_proc.columns:
#              df_meta_proc[col] = None

#     df_meta = df_meta_proc[["miembro", "Nombre", "Apellidos", email_col, instrumento_col, info_col]].copy()
#     df_meta = df_meta.drop_duplicates(subset=["miembro"])

#     # 6. Crear tabla miembros
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
#     cur = conn.cursor()
#     cur.execute(create_table_sql)
#     conn.commit()

#     # 7. Insertar o Actualizar datos
#     datos = df_meta[["miembro", "Nombre", "Apellidos", email_col, instrumento_col, info_col]].values.tolist()
#     insert_sql = """
#     INSERT INTO miembros (miembro, nombre, apellidos, email, instrumento, informacion_adicional)
#     VALUES %s
#     ON CONFLICT (miembro) DO UPDATE SET
#         nombre = EXCLUDED.nombre,
#         apellidos = EXCLUDED.apellidos,
#         email = EXCLUDED.email,
#         instrumento = EXCLUDED.instrumento,
#         informacion_adicional = EXCLUDED.informacion_adicional;
#     """
#     execute_values(cur, insert_sql, datos)
#     conn.commit()
#     cur.close()
#     st.success("Metadata processed and 'miembros' table updated.")

# # ---------------------------
# # Logic from help.py
# # ---------------------------
# def tipo_evento(nombre):
#     nombre_norm = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('utf-8').lower()

#     ensayo_keywords = ["assaig", "parcial","ensayo"]
#     actuacion_keywords = ["acte", "concert", "presentacio", "certamen", "entra",
#                           "moros i cristians", "alardo", "fira",
#                           "processo", "disfresses", "mati", "entrada", "festes", "barri", "falles", "mic",
#                           "sant", "sants", "desperta", "acompanyament", "mig", "any", "pasacarrer", "local","deu"]
#     otros_keywords = ["assemblea", "dinar", "soterrar", "esmorzar", "sopar"]

#     if any(k in nombre_norm for k in ensayo_keywords):
#         return "Ensayo"
#     elif any(k in nombre_norm for k in actuacion_keywords):
#         return "Actuación"
#     elif any(k in nombre_norm for k in otros_keywords):
#         return "Otros"
#     else:
#         return "desconocido"

# def process_events(df, conn):
#     st.info("Processing Events...")
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
#     if df_events.empty:
#         st.warning("No events found to process.")
#         return

#     df_events['tipo'] = df_events['evento'].apply(tipo_evento)

#     # 2. Insertar en PostgreSQL
#     cur = conn.cursor()
#     create_eventos_sql = """
#     CREATE TABLE IF NOT EXISTS eventos (
#         id SERIAL PRIMARY KEY,
#         evento VARCHAR(255),
#         fecha DATE,
#         tipo VARCHAR(50)
#     );
#     """
#     cur.execute(create_eventos_sql)
#     conn.commit()

#     datos_eventos = df_events[["evento", "fecha", "tipo"]].values.tolist()
#     insert_eventos_sql = """
#     INSERT INTO eventos (evento, fecha, tipo)
#     VALUES %s;
#     """
#     # Note: The original script didn't have ON CONFLICT, so it might duplicate events if run multiple times.
#     # I'll leave it as is to match original logic, but maybe adding a unique constraint would be better.
#     # For now, stick to original logic but maybe clear table or handle duplicates? 
#     # The user asked for "plug and play", duplicates might be annoying.
#     # Let's stick to original for now to avoid changing behavior too much, but maybe warn user.
#     execute_values(cur, insert_eventos_sql, datos_eventos)
#     conn.commit()
#     cur.close()
#     st.success(f"Events processed. {len(df_events)} events inserted into 'eventos' table.")
#     with st.expander("View Processed Events"):
#         st.dataframe(df_events)

# # ---------------------------
# # Logic from main.py
# # ---------------------------
# def normalize_asistencia(x):
#     if pd.isna(x):
#         return 0
#     if isinstance(x, str):
#         x = x.strip()
#         if x in ["Sí"]:
#             return 1
#         elif x in ["No", "Pendiente", "No convocado", "0 convocado"]:
#             return 0
#         else:
#             if x.endswith('%'):
#                 try:
#                     return int(x.replace('%','')) // 100
#                 except:
#                     return 0
#             return 0
#     elif isinstance(x, (int, float)):
#         return int(x)
#     return 0

# def process_attendance(df, conn):
#     st.info("Processing Attendance...")
#     personal_cols = ["Nombre", "Apellidos", "email", "Instrumento", "Información adicional"]
#     event_fecha_map = {}
#     new_columns = []

#     for col_idx, col in enumerate(df.columns.to_flat_index()):
#         col0 = str(col[0]).strip()
#         col1 = str(col[1]).strip()
#         if col0 in personal_cols:
#             new_columns.append(col0)
#         else:
#             unique_event_name = f"{col0}_{col1}_{col_idx}"
#             new_columns.append(unique_event_name)
#             try:
#                 fecha = pd.to_datetime(col1, dayfirst=True, errors='coerce').date()
#             except:
#                 fecha = None
#             event_fecha_map[unique_event_name] = {"original_name": col0, "date": fecha}

#     df_att = df.copy()
#     df_att.columns = new_columns
    
#     # Ensure name columns exist
#     if "Nombre" not in df_att.columns or "Apellidos" not in df_att.columns:
#         st.error("Missing 'Nombre' or 'Apellidos' columns.")
#         return

#     df_att["miembro"] = df_att["Nombre"].astype(str).str.strip().str.lower() + " " + df_att["Apellidos"].astype(str).str.strip().str.lower()

#     event_cols = [c for c in df_att.columns if c not in personal_cols + ["miembro"]]

#     df_long = df_att.melt(
#         id_vars=["miembro"],
#         value_vars=event_cols,
#         var_name="unique_event_id",
#         value_name="asistencia"
#     )

#     df_long["evento"] = df_long["unique_event_id"].map(lambda x: event_fecha_map[x]["original_name"])
#     df_long["fecha"] = df_long["unique_event_id"].map(lambda x: event_fecha_map[x]["date"])
#     df_long = df_long[df_long["fecha"].notna()]
#     df_long["asistencia"] = df_long["asistencia"].apply(normalize_asistencia)

#     cur = conn.cursor()
#     create_table_sql = """
#     CREATE TABLE IF NOT EXISTS asistencia (
#         id SERIAL PRIMARY KEY,
#         miembro VARCHAR(255),
#         evento VARCHAR(255),
#         fecha DATE,
#         asistencia INT,
#         UNIQUE (miembro, evento, fecha)
#     );
#     """
#     cur.execute(create_table_sql)
#     conn.commit()

#     datos = df_long[["miembro", "evento", "fecha", "asistencia"]].values.tolist()
#     insert_sql = """
#     INSERT INTO asistencia (miembro, evento, fecha, asistencia)
#     VALUES %s
#     ON CONFLICT (miembro, evento, fecha) DO NOTHING;
#     """
#     execute_values(cur, insert_sql, datos)
#     conn.commit()
#     cur.close()
#     st.success("Attendance processed and 'asistencia' table updated.")

# # ---------------------------
# # Main App
# # ---------------------------
# def main():
#     st.set_page_config(page_title="SUMA Data Processor", layout="wide")
#     st.title("🎼 SUMA Data Processor")
#     st.markdown("Upload the SUMA Members Excel file to automatically process metadata, events, and attendance.")

#     uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

#     if uploaded_file is not None:
#         st.write("File uploaded successfully!")
        
#         if st.button("Process File"):
#             conn = get_db_connection()
#             if conn:
#                 try:
#                     # Read Excel once
#                     # header=[0, 1] is crucial as per original scripts
#                     df = pd.read_excel(uploaded_file, header=[0, 1])
                    
#                     # Process all parts
#                     process_metadata(df, conn)
#                     process_events(df, conn)
#                     process_attendance(df, conn)
                    
#                     st.balloons()
#                     st.success("All processing completed successfully!")
#                 except Exception as e:
#                     st.error(f"An error occurred during processing: {e}")
#                 finally:
#                     if conn:
#                         conn.close()

# if __name__ == "__main__":
#     main()


import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv
import unicodedata

load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")


def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=DBNAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None


# ---------------------------
# Logic from metadata.py
# ---------------------------
def process_metadata(df, conn):
    st.info("Processing Metadata...")

    new_columns = []
    for col in df.columns.to_flat_index():
        col0 = str(col[0]).strip()
        col1 = str(col[1]).strip()
        if "Unnamed" in col0:
            new_columns.append(col1)
        else:
            if col0 in ["Nombre", "Apellidos", "email", "Instrumento", "Información adicional"]:
                new_columns.append(col0)
            else:
                new_columns.append(f"{col0}_{col1}")

    df_meta_proc = df.copy()
    df_meta_proc.columns = new_columns

    df_meta_proc["Nombre"] = df_meta_proc["Nombre"].astype(str).str.strip().str.lower()
    df_meta_proc["Apellidos"] = df_meta_proc["Apellidos"].astype(str).str.strip().str.lower()
    df_meta_proc["miembro"] = df_meta_proc["Nombre"] + " " + df_meta_proc["Apellidos"]

    email_col = "email"
    instrumento_col = "Instrumento"
    info_col = "Información adicional"

    for col in [email_col, instrumento_col, info_col]:
        if col not in df_meta_proc.columns:
            df_meta_proc[col] = None

    df_meta = df_meta_proc[["miembro", "Nombre", "Apellidos", email_col, instrumento_col, info_col]].copy()
    df_meta = df_meta.drop_duplicates(subset=["miembro"])

    cur = conn.cursor()
    datos = df_meta[["miembro", "Nombre", "Apellidos", email_col, instrumento_col, info_col]].values.tolist()
    execute_values(cur, """
        INSERT INTO miembros (miembro, nombre, apellidos, email, instrumento, informacion_adicional)
        VALUES %s
        ON CONFLICT (miembro) DO UPDATE SET
            nombre = EXCLUDED.nombre,
            apellidos = EXCLUDED.apellidos,
            email = EXCLUDED.email,
            instrumento = EXCLUDED.instrumento,
            informacion_adicional = EXCLUDED.informacion_adicional
    """, datos)
    conn.commit()
    cur.close()
    st.success("Metadata processed and 'miembros' table updated.")


# ---------------------------
# Logic from help.py
# ---------------------------
def tipo_evento(nombre):
    nombre_norm = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('utf-8').lower()

    ensayo_keywords = ["assaig", "parcial", "ensayo"]
    actuacion_keywords = ["acte", "concert", "presentacio", "certamen", "entra",
                          "moros i cristians", "alardo", "fira",
                          "processo", "disfresses", "mati", "entrada", "festes", "barri", "falles", "mic",
                          "sant", "sants", "desperta", "acompanyament", "mig", "any", "pasacarrer", "local", "deu", "crida", "gala", "falla", "ofrena"]
    otros_keywords = ["assemblea", "dinar", "soterrar", "esmorzar", "sopar"]

    if any(k in nombre_norm for k in ensayo_keywords):
        return "Ensayo"
    elif any(k in nombre_norm for k in actuacion_keywords):
        return "Actuación"
    elif any(k in nombre_norm for k in otros_keywords):
        return "Otros"
    else:
        return "desconocido"


def process_events(df, conn):
    st.info("Processing Events...")
    personal_cols = ["Nombre", "Apellidos", "email", "Instrumento", "Información adicional"]
    event_data_for_display = []

    for col_tuple in df.columns.to_flat_index():
        col0 = str(col_tuple[0]).strip()
        col1 = str(col_tuple[1]).strip()

        if col0 not in personal_cols:
            try:
                fecha = pd.to_datetime(col1, dayfirst=True, errors='coerce').date()
            except Exception:
                fecha = None

            if pd.notna(fecha):
                event_data_for_display.append({"evento": col0, "fecha": fecha})

    df_events = pd.DataFrame(event_data_for_display).drop_duplicates(subset=["evento", "fecha"])
    if df_events.empty:
        st.warning("No events found to process.")
        return

    df_events["tipo"] = df_events["evento"].apply(tipo_evento)

    # Solo insertar eventos que no existan ya en la BD
    cur = conn.cursor()
    cur.execute("SELECT evento, fecha FROM eventos")
    eventos_existentes = {(row[0], row[1]) for row in cur.fetchall()}

    eventos_nuevos = [
        (row["evento"], row["fecha"], row["tipo"])
        for _, row in df_events.iterrows()
        if (row["evento"], row["fecha"]) not in eventos_existentes
    ]
    if eventos_nuevos:
        execute_values(cur, "INSERT INTO eventos (evento, fecha, tipo) VALUES %s", eventos_nuevos)
    conn.commit()
    cur.close()

    st.success(f"Events processed. {len(eventos_nuevos)} new events inserted into 'eventos' table.")
    with st.expander("View Processed Events"):
        st.dataframe(df_events)


# ---------------------------
# Logic from main.py
# ---------------------------
def normalize_asistencia(x):
    """Normaliza valores de asistencia a True (Sí) o False (No/Pendiente)"""
    if pd.isna(x):
        return False
    if isinstance(x, str):
        return x.strip() == "Sí"
    if isinstance(x, (int, float)):
        return bool(int(x))
    return False


def process_attendance(df, conn):
    st.info("Processing Attendance...")
    personal_cols = ["Nombre", "Apellidos", "email", "Instrumento", "Información adicional"]
    event_fecha_map = {}
    new_columns = []

    for col_idx, col in enumerate(df.columns.to_flat_index()):
        col0 = str(col[0]).strip()
        col1 = str(col[1]).strip()
        if col0 in personal_cols:
            new_columns.append(col0)
        else:
            unique_event_name = f"{col0}_{col1}_{col_idx}"
            new_columns.append(unique_event_name)
            try:
                fecha = pd.to_datetime(col1, dayfirst=True, errors='coerce').date()
            except Exception:
                fecha = None
            event_fecha_map[unique_event_name] = {"original_name": col0, "date": fecha}

    df_att = df.copy()
    df_att.columns = new_columns

    if "Nombre" not in df_att.columns or "Apellidos" not in df_att.columns:
        st.error("Missing 'Nombre' or 'Apellidos' columns.")
        return

    df_att["miembro"] = (
        df_att["Nombre"].astype(str).str.strip().str.lower()
        + " "
        + df_att["Apellidos"].astype(str).str.strip().str.lower()
    )

    event_cols = [c for c in df_att.columns if c not in personal_cols + ["miembro"]]

    df_long = df_att.melt(
        id_vars=["miembro"],
        value_vars=event_cols,
        var_name="unique_event_id",
        value_name="asistencia"
    )

    df_long["evento"] = df_long["unique_event_id"].map(lambda x: event_fecha_map[x]["original_name"])
    df_long["fecha"] = df_long["unique_event_id"].map(lambda x: event_fecha_map[x]["date"])
    df_long = df_long[df_long["fecha"].notna()]
    df_long["asistencia"] = df_long["asistencia"].apply(normalize_asistencia)

    cur = conn.cursor()

    # Resolver miembro -> id
    cur.execute("SELECT miembro, id FROM miembros")
    miembro_id_map = {row[0]: row[1] for row in cur.fetchall()}

    # Resolver (evento, fecha) -> id
    cur.execute("SELECT evento, fecha, id FROM eventos")
    evento_id_map = {(row[0], row[1]): row[2] for row in cur.fetchall()}

    # Insertar/actualizar asistencia usando IDs enteros y boolean
    # Usar dict para deduplicar: si hay duplicados (miembro_id, evento_id), el último valor gana
    asistencia_dict = {}
    for _, row in df_long.iterrows():
        miembro_id = miembro_id_map.get(row["miembro"])
        evento_id = evento_id_map.get((row["evento"], row["fecha"]))
        if miembro_id and evento_id:
            asistencia_dict[(miembro_id, evento_id)] = row["asistencia"]

    asistencia_data = [(mid, eid, val) for (mid, eid), val in asistencia_dict.items()]

    execute_values(cur, """
        INSERT INTO asistencia (miembro_id, evento_id, asistencia)
        VALUES %s
        ON CONFLICT (miembro_id, evento_id) DO UPDATE SET asistencia = EXCLUDED.asistencia
    """, asistencia_data)
    conn.commit()
    cur.close()
    st.success(f"Attendance processed. {len(asistencia_data)} records updated in 'asistencia' table.")


# ---------------------------
# Main App
# ---------------------------
def main():
    st.set_page_config(page_title="SUMA Data Processor", layout="wide")
    st.title("🎼 SUMA Data Processor")
    st.markdown("Upload the SUMA Members Excel file to automatically process metadata, events, and attendance.")

    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:
        st.write("File uploaded successfully!")

        if st.button("Process File"):
            conn = get_db_connection()
            if conn:
                try:
                    df = pd.read_excel(uploaded_file, header=[0, 1])

                    process_metadata(df, conn)
                    process_events(df, conn)
                    process_attendance(df, conn)

                    st.balloons()
                    st.success("All processing completed successfully!")
                except Exception as e:
                    st.error(f"An error occurred during processing: {e}")
                finally:
                    if conn:
                        conn.close()


if __name__ == "__main__":
    main()
