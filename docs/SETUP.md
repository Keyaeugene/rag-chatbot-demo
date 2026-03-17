# Setup Guide - RAG Chatbot

Complete step-by-step guide for setting up and deploying the Restaurant FAQ RAG Chatbot.

## Prerequisites

- **Python:** 3.10 or higher
- **Git:** For version control
- **OpenAI Account:** With API access and credits
- **Terminal/Command Line:** Basic familiarity

## Step 1: Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create new secret key**
5. Copy the key (you won't see it again!)
6. Keep it safe - never share or commit to git

## Step 2: Clone the Repository

```bash
git clone https://github.com/yourusername/rag-chatbot-demo.git
cd rag-chatbot-demo
```

## Step 3: Create Virtual Environment

### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

## Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Wait for all packages to install (may take 2-5 minutes).

## Step 5: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-key-here
LLM_MODEL=gpt-4
TEMPERATURE=0.7
MAX_TOKENS=1000
CHUNK_SIZE=500
CHUNK_OVERLAP=100
MAX_RETRIEVAL_RESULTS=3
DATA_FOLDER=data/
DEBUG=False
```

**Important:** Never commit `.env` to git!

## Step 6: Verify Setup

```bash
# Check Python version
python --version  # Should be 3.10+

# Check packages installed
pip list | grep langchain

# Test OpenAI connection (optional)
python -c "from src.llm_handler import LLMHandler; print('✅ OpenAI connection OK')"
```

## Step 7: Run the Chatbot

```bash
streamlit run app.py
```

You should see:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
```

Open http://localhost:8501 in your browser. The chatbot should be ready to use!

## Step 8: Test the Chatbot

Try asking these sample questions:

- "What are your operating hours?"
- "Do you have vegetarian options?"
- "What's the price of the Caesar salad?"
- "Can I make a reservation?"

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'langchain'"

**Solution:**
```bash
pip install -r requirements.txt
# Make sure your virtual environment is activated: source venv/bin/activate
```

### Issue: "OPENAI_API_KEY not found"

**Solution:**
```bash
# Check .env file exists
ls .env

# Verify API key is in .env
cat .env | grep OPENAI_API_KEY

# If not, add it: nano .env
```

### Issue: "Connection timeout" or "API Error"

**Solution:**
- Check your internet connection
- Verify API key is correct
- Confirm you have API credits: https://platform.openai.com/account/billing/overview
- Try restarting the app: Ctrl+C and `streamlit run app.py`

### Issue: "Slow responses"

**Solution:**
- Reduce `MAX_RETRIEVAL_RESULTS` in `.env` (try 2 instead of 3)
- Use `gpt-3.5-turbo` instead of `gpt-4` for faster but less accurate responses
- Reduce `CHUNK_SIZE` to 300

### Issue: "Vector store not found"

**Solution:**
```bash
# Delete and recreate embeddings
rm -rf embeddings/
# Restart the app - it will regenerate
streamlit run app.py
```

## Adding New Documents

1. Create a text file in the `data/` folder:
```bash
echo "Your content here" > data/my_document.txt
```

2. Reload the chatbot (click 🔄 in sidebar or restart)

3. The document will be automatically loaded and embedded

**Supported formats:**
- `.txt` - Plain text
- `.md` - Markdown
- `.pdf` - PDF files (requires PyPDF2)

## Deployment to Streamlit Cloud

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Add RAG chatbot"
git push origin main
```

**Don't forget:** `.env` should be in `.gitignore` (it is by default)

### Step 2: Create Streamlit Cloud Account

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Click **Sign up**
3. Choose GitHub as provider
4. Authorize Streamlit

### Step 3: Deploy

1. Click **New app**
2. Select your GitHub repo
3. Select branch (main)
4. Select file: `app.py`
5. Click **Deploy**

### Step 4: Add Secrets

1. Go to app settings (gear icon)
2. Click **Secrets**
3. Add your secrets:
```
OPENAI_API_KEY = sk-your-key-here
DEBUG = False
```

4. Deploy will restart automatically

Your app is now live! Share the URL with anyone.

## Deployment to AWS/GCP

### Docker Setup

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV OPENAI_API_KEY=${OPENAI_API_KEY}

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

Build and run:
```bash
docker build -t rag-chatbot .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-... rag-chatbot
```

### AWS Deployment

```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Use AWS App Runner or ECS to deploy the Docker container
```

## Development Commands

```bash
# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=src/

# Format code
black src/ app.py

# Lint code
pylint src/

# Type check
mypy src/
```

## Performance Tuning

### For Faster Responses:
```
LLM_MODEL=gpt-3.5-turbo  # Faster, slightly less accurate
TEMPERATURE=0.3          # More consistent responses
MAX_TOKENS=500          # Shorter responses
MAX_RETRIEVAL_RESULTS=2  # Fewer documents to process
```

### For More Accurate Responses:
```
LLM_MODEL=gpt-4          # Most accurate
TEMPERATURE=0.7          # More creative
CHUNK_SIZE=300          # Smaller chunks = better relevance
CHUNK_OVERLAP=50        # Less overlap = faster
```

## Monitoring

Check logs:
```bash
tail -f logs/chatbot.log
```

Monitor API usage:
https://platform.openai.com/account/usage/overview

## Security Best Practices

1. ✅ Keep `.env` in `.gitignore`
2. ✅ Rotate API keys regularly
3. ✅ Use separate API keys for dev/prod
4. ✅ Monitor API usage for anomalies
5. ✅ Update packages regularly: `pip install --upgrade -r requirements.txt`

## Maintenance

### Weekly:
- Check API usage
- Review logs for errors
- Test chatbot responses

### Monthly:
- Update dependencies: `pip list --outdated`
- Review and update documents
- Monitor cost

### Quarterly:
- Evaluate new LLM models
- Consider fine-tuning on domain data
- Performance optimization review

## Support & Help

- **LangChain:** https://python.langchain.com/docs/
- **Streamlit:** https://docs.streamlit.io/
- **OpenAI:** https://platform.openai.com/docs/
- **GitHub Issues:** [Report bugs here]

---

**Still stuck?** Check the README.md for FAQ or open a GitHub issue.