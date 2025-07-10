import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the content creation tool."""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Medium API Configuration
    MEDIUM_ACCESS_TOKEN = os.getenv('MEDIUM_ACCESS_TOKEN')
    MEDIUM_USER_ID = os.getenv('MEDIUM_USER_ID')
    
    # MCP Filesystem Configuration
    MCP_FILESYSTEM_PATH = os.getenv('MCP_FILESYSTEM_PATH', './content-workspace')
    
    # Workspace directories
    IDEAS_DIR = os.path.join(MCP_FILESYSTEM_PATH, 'ideas')
    GENERATED_DIR = os.path.join(MCP_FILESYSTEM_PATH, 'generated')
    PUBLISHED_DIR = os.path.join(MCP_FILESYSTEM_PATH, 'published')
    TEMPLATES_DIR = os.path.join(MCP_FILESYSTEM_PATH, 'templates')
    
    # App Configuration
    STREAMLIT_SERVER_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', 8501))
    STREAMLIT_SERVER_ADDRESS = os.getenv('STREAMLIT_SERVER_ADDRESS', 'localhost')
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present."""
        missing_keys = []
        
        if not cls.OPENAI_API_KEY:
            missing_keys.append('OPENAI_API_KEY')
        if not cls.MEDIUM_ACCESS_TOKEN:
            missing_keys.append('MEDIUM_ACCESS_TOKEN')
        if not cls.MEDIUM_USER_ID:
            missing_keys.append('MEDIUM_USER_ID')
            
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
        
        return True
    
    @classmethod
    def create_workspace_directories(cls):
        """Create the workspace directory structure."""
        directories = [cls.IDEAS_DIR, cls.GENERATED_DIR, cls.PUBLISHED_DIR, cls.TEMPLATES_DIR]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        return directories 