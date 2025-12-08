"""
Application configuration settings
Centralized configuration management for the Tech Mahindra AI Assistant
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Main configuration class for the application"""
    
    # Application settings
    APP_TITLE = "Tech Mahindra AI Assistant - Developed BY Samriddhi"
    APP_ICON = "🤖"
    LAYOUT = "wide"
    SIDEBAR_STATE = "collapsed"
    
    # Database settings
    DATABASE_PATH = "telecom.db"
    CHROMA_DB_PATH = "./chroma_db"
    DOWNLOAD_DIR = "downloads"
    
    # API settings
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "llama3-8b-8192"
    GROQ_MAX_TOKENS = 500
    GROQ_TEMPERATURE = 0.7
    
    # Google Drive settings
    GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    GOOGLE_CREDENTIALS_FILE = "client_secret_671068610606-0dtubpgrm8d76kmfh19lcsueuruc3bpe.apps.googleusercontent.com.json"
    GOOGLE_TOKEN_FILE = "token.pickle"
    
    # File processing settings
    SUPPORTED_FILE_TYPES = ['pdf', 'docx', 'pptx', 'txt']
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    TEXT_EXTRACTION_LIMIT = 500  # characters per document (further reduced for token limits)
    
    # Security settings
    PASSWORD_MIN_LENGTH = 6
    SESSION_TIMEOUT = 3600  # 1 hour
    
    # UI settings
    CHAT_HISTORY_LIMIT = 50
    MAX_CONTEXT_LENGTH = 800  # further reduced for token limits
    
    # Default admin credentials
    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "admin123"
    
    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FILE = "app.log"
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        required_vars = [
            'GROQ_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Initialize configuration
try:
    Config.validate_config()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please check your .env file and ensure all required variables are set.") 