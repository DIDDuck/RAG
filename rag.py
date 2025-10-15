from config import llm_model, embedding_model, db_path, file_path, filename_filter
import os, math
from dotenv import load_dotenv
import ollama, chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

# Initialize documents folder
if not os.path.exists("./documents"): os.mkdir("./documents")


def split_file_to_chunks(file_path):
    '''File loader: load file and split it to chunks'''

    if not os.path.exists(file_path):
        print(f"File \"{file_path}\" does not exist.")
        exit()
    loader = PyPDFLoader(
        file_path = file_path,
        )
    pages = loader.load()

    # After loading documents, they need to be split into small pieces (chuncks).
    splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 100)
    chunks = splitter.split_documents(pages)

    return chunks


# Create embeddings Using embedding model: nomic-embed-text. Using Langchain Ollama here.
embeddings = OllamaEmbeddings(
    model = embedding_model,
    base_url = os.getenv("LLM_URL")
)

# Send (embedded) chunks to vectorstore (ChromaDB for example). Use existing store or create new.
if os.path.exists(db_path):
    print("Opening existing vectorstore.") 
    chroma_client = chromadb.PersistentClient(path = db_path)
    collection = chroma_client.get_or_create_collection(
        name = os.getenv("COLLECTION_NAME")
    )
    vector_db = Chroma(
        client = chroma_client,
        collection_name = os.getenv("COLLECTION_NAME"),
        embedding_function = embeddings
    )
    # If documents from current filename don't exist, send chunks to db.
    if len(vector_db.similarity_search(query = file_path, k = 1, filter = {"source": f"{file_path}"})) == 0:
        print("Saving data to vectorstore, please wait...")
        chunks = split_file_to_chunks(file_path)
        vector_db.add_documents(documents = chunks)
        print("Opened existing vectorstore and saved data in it.") 
    else:   
        print(f"Opened existing vectorstore with existing data from file: {file_path}")
else:   
    print("Creating new vectorstore, please wait... ")
    chunks = split_file_to_chunks(file_path)
    os.mkdir(db_path) 
    vector_db = Chroma.from_documents(
        documents = chunks,
        collection_name = os.getenv("COLLECTION_NAME"), 
        embedding = embeddings,
        persist_directory = db_path
    )
    print("Created new vectorstore and saved data in it.")


# When user has a question, it is sent for retrieval from vectorstore.
query = input("\nGive me a question for RAG App: ")

# Question/query also needs to be converted to embedded form so that it can searched in vectorstore. Using retriever for this.
retriever = vector_db.as_retriever(search_kwargs = {"k": 10})
retrieved_documents = retriever.invoke(input = query, filter = None if not filename_filter else {"source": f"{file_path}"})

#for document in retrieved_documents:
#    print("Source:", document.metadata["source"])
#print(f"NUMBER of documents: {len(retrieved_documents)}")

# Setting context for sending query to LLM: relevant documents from Chromadb and some specific notes.
documents_for_context = "\n\n".join([document.page_content for document in retrieved_documents]) # The most informative documents' content retrieved from vector store.
notes_for_context = os.getenv("NOTES_FOR_CONTEXT")

# For custom url, client is needed
ollama_client = ollama.Client(
    host = os.getenv("LLM_URL")
)

# Send context and query to LLM
print("Sending query for LLM. Please wait for an answer...\n")

response_chat = ollama_client.chat(
    model = llm_model,
    messages = [
        {
            "role": "system",
            "content": notes_for_context + documents_for_context + "Use ONLY this information and base your answer on it."
        },
        {
            "role": "user",
            "content": query
        } 
    ],
    stream = True
)


# Streaming chat response
for part in response_chat:
    print(part["message"]["content"], end = "")
print("\n")

