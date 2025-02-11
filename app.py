import streamlit as st
import openai
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.prompts import AIMessagePromptTemplate

# Configuration de l'application
st.set_page_config(
    page_title="AI Tutor Pro",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Récupération de la clé API depuis secrets.toml (Streamlit Cloud)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Titre stylisé
st.markdown("""
    <h1 style='text-align: center; color: #2B7A78; 
    border-bottom: 3px solid #17252A; padding-bottom: 10px;'>
    🎓 AI Tutor Pro - Your Smart Learning Companion
    </h1>
""", unsafe_allow_html=True)

# Configuration du modèle dans la sidebar
with st.sidebar:
    st.header("⚙️ Paramètres du modèle")
    model_name = st.selectbox("Modèle LLM", ["gpt-3.5-turbo", "gpt-4"], index=0)
    temperature = st.slider("Créativité (temperature)", 0.0, 1.0, 0.7)
    max_length = st.slider("Longueur maximale", 100, 2000, 1000)

    st.header("💬 Historique de chat")
    if st.button("Effacer l'historique", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.download_button(
        label="Exporter l'historique",
        data="\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.get('history', [])]),
        file_name="chat_history.txt",
        mime="text/plain",
        use_container_width=True
    )

# Gestion de l'historique
if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.history.append({
        "role": "system",
        "content": "Vous êtes un tuteur IA expert pour collégiens. Expliquez de manière claire et concise, avec des exemples concrets."
    })

# Interface de chat principale
for message in st.session_state.history:
    if message["role"] not in ["system", "assistant", "user"]:
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Gestion de l'entrée utilisateur
if prompt := st.chat_input("Posez votre question..."):
    # Ajout du message utilisateur
    st.session_state.history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Génération de la réponse via OpenAI API
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.history],
                temperature=temperature,
                max_tokens=max_length
            )

            full_response = response["choices"][0]["message"]["content"]
            response_placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"❌ Erreur: {str(e)}"
            response_placeholder.error(full_response)

        # Mise à jour de l'historique
        st.session_state.history.append({"role": "assistant", "content": full_response})

# Section d'information
with st.expander("ℹ️ À propos de cette application"):
    st.markdown("""
    **Fonctionnalités clés :**
    - 🎨 Interface utilisateur moderne et professionnelle
    - 🔄 Historique de conversation persistante
    - ⚙️ Paramètres ajustables en temps réel
    - 📤 Exportation des conversations
    - 🚀 Génération de réponse avec OpenAI API
    - 🛠️ Gestion des erreurs robuste
    - 📱 Design responsive
        
    **Technologies utilisées :**
    - [OpenAI](https://platform.openai.com/) - API LLM
    - [LangChain](https://www.langchain.com/) - Orchestration LLM
    - [Streamlit](https://streamlit.io/) - Interface utilisateur
    """)
