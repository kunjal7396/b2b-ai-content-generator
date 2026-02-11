# Google OAuth Setup Guide

This guide will help you set up Google authentication so you can export articles directly to Google Docs.

## Prerequisites

- A Google account
- The app installed and running locally

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click **"New Project"**
4. Enter a project name (e.g., "Content Generator")
5. Click **"Create"**

## Step 2: Enable Required APIs

1. In your new project, go to **"APIs & Services"** → **"Library"**
2. Search for and enable these APIs:
   - **Google Docs API**
   - **Google Drive API**

### Enable Google Docs API:
- Search "Google Docs API"
- Click on it
- Click **"Enable"**

### Enable Google Drive API:
- Search "Google Drive API"
- Click on it
- Click **"Enable"**

## Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** user type
3. Click **"Create"**

Fill in the required fields:
- **App name**: Content Generator (or your preferred name)
- **User support email**: Your email
- **Developer contact**: Your email
4. Click **"Save and Continue"**

### Scopes:
5. Click **"Add or Remove Scopes"**
6. Add these scopes:
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/drive.file`
7. Click **"Update"** then **"Save and Continue"**

### Test Users:
8. Click **"Add Users"**
9. Add your Google email address
10. Click **"Save and Continue"**

## Step 4: Create OAuth Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Select **"Desktop app"** as the application type
4. Name it (e.g., "Content Generator Desktop")
5. Click **"Create"**

## Step 5: Download Credentials

1. You'll see a dialog with your client ID and secret
2. Click **"Download JSON"**
3. **Important**: Rename the downloaded file to exactly `credentials.json`
4. Move `credentials.json` to your app folder (same directory as `app.py`)

Your folder structure should look like:
```
content-generator-app/
├── app.py
├── utils.py
├── google_auth.py
├── credentials.json  ← Your downloaded file here
├── requirements.txt
└── ...
```

## Step 6: Test Authentication

1. Run your Streamlit app: `streamlit run app.py`
2. Look at the sidebar under "📤 Google Docs"
3. Click **"🔗 Connect Google Account"**
4. A browser window will open
5. Sign in with your Google account
6. Click **"Allow"** to grant permissions
7. You should see "✓ Connected to Google" in the sidebar

## Step 7: Export to Google Docs

1. Generate an article
2. Click **"📤 Export to Google Docs"**
3. A link to your new Google Doc will appear
4. Click it to open the document

## Troubleshooting

### "credentials.json not found"
- Make sure the file is in the same folder as `app.py`
- Make sure it's named exactly `credentials.json` (not `credentials (1).json`)

### "Access blocked: Content Generator hasn't completed Google verification"
- This happens because your app isn't verified
- Solution: Add your email as a test user (Step 3)
- Or: Click "Advanced" → "Go to Content Generator (unsafe)" during auth

### "Invalid grant" error
- Delete `token.pickle` file from your app folder
- Click "Disconnect" in the sidebar
- Click "Connect Google Account" again

### Browser doesn't open
- Check your firewall settings
- Try running on a different port
- Make sure no other app is using port 8501

### "Insufficient permissions"
- Make sure you selected the correct scopes in Step 3
- Delete `token.pickle` and re-authenticate

## Security Notes

⚠️ **Important Security Information:**

1. **Never commit `credentials.json` to GitHub**
   - It's already in `.gitignore`
   - If accidentally committed, revoke it immediately in Google Cloud Console

2. **Never share your credentials file**
   - It allows access to create documents in your Google Drive

3. **Token storage**
   - `token.pickle` is created after first auth
   - It's also in `.gitignore`
   - Delete it if you want to re-authenticate

4. **Publishing the app**
   - For production, you'll need to verify your app with Google
   - Or use a service account instead of OAuth

## Alternative: Service Account (Advanced)

For production/deployed apps, consider using a Service Account instead:

1. Create a service account in Google Cloud Console
2. Download the service account JSON key
3. Modify `google_auth.py` to use service account authentication
4. Share documents with the service account email

This avoids the OAuth flow but requires sharing documents programmatically.

## Need Help?

- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Docs API Reference](https://developers.google.com/docs/api)
- Check the app's error messages for specific issues

## Verification Checklist

Before asking for help, verify:
- [ ] `credentials.json` exists in the app folder
- [ ] Both APIs are enabled in Google Cloud Console
- [ ] Your email is added as a test user
- [ ] You're using the correct Google account
- [ ] No firewall blocking localhost connections
- [ ] `token.pickle` doesn't exist (if having issues)

---

Once setup is complete, you can export unlimited articles to Google Docs! 🎉
