from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_session import Session 
import urllib.request
import json
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def allowSelfSignedHttps(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True)

# GRO Chatbot Setup
def get_chat_response(question):
    api_chat_history = []

    for chat in session['chat_history']:
        if chat.get('type') == 'user':
            api_chat_history.append({ "inputs": { "question": chat.get('text')}})
        elif chat.get('type') == 'bot':
            api_chat_history.append({ "outputs": { "answer": chat.get('text')}})
        
    data = {"chat_history": [], "question": question}
    body = str.encode(json.dumps(data))

    url = os.getenv('URL')
    api_key = os.getenv('KEY')
    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': os.getenv('DEPLOYMENT') }

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        return json.loads(result)
    except urllib.error.HTTPError as error:
        print("Request failed with status code: " + str(error.code))
        return {"error": error.read().decode("utf8", 'ignore')}

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'chat_history' not in session:
            session['chat_history'] = []

    if request.method == 'POST':
        question = request.form.get('question')

        response = get_chat_response(question)

        session['chat_history'].append({'type': 'user', 'text': question})
        session['chat_history'].append({'type': 'bot', 'text': response.get('answer')})
        session.modified = True

        return jsonify(session['chat_history'])
    
    return render_template('index.html')

@app.route('/clear', methods=['GET'])
def clear():
    session.pop('chat_history', None)
    return redirect(url_for('index'))

# Reed Chatbot Setup
def get_chat_response_reed(question):
    api_chat_history = []

    for chat in session['chat_history_reed']:
        if chat.get('type') == 'user':
            api_chat_history.append({ "inputs": { "question": chat.get('text')}})
        elif chat.get('type') == 'bot':
            api_chat_history.append({ "outputs": { "answer": chat.get('text')}})
        
    data = {"chat_history": [], "question": question}
    body = str.encode(json.dumps(data))

    url = os.getenv('REED_URL')
    api_key = os.getenv('REED_KEY')
    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': os.getenv('REED_DEPLOYMENT') }

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        return json.loads(result)
    except urllib.error.HTTPError as error:
        print("Request failed with status code: " + str(error.code))
        return {"error": error.read().decode("utf8", 'ignore')}

@app.route('/reed', methods=['GET', 'POST'])
def reed():
    if 'chat_history_reed' not in session:
            session['chat_history_reed'] = []

    if request.method == 'POST':
        question = request.form.get('question')

        response = get_chat_response_reed(question)

        session['chat_history_reed'].append({'type': 'user', 'text': question})
        session['chat_history_reed'].append({'type': 'bot', 'text': response.get('answer')})
        session.modified = True

        return jsonify(session['chat_history_reed'])
    
    return render_template('reed.html')

@app.route('/clear_reed', methods=['GET'])
def clear_reed():
    session.pop('chat_history_reed', None)
    return redirect(url_for('reed'))

if __name__ == '__main__':
    app.run(debug=True)
