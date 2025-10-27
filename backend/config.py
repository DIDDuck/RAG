import os
from dotenv import load_dotenv

development = True
production = not development

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

if development:
    allowed_origin = "http://localhost:5173"

if production:
    allowed_origin = os.getenv("PRODUCTION_FRONTEND")



file_path = "./documents/file2.pdf" # Place your file under documents folder
llm_model = "nemotron-mini"
embeddings_model = "nomic-embed-text" # Model needs to be installed in Ollama
db_path = "./chroma_db"
filename_filter = True # Searching from only current file or from whole collection
stream = False