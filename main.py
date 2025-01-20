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
    st.rerun()

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
        
        # Debug info container
        with st.container(border=True):
            st.subheader("Debug Information")
            st.write(f"Database path: {Config.DB_PATH}")
            debug_container = st.empty()
        
        # Clear history button with confirmation dialog
        if st.button("🗑️ Clear All History", type="primary"):
            st.warning("Are you sure you want to delete ALL chat history?")
            st.write("This action cannot be undone.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirm Clear"):
                    with st.spinner("Clearing history..."):
                        try:
                            # Debug: Show current chat count before clearing
                            pre_count = len(st.session_state.db.get_all_chats())
                            debug_container.write(f"Chats before clear: {pre_count}")
                            st.write(f"Chats before clear: {pre_count}")
                            st.session_state.debug_log.write(f"Chats before clear: {pre_count}\n")
                            st.session_state.debug_log.flush()
                            # Perform clear operation
                            st.session_state.db.clear_all_history()
                            
                            # Debug: Show current chat count after clearing
                            post_count = len(st.session_state.db.get_all_chats())
                            debug_container.write(f"Chats after clear: {post_count}")
                            st.write(f"Chats after clear: {post_count}")
                            st.session_state.debug_log.write(f"Chats after clear: {post_count}\n")
                            st.session_state.debug_log.flush()
                            
                            # Reset session state
                            st.session_state.chat_id = None
                            st.session_state.messages = []
                            
                            if post_count == 0:
                                st.success("All chat history cleared successfully!")
                            else:
                                st.error(f"Clear operation failed - {post_count} chats remain")
                            
                            # Force immediate UI refresh
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error clearing history: {str(e)}")
                            st.experimental_rerun()
            with col2:
                if st.button("Cancel Clear"):
                    st.info("Clear operation cancelled")
                    st.rerun()
        
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
                        st.rerun()
        except Exception as e:
            st.error(f"Error loading chat history: {str(e)}")

    # Chat interface
    if not model_provider or not model_name:
        st.warning("Please select an AI model provider and model to start chatting.")
        return

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Type your message here..."):
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

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
