import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Model Configuration
MODEL_VISION = "openai/gpt-4o-mini"  # For vision tasks
MODEL_SYNTHESIS = "openai/gpt-4.1"  # For synthesis

# Temperature Configuration
TEMPERATURE_MIN = 0.0
TEMPERATURE_MAX = 1.0
TEMPERATURE_DEFAULT = 0.7
TEMPERATURE_STEP = 0.1

# File Processing Configuration
SUPPORTED_FILE_TYPES = ['pdf', 'jpg', 'jpeg', 'png', 'txt']
MAX_TEXT_LENGTH = 100000
MAX_SYNTHESIS_LENGTH = 100000

# UI Configuration
PAGE_TITLE = "🔮 Hermetic Workbench"
PAGE_ICON = "🔮"

# Synthesis Templates
SYNTHESIS_PROMPTS = {
    "Tarot Reading": """Create a comprehensive tarot synthesis based on these materials.
    Include: General meaning, Harmonic interpretation, Disharmonic interpretation.""",
    
    "Hermetic Synthesis": """Create a hermetic synthesis exploring the esoteric connections 
    between these materials. Include symbolic, alchemical, and practical insights.""",
    
    "Astrological Analysis": """Create an astrological analysis based on these materials.
    Include planetary influences, sign characteristics, and practical applications."""
}

# Session Configuration
SESSIONS_DIR = "sessions" 