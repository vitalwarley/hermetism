import streamlit as st
from config.settings import MODEL_VISION, MODEL_SYNTHESIS

def render_sidebar():
    """Render the sidebar configuration panel."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        artifact_type = st.selectbox(
            "Artifact Type",
            ["Tarot Reading", "Hermetic Synthesis", "Astrological Analysis", "Custom"]
        )
        
        custom_prompt = None
        if artifact_type == "Custom":
            custom_prompt = st.text_area("Custom Synthesis Prompt")
        
        st.divider()
        
        # Model selection (optional override)
        with st.expander("Advanced Settings"):
            vision_model = st.text_input("Vision Model", MODEL_VISION)
            synthesis_model = st.text_input("Synthesis Model", MODEL_SYNTHESIS)
        
        return {
            "artifact_type": artifact_type,
            "custom_prompt": custom_prompt,
            "vision_model": vision_model,
            "synthesis_model": synthesis_model
        } 