# Amber AI Assistant

Amber is a versatile AI chatbot that connects to multiple Large Language Models (LLMs) including OpenAI, Google Gemini, DeepSeek, Anthropic, and local Ollama models. Built with Streamlit, it provides a clean and intuitive interface for AI interactions.

## Features
- Multi-model support (OpenAI, Google Gemini, DeepSeek, Anthropic, Ollama)
- Automatic chat title generation
- Persistent chat history
- Easy navigation between past conversations
- Local model auto-detection (Ollama)
- Clean, intuitive user interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/amber.git
cd amber
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your API keys:
```
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
```

## Usage

Run the application:
```bash
streamlit run main.py
```

The application will be available at `http://localhost:8501`

## Project Structure
```
amber/
├── config.py           # Configuration settings
├── database.py        # Database management
├── main.py           # Main Streamlit application
├── router.py         # Model routing logic
├── requirements.txt  # Project dependencies
├── .env             # API keys (create this)
└── models/          # Model implementations
    ├── __init__.py
    ├── base_model.py
    ├── openai_model.py
    ├── ollama_model.py
    └── other_models.py
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.