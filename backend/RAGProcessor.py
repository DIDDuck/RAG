import os, chromadb, ollama
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


class RAGProcessor:
    def __init__(self, file_path, db_path, llm_model, llm_url, embeddings_model, filename_filter, stream):
        self.file_path = file_path
        self.db_path = db_path
        self.llm_model = llm_model
        self.llm_url = llm_url
        self.embeddings_model = embeddings_model
        self.filename_filter = filename_filter
        self.stream = stream
        # Initialize documents folder
        if not os.path.exists("./documents"): os.mkdir("./documents")

    def split_file_to_chunks(self):
        '''File loader: load file and split it to chunks'''

        if not os.path.exists(self.file_path):
            print(f"File \"{self.file_path}\" does not exist.")
            exit()
        file_name: str = os.path.split(self.file_path)[1]
        if not file_name == "" and file_name.endswith(".pdf"):
            loader = PyPDFLoader(
                file_path = self.file_path,
            )
        elif not file_name == "" and file_name.endswith(".txt"):
            loader = TextLoader(
                file_path = self.file_path,
            )  
        pages = loader.load()

        # After loading documents, they need to be split into small pieces (chuncks).
        splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 100)
        chunks = splitter.split_documents(pages)

        return chunks
    
    def create_embeddings(self):
        '''Create embeddings Using embedding model: nomic-embed-text. Using Langchain Ollama here.'''
        embeddings = OllamaEmbeddings(
            model = self.embeddings_model,
            base_url = self.llm_url
        )
        return embeddings

    def send_data_to_vectorstore(self):
        '''Send (embedded) chunks to vectorstore (ChromaDB for example). Use existing store or create new. Returns vectorstore.'''
        if os.path.exists(self.db_path):
            print("Opening existing vectorstore.") 
            chroma_client = chromadb.PersistentClient(path = self.db_path)
            vector_db = Chroma(
                client = chroma_client,
                collection_name = os.getenv("COLLECTION_NAME"),
                embedding_function = self.create_embeddings()
            )
            # If documents from current filename don't exist, send chunks to db.
            if len(vector_db.similarity_search(query = self.file_path, k = 1, filter = {"source": f"{self.file_path}"})) == 0:
                print("Saving data to vectorstore, please wait...")
                chunks = self.split_file_to_chunks()
                vector_db.add_documents(documents = chunks)
                print("Opened existing vectorstore and saved data in it.") 
            else:   
                print(f"Opened existing vectorstore with existing data from file: {self.file_path}")
        else:   
            print("Creating new vectorstore, please wait... ")
            chunks = self.split_file_to_chunks()
            os.mkdir(self.db_path) 
            vector_db = Chroma.from_documents(
                documents = chunks,
                collection_name = os.getenv("COLLECTION_NAME"), 
                embedding = self.create_embeddings(),
                persist_directory = self.db_path
            )
            print("Created new vectorstore and saved data in it.")
        return vector_db

    def get_user_query(self):
        '''When user has a question, it is sent for retrieval from vectorstore.'''
        query = input("\nGive me a question for RAG App: ")
        return query
    
    def retrieve_documents(self, vector_db, query):
        '''User question/query also needs to be converted to embedded form so that it can be searched in vectorstore. Using retriever to get most relevant documents from db.'''
        retriever = vector_db.as_retriever(search_kwargs = {"k": 5})
        retrieved_documents = retriever.invoke(input = query, filter = None if not self.filename_filter else {"source": f"{self.file_path}"})
        return retrieved_documents

    def create_context_from_documents(self, documents):
        '''Create context from documents retrieved from vectorstore.'''
        return "\n\n".join([document.page_content for document in documents]) # The most informative documents' content retrieved from vector store.
    
    def create_context_from_notes(self, notes):
        '''Create context from notes in .env'''
        return notes
    
    def create_ollama_client(self):
        '''Set up client for accessing running Ollama server'''
        return ollama.Client(host = self.llm_url)

    def send_query(self, ollama_client, documents_for_context, notes_for_context, query):
        '''Send context and query to LLM in Ollama server'''
        print("Sending query for LLM. Please wait for an answer...\n")

        response_chat = ollama_client.chat(
            model = self.llm_model,
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
            stream = self.stream
        )
        return response_chat
    
    def show_streaming_response(self, response):
        for part in response:
            print(part["message"]["content"], end = "")
        print("\n")    
