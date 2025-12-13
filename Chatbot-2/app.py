import os
import uuid
import gradio as gr
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Qdrant
# CAMBIO: Usar la librería dedicada langchain-huggingface
from langchain_community.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient, models
from qdrant_client.http import models as rest_models
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# --- 1. CONFIGURACIÓN Y VARIABLES DE ENTORNO ---
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COLLECTION_NAME = "dgt_documents_qdrant_memory_filter_fixed_2"

# Categorías disponibles
OPCIONES_CATEGORIAS = [
    "Todas",
    "Documentos de la SUMA",
    "Manuales Técnicos y Procedimientos",
    "Inventarios y Activos SUMA",
    "Otros"
]

# --- 2. INICIALIZAR CLIENTES ---

# Cliente Qdrant
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Embeddings (Actualizado para usar langchain_huggingface)
embeddings_model = HuggingFaceEmbeddings(
    model_name="intfloat/e5-large-v2",
    model_kwargs={'device': 'cpu'}, 
    encode_kwargs={'normalize_embeddings': False}
)

# LLM
llm_openai = ChatOpenAI(
    model="gpt-4o-mini", 
    temperature=0.1,
    api_key=OPENAI_API_KEY
)

# Conexión a la VectorDB (Actualizado a QdrantVectorStore)
vectordb = Qdrant(
    client=client,
    collection_name=COLLECTION_NAME,
    embeddings=embeddings_model,
    content_payload_key="content"
)

# --- 3. PROMPTS ---

contextualize_q_system_prompt = """Dado un historial de chat y la última pregunta del usuario \
que podría hacer referencia al contexto en el historial de chat, formula una pregunta independiente \
que pueda entenderse sin el historial de chat. NO respondas a la pregunta, \
solo reformúlala si es necesario y, si no, devuélvela tal cual."""

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

qa_system_prompt = """Eres un asistente especializado en los documentos sobre la Sociedad Musical de Alberic (SUMA). \
Utiliza los siguientes fragmentos de contexto recuperado para responder a la pregunta. \
Si no sabes la respuesta, di que no lo sabes. \
Menciona siempre de qué documentos has extraído la información (usando el metadato 'source'). \
Profundiza en la respuesta.
Contexto:
{context}"""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# --- 4. GESTIÓN DE MEMORIA EN RAM ---
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# --- 5. LÓGICA DEL CHAT ---

def build_qdrant_filter(category_name):
    if not category_name or category_name == "Todas":
        return None
    return rest_models.Filter(
        must=[
            rest_models.FieldCondition(
                key="category", 
                match=rest_models.MatchValue(value=category_name)
            )
        ]
    )

def chat_logic(message, history, selected_category, session_id):
    # Seguridad: Si por error session_id viene vacío, generamos uno temporal
    if not session_id:
        session_id = str(uuid.uuid4())

    # 1. Construir filtro
    qdrant_filter = build_qdrant_filter(selected_category)
    
    # 2. Retriever dinámico
    dynamic_retriever = vectordb.as_retriever(
        search_kwargs={
            "k": 4, 
            "filter": qdrant_filter 
        }
    )

    # 3. Cadenas LangChain
    history_aware_retriever = create_history_aware_retriever(
        llm_openai, dynamic_retriever, contextualize_q_prompt
    )
    question_answer_chain = create_stuff_documents_chain(llm_openai, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    # 4. Generar respuesta streaming usando el ID único del usuario
    full_response = ""
    # En versiones nuevas, a veces history devuelve objetos, aseguramos manejo de errores básico
    try:
        for chunk in conversational_rag_chain.stream(
            {"input": message},
            config={"configurable": {"session_id": session_id}}
        ):
            if "answer" in chunk:
                full_response += chunk["answer"]
                yield full_response
    except Exception as e:
        yield f"Error al procesar la respuesta: {str(e)}"

# --- 6. INTERFAZ GRÁFICA ---

custom_css = """
footer {visibility: hidden}
.gradio-container {background-color: #f9fafb}
"""

tema_musical = gr.themes.Soft(primary_hue="indigo", secondary_hue="slate")

with gr.Blocks(theme=tema_musical, css=custom_css, title="Chatbot SUMA") as demo:
    
    # ESTADO: Genera un ID único cada vez que se carga la página
    session_state = gr.State(lambda: str(uuid.uuid4()))
    
    gr.Markdown("# 🎵 Asistente Virtual SUMA")
    gr.Markdown("Pregunta sobre normativas, manuales y documentos internos.")

    filtro_dropdown = gr.Dropdown(
        choices=OPCIONES_CATEGORIAS,
        value="Todas", 
        label="📂 Filtrar por Categoría",
        info="Acota la búsqueda a un tipo de documento específico."
    )

    chat_interface = gr.ChatInterface(
        fn=chat_logic,
        # Pasamos el session_state (el ID oculto) a la función lógica
        additional_inputs=[filtro_dropdown, session_state],
        examples=[
            ["¿Cuáles son los requisitos para ser socio?"], 
            ["Resumen del manual de procedimientos"],
        ]
    )

if __name__ == "__main__":
    demo.launch()