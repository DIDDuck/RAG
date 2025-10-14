# Unnamed RAG App
This app, at the moment called Unnamed RAG App, gives answers to user with help of document(s) that the app has been given access to.

### Configuration
In your .env file, set constants:
- LLM_URL: This is a url for running Ollama server.
- COLLECTION_NAME: Just a name for collection of your data in vectorstore db.
- NOTES_FOR_CONTEXT: Additional information/context for LLM when asking question.