## ⚡ Quick Start

Get PixelRAG running locally in a few steps.

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/PixelRAG.git
cd PixelRAG
```

### 2. Create and activate a virtual environment

**Windows:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_api_key_here
```

> Keep your API keys private and never commit `.env` to GitHub.

### 5. Run PixelRAG

```bash
streamlit run app.py
```

If your application entry point is located inside the `app` directory:

```bash
streamlit run app/app.py
```

### 6. Start using PixelRAG

1. Upload a supported document.
2. Wait for document processing and indexing to complete.
3. Enter a question about the document.
4. PixelRAG retrieves the most relevant content using vector similarity search.
5. The generative model uses the retrieved context to produce the answer.

**That's it — upload a document and start asking questions.** 🚀
