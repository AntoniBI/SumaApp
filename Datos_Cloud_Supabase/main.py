import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

EXCEL_FILE = r"/home/antonim/proyectos/test/Datos_Cloud_Supabase/Miembros de SUMA - Asistencia.xlsx"

def normalize_asistencia(x):
    """Normaliza valores de asistencia a 1 (Sí) o 0 (No/Pendiente)"""
    if pd.isna(x):
        return 0
    if isinstance(x, str):
        x = x.strip()
        if x in ["Sí"]:
            return 1
        elif x in ["No", "Pendiente", "No convocado", "0 convocado"]:
            return 0
        else:
            # Por si hay valores tipo '0%' u otros
            if x.endswith('%'):
                try:
                    return int(x.replace('%','')) // 100
                except:
                    return 0
            return 0
    elif isinstance(x, (int, float)):
        return int(x)
    return 0

def main():

    df = pd.read_excel(EXCEL_FILE, header=[0, 1])


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
            except:
                fecha = None
            event_fecha_map[unique_event_name] = {"original_name": col0, "date": fecha}

    df.columns = new_columns


    df["miembro"] = df["Nombre"] + " " + df["Apellidos"]


    event_cols = [c for c in df.columns if c not in personal_cols + ["miembro"]]


    df_long = df.melt(
        id_vars=["miembro"],
        value_vars=event_cols,
        var_name="unique_event_id",
        value_name="asistencia"
    )


    df_long["evento"] = df_long["unique_event_id"].map(lambda x: event_fecha_map[x]["original_name"])
    df_long["fecha"] = df_long["unique_event_id"].map(lambda x: event_fecha_map[x]["date"])


    df_long = df_long[df_long["fecha"].notna()]


    df_long["asistencia"] = df_long["asistencia"].apply(normalize_asistencia)

    print("📌 Ejemplo de datos transformados:")
    print(df_long.head())


    conn = psycopg2.connect(
        dbname=DBNAME, user=USER, password=PASSWORD, host=HOST, port=PORT
    )
    cur = conn.cursor()

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS asistencia (
        id SERIAL PRIMARY KEY,
        miembro VARCHAR(255),
        evento VARCHAR(255),
        fecha DATE,
        asistencia INT,
        UNIQUE (miembro, evento, fecha)
    );
    """
    cur.execute(create_table_sql)
    conn.commit()

    datos = df_long[["miembro", "evento", "fecha", "asistencia"]].values.tolist()

    insert_sql = """
    INSERT INTO asistencia (miembro, evento, fecha, asistencia)
    VALUES %s
    ON CONFLICT (miembro, evento, fecha) DO NOTHING;
    """
    execute_values(cur, insert_sql, datos)
    conn.commit()

    cur.close()
    conn.close()

    print("Proceso completado: datos cargados en PostgreSQL")

if __name__ == "__main__":
    main()
