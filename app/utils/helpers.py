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
    # Project management
    if 'current_project_id' not in st.session_state:
        st.session_state.current_project_id = None
    
    if 'current_project' not in st.session_state:
        st.session_state.current_project = None
    
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = 'dashboard'  # 'dashboard', 'workbench', 'prompts', 'materials_workspace'
    
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
    
    if 'synthesis_results' not in st.session_state:
        st.session_state.synthesis_results = []
    
    # Materials Workspace specific state
    if 'workspace_mode' not in st.session_state:
        st.session_state.workspace_mode = 'overview'  # 'overview', 'materials', 'extractions', 'import'
    
    if 'selected_material' not in st.session_state:
        st.session_state.selected_material = None
    
    if 'selected_extraction' not in st.session_state:
        st.session_state.selected_extraction = None
    
    if 'show_extraction_form' not in st.session_state:
        st.session_state.show_extraction_form = False
    
    if 'workspace_extractions' not in st.session_state:
        st.session_state.workspace_extractions = {}  # For synthesis phase
    
    if 'selected_placeholders' not in st.session_state:
        st.session_state.selected_placeholders = []  # For placeholder selection
    
    # Legacy support (will be migrated)
    if 'materials' not in st.session_state:
        st.session_state.materials = {}
    
    if 'synthesis' not in st.session_state:
        st.session_state.synthesis = ""
    
    # Model configuration - separate models for different tasks
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7
    
    if 'model_vision' not in st.session_state:
        from config.settings import MODEL_VISION
        st.session_state.model_vision = MODEL_VISION
    
    if 'model_synthesis' not in st.session_state:
        from config.settings import MODEL_SYNTHESIS
        st.session_state.model_synthesis = MODEL_SYNTHESIS
    
    # Legacy single model for backward compatibility
    if 'model' not in st.session_state:
        st.session_state.model = st.session_state.model_synthesis

def get_project_state() -> dict:
    """Get the current project state from session state."""
    return {
        'current_phase': st.session_state.current_phase,
        'uploaded_materials': st.session_state.uploaded_materials,
        'extraction_configs': st.session_state.extraction_configs,
        'extracted_content': st.session_state.extracted_content,
        'synthesis_config': st.session_state.synthesis_config,
        'synthesis': st.session_state.synthesis,
        'synthesis_results': st.session_state.get('synthesis_results', []),
        'temperature': st.session_state.temperature,
        'model_vision': st.session_state.model_vision,
        'model_synthesis': st.session_state.model_synthesis,
        'model': st.session_state.model,  # Legacy support
        'materials': st.session_state.materials  # Legacy support
    }

def load_project_state(state: dict):
    """Load project state into session state."""
    # Clear synthesis results first to prevent cross-project contamination
    st.session_state.synthesis_results = []
    
    for key, value in state.items():
        if key in st.session_state:
            st.session_state[key] = value
    
    # Ensure model settings are loaded with defaults if not present
    if 'model_vision' not in state:
        from config.settings import MODEL_VISION
        st.session_state.model_vision = MODEL_VISION
    
    if 'model_synthesis' not in state:
        from config.settings import MODEL_SYNTHESIS
        st.session_state.model_synthesis = MODEL_SYNTHESIS

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
    
    # Don't show title here anymore - will be shown conditionally in app.py 