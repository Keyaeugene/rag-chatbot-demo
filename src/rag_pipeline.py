"""
RAG Pipeline Module
Handles document loading, embedding, and retrieval
"""

import os
import logging
from typing import List, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Retrieval Augmented Generation Pipeline
    Manages document loading, embedding, and similarity search
    """

    def __init__(
        self,
        data_folder: str = "data",
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        embedding_model: str = "text-embedding-3-small",
    ):
        self.data_folder = data_folder
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model
        self.vector_store = None
        self.documents = None
        logger.info(f"RAG Pipeline initialized with chunk_size={chunk_size}")

    def load_documents(self) -> List[Document]:
        """Load documents from data folder"""
        logger.info(f"Loading documents from {self.data_folder}")
        documents = []

        if os.path.exists(self.data_folder):
            text_loader = DirectoryLoader(
                self.data_folder,
                glob="**/*.txt",
                loader_cls=TextLoader,
                show_progress=True,
            )
            documents.extend(text_loader.load())

            pdf_loader = DirectoryLoader(
                self.data_folder,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader,
                show_progress=True,
            )
            documents.extend(pdf_loader.load())

        logger.info(f"Loaded {len(documents)} documents")
        self.documents = documents
        return documents

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks for better retrieval"""
        logger.info(f"Chunking {len(documents)} documents")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )

        chunked_docs = splitter.split_documents(documents)
        logger.info(f"Created {len(chunked_docs)} chunks")
        return chunked_docs

    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """Create Chroma vector store from documents"""
        logger.info("Creating vector store...")
        embeddings = OpenAIEmbeddings(model=self.embedding_model)

        vector_store = Chroma.from_documents(
            documents=documents, embedding=embeddings
        )

        logger.info("Vector store created successfully")
        self.vector_store = vector_store
        return vector_store

    def retrieve_documents(self, query: str, k: int = 3) -> List[Tuple[Document, float]]:
        """Retrieve relevant documents for a query"""
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call create_vector_store first.")

        results = self.vector_store.similarity_search_with_score(query, k=k)
        logger.info(f"Retrieved {len(results)} documents for query: {query[:50]}...")
        return results

    def setup_pipeline(self) -> Chroma:
        """Complete setup: load docs -> chunk -> embed -> create store"""
        logger.info("Setting up RAG pipeline...")
        documents = self.load_documents()
        
        if not documents:
            logger.warning("No documents found in data folder")
            return None
            
        chunked_docs = self.chunk_documents(documents)
        vector_store = self.create_vector_store(chunked_docs)
        logger.info("RAG pipeline setup complete")
        return vector_store

    def get_context_from_query(self, query: str, k: int = 3) -> Tuple[str, List[str]]:
        """Get context and source info for a query"""
        results = self.retrieve_documents(query, k=k)

        context_text = "\n\n".join(
            [f"Document: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}"
             for doc, score in results]
        )

        sources = [doc.metadata.get("source", "Unknown") for doc, score in results]
        return context_text, sources