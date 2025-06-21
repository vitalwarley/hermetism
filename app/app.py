"""
Hermetic Workbench - MVP
A modular Streamlit app for transforming esoteric materials into hermetic syntheses.
"""

import streamlit as st

# Import modular components
from utils.helpers import setup_logging, initialize_session_state, configure_page
from ui.sidebar import render_sidebar  
from ui.input_panel import render_input_panel
from ui.synthesis_panel import render_synthesis_panel

def main():
    """Main application entry point."""
    # Setup
    setup_logging()
    configure_page()
    initialize_session_state()
    
    # Render sidebar and get configuration
    config = render_sidebar()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_input_panel()
    
    with col2:
        render_synthesis_panel(config)
    
    # Footer
    st.divider()
    st.caption("Hermetic Workbench MVP - Transforming wisdom through AI synthesis")

if __name__ == "__main__":
    main()