"""
Google OAuth authentication module for Streamlit
"""

import streamlit as st
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the token.pickle file.
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]

def get_credentials():
    """
    Get Google credentials using OAuth flow
    Returns credentials object or None
    """
    creds = None
    
    # Check if we have stored credentials in session state
    if 'google_creds' in st.session_state and st.session_state.google_creds:
        creds = st.session_state.google_creds
        
        # Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                st.session_state.google_creds = creds
            except Exception as e:
                st.error(f"Failed to refresh credentials: {str(e)}")
                creds = None
                st.session_state.google_creds = None
        
        return creds
    
    # Check for token file
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        
        if not creds:
            # Check if credentials.json exists
            if not os.path.exists('credentials.json'):
                return None
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
                    
            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")
                return None
    
    # Store in session state
    st.session_state.google_creds = creds
    return creds


def create_google_doc(title, content, creds):
    """
    Create a Google Doc with the given title and content
    
    Args:
        title (str): Document title
        content (str): Document content (markdown will be converted to plain text)
        creds: Google credentials object
        
    Returns:
        tuple: (doc_id, doc_url) or (None, None) if failed
    """
    try:
        # Build the Docs and Drive services
        docs_service = build('docs', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Create a new document
        doc = docs_service.documents().create(body={'title': title}).execute()
        doc_id = doc.get('documentId')
        
        # Insert the content
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 1,
                    },
                    'text': content
                }
            }
        ]
        
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        
        # Make the document accessible
        drive_service.permissions().create(
            fileId=doc_id,
            body={
                'type': 'anyone',
                'role': 'reader'
            }
        ).execute()
        
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
        
        return doc_id, doc_url
        
    except Exception as e:
        st.error(f"Failed to create Google Doc: {str(e)}")
        return None, None


def is_authenticated():
    """
    Check if user is authenticated with Google
    """
    return 'google_creds' in st.session_state and st.session_state.google_creds is not None


def logout():
    """
    Logout from Google
    """
    if 'google_creds' in st.session_state:
        st.session_state.google_creds = None
    
    # Remove token file
    if os.path.exists('token.pickle'):
        try:
            os.remove('token.pickle')
        except:
            pass
