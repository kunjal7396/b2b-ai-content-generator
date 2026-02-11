# AI Content Generator

An AI-powered content generation tool that analyzes competitor content, extracts key entities, and generates SEO-optimized articles based on industry best practices.

## Features

- 🔍 **SERP Analysis**: Automatically fetches and analyzes top-ranking content
- 🎯 **Competitor Research**: Selects most relevant competitors using semantic similarity
- 🏷️ **Entity Extraction**: Identifies key entities to include in your content
- ✍️ **AI Content Generation**: Creates structured, professional articles using GPT-5
- 📊 **Style Enforcement**: Ensures consistent formatting and quality standards
- 📤 **Google Docs Export**: Export generated content directly to Google Docs (requires setup)

## Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd content-generator-app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get API Keys

You'll need the following API keys:

- **OpenAI API Key**: [Get it here](https://platform.openai.com/api-keys)
- **SerpAPI Key**: [Get it here](https://serpapi.com/)
- **TextRazor API Key**: [Get it here](https://www.textrazor.com/)

### 4. Run the Application

```bash
streamlit run app.py
```

## Usage

### Basic Workflow

1. **Configure API Keys**: Enter your API keys in the sidebar
2. **Set Content Parameters**:
   - Topic: Main subject of your article
   - Tonality: Desired writing style
   - Context: Audience context and knowledge level
   - Theme: Core themes to emphasize
   - Audience Persona: Target reader description

3. **Generate Content**: Click "Generate Content" button
4. **Review & Export**: Download as Markdown or export to Google Docs

### Content Settings

#### Default Configuration

The app comes pre-configured with professional defaults suitable for technical content:

- **Tonality**: Clear, direct, neutral, factual
- **Context**: Written for experienced professionals with baseline domain knowledge
- **Theme**: Clarity, accuracy, practical understanding
- **Audience**: Senior practitioners, decision-makers, technical leaders

You can modify these settings based on your specific needs.

### Style Rules

The generator enforces strict style rules:

- One H1 heading only
- Each H2 starts with a framing paragraph (60-90 words)
- 2-5 H3 subsections per H2
- Maximum 120 words per paragraph
- Bullets for lists, features, and steps
- Tables for comparisons and mappings
- Non-opinionated FAQs (max 3 lines per answer)

### Banned Words

The following marketing buzzwords are automatically filtered:
- remarkable, ground breaking, excitingly, revolutionize
- transformative, unrivaled, game-changer, cutting-edge
- next-level, unlock, seamless, synergy

## Google Docs Integration

### Setup OAuth (Optional)

To enable Google Docs export:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable Google Docs API and Google Drive API
4. Create OAuth 2.0 credentials (Desktop app type)
5. Download the credentials JSON file
6. Create `.streamlit/secrets.toml`:

```toml
[google_oauth]
client_id = "your-client-id"
client_secret = "your-client-secret"
redirect_uri = "http://localhost:8501"
```

**Note**: For deployed apps, update the redirect URI accordingly.

## Project Structure

```
content-generator-app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore file
└── .streamlit/           # Streamlit configuration (create as needed)
    └── secrets.toml      # API keys and secrets (not in repo)
```

## Configuration

### Search Parameters

- **GL (Country Code)**: Default is "us" (United States)
- **HL (Language)**: Default is "en" (English)

These can be modified in the sidebar to target different regions or languages.

## How It Works

1. **SERP Analysis**: Fetches top 10 organic results for your topic
2. **Similarity Filtering**: Selects 3 most relevant competitors using semantic embeddings
3. **Content Analysis**: Extracts heading structure from competitor pages
4. **Entity Extraction**: Uses TextRazor to identify key entities with relevance scoring
5. **Outline Generation**: Creates a structured outline based on competitor analysis
6. **Content Writing**: Generates full article following style rules
7. **Refinement**: Automatically refactors long paragraphs and polishes content
8. **Quality Check**: Removes banned words and ensures compliance with style guide

## Troubleshooting

### Common Issues

**Issue**: API key errors
- **Solution**: Ensure all three API keys are correctly entered in the sidebar

**Issue**: "gpt-5" model not found
- **Solution**: The code uses `gpt-5` - update to `gpt-4` or your preferred model in `app.py`

**Issue**: Timeout errors during web scraping
- **Solution**: Some websites may block requests; the app will skip them and continue

**Issue**: Google OAuth errors
- **Solution**: Ensure redirect URIs match in Google Cloud Console and your app config

## Customization

### Modifying Style Rules

Edit the `get_style_rules()` function in `app.py` to adjust content guidelines.

### Changing the Number of Competitors

Modify the `k=3` parameter in the `select_similar()` function call to analyze more or fewer competitors.

### Adjusting Entity Threshold

Change `e.relevance_score >= 0.2` in `extract_entities()` to be more or less selective.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for your own purposes.

## Disclaimer

This tool is for content research and generation assistance. Always review and fact-check generated content before publication. Ensure compliance with your organization's content guidelines and policies.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation for the individual APIs used
- Review Streamlit documentation at [docs.streamlit.io](https://docs.streamlit.io)
