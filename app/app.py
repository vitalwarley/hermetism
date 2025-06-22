"""
Hermetic Workbench - MVP
A modular Streamlit app for transforming esoteric materials into hermetic syntheses.
"""

import streamlit as st

# Import modular components
from utils.helpers import setup_logging, initialize_session_state, configure_page
from ui.sidebar import render_sidebar
from ui.upload_phase import render_upload_phase
from ui.extraction_config_phase import render_extraction_config_phase
from ui.extraction_phase import render_extraction_phase
from ui.synthesis_phase import render_synthesis_phase

def main():
    """Main application entry point."""
    # Setup
    setup_logging()
    configure_page()
    initialize_session_state()
    
    # Render sidebar and get configuration
    config = render_sidebar()
    
    # Main content area with phase-based workflow
    st.title("🔮 Hermetic Workbench - Phase-Based Workflow")
    
    # Phase navigation
    phases = ["📥 Upload", "⚙️ Configure", "🔍 Extract", "✨ Synthesize"]
    current_phase = st.session_state.get('current_phase', 0)
    
    # Display phase indicator
    phase_cols = st.columns(len(phases))
    for i, (phase_col, phase_name) in enumerate(zip(phase_cols, phases)):
        with phase_col:
            if i < current_phase:
                st.success(f"✅ {phase_name}")
            elif i == current_phase:
                st.info(f"▶️ {phase_name}")
            else:
                st.caption(f"⏳ {phase_name}")
    
    st.divider()
    
    # Render current phase
    if current_phase == 0:
        render_upload_phase()
    elif current_phase == 1:
        render_extraction_config_phase()
    elif current_phase == 2:
        render_extraction_phase()
    elif current_phase == 3:
        render_synthesis_phase(config)
    
    # Phase navigation controls
    st.divider()
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    
    with nav_col1:
        if current_phase > 0:
            if st.button("← Previous", use_container_width=True):
                st.session_state.current_phase = current_phase - 1
                st.rerun()
    
    with nav_col3:
        # Check if current phase requirements are met
        can_proceed = False
        if current_phase == 0:  # Upload phase
            can_proceed = len(st.session_state.get('uploaded_materials', {})) > 0
        elif current_phase == 1:  # Config phase
            can_proceed = len(st.session_state.get('extraction_configs', {})) > 0
        elif current_phase == 2:  # Extract phase
            can_proceed = len(st.session_state.get('extracted_content', {})) > 0
        
        if current_phase < len(phases) - 1:
            if st.button("Next →", use_container_width=True, disabled=not can_proceed):
                st.session_state.current_phase = current_phase + 1
                st.rerun()
    
    # Footer
    st.divider()
    st.caption("Hermetic Workbench MVP - Transforming wisdom through AI synthesis")

if __name__ == "__main__":
    main()