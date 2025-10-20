from config import llm_model, embeddings_model, db_path, file_path, filename_filter
import os, math
from dotenv import load_dotenv
import ollama, chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from RAGProcessor import RAGProcessor

load_dotenv()

rag = RAGProcessor(file_path, db_path, llm_model, os.getenv("LLM_URL"), embeddings_model, filename_filter, stream = True)

# Split data and send it to vectorstore (db)
vector_db =  rag.send_data_to_vectorstore()

# Get query from user
query = rag.get_user_query()

# Get most relevant documents from db
relevant_documents = rag.retrieve_documents(vector_db, query)

# Form context to send to LLM
context_from_documents = rag.create_context_from_documents(relevant_documents)
context_from_notes = rag.create_context_from_notes(os.getenv("NOTES_FOR_CONTEXT"))

# Client for contacting Ollama server
ollama_client = rag.create_ollama_client()

# Get response
response = rag.send_query(ollama_client, context_from_documents, context_from_notes, query)
rag.show_streaming_response(response)