import streamlit as st
from config.settings import MODEL_VISION, MODEL_SYNTHESIS

def render_sidebar():
    """Render the sidebar configuration panel."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection (optional override)
        with st.expander("Advanced Settings"):
            vision_model = st.text_input("Vision Model", MODEL_VISION)
            synthesis_model = st.text_input("Synthesis Model", MODEL_SYNTHESIS)
        
        return {
            "vision_model": vision_model,
            "synthesis_model": synthesis_model
        } 