document.addEventListener('DOMContentLoaded', function () {
    const recordBtn = document.getElementById('record-btn');
    const translateBtn = document.getElementById('translate-btn');
    const speakBtn = document.getElementById('speak-btn');
    const recordedText = document.getElementById('recorded-text');
    const translatedText = document.getElementById('translated-text');
    const languages = document.getElementById('languages');

    recordBtn.addEventListener('click', () => {
        // Gravação de áudio (este é um exemplo simples e não funcional)
        alert('Gravação de áudio não implementada.');
    });

    translateBtn.addEventListener('click', () => {
        const text = recordedText.value;
        const language = languages.value;

        fetch('/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text, language: language }),
        })
        .then(response => response.json())
        .then(data => {
            translatedText.value = data.translated_text;
        })
        .catch(error => console.error('Erro:', error));
    });

    speakBtn.addEventListener('click', () => {
        const text = translatedText.value;

        fetch('/speak', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text }),
        })
        .catch(error => console.error('Erro:', error));
    });
});
