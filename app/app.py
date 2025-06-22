"""
Hermetic Workbench - MVP
A modular Streamlit app for transforming esoteric materials into hermetic syntheses.
"""

import streamlit as st

# Import modular components
from utils.helpers import setup_logging, initialize_session_state, configure_page, get_project_state
from ui.sidebar import render_sidebar
from ui.upload_phase import render_upload_phase
from ui.extraction_config_phase import render_extraction_config_phase
from ui.extraction_phase import render_extraction_phase
from ui.synthesis_phase import render_synthesis_phase
from ui.project_dashboard import render_project_dashboard
from services.project import project_service

def render_workbench(config):
    """Render the workbench view with phase-based workflow."""
    # Show project name in title
    if st.session_state.current_project:
        st.title(f"🔮 {st.session_state.current_project['name']}")
        st.markdown("Transform esoteric materials into hermetic syntheses")
    else:
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
                # Auto-save on phase change
                if st.session_state.current_project_id:
                    # Verify project exists before saving
                    project_data = project_service.load_project(st.session_state.current_project_id)
                    if project_data:
                        project_service.save_project_state(
                            st.session_state.current_project_id,
                            get_project_state()
                        )
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
                # Auto-save on phase change
                if st.session_state.current_project_id:
                    # Verify project exists before saving
                    project_data = project_service.load_project(st.session_state.current_project_id)
                    if project_data:
                        project_service.save_project_state(
                            st.session_state.current_project_id,
                            get_project_state()
                        )
                st.rerun()
    
    # Footer
    st.divider()
    st.caption("Hermetic Workbench MVP - Transforming wisdom through AI synthesis")

def main():
    """Main application entry point."""
    # Setup
    setup_logging()
    configure_page()
    initialize_session_state()
    
    # Validate current project if in workbench mode
    if st.session_state.view_mode == 'workbench' and st.session_state.current_project_id:
        # Check if project still exists
        project_data = project_service.load_project(st.session_state.current_project_id)
        if not project_data:
            # Project doesn't exist, reset to dashboard
            st.warning(f"Project not found. Returning to dashboard.")
            st.session_state.current_project_id = None
            st.session_state.current_project = None
            st.session_state.view_mode = 'dashboard'
    
    # Handle view mode routing
    if st.session_state.view_mode == 'dashboard':
        # Project Dashboard View
        render_project_dashboard()
    else:
        # Workbench View
        # Render sidebar and get configuration
        config = render_sidebar()
        
        # Main content area
        render_workbench(config)
        
        # Handle session management actions from sidebar
        if st.session_state.get('save_session_clicked'):
            # Save session logic
            from services.session import session_service
            materials_dict = {}
            for key, material in st.session_state.uploaded_materials.items():
                if key in st.session_state.extracted_content:
                    materials_dict[material['display_name']] = st.session_state.extracted_content[key]
            
            if materials_dict and st.session_state.synthesis:
                session_path = session_service.save_session(
                    materials=materials_dict,
                    synthesis=st.session_state.synthesis,
                    custom_prompt=st.session_state.synthesis_config.get('custom_prompt', ''),
                    metadata={
                        'project_id': st.session_state.current_project_id,
                        'project_name': st.session_state.current_project.get('name') if st.session_state.current_project else None
                    }
                )
                st.success(f"Session saved to {session_path}")
            
            st.session_state['save_session_clicked'] = False
        
        if st.session_state.get('load_session_clicked'):
            st.info("Session loading will be implemented in the Load Session dialog")
            st.session_state['load_session_clicked'] = False

if __name__ == "__main__":
    main()