"""
Restaurant FAQ RAG Chatbot
Streamlit web interface for the chatbot
"""

import streamlit as st
import logging
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from src.rag_pipeline import RAGPipeline
from src.llm_handler import LLMHandler
from src.utils import (
    setup_logging,
    load_environment,
    ensure_directories,
    format_response,
    validate_api_key,
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Setup directories
ensure_directories()

# Load configuration
config = load_environment()

# Page configuration
st.set_page_config(
    page_title="🍔 Restaurant FAQ Assistant",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main { padding: 0rem 1rem; }
    .stChatMessage { padding: 1rem; margin: 0.5rem 0; border-radius: 0.5rem; }
    h1 { color: #ff6b35; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def initialize_chatbot():
    """Initialize RAG pipeline and LLM (cached)"""
    try:
        # Check API key
        if not config.get("openai_api_key"):
            st.error("❌ OPENAI_API_KEY not found in .env file")
            st.stop()

        # Initialize RAG Pipeline
        rag_pipeline = RAGPipeline(
            data_folder=config["data_folder"],
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"],
        )

        # Load or create vector store
        embeddings_path = "embeddings"
        if os.path.exists(embeddings_path):
            rag_pipeline.load_vector_store(embeddings_path)
            logger.info("Loaded existing vector store")
        else:
            rag_pipeline.setup_pipeline()
            rag_pipeline.save_vector_store(embeddings_path)
            logger.info("Created new vector store")

        # Initialize LLM
        llm = LLMHandler(
            model=config["llm_model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
        )

        return rag_pipeline, llm

    except Exception as e:
        st.error(f"❌ Error initializing chatbot: {str(e)}")
        logger.error(f"Initialization error: {str(e)}")
        st.stop()


def process_query(query: str, rag_pipeline: RAGPipeline, llm: LLMHandler) -> dict:
    """
    Process user query and generate response

    Args:
        query: User question
        rag_pipeline: RAG pipeline instance
        llm: LLM handler instance

    Returns:
        Dictionary with response and sources
    """
    try:
        # Retrieve context
        context, sources = rag_pipeline.get_context_from_query(
            query, k=config["max_results"]
        )

        # Generate response
        response = llm.generate_response(query, context, use_citations=True)

        return {
            "response": response,
            "sources": sources,
            "success": True,
        }

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return {
            "response": f"Sorry, I encountered an error: {str(e)}",
            "sources": [],
            "success": False,
        }


# Main UI
st.title("🍔 Restaurant FAQ Assistant")
st.markdown("*Ask me anything about our restaurant!*")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown(
        """
        This chatbot uses **RAG (Retrieval Augmented Generation)** to answer questions about our restaurant.
        
        **Features:**
        - 📖 Answers from our knowledge base
        - 📚 Shows source documents
        - ⚡ Real-time responses
        """
    )

    st.divider()

    if st.button("🔄 Reload Documents"):
        st.cache_resource.clear()
        st.rerun()

    st.markdown(
        """
        ---
        **Built with:**
        - LangChain
        - OpenAI GPT-4
        - Streamlit
        """
    )

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag_pipeline" not in st.session_state or "llm" not in st.session_state:
    with st.spinner("🔄 Initializing chatbot..."):
        st.session_state.rag_pipeline, st.session_state.llm = initialize_chatbot()
    st.success("✅ Chatbot ready!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if query := st.chat_input("Ask me about our menu, hours, policies..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            result = process_query(
                query,
                st.session_state.rag_pipeline,
                st.session_state.llm,
            )

        if result["success"]:
            response_text = result["response"]

            # Display response
            st.markdown(response_text)

            # Display sources
            if result["sources"]:
                st.divider()
                st.markdown("**📚 Sources:**")
                for source in set(result["sources"]):
                    st.caption(f"📄 {os.path.basename(source)}")

            # Add to history
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": format_response(response_text, result["sources"]),
                }
            )
        else:
            st.error(result["response"])

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    🔧 RAG Chatbot | Powered by LangChain & OpenAI | Built by Eugene Keya
    </div>
    """,
    unsafe_allow_html=True,
)
