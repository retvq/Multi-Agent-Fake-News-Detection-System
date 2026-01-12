# Fake News Detection AI

A multi-model AI system that analyzes news articles to detect potential misinformation.

## Quick Start

### 1. Install

```bash
# Clone and setup
git clone <repository-url>
cd "Multi-Agent Fake News Detection System"

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Add API Keys (Optional)

Create `.env` file in the project root:

```
HF_API_KEY=hf_your_key_here
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
```

> Works without API keys using heuristic-only mode.

### 3. Run

```bash
streamlit run app.py
```

Open http://localhost:8501

---

## How to Use

1. **Paste** your article text (50-5000 characters)
2. **Click** "Analyze Article"
3. **View** the verdict and confidence scores
4. **Download** the report as JSON

---

## Pipeline Architecture

![Flowchart](FlowChart.png)

[View PDF version](FlowChart.pdf)

---

## Models

| Model | Weight | Description |
|-------|--------|-------------|
| HuggingFace | 40% | Sentiment-based detection |
| Gemini/Groq | 35% | LLM reasoning |
| Heuristic | 25% | Pattern detection (always available) |

---

## Project Structure

```
├── app.py              # Main application
├── pages/              # Analytics, Monitoring, About
├── core/               # API clients, ensemble logic
├── components/         # UI components
└── tests/              # Unit tests
```

---

## Get API Keys

- **HuggingFace**: https://huggingface.co/settings/tokens
- **Google Gemini**: https://makersuite.google.com/app/apikey
- **Groq**: https://console.groq.com/

---

## Run Tests

```bash
python -m pytest tests/ -v
```

---

## Limitations

- AI can make mistakes - verify with trusted sources
- English text only
- Analyzes patterns, not factual claims

---

## License

MIT License
