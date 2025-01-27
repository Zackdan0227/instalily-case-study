import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from agents import plan_and_execute_agent  # ✅ Fixed import

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route('/chat', methods=['POST'])
def chat():
    """
    The main endpoint for your chatbot.
    Expects JSON: {"query": "<user's question>"}
    Returns JSON: {"response": "<chatbot answer>"}
    """
    data = request.get_json()
    user_query = data.get('query', '')

    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    response = plan_and_execute_agent(user_query)  # ✅ Fixed function call
    return jsonify({'response': response})

if __name__ == '__main__':
    # Flask dev server
    app.run(host='0.0.0.0', port=5001, debug=True)
