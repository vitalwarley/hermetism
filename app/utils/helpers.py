import logging
import streamlit as st
from typing import Union

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def initialize_session_state():
    """Initialize session state variables with phase-based structure."""
    # Phase management
    if 'current_phase' not in st.session_state:
        st.session_state.current_phase = 0
    
    # Phase 1: Upload state
    if 'uploaded_materials' not in st.session_state:
        st.session_state.uploaded_materials = {}  # {file_key: file_object}
    
    # Phase 2: Extraction configuration state
    if 'extraction_configs' not in st.session_state:
        st.session_state.extraction_configs = {}  # {file_key: config_dict}
    
    # Phase 3: Extracted content state
    if 'extracted_content' not in st.session_state:
        st.session_state.extracted_content = {}  # {file_key: extracted_text}
    
    # Phase 4: Synthesis state
    if 'synthesis_config' not in st.session_state:
        st.session_state.synthesis_config = {
            'custom_prompt': '',
            'material_placeholders': {}
        }
    
    # Legacy support (will be migrated)
    if 'materials' not in st.session_state:
        st.session_state.materials = {}
    
    if 'synthesis' not in st.session_state:
        st.session_state.synthesis = ""
    
    # Model configuration
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7
    
    if 'model' not in st.session_state:
        st.session_state.model = "gpt-4-turbo-preview"

def format_file_size(size_bytes: Union[int, float]) -> str:
    """
    Format file size in bytes to human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB", "256 KB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def configure_page():
    """Configure Streamlit page settings."""
    from config.settings import PAGE_TITLE, PAGE_ICON
    
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide"
    )
    
    st.title(f"{PAGE_ICON} Hermetic Workbench - MVP")
    st.markdown("Transform esoteric materials into hermetic syntheses") 