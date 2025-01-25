# main.py
import streamlit as st
from router import ModelRouter
from database import Database
from config import Config
import asyncio

def init_debug_log():
    """Initialize debug log file only once per session"""
    if "debug_log_initialized" not in st.session_state:
        # Open in append mode to preserve existing logs
        st.session_state.debug_log = open("debug.log", "a")
        st.session_state.debug_log.write("Debug log initialized\n")
        st.session_state.debug_log.flush()
        st.session_state.debug_log_initialized = True

def init_session_state():
    # Initialize debug logging
    init_debug_log()
    
    if "chat_id" not in st.session_state:
        st.session_state.chat_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "router" not in st.session_state:
        st.session_state.router = ModelRouter()
    if "db" not in st.session_state:
        st.session_state.db = Database(Config.DB_PATH)

def create_new_chat():
    st.session_state.messages = []
    st.session_state.chat_id = None
    st.session_state.needs_rerun = True

def clear_all_chat():
    st.session_state.db.clear_all_history()

def main():
    st.set_page_config(
        page_title=Config.APP_NAME,
        page_icon="🔸",
        layout="wide"
    )
    
    st.title(f"{Config.APP_NAME} AI Assistant")
    init_session_state()

    # Sidebar
    with st.sidebar:
        st.button("New Chat", on_click=create_new_chat)
        st.button("Clear Chat", on_click=clear_all_chat)
        
        # File upload
        uploaded_file = st.file_uploader(
            "Load File",
            type=None,
            key="file_upload",
            help="Select a file to analyze"
        )
        
        # Model selection
        available_models = st.session_state.router.get_available_models()
        
        if not available_models:
            st.error("No AI models available. Please check your API keys and connections.")
            model_provider = None
            model_name = None
        else:
            model_provider = st.selectbox(
                "Select Provider",
                options=list(available_models.keys()),
                key="model_provider"
            )
            
            if model_provider:
                model_name = st.selectbox(
                    "Select Model",
                    options=available_models.get(model_provider, []),
                    key="model_name"
                )

                # Set the selected model for Ollama
                if model_provider == "ollama":
                    model = st.session_state.router.get_model("ollama")
                    if model:
                        model.set_model(model_name)
        
        # Chat history
        st.subheader("Chat History")
                
        # Display chat history after clear operation
        try:
            chats = st.session_state.db.get_all_chats()
            if not chats:
                st.info("No chat history available")
            else:
                for chat in chats:
                    if st.button(f"{chat['title']} - {chat['created_at']}", key=chat['id']):
                        st.session_state.chat_id = chat['id']
                        st.session_state.messages = st.session_state.db.get_chat_messages(chat['id'])
                        st.session_state.needs_rerun = True
        except Exception as e:
            st.error(f"Error loading chat history: {str(e)}")
            
    if st.session_state.get('needs_rerun'):
        st.session_state.needs_rerun = False
        st.rerun()

    # Chat interface
    if not model_provider or not model_name:
        st.warning("Please select an AI model provider and model to start chatting.")
        return

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Type your message here..."):
        # User message
        # Add file content to message if uploaded
        full_content = prompt
        if st.session_state.get("file_upload"):
            file = st.session_state.file_upload
            full_content += f"\n\n[Attached file: {file.name}]\n"
            full_content += file.getvalue().decode(errors="ignore")
            
        st.session_state.messages.append({"role": "user", "content": full_content})
        with st.chat_message("user"):
            st.write(prompt)
            if st.session_state.get("file_upload"):
                st.write(f"📎 Attached file: {st.session_state.file_upload.name}")

        # Create new chat if needed
        if not st.session_state.chat_id:
            try:
                model = st.session_state.router.get_model(model_provider)
                title = asyncio.run(model.get_title_from_first_message(prompt))
                st.session_state.chat_id = st.session_state.db.create_chat(title, f"{model_provider}/{model_name}")
                st.session_state.db.save_message(st.session_state.chat_id, "user", prompt)
            except Exception as e:
                st.error(f"Error creating new chat: {str(e)}")
                return

        # Generate response
        with st.chat_message("assistant"):
            try:
                model = st.session_state.router.get_model(model_provider)
                with st.spinner("Thinking..."):
                    response = asyncio.run(model.generate_response(st.session_state.messages))
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.db.save_message(st.session_state.chat_id, "assistant", response)
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

if __name__ == "__main__":
    main()
