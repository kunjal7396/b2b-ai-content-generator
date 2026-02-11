# Setup Guide

This guide will walk you through setting up the AI Content Generator application.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd content-generator-app
```

## Step 2: Create a Virtual Environment (Recommended)

### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- Streamlit
- OpenAI
- SerpAPI
- TextRazor
- Sentence Transformers
- BeautifulSoup4
- And other dependencies

## Step 4: Obtain API Keys

### OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy and save your key securely

**Cost**: Pay-as-you-go. GPT-4 costs approximately $0.03-0.12 per 1K tokens depending on the model variant.

### SerpAPI Key

1. Go to [SerpAPI](https://serpapi.com/)
2. Sign up for an account
3. Navigate to Dashboard
4. Copy your API key

**Cost**: Free tier includes 100 searches/month. Paid plans start at $50/month for 5,000 searches.

### TextRazor API Key

1. Go to [TextRazor](https://www.textrazor.com/)
2. Sign up for an account
3. Navigate to Account section
4. Copy your API key

**Cost**: Free tier includes 500 requests/day. Pro plans start at $200/month.

## Step 5: Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Step 6: Using the Application

1. **Enter API Keys**: In the sidebar, enter your three API keys
2. **Configure Content Settings**:
   - Topic: What you want to write about
   - Tonality: Writing style
   - Context: Audience background
   - Theme: Core themes
   - Audience Persona: Target readers

3. **Click Generate Content**: The app will:
   - Search for top competing content
   - Analyze competitor structure
   - Extract key entities
   - Generate an outline
   - Write the full article
   - Refactor and polish

4. **Download Results**: Download your article as Markdown

## Optional: Google Docs Integration

To enable Google Docs export (currently disabled in the basic setup):

### Step 1: Enable Google APIs

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable the following APIs:
   - Google Docs API
   - Google Drive API

### Step 2: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Desktop app" as application type
4. Download the credentials JSON file

### Step 3: Configure Streamlit Secrets

Create `.streamlit/secrets.toml`:

```toml
[google_oauth]
client_id = "your-client-id.apps.googleusercontent.com"
client_secret = "your-client-secret"
redirect_uri = "http://localhost:8501"
```

### Step 4: Implement OAuth Flow

You'll need to add OAuth flow code to the app. See [Streamlit OAuth documentation](https://docs.streamlit.io/) for details.

## Troubleshooting

### Issue: Module not found errors
**Solution**: Make sure you've activated your virtual environment and installed all requirements

### Issue: API key errors
**Solution**: Double-check your API keys are correct and have not expired

### Issue: "gpt-5" model not found
**Solution**: The original code uses "gpt-5" which doesn't exist. The app has been updated to use "gpt-4", "gpt-4-turbo", or "gpt-3.5-turbo"

### Issue: Rate limiting errors
**Solution**: You may be hitting API rate limits. Wait a few minutes and try again, or upgrade your API plan

### Issue: Timeout errors during web scraping
**Solution**: Some websites may block automated requests. This is expected behavior and the app will skip problematic URLs

## Development

### Project Structure

```
content-generator-app/
├── app.py              # Main Streamlit application
├── utils.py            # Helper functions
├── requirements.txt    # Python dependencies
├── README.md          # Main documentation
├── SETUP.md           # This file
├── .gitignore         # Git ignore rules
└── .streamlit/        # Streamlit configuration
    ├── config.toml.example
    └── secrets.toml.example
```

### Running in Development Mode

```bash
streamlit run app.py --server.runOnSave true
```

This enables auto-reload when you save changes to the code.

## Deployment

### Deploy to Streamlit Cloud (Free)

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Select your repository
5. Add your API keys in "Advanced settings" → "Secrets"
6. Deploy!

### Deploy to Other Platforms

The app can also be deployed to:
- Heroku
- AWS EC2
- Google Cloud Run
- Azure App Service
- DigitalOcean

See the [Streamlit deployment documentation](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app) for platform-specific guides.

## Security Notes

⚠️ **Never commit API keys to version control**

- Always use `.gitignore` to exclude secrets
- Use environment variables or Streamlit secrets for API keys
- Rotate keys if accidentally exposed
- Use separate API keys for development and production

## Support

For issues:
1. Check this setup guide
2. Review the main README.md
3. Check API provider documentation
4. Open an issue on GitHub

## Next Steps

- Customize the style rules in `utils.py`
- Adjust the banned words list
- Modify the competitor selection algorithm
- Add custom entity extraction rules
- Implement Google Docs export
- Add analytics tracking
- Create custom templates
