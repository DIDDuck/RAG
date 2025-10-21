# Unnamed RAG App
This app, at the moment called unnamed RAG App, gives answers to user with help of document(s) that the app has been given access to.
Frontend is written using React + TypeScript + Tailwind and backend using Flask (Python).
App can be used from command line running backend/rag.py using python. Web UI in frontend folder can also be used to connect to backend app.py.

### Configuration
In your backend .env file, set constants:
- LLM_URL: This is a url for running Ollama server.
- COLLECTION_NAME: Just a name for collection of your data in vectorstore db.
- NOTES_FOR_CONTEXT: Additional information/context for LLM when asking question.
- PRODUCTION_FRONTEND: If running in production mode, set your frontend url here. In production mode also remember to set 'const development = false' (in config.ts) and 'development = False' (in config.py).