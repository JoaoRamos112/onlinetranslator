function translateText() {
    const text = document.getElementById('text-to-translate').value;
    const language = document.getElementById('language-select').value;

    fetch('/translate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text, language: language }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.translated_text) {
            document.getElementById('translated-text').value = data.translated_text;
        } else {
            console.error('Error:', data);
            alert('Error translating text. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error translating text. Please try again.');
    });
}

function speakText() {
    const text = document.getElementById('translated-text').value;

    fetch('/speak', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text }),
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.play();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error speaking text. Please try again.');
    });
}

function startRecognition() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'pt-PT';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.start();

    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        document.getElementById('text-to-translate').value = text;
    };

    recognition.onspeechend = function() {
        recognition.stop();
    };

    recognition.onerror = function(event) {
        console.error('Speech recognition error detected: ' + event.error);
    };
}

function uploadPDF() {
    const formData = new FormData(document.getElementById('upload-form'));

    fetch('/upload_pdf', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const link = document.getElementById('download-link');
        link.href = url;
        link.download = 'translated.pdf';
        link.style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error uploading PDF. Please try again.');
    });
}
