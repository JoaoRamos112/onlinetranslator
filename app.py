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
from flask import Flask, render_template, request, jsonify, send_file
import requests
import uuid
import pyttsx3
import os
from PyPDF2 import PdfReader
from fpdf import FPDF

app = Flask(__name__)

# Configurações da API do Azure
subscription_key = 'YOUR_AZURE_TRANSLATOR_KEY'
endpoint = 'https://api.cognitive.microsofttranslator.com'
location = 'YOUR_RESOURCE_LOCATION'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text')
    dest_language = data.get('language')

    translated_text = translate_text(text, dest_language)

    return jsonify({'translated_text': translated_text})


@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get('text')

    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    return '', 204


@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = os.path.join('uploads', file.filename)
        file.save(filename)

        dest_language = request.form.get('language')
        translated_text = translate_pdf(filename, dest_language)

        translated_pdf_path = create_translated_pdf(translated_text)

        return send_file(translated_pdf_path, as_attachment=True)

    return jsonify({'error': 'Invalid file type'}), 400


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}


def translate_text(text, dest_language):
    path = '/translate'
    constructed_url = endpoint + path

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{
        'text': text
    }]

    params = {
        'api-version': '3.0',
        'to': [dest_language]
    }

    response = requests.post(constructed_url, params=params, headers=headers, json=body)
    response_json = response.json()
    translated_text = response_json[0]['translations'][0]['text']

    return translated_text


def translate_pdf(file_path, dest_language):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() + "\n"

    translated_text = translate_text(text, dest_language)
    return translated_text


def create_translated_pdf(translated_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in translated_text.split('\n'):
        pdf.multi_cell(0, 10, txt=line)

    translated_pdf_path = os.path.join('uploads', 'translated.pdf')
    pdf.output(translated_pdf_path)
    return translated_pdf_path


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=8080)
