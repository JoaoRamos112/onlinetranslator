from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from googletrans import Translator
import pyttsx3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text')
    dest_language = data.get('language')

    translator = Translator()
    translated = translator.translate(text, dest=dest_language)
    return jsonify({'translated_text': translated.text})

@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get('text')

    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
