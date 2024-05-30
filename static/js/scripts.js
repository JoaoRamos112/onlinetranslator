document.getElementById('translate-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const textInput = document.getElementById('text-input').value;
    const languageSelect = document.getElementById('language-select').value;

    try {
        const response = await fetch('/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: textInput,
                language: languageSelect,
            }),
        });

        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }

        document.getElementById('translated-text').value = data.translated_text;
    } catch (error) {
        alert('Erro na tradução: ' + error.message);
    }
});

document.getElementById('pdf-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData();
    const pdfFile = document.getElementById('pdf-file').files[0];
    const language = document.getElementById('language').value;

    formData.append('file', pdfFile);
    formData.append('language', language);

    try {
        const response = await fetch('/upload_pdf', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Erro ao traduzir PDF');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'translated.pdf';
        document.getElementById('translated-pdf').appendChild(a);
        a.click();
        a.remove();
    } catch (error) {
        alert('Erro na tradução do PDF: ' + error.message);
    }
});

const recordButton = document.getElementById('record-button');
const textInput = document.getElementById('text-input');

recordButton.addEventListener('click', () => {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'pt-PT'; // Set the language to Portuguese (Portugal)
    recognition.interimResults = false;

    recognition.onstart = function () {
        console.log('Recording...');
    };

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        textInput.value = transcript;
    };

    recognition.onerror = function (event) {
        alert('Erro no reconhecimento de fala: ' + event.error);
    };

    recognition.onend = function () {
        console.log('Recording ended.');
    };

    recognition.start();
});

function speak(text) {
    fetch('/speak', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: text })
    })
   .then(response => response.blob())
   .then(blob => {
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        audio.play();
    })
   .catch(error => console.error(error));
}

document.getElementById('speak-button').addEventListener('click', async function () {
    const textToSpeak = document.getElementById('translated-text').value;

    try {
        const response = await fetch('/speak', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: textToSpeak,
            }),
        });

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.play();
    } catch (error) {
        alert('Erro na reprodução: ' + error.message);
    }
});
