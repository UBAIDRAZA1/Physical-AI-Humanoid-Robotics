import sys
import os

# ==============================================================================
# INSTRUCTIONS FOR PYTHONANYWHERE:
# 1. Go to the "Web" tab in your PythonAnywhere dashboard.
# 2. Click on the link to edit your WSGI configuration file (e.g., /var/www/username_pythonanywhere_com_wsgi.py).
# 3. Delete everything in that file and paste the content of this file.
# 4. Update the 'path' variable below to match your actual file structure on PythonAnywhere.
# ==============================================================================

# 1. Add your project directory to the sys.path
# CHANGE THIS PATH: It should point to the folder containing this main.py file.
# If you uploaded the 'Ai-book' folder to your home directory, it might look like this:
path = '/home/yourusername/Ai-book/backend' 

if path not in sys.path:
    sys.path.append(path)

# 2. Load Environment Variables
# PythonAnywhere doesn't automatically load .env files in the WSGI interface.
# You can load them manually here using python-dotenv.
from dotenv import load_dotenv
project_folder = os.path.expanduser(path)  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

# Alternatively, set critical env vars directly here if .env loading fails:
# os.environ['GOOGLE_API_KEY'] = 'your_key_here'

# 3. Import the FastAPI app
try:
    from main import app
except ImportError as e:
    # This helps debug if the path is wrong
    raise ImportError(f"Could not import main from {path}. Error: {e}")

# 4. Wrap the ASGI app with a WSGI adapter
# This is required because PythonAnywhere uses WSGI, but FastAPI is ASGI.
from a2wsgi import ASGIMiddleware
application = ASGIMiddleware(app)
