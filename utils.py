"""
Utility functions for the AI Content Generator
"""

import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from serpapi import GoogleSearch
import textrazor
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def serp_top_organic(topic, api_key, gl="us", hl="en", num=10):
    """
    Fetch top organic search results for a given topic
    
    Args:
        topic (str): Search query
        api_key (str): SerpAPI key
        gl (str): Country code
        hl (str): Language code
        num (int): Number of results to return
        
    Returns:
        list: Top organic search results
    """
    params = {
        "engine": "google",
        "q": topic,
        "api_key": api_key,
        "gl": gl,
        "hl": hl,
        "num": num
    }
    res = GoogleSearch(params).get_dict()
    return res.get("organic_results", [])[:num]


def is_docs_domain(url):
    """
    Check if URL is a documentation domain (to filter out)
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if docs domain
    """
    try:
        return urlparse(url).netloc.lower().startswith("docs.")
    except:
        return True


def select_similar(topic, results, embed_model, k=3):
    """
    Select top K most similar results to the topic using embeddings
    
    Args:
        topic (str): Target topic
        results (list): List of search results
        embed_model: Sentence transformer model
        k (int): Number of results to return
        
    Returns:
        list: Top K similar results
    """
    filtered = [r for r in results if r.get("link") and not is_docs_domain(r["link"])]
    
    if not filtered:
        return []
    
    texts = [r["title"] + " " + r.get("snippet", "") for r in filtered]
    
    topic_vec = embed_model.encode([topic], normalize_embeddings=True)
    text_vecs = embed_model.encode(texts, normalize_embeddings=True)
    
    sims = cosine_similarity(topic_vec, text_vecs)[0]
    ranked = sorted(zip(filtered, sims), key=lambda x: x[1], reverse=True)
    
    return [r[0] for r in ranked[:k]]


def extract_headings(url, max_headings=150):
    """
    Extract H1, H2, H3 headings from a URL
    
    Args:
        url (str): URL to scrape
        max_headings (int): Maximum number of headings to return
        
    Returns:
        list: List of tuples (tag_name, text)
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "lxml")
        out = []
        
        for tag in soup.find_all(["h1", "h2", "h3"]):
            txt = tag.get_text(strip=True)
            if txt:
                out.append((tag.name.upper(), txt))
        
        return out[:max_headings]
    except Exception as e:
        return []


def extract_entities(urls, textrazor_key, min_relevance=0.2, top_n=15):
    """
    Extract key entities from competitor URLs using TextRazor
    
    Args:
        urls (list): List of URL dictionaries
        textrazor_key (str): TextRazor API key
        min_relevance (float): Minimum relevance score
        top_n (int): Number of top entities to return
        
    Returns:
        list: Top entities by frequency
    """
    textrazor.api_key = textrazor_key
    tr_client = textrazor.TextRazor(extractors=["entities", "topics"])
    
    all_entities = []
    
    for r in urls:
        try:
            resp = tr_client.analyze_url(r["link"])
            for e in resp.entities():
                if e.relevance_score >= min_relevance:
                    all_entities.append(e.id.lower())
        except Exception as e:
            # Silently skip failed URLs
            continue
    
    if not all_entities:
        return []
    
    entity_freq = pd.Series(all_entities).value_counts()
    return entity_freq.head(top_n).index.tolist()


def has_long_paragraph(markdown_text, word_limit=130):
    """
    Check if markdown has any paragraphs exceeding word limit
    
    Args:
        markdown_text (str): Markdown content
        word_limit (int): Maximum words per paragraph
        
    Returns:
        bool: True if any paragraph exceeds limit
    """
    paragraphs = re.split(r"\n\s*\n", markdown_text)
    
    for p in paragraphs:
        # Skip headings
        if p.strip().startswith("#"):
            continue
        
        word_count = len(p.split())
        if word_count > word_limit:
            return True
    
    return False


def get_style_rules(tonality, context, theme, audience_persona, banned_words):
    """
    Generate style rules string for LLM prompts
    
    Args:
        tonality (str): Desired tone
        context (str): Audience context
        theme (str): Content themes
        audience_persona (str): Target audience description
        banned_words (list): Words to avoid
        
    Returns:
        str: Formatted style rules
    """
    banned_words_str = ", ".join(banned_words)
    
    return f"""
GLOBAL CONTENT RULES
- One H1 only
- Each H2 starts with exactly ONE short framing paragraph (60–90 words)
- H2 must never start with H3, bullets, tables, or code
- Under each H2: 2–5 H3 subsections
- Each H3: max 2 paragraphs, max ~120 words per paragraph
- Each H2 section max 3 paragraphs total (excluding tables)

BULLETS
- Required for lists, criteria, features, steps, comparisons
- Never bullet-only sections

TABLES
- Required when explaining comparisons, components, mappings, limits, configurations
- Use Markdown tables (not code blocks)

FAQ
- Non-opinionated
- Max 3 short lines per answer
- No bullets or tables

FACTUAL ACCURACY
- Do not invent numbers, limits, defaults, or guarantees
- If specifics vary, qualify with "depends on configuration / region / setup"
- Prefer neutral wording ("is used for", "typically", "commonly")
- Avoid marketing or subjective claims

BANNED WORDS
{banned_words_str}

Tone: {tonality}
Context: {context}
Theme: {theme}
Audience: {audience_persona}
"""


def call_llm(prompt, client, model="gpt-4"):
    """
    Call OpenAI API with error handling
    
    Args:
        prompt (str): Prompt text
        client: OpenAI client instance
        model (str): Model to use
        
    Returns:
        str: Generated text
    """
    try:
        # Note: Update this if using different OpenAI API structure
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"LLM API error: {str(e)}")


def create_outline_prompt(topic, tonality, context, theme, style_rules, 
                         competitor_outlines, entities):
    """
    Create prompt for outline generation
    """
    return f"""
Create a neutral, production-ready article outline.

Topic: {topic}

Tone: {tonality}
Context: {context}
Theme: {theme}

{style_rules}

Competitor coverage:
{competitor_outlines}

Important entities to cover naturally:
{entities}

Outline requirements:
- H1 once
- Each H2 must have multiple H3 subsections
- Introduce tables where comparisons or mappings exist
- Do not force sections that are not relevant
- Include a decision/fit section
- End with FAQs (4–6)

Return ONLY Markdown outline.
"""


def create_article_prompt(topic, audience_persona, style_rules, entities, outline):
    """
    Create prompt for article generation
    """
    return f"""
Write the full article using the outline below.

Topic: {topic}
Audience: {audience_persona}

{style_rules}

Entities to include naturally:
{entities}

Outline:
{outline}

STRUCTURE ENFORCEMENT
- Every H2 starts with one framing paragraph
- Use H3 subsections for depth
- Insert tables where comparison/mapping is implied
- Insert bullets when listing items
- Do not exceed 3 paragraphs per section
- No speculation, no invented specifics

Return ONLY Markdown article.
"""


def create_refactor_prompt(article):
    """
    Create prompt for refactoring long paragraphs
    """
    return f"""
Refactor the article below:
- Split long paragraphs
- Add H3 subsections where needed
- Preserve facts and structure

Article:
{article}

Return ONLY revised Markdown.
"""


def create_polish_prompt(article):
    """
    Create prompt for final polish
    """
    return f"""
Improve clarity and readability without changing meaning.

Rules:
- Preserve structure
- No new claims
- No marketing language
- Remove banned words
- Keep paragraphs concise

Article:
{article}

Return ONLY revised Markdown.
"""
