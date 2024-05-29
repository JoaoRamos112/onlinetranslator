document.getElementById('translate-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const text = document.getElementById('text-input').value;
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
            alert('Erro na tradução: ' + data.error);
        }
    })
    .catch(error => console.error('Error:', error));
});

document.getElementById('speak-button').addEventListener('click', function() {
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
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.play();
    })
    .catch(error => console.error('Error:', error));
});

document.getElementById('pdf-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData();
    const fileInput = document.getElementById('pdf-file');
    const language = document.getElementById('language').value;

    formData.append('file', fileInput.files[0]);
    formData.append('language', language);

    fetch('/upload_pdf', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'translated.pdf';
        a.click();
    })
    .catch(error => console.error('Error:', error));
});

document.getElementById('record-button').addEventListener('click', function() {
    const recordButton = this;
    const textInput = document.getElementById('text-input');
    const languageSelect = document.getElementById('language-select');

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'pt-PT';
    recognition.interimResults = false;

    recognition.onstart = function() {
        recordButton.disabled = true;
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        textInput.value = transcript;

        fetch('/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: transcript, language: languageSelect.value }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.translated_text) {
                document.getElementById('translated-text').value = data.translated_text;
            } else {
                alert('Erro na tradução: ' + data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    };

    recognition.onerror = function(event) {
        console.error('Error occurred in recognition: ' + event.error);
    };

    recognition.onend = function() {
        recordButton.disabled = false;
    };

    recognition.start();
});
