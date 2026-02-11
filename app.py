import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from utils import (
    serp_top_organic,
    select_similar,
    extract_headings,
    extract_entities,
    has_long_paragraph,
    get_style_rules,
    call_llm,
    create_outline_prompt,
    create_article_prompt,
    create_refactor_prompt,
    create_polish_prompt
)
from google_auth import (
    get_credentials,
    create_google_doc,
    is_authenticated,
    logout
)

# Page config
st.set_page_config(
    page_title="AI Content Generator",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if 'article' not in st.session_state:
    st.session_state.article = None
if 'outline' not in st.session_state:
    st.session_state.outline = None

st.title("📝 AI-Powered Content Generator")
st.markdown("Generate SEO-optimized, competitor-analyzed content")

# Sidebar for API keys and configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Keys
    st.subheader("API Keys")
    openai_api_key = st.text_input("OpenAI API Key", type="password", help="Your OpenAI API key")
    serpapi_key = st.text_input("SerpAPI Key", type="password", help="Your SerpAPI key")
    textrazor_key = st.text_input("TextRazor API Key", type="password", help="Your TextRazor API key")
    
    st.divider()
    
    # Search parameters
    st.subheader("Search Parameters")
    gl = st.text_input("Country Code (GL)", value="us", help="Google country code")
    hl = st.text_input("Language (HL)", value="en", help="Google language code")
    
    st.divider()
    
    # Model selection
    st.subheader("AI Model")
    model_choice = st.selectbox(
        "OpenAI Model",
        ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        help="Select the OpenAI model to use"
    )
    
    st.divider()
    
    # Google Authentication
    st.subheader("📤 Google Docs")
    
    if is_authenticated():
        st.success("✓ Connected to Google")
        if st.button("Disconnect", use_container_width=True):
            logout()
            st.rerun()
    else:
        st.info("Not connected")
        if st.button("🔗 Connect Google Account", use_container_width=True):
            with st.spinner("Authenticating..."):
                creds = get_credentials()
                if creds:
                    st.success("✓ Successfully authenticated!")
                    st.rerun()
                else:
                    st.error("⚠️ Authentication failed. Make sure credentials.json exists in the project folder.")
                    with st.expander("How to setup Google OAuth"):
                        st.markdown("""
                        1. Go to [Google Cloud Console](https://console.cloud.google.com)
                        2. Create a new project
                        3. Enable Google Docs API and Google Drive API
                        4. Create OAuth 2.0 credentials (Desktop app)
                        5. Download as `credentials.json`
                        6. Place it in the app folder
                        7. Click 'Connect Google Account' again
                        """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Content Settings")
    
    topic = st.text_input(
        "Topic",
        value="What Is Streaming Analytics",
        help="The main topic for your article"
    )
    
    tonality = st.text_area(
        "Tonality",
        value="Clear, direct, neutral, factual.",
        height=70,
        help="Desired tone of the article"
    )
    
    context = st.text_area(
        "Context",
        value="Written for experienced professionals. Assume baseline domain knowledge. The audience is data engineers",
        height=70,
        help="Context about the target audience"
    )
    
    theme = st.text_area(
        "Theme",
        value="Clarity, accuracy, practical understanding.",
        height=70,
        help="Core themes to emphasize"
    )
    
    audience_persona = st.text_input(
        "Audience Persona",
        value="Senior practitioners, decision-makers, technical leaders",
        help="Description of the target reader"
    )

with col2:
    st.header("Style Rules")
    st.markdown("""
    **Global Rules:**
    - One H1 only
    - Each H2 starts with framing paragraph
    - 2-5 H3 subsections per H2
    - Max 120 words per paragraph
    
    **Content:**
    - Bullets for lists/features
    - Tables for comparisons
    - FAQs: max 3 lines per answer
    - No marketing language
    """)

# Banned words
banned_words = [
    "remarkable", "ground breaking", "excitingly", "revolutionize",
    "transformative", "unrivaled", "game-changer", "cutting-edge",
    "next-level", "unlock", "seamless", "synergy"
]

# Helper functions
@st.cache_resource
def load_embedding_model():
    """Load and cache the sentence transformer model"""
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Main generate button
if st.button("🚀 Generate Content", type="primary", use_container_width=True):
    # Validate API keys
    if not all([openai_api_key, serpapi_key, textrazor_key]):
        st.error("❌ Please provide all API keys in the sidebar")
    elif not topic.strip():
        st.error("❌ Please enter a topic")
    else:
        try:
            with st.spinner("Generating content..."):
                # Initialize clients
                client = OpenAI(api_key=openai_api_key)
                embed_model = load_embedding_model()
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Get SERP results
                status_text.text("🔍 Searching top organic results...")
                progress_bar.progress(10)
                top10 = serp_top_organic(topic, serpapi_key, gl, hl)
                
                if not top10:
                    st.error("No search results found. Please check your topic and API key.")
                    st.stop()
                
                st.success(f"✓ Found {len(top10)} results")
                progress_bar.progress(20)
                
                # Step 2: Select similar URLs
                status_text.text("🎯 Selecting most relevant competitors...")
                selected_urls = select_similar(topic, top10, embed_model, k=3)
                
                if not selected_urls:
                    st.warning("Could not find suitable competitor URLs. Proceeding with available data.")
                else:
                    st.success(f"✓ Selected {len(selected_urls)} URLs for analysis")
                
                progress_bar.progress(30)
                
                # Display selected URLs
                with st.expander("📊 Selected Competitor URLs"):
                    for i, url in enumerate(selected_urls, 1):
                        st.write(f"{i}. [{url.get('title', 'No title')}]({url.get('link', '#')})")
                
                # Step 3: Extract headings
                status_text.text("📋 Extracting competitor outlines...")
                competitor_outlines = []
                for r in selected_urls:
                    headings = extract_headings(r["link"])
                    competitor_outlines.append({
                        "url": r["link"],
                        "headings": headings
                    })
                
                st.success("✓ Outlines extracted")
                progress_bar.progress(40)
                
                # Step 4: Extract entities
                status_text.text("🏷️ Analyzing key entities...")
                must_include_entities = extract_entities(selected_urls, textrazor_key)
                
                if must_include_entities:
                    st.success(f"✓ Found {len(must_include_entities)} key entities")
                else:
                    st.info("No entities extracted. Proceeding without entity requirements.")
                    must_include_entities = []
                
                progress_bar.progress(50)
                
                with st.expander("🔑 Key Entities"):
                    if must_include_entities:
                        st.write(must_include_entities)
                    else:
                        st.write("No entities found")
                
                # Step 5: Generate outline
                status_text.text("✍️ Generating content outline...")
                style_rules = get_style_rules(tonality, context, theme, audience_persona, banned_words)
                
                outline_prompt = create_outline_prompt(
                    topic, tonality, context, theme, style_rules,
                    competitor_outlines, must_include_entities
                )
                
                outline = call_llm(outline_prompt, client, model_choice)
                st.session_state.outline = outline
                st.success("✓ Outline generated")
                progress_bar.progress(60)
                
                with st.expander("📝 Content Outline"):
                    st.markdown(outline)
                
                # Step 6: Generate article
                status_text.text("📄 Writing full article...")
                article_prompt = create_article_prompt(
                    topic, audience_persona, style_rules,
                    must_include_entities, outline
                )
                
                article = call_llm(article_prompt, client, model_choice)
                st.success("✓ Article generated")
                progress_bar.progress(75)
                
                # Step 7: Refactor if needed
                if has_long_paragraph(article):
                    status_text.text("🔧 Refactoring long paragraphs...")
                    refactor_prompt = create_refactor_prompt(article)
                    article = call_llm(refactor_prompt, client, model_choice)
                    st.success("✓ Paragraphs refactored")
                
                progress_bar.progress(85)
                
                # Step 8: Final polish
                status_text.text("✨ Polishing content...")
                polish_prompt = create_polish_prompt(article)
                article = call_llm(polish_prompt, client, model_choice)
                
                st.session_state.article = article
                progress_bar.progress(100)
                status_text.text("✅ Content generation complete!")
                
                st.balloons()
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

# Display generated content
if st.session_state.article:
    st.markdown("---")
    st.header("📄 Generated Article")
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.download_button(
            "⬇️ Download Markdown",
            st.session_state.article,
            file_name=f"{topic.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col2:
        st.download_button(
            "⬇️ Download Outline",
            st.session_state.outline if st.session_state.outline else "No outline available",
            file_name=f"{topic.replace(' ', '_')}_outline.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col3:
        # Google Docs Export
        if is_authenticated():
            if st.button("📤 Export to Google Docs", use_container_width=True):
                with st.spinner("Creating Google Doc..."):
                    creds = get_credentials()
                    if creds:
                        doc_id, doc_url = create_google_doc(
                            topic,
                            st.session_state.article,
                            creds
                        )
                        if doc_url:
                            st.success("✓ Document created!")
                            st.markdown(f"**[Open in Google Docs]({doc_url})**")
                            # Store in session state to show link persistently
                            st.session_state.google_doc_url = doc_url
                        else:
                            st.error("Failed to create document")
                    else:
                        st.error("Not authenticated. Please connect your Google account.")
        else:
            st.button("📤 Export to Google Docs", use_container_width=True, disabled=True, 
                     help="Connect your Google account in the sidebar first")
    
    with col4:
        # Word count
        word_count = len(st.session_state.article.split())
        st.metric("Word Count", f"{word_count:,}")
    
    # Show persistent Google Doc link if exists
    if 'google_doc_url' in st.session_state and st.session_state.google_doc_url:
        st.info(f"📄 Google Doc: [{topic}]({st.session_state.google_doc_url})")
    
    # Clear button
    if st.button("🔄 Clear All", use_container_width=False):
        st.session_state.article = None
        st.session_state.outline = None
        if 'google_doc_url' in st.session_state:
            del st.session_state.google_doc_url
        st.rerun()
    
    # Display the article
    st.markdown("---")
    st.markdown(st.session_state.article)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>Built with Streamlit • Powered by OpenAI, SerpAPI & TextRazor</p>
    <p style="font-size: 0.8em;">Always review and fact-check generated content before publication</p>
</div>
""", unsafe_allow_html=True)
