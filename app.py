from flask import Flask, render_template, request, jsonify, send_file
import requests
import uuid
import os
from PyPDF2 import PdfReader
from fpdf import FPDF
import azure.cognitiveservices.speech as speechsdk
import redis

app = Flask(__name__)

# Configurações da API do Azure
subscription_key = '683d4d5e89244d31b649623d60c684ff'
endpoint = 'https://api.cognitive.microsofttranslator.com'
location = 'francecentral'

# Configurações do Azure Speech
speech_key = '9cad95fdff5449f2bd01335c5b840dcc'
speech_region = 'eastus'

# Configurações do Azure Redis
redis_host = 'translatorcn.redis.cache.windows.net'
redis_port = 6379
redis_password = 'QruzOK0wvBVyH96TnipvG3BNYSeSN9YDWAzCaHucXiI='


def get_redis_client():
    return redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)


@app.route('/')
def index():
    app.logger.info('Index page accessed')
    return render_template('index.html')

#POST da tradução
@app.route('/translate', methods=['POST'])
def translate():
    app.logger.info('Translate endpoint accessed')
    try:
        data = request.get_json()
        text = data.get('text')
        dest_language = data.get('language')

        if not dest_language:
            raise ValueError("Destination language is required")

        app.logger.debug(f'Translating text: {text} to {dest_language}')

        cached_translation = get_translation_from_cache(text, dest_language)
        if cached_translation:
            app.logger.debug(f'Cache hit: {cached_translation}')
            return jsonify({'translated_text': cached_translation})

        translated_text = translate_text(text, dest_language)

        save_translation_to_cache(text, translated_text, dest_language)

        return jsonify({'translated_text': translated_text})
    except Exception as e:
        app.logger.error(f'Error translating text: {str(e)}')
        return jsonify({'error': str(e)}), 500


#POST do text-to-Speech
@app.route('/speak', methods=['POST'])
def speak():
    try:
        data = request.get_json()
        text = data.get('text')

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        speech_config.speech_synthesis_voice_name = 'en-US-AvaNeural'

        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

        app.logger.debug(f'Generating speech for text: {text}')
        result = speech_synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            audio_data = result.audio
            return send_audio(audio_data)
        else:
            app.logger.error(f"Speech synthesis failed: {result.error_details}")
            return jsonify({'error': result.error_details}), 500
    except Exception as e:
        app.logger.error(f'Error generating speech: {str(e)}')
        return jsonify({'error': str(e)}), 500

        
#POST da tradução do PDF
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    app.logger.info('Upload PDF endpoint accessed')
    try:
        if 'file' not in request.files:
            app.logger.error('No file part in the request')
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        if file.filename == '':
            app.logger.error('No selected file')
            return jsonify({'error': 'No selected file'}), 400

        dest_language = request.form.get('language')

        if not dest_language:
            app.logger.error('Destination language is required')
            return jsonify({'error': 'Destination language is required'}), 400

        if file and allowed_file(file.filename):
            filename = os.path.join('uploads', file.filename)
            file.save(filename)

            app.logger.debug(f'Translating PDF file: {filename} to {dest_language}')
            translated_text = translate_pdf(filename, dest_language)

            translated_pdf_path = create_translated_pdf(translated_text)
            app.logger.debug(f'Translated PDF saved to: {translated_pdf_path}')

            return send_file(translated_pdf_path, as_attachment=True)

        app.logger.error('Invalid file type')
        return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        app.logger.error(f'Error uploading and translating PDF: {str(e)}')
        return jsonify({'error': str(e)}), 500
   
    

def send_audio(audio_data):
    response = make_response(audio_data)
    response.headers['Content-Type'] = 'audio/wav'
    response.headers['Content-Disposition'] = 'inline; filename="audio.wav"'
    return response

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

    app.logger.debug(f'Sending translation request: {constructed_url} with params: {params} and body: {body}')
    response = requests.post(constructed_url, params=params, headers=headers, json=body)
    response_json = response.json()

    if response.status_code != 200 or 'translations' not in response_json[0]:
        raise ValueError(f"Translation API error: {response_json}")

    translated_text = response_json[0]['translations'][0]['text']

    app.logger.debug(f'Received translated text: {translated_text}')
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
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in translated_text.split('\n'):
        pdf.multi_cell(0, 10, txt=line.encode('latin-1', 'replace').decode('latin-1'))

    translated_pdf_path = os.path.join('uploads', 'translated.pdf')
    pdf.output(translated_pdf_path, 'F')
    return translated_pdf_path


def save_translation_to_cache(text, translated_text, dest_language):
    client = get_redis_client()
    key = f"{text}:{dest_language}"
    client.set(key, translated_text)


def get_translation_from_cache(text, dest_language):
    client = get_redis_client()
    key = f"{text}:{dest_language}"
    return client.get(key)


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=8080)
