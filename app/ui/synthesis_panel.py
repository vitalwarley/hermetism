import streamlit as st
from datetime import datetime
from services.ai_service import ai_service
from services.session import session_service

def render_synthesis_panel(config: dict):
    """Render the synthesis generation and display panel."""
    st.header("✨ Synthesis")
    
    # Generate synthesis button
    if st.session_state.materials:
        # Check if custom prompt is provided
        custom_prompt = getattr(st.session_state, 'custom_prompt', '')
        if not custom_prompt.strip():
            st.warning("⚠️ Please enter a custom synthesis prompt in the Input Materials section before generating.")
        else:
            if st.button("🔮 Generate Synthesis", type="primary"):
                with st.spinner("Consulting the cosmic wisdom..."):
                    # Get material placeholders from session state
                    material_placeholders = getattr(st.session_state, 'material_placeholders', {})
                    
                    synthesis = ai_service.synthesize_content(
                        st.session_state.materials,
                        custom_prompt=custom_prompt,
                        material_placeholders=material_placeholders
                    )
                    
                    if synthesis:
                        st.session_state.synthesis = synthesis
                        
                        # Auto-save session
                        session_dir = session_service.save_session(
                            st.session_state.materials,
                            synthesis,
                            custom_prompt_preview=custom_prompt[:100] + "..." if len(custom_prompt) > 100 else custom_prompt
                        )
                        st.success(f"Session saved to: {session_dir}")
    
    # Display synthesis
    if st.session_state.synthesis:
        st.markdown(st.session_state.synthesis)
        
        # Export and review options
        _render_export_options()
        _render_quality_review()
    else:
        st.info("Upload materials and click 'Generate Synthesis' to begin")

def _render_export_options():
    """Render export options for the synthesis."""
    col_download, col_copy = st.columns(2)
    
    with col_download:
        st.download_button(
            "📥 Download",
            st.session_state.synthesis,
            file_name=f"synthesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
    
    with col_copy:
        if st.button("📋 Copy to Clipboard"):
            st.write("Copy the text above manually")  # Clipboard API needs JS

def _render_quality_review():
    """Render quality review section."""
    with st.expander("📊 Quality Review"):
        metrics = ["Accuracy", "Completeness", "Clarity", "Depth"]
        ratings = {}
        
        cols = st.columns(len(metrics))
        for i, metric in enumerate(metrics):
            with cols[i]:
                ratings[metric] = st.slider(metric, 1, 5, 3, key=f"rating_{metric}")
        
        if st.button("Save Review"):
            # Could extend to save ratings to session metadata
            st.info("Review saved to session") 