import sys
import os
from asgiref.wsgi import WsgiToAsgi

# ✅ CORRECT PATH (tumhara actual backend path)
project_home = '/home/UbaidRaza2526/backend/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# ❌ .env load mat karo yahan
# ❌ dotenv ki zarurat nahi

# ✅ FastAPI app import
from main import app

# ✅ ASGI → WSGI bridge
application = WsgiToAsgi(app)
