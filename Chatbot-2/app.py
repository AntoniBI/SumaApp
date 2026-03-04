# import os
# import uuid
# import gradio as gr
# from langchain_openai import ChatOpenAI
# from langchain_community.vectorstores import Qdrant
# # CAMBIO: Usar la librería dedicada langchain-huggingface
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from qdrant_client import QdrantClient, models
# from qdrant_client.http import models as rest_models
# from langchain.chains.history_aware_retriever import create_history_aware_retriever
# from langchain.chains.retrieval import create_retrieval_chain
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain_core.runnables.history import RunnableWithMessageHistory

# # --- 1. CONFIGURACIÓN Y VARIABLES DE ENTORNO ---
# QDRANT_URL = os.getenv("QDRANT_URL")
# QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# COLLECTION_NAME = "dgt_documents_qdrant_memory_filter_fixed_2"

# # Categorías disponibles
# OPCIONES_CATEGORIAS = [
#     "Todas",
#     "Documentos de la SUMA",
#     "Manuales Técnicos y Procedimientos",
#     "Inventarios y Activos SUMA",
#     "Otros"
# ]

# # --- 2. INICIALIZAR CLIENTES ---

# # Cliente Qdrant
# client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# # Embeddings (Actualizado para usar langchain_huggingface)
# embeddings_model = HuggingFaceEmbeddings(
#     model_name="intfloat/e5-large-v2",
#     model_kwargs={'device': 'cpu'}, 
#     encode_kwargs={'normalize_embeddings': False}
# )

# # LLM
# llm_openai = ChatOpenAI(
#     model="gpt-4o-mini", 
#     temperature=0.1,
#     api_key=OPENAI_API_KEY
# )

# # Conexión a la VectorDB (Actualizado a QdrantVectorStore)
# vectordb = Qdrant(
#     client=client,
#     collection_name=COLLECTION_NAME,
#     embeddings=embeddings_model,
#     content_payload_key="content"
# )

# # --- 3. PROMPTS ---

# contextualize_q_system_prompt = """Dado un historial de chat y la última pregunta del usuario \
# que podría hacer referencia al contexto en el historial de chat, formula una pregunta independiente \
# que pueda entenderse sin el historial de chat. NO respondas a la pregunta, \
# solo reformúlala si es necesario y, si no, devuélvela tal cual."""

# contextualize_q_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", contextualize_q_system_prompt),
#         MessagesPlaceholder("chat_history"),
#         ("human", "{input}"),
#     ]
# )

# qa_system_prompt = """Eres un asistente especializado en los documentos sobre la Sociedad Musical de Alberic (SUMA). \
# Utiliza los siguientes fragmentos de contexto recuperado para responder a la pregunta. \
# Si no sabes la respuesta, di que no lo sabes. \
# Menciona siempre de qué documentos has extraído la información (usando el metadato 'source'). \
# Profundiza en la respuesta.
# Contexto:
# {context}"""

# qa_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", qa_system_prompt),
#         MessagesPlaceholder("chat_history"),
#         ("human", "{input}"),
#     ]
# )

# # --- 4. GESTIÓN DE MEMORIA EN RAM ---
# store = {}

# def get_session_history(session_id: str):
#     if session_id not in store:
#         store[session_id] = ChatMessageHistory()
#     return store[session_id]

# # --- 5. LÓGICA DEL CHAT ---

# def build_qdrant_filter(category_name):
#     if not category_name or category_name == "Todas":
#         return None
#     return rest_models.Filter(
#         must=[
#             rest_models.FieldCondition(
#                 key="category", 
#                 match=rest_models.MatchValue(value=category_name)
#             )
#         ]
#     )

# def chat_logic(message, history, selected_category, session_id):
#     # Seguridad: Si por error session_id viene vacío, generamos uno temporal
#     if not session_id:
#         session_id = str(uuid.uuid4())

#     # 1. Construir filtro
#     qdrant_filter = build_qdrant_filter(selected_category)
    
#     # 2. Retriever dinámico
#     dynamic_retriever = vectordb.as_retriever(
#         search_kwargs={
#             "k": 4, 
#             "filter": qdrant_filter 
#         }
#     )

#     # 3. Cadenas LangChain
#     history_aware_retriever = create_history_aware_retriever(
#         llm_openai, dynamic_retriever, contextualize_q_prompt
#     )
#     question_answer_chain = create_stuff_documents_chain(llm_openai, qa_prompt)
#     rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
#     conversational_rag_chain = RunnableWithMessageHistory(
#         rag_chain,
#         get_session_history,
#         input_messages_key="input",
#         history_messages_key="chat_history",
#         output_messages_key="answer",
#     )

#     # 4. Generar respuesta streaming usando el ID único del usuario
#     full_response = ""
#     # En versiones nuevas, a veces history devuelve objetos, aseguramos manejo de errores básico
#     try:
#         for chunk in conversational_rag_chain.stream(
#             {"input": message},
#             config={"configurable": {"session_id": session_id}}
#         ):
#             if "answer" in chunk:
#                 full_response += chunk["answer"]
#                 yield full_response
#     except Exception as e:
#         yield f"Error al procesar la respuesta: {str(e)}"

# # --- 6. INTERFAZ GRÁFICA ---

# custom_css = """
# footer {visibility: hidden}
# .gradio-container {background-color: #f9fafb}
# """

# tema_musical = gr.themes.Soft(primary_hue="indigo", secondary_hue="slate")

# with gr.Blocks(theme=tema_musical, css=custom_css, title="Chatbot SUMA") as demo:
    
#     # ESTADO: Genera un ID único cada vez que se carga la página
#     session_state = gr.State(lambda: str(uuid.uuid4()))
    
#     gr.Markdown("# 🎵 Asistente Virtual SUMA")
#     gr.Markdown("Pregunta sobre normativas, manuales y documentos internos.")

#     filtro_dropdown = gr.Dropdown(
#         choices=OPCIONES_CATEGORIAS,
#         value="Todas", 
#         label="📂 Filtrar por Categoría",
#         info="Acota la búsqueda a un tipo de documento específico."
#     )

#     chat_interface = gr.ChatInterface(
#         fn=chat_logic,
#         # Pasamos el session_state (el ID oculto) a la función lógica
#         additional_inputs=[filtro_dropdown, session_state],
#         examples=[
#             ["¿Cuáles son los requisitos para ser socio?"], 
#             ["Resumen del manual de procedimientos"],
#         ]
#     )

# if __name__ == "__main__":
#     demo.launch()


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
