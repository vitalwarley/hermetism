import streamlit as st
from config.settings import TEMPERATURE_MIN, TEMPERATURE_MAX, TEMPERATURE_DEFAULT, TEMPERATURE_STEP

def render_sidebar():
    """Render the sidebar with configuration options."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Navigation section
        st.markdown("### 🧭 Navigation")
        
        # Materials Workspace button (always visible)
        if st.button("📚 Materials Workspace", use_container_width=True, 
                     type="primary" if st.session_state.get('view_mode') == 'materials_workspace' else "secondary"):
            # Save current project state if in workbench mode
            if st.session_state.get('view_mode') == 'workbench' and st.session_state.get('current_project_id'):
                from services.project import project_service
                from utils.helpers import get_project_state
                
                if project_service.load_project(st.session_state.current_project_id):
                    project_service.save_project_state(
                        st.session_state.current_project_id,
                        get_project_state()
                    )
            
            # Clear workspace-specific state
            if hasattr(st.session_state, 'selected_material'):
                del st.session_state.selected_material
            if hasattr(st.session_state, 'selected_extraction'):
                del st.session_state.selected_extraction
            if hasattr(st.session_state, 'show_extraction_form'):
                del st.session_state.show_extraction_form
            
            st.session_state.view_mode = 'materials_workspace'
            st.rerun()
        
        # Prompt Workspace button
        if st.button("📝 Prompt Workspace", use_container_width=True,
                     type="primary" if st.session_state.get('view_mode') == 'prompts' else "secondary"):
            # Save current project state if in workbench mode
            if st.session_state.get('view_mode') == 'workbench' and st.session_state.get('current_project_id'):
                from services.project import project_service
                from utils.helpers import get_project_state
                
                if project_service.load_project(st.session_state.current_project_id):
                    project_service.save_project_state(
                        st.session_state.current_project_id,
                        get_project_state()
                    )
            
            st.session_state.view_mode = 'prompts'
            st.rerun()
        
        # Project Dashboard button
        if st.button("🏠 Project Dashboard", use_container_width=True,
                     type="primary" if st.session_state.get('view_mode') == 'dashboard' else "secondary"):
            # Save current project state if in workbench mode
            if st.session_state.get('view_mode') == 'workbench' and st.session_state.get('current_project_id'):
                from services.project import project_service
                from utils.helpers import get_project_state
                
                if project_service.load_project(st.session_state.current_project_id):
                    project_service.save_project_state(
                        st.session_state.current_project_id,
                        get_project_state()
                    )
            
            st.session_state.view_mode = 'dashboard'
            st.rerun()
        
        st.divider()
        
        # Project info section (only in workbench mode)
        if st.session_state.get('view_mode') == 'workbench' and st.session_state.get('current_project'):
            project = st.session_state.current_project
            st.markdown("### 📁 Current Project")
            st.markdown(f"**{project['name']}**")
            if project.get('description'):
                st.caption(project['description'])
            
            # Back to projects button
            if st.button("← Back to Projects", use_container_width=True):
                # Save current state before leaving
                from services.project import project_service
                from utils.helpers import get_project_state
                
                if st.session_state.current_project_id:
                    # Verify project exists before saving
                    if project_service.load_project(st.session_state.current_project_id):
                        project_service.save_project_state(
                            st.session_state.current_project_id,
                            get_project_state()
                        )
                
                st.session_state.view_mode = 'dashboard'
                st.rerun()
            
            st.divider()
        
        # Model settings
        st.subheader("🤖 Model Settings")
        
        # Model options
        vision_model_options = [
            "openai/gpt-4o-mini",
        ]
        
        synthesis_model_options = [
            "openai/gpt-4.1",
            "anthropic/claude-opus-4",
            "google/gemini-2.5-pro"
        ]
        
        # Vision model selection
        st.session_state.model_vision = st.selectbox(
            "Vision Model (Extraction)",
            options=vision_model_options,
            index=vision_model_options.index(st.session_state.get('model_vision', vision_model_options[0])) if st.session_state.get('model_vision', vision_model_options[0]) in vision_model_options else 0,
            help="Model used for extracting content from images and PDFs"
        )
        
        # Synthesis model selection
        st.session_state.model_synthesis = st.selectbox(
            "Synthesis Model",
            options=synthesis_model_options,
            index=synthesis_model_options.index(st.session_state.get('model_synthesis', synthesis_model_options[0])) if st.session_state.get('model_synthesis', synthesis_model_options[0]) in synthesis_model_options else 0,
            help="Model used for generating hermetic syntheses"
        )
        
        # Temperature control
        st.session_state.temperature = st.slider(
            "Temperature",
            min_value=TEMPERATURE_MIN,
            max_value=TEMPERATURE_MAX,
            value=st.session_state.get('temperature', TEMPERATURE_DEFAULT),
            step=TEMPERATURE_STEP,
            help="Controls creativity/randomness. Lower = more focused, Higher = more creative"
        )
        
        # Display temperature description
        if st.session_state.temperature < 0.3:
            st.caption("🎯 Very focused and deterministic")
        elif st.session_state.temperature < 0.7:
            st.caption("⚖️ Balanced creativity")
        else:
            st.caption("🎨 High creativity and variation")
        
        st.divider()
        
        # Session management (only in workbench mode)
        if st.session_state.get('view_mode') == 'workbench':
            st.subheader("💾 Session Management")
            
            # Save current session
            if st.button("📥 Save Session", use_container_width=True, 
                        disabled=not st.session_state.get('synthesis', '')):
                # Implementation will be in the main app
                st.session_state['save_session_clicked'] = True
            
            # Load previous session
            if st.button("📤 Load Session", use_container_width=True):
                st.session_state['load_session_clicked'] = True
            
            st.divider()
        
        # Info section
        st.caption("🔮 Hermetic Workbench MVP")
        st.caption("Transform esoteric materials into hermetic syntheses")
    
    # Return configuration
    return {
        'model_vision': st.session_state.model_vision,
        'model_synthesis': st.session_state.model_synthesis,
        'temperature': st.session_state.temperature
    } 