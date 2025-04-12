document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('prompt-form');
    const input = document.getElementById('prompt-input');
    const resultContainer = document.getElementById('result-container');
    const loader = document.getElementById('loader');
    const submitButton = form.querySelector('button[type="submit"]');

    let socket;

    function appendMessage(text, type = 'http') {
        const p = document.createElement("p");
        p.textContent = type === 'ws'
            ? `[🔁 AI Real-Time]: ${text}`
            : `[📡 AI HTTP]: ${text}`;
        p.className = type === 'ws' ? "ws-response" : "http-response";
        resultContainer.appendChild(p);
    }

    function initializeWebSocket() {
        socket = new WebSocket("ws://localhost:8000/ws");

        socket.onopen = () => {
            console.log("✅ WebSocket connected");
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            appendMessage(data.text, 'ws');
        };

        socket.onerror = (err) => {
            console.error("❌ WebSocket error:", err);
        };

        socket.onclose = () => {
            console.warn("⚠️ WebSocket closed, retrying in 3s...");
            setTimeout(initializeWebSocket, 3000); // retry connection
        };
    }

    initializeWebSocket(); // Kick off WebSocket

    // 🚀 Handle form submission (HTTP + WS hybrid)
    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        const userInput = input.value.trim();

        if (!userInput) {
            alert('Please enter a prompt.');
            return;
        }

        loader.style.display = 'block';
        resultContainer.innerHTML = '';
        submitButton.disabled = true;

        // 🔁 Try WebSocket send
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(userInput);
        }

        // 📡 HTTP fallback / secondary
        try {
            const response = await fetch('http://localhost:8000/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: userInput })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Network error');
            }

            const data = await response.json();
            appendMessage(data.result || 'No result received.', 'http');
        } catch (error) {
            appendMessage(`❌ ${error.message}`, 'http');
        } finally {
            loader.style.display = 'none';
            submitButton.disabled = false;
            input.value = '';
        }
    });

    // 💡 Shift+Enter → WebSocket only
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && e.shiftKey) {
            e.preventDefault();
            const msg = input.value.trim();
            if (msg && socket.readyState === WebSocket.OPEN) {
                socket.send(msg);
                input.value = '';
            }
        }
    });
});
