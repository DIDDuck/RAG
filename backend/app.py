from flask import Flask, jsonify, request, Response, stream_with_context
import os, config
import requests
from config import llm_model, embeddings_model, db_path, filename_filter, stream
from RAGProcessor import RAGProcessor

app = Flask(__name__)

@app.after_request
def add_headers(response):
    if request.path in ["/files", "/upfile"]: 
        response.headers.add("Access-Control-Allow-Headers", "Access-Control-Allow-Origin")
        response.headers.add("Access-Control-Allow-Origin", config.allowed_origin)

    if request.path in ["/chat"]:
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Access-Control-Allow-Origin")
        if not stream: response.headers.add("Content-Type", "application/json")
        response.headers.add("Access-Control-Allow-Origin", config.allowed_origin)

    return response


@app.route("/files")
def list():
    documents_directory = "./documents"
    files = os.listdir(documents_directory)
    files.sort()
    print(files)
    if not files:
        files = []
    res = jsonify({"files": files})
    res.status_code = 200

    return res


@app.route("/upfile", methods = ["POST", "OPTIONS"])
def upfile():

    if request.method == "POST":
        if "file" not in request.files:
            print("No file in request.")
            res = jsonify({
                "error": True,
                "message": "No file in request."
            })
            res.status_code = 400
            return res
        else:
            file = request.files.get("file")
            allowed_file_types = ["text/plain", "application/pdf"]
            if file.content_type not in allowed_file_types:
                res = jsonify({
                "error": True,
                "message": "Wrong file type."
            })
                res.status_code = 400
                return res    
            print("FILE:", file, file.content_type)

    res = jsonify({})
    res.status_code = 200
    return res


@app.route("/chat", methods = ["POST", "OPTIONS"])
def answer():

    # We wait for the response to be complete
    if request.method == "POST":

        content_type = request.headers.get('Content-Type')

        if (content_type == 'application/json'):

            try:
                print("REQUEST:", request.json)
                error_message_to_frontend = "Failed to get an answer from AI."
                user_message = request.json["message"]
                user_file = request.json["file"]
                stream = request.json["stream"] # Server sets default to False, use client choice
                if not user_file == None:
                    file_path = os.path.join("./documents", user_file) # override the one from config.py with one that user selects in UI.
                else:
                    no_files_available = "No files available."
                    raise Exception("No files available.")
                #messages = request.json["messages"]
                print("USER_PROMPT:", user_message)

                        
                ### Use RAGProcessor class to process question (and file).

                rag = RAGProcessor(file_path, db_path, llm_model, os.getenv("LLM_URL"), embeddings_model, filename_filter, stream)

                # Split data and send it to vectorstore (db)
                vector_db =  rag.send_data_to_vectorstore()

                # Get query from frontend form
                query = user_message

                # Get most relevant documents from db
                relevant_documents = rag.retrieve_documents(vector_db, query)

                # Form context to send to LLM
                context_from_documents = rag.create_context_from_documents(relevant_documents)
                context_from_notes = rag.create_context_from_notes(os.getenv("NOTES_FOR_CONTEXT"))

                # Client for contacting Ollama server
                ollama_client = rag.create_ollama_client()

                # Get response
                api_response = rag.send_query(ollama_client, context_from_documents, context_from_notes, query)
                #rag.show_streaming_response(api_response)
        
            except Exception as e:
                print("Fail:", e)
                res = jsonify({
                    "error": True,
                    "message": no_files_available if no_files_available else error_message_to_frontend
                })
                res.status_code = 200

                return res

        if stream == True:
            def generate():
                for part in api_response:
                    #print(part["message"]["content"])
                    yield part["message"]["content"]
            res = Response(generate(), content_type = "text/plain")

        else:    
            res = jsonify({
                "from": "AI Assistant",
                "text": api_response["message"]["content"]
                })
            res.status_code = 200

        return res 


    if request.method == "OPTIONS":

        res = jsonify({}) # dummy payload 
        res.status_code = 200

        return res

    
    
    
    