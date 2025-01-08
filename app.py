import os
import json
from flask import Flask, render_template, request, jsonify
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import SystemMessage, HumanMessage, Document
from langchain.prompts import ChatPromptTemplate
import subprocess
import threading
import time
import requests

# Initialize Flask app
app = Flask(__name__)

# Load Hugging Face embeddings
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Set up FAISS Vector Store
vectorstore_path = "courses_faiss_index"
def load_vectorstore():
    if not os.path.exists(vectorstore_path):
        # Load data from JSON
        with open('all_courses.json', 'r') as f:
            courses = json.load(f)

        # Prepare documents
        documents = [
            Document(
                page_content=course['description'],
                metadata={
                    'title': course['title'],
                    'length': course.get('length', 'N/A'),
                    'level': course.get('level', 'N/A'),
                    'rating': course.get('rating', 'N/A'),
                    'link': course.get('link', 'N/A'),
                    'price': course.get('price', 'Free'),  # Default to 'Free' if price is not available
                    'image_url': course.get('image_url', 'https://i.imgur.com/VWvknw2.png')  # Default to empty string if image link is not available
                }
            )
            for course in courses
        ]

        # Initialize FAISS vector store
        vectorstore = FAISS.from_documents(documents, embedding_model)
        vectorstore.save_local(vectorstore_path)
    else:
        vectorstore = FAISS.load_local(vectorstore_path, embedding_model, allow_dangerous_deserialization=True)
    return vectorstore

vectorstore = load_vectorstore()

# Initialize OpenAI Chat LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    filters = request.json.get('filters', {})  # Filters for metadata

    # Generate refined query using Chat LLM
    try:
        chat_prompt = [
            SystemMessage(content="You are a helpful assistant for refining search queries."),
            HumanMessage(content=f"Refine the following query for better course search: {query}")
        ]
        refined_query_response = llm.invoke(chat_prompt)
        refined_query = refined_query_response.content.strip()
    except Exception as e:
        return jsonify({"error": f"Error refining query: {str(e)}"}), 500

    # Search FAISS with refined query
    try:
        results = vectorstore.similarity_search(refined_query, k=10)
    except Exception as e:
        return jsonify({"error": f"Error searching vector store: {str(e)}"}), 500

    # Filter results if needed
    filtered_results = []
    for doc in results:
        metadata = doc.metadata
        if filters:
            if filters.get('level') and metadata['level'] != filters['level']:
                continue
            if filters.get('rating') and metadata['rating'] != filters['rating']:
                continue
            if filters.get('length') and metadata['length'] != filters['length']:
                continue
        filtered_results.append(doc)

    # Use Chat LLM to generate suggestions
    try:
        suggestions_prompt = [
            SystemMessage(content="You are a helpful assistant for providing course recommendations."),
            HumanMessage(content=f"Based on these courses, suggest the best options: {[doc.metadata for doc in filtered_results]}")
        ]
        suggestions_response = llm.invoke(suggestions_prompt)
        suggestions = suggestions_response.content.strip()
    except Exception as e:
        return jsonify({"error": f"Error generating suggestions: {str(e)}"}), 500

    # Format results
    response = {
        "results": [
            {
                'title': doc.metadata['title'],
                'description': doc.page_content,
                'length': doc.metadata['length'],
                'level': doc.metadata['level'],
                'rating': doc.metadata['rating'],
                'link': doc.metadata['link'],
                'price': doc.metadata.get('price', 'Free'),  # Include price
                'image_url': doc.metadata.get('image_url', 'https://i.imgur.com/VWvknw2.png')  # Include image link
            }
            for doc in filtered_results
        ],
        "suggestions": suggestions
    }

    return jsonify(response)


@app.route('/update-courses', methods=['POST'])
def update_courses():
    try:
        # Run the scraper script

        subprocess.run(["python", "scrapebest.py"], check=True)
        global vectorstore
        vectorstore = load_vectorstore()  # Reload the vectorstore with new data
        return jsonify({"message": "Courses updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Self-pinging functionality to keep the server running
def self_ping():
    """Function to keep the app awake by pinging itself."""
    while True:
        try:
            url = "https://smart-course-search-platform.onrender.com/"
            response = requests.get(url)
            print(f"Self-ping status: {response.status_code}")
        except Exception as e:
            print(f"Error in self-ping: {e}")
        time.sleep(600) 


if __name__ == "__main__":
    threading.Thread(target=self_ping, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port, debug=False)
