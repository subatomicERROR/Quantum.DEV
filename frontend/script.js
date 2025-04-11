document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prompt-form');
    const input = document.getElementById('prompt-input');
    const resultContainer = document.getElementById('result-container');
    const loader = document.getElementById('loader');
    const submitButton = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const userInput = input.value.trim();

        if (!userInput) {
            alert('Please enter a prompt.');
            return;
        }

        // Show loader and disable submit button
        loader.style.display = 'block';
        resultContainer.innerHTML = '';
        submitButton.disabled = true;

        try {
            const response = await fetch('http://localhost:8000/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt: userInput })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Network response was not ok');
            }

            const data = await response.json();
            resultContainer.innerHTML = data.result || 'No result received.';
        } catch (error) {
            resultContainer.innerHTML = 'Error: ' + error.message;
        } finally {
            // Hide loader and re-enable submit button
            loader.style.display = 'none';
            submitButton.disabled = false;
        }
    });
});