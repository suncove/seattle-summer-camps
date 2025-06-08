import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration settings
CONFIG = {
    'ZIP_CODES_FILE': 'data/zip_codes.json',
    'CAMP_SOURCES_FILE': 'data/camp_sources.json',
    'MAX_SEARCH_RADIUS': 20,  # miles
    'MIN_AGE': 3,
    'MAX_AGE': 18,
    'DEFAULT_SEARCH_RADIUS': 5,
}

# API Keys (to be moved to .env file for production)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
FIREBASE_CONFIG = {
    'apiKey': os.getenv('FIREBASE_API_KEY', ''),
    'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN', ''),
    'projectId': os.getenv('FIREBASE_PROJECT_ID', ''),
    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', ''),
    'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID', ''),
    'appId': os.getenv('FIREBASE_APP_ID', '')
}

