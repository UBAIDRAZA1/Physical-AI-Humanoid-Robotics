"""
OAuth 2.0 integration with Google, compatible with BetterAuth patterns.
"""
import os
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv

load_dotenv()

# Get Google client ID and secret from environment
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Check for required configuration
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("Warning: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET not set. Google OAuth disabled.")
    oauth = None
else:
    # Initialize OAuth registry
    oauth = OAuth()
    
    # Register Google OAuth client
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

async def is_google_oauth_enabled() -> bool:
    """Check if Google OAuth is configured and enabled."""
    return oauth is not None

