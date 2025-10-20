from flask import Flask, jsonify, request, Response, stream_with_context
import os, config
import requests
from config import llm_model, embeddings_model, db_path, file_path, filename_filter, stream
from RAGProcessor import RAGProcessor

app = Flask(__name__)

@app.route("/chat", methods = ["POST", "OPTIONS"])
def answer():

    # We wait for the response to be complete
    if request.method == "POST":

        content_type = request.headers.get('Content-Type')

        if (content_type == 'application/json'):
            print("REQUEST:", request.json)
            user_message = request.json["message"]
            #messages = request.json["messages"]
            message_to_frontend = "Failed to get an answer from AI."
        
            print("USER_PROMPT:", user_message)


        try:           
            
            ################ RUN RAGPROCESSOR CLASS #################################

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
            #rag.show_streaming_response(response)

            #########################################################################
            
        except:
            print("Something failed")
            res = jsonify({
                "error": True,
                "message": message_to_frontend
            })
            res.headers.add("Access-Control-Allow-Headers", "Content-Type,Access-Control-Allow-Origin")
            res.headers.add("Content-Type", "application/json")
            res.headers.add("Access-Control-Allow-Origin", config.allowed_origin)
            res.status_code = 200

            return res

        # Response from Ollama /api/chat
        if "error" in api_response:
            res = jsonify({
                "error": True,
                "message": message_to_frontend 
            })
            res.status_code = 500
            
        else:
            print(api_response.message)    
            res = jsonify({
                "from": "AI Assistant",
                "text": api_response["message"]["content"]
                })
            res.status_code = 200

        res.headers.add("Access-Control-Allow-Headers", "Content-Type,Access-Control-Allow-Origin")
        res.headers.add("Content-Type", "application/json")
        res.headers.add("Access-Control-Allow-Origin", config.allowed_origin)
        return res 


    if request.method == "OPTIONS":

        res = jsonify({}) # dummy payload 
        
        res.headers.add("Access-Control-Allow-Headers", "Content-Type,Access-Control-Allow-Origin")
        res.headers.add("Content-Type", "application/json")
        res.headers.add("Access-Control-Allow-Origin", config.allowed_origin)
        res.status_code = 200

        return res

    
    
    
    