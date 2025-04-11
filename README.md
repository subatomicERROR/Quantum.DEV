# README for quantum.dev

## Overview

Welcome to **quantum.dev**, a quantum-AI development environment designed to facilitate rapid application development using Hugging Face's powerful AI models. This project aims to create a lightweight, modular, and efficient workspace that allows developers to generate applications from simple prompts.

## Project Structure

The project is organized as follows:

```
quantum.dev
├── backend
│   ├── main.py            # FastAPI backend service
│   ├── .env               # Environment variables (HF_TOKEN)
│   ├── requirements.txt   # Python dependencies
│   └── Procfile           # Heroku deployment configuration
├── frontend
│   ├── index.html         # Frontend HTML structure
│   └── script.js          # JavaScript for frontend interactions
├── vercel.json            # Vercel deployment configuration
├── replit.nix             # Replit runtime configuration
├── .gitignore             # Git ignore rules
├── README.md              # Project documentation
└── copilot-prompt.txt     # Project blueprint and guidelines
```

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- Node.js (for frontend development)
- A Hugging Face account to obtain your API key

### Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourname/quantum.dev
   cd quantum.dev/backend
   ```

2. Create a `.env` file in the `backend` directory and add your Hugging Face API token:
   ```
   HF_TOKEN=your_huggingface_api_key
   ```

3. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the FastAPI backend:
   ```
   python3 -m uvicorn main:app --reload
   ```

### Frontend Setup

1. Open `frontend/index.html` in your web browser to access the application interface.

2. Type your prompt in the input box and submit to receive AI-generated outputs.

## Deployment

### Vercel

To deploy the frontend on Vercel, ensure you have a `vercel.json` file configured for API rewrites.

### Replit

You can also run the entire application on Replit by using the provided `replit.nix` configuration.

## Contributing

Feel free to contribute to the project by submitting issues or pull requests. Your feedback and contributions are welcome!

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

Special thanks to Hugging Face for providing the AI models and FastAPI for the backend framework.