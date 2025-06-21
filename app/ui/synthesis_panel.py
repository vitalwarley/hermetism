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
                            custom_prompt=custom_prompt
                        )
                        
                        # Store session ID for quality review
                        st.session_state.current_session_id = session_dir.name
                        
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
        # Check if we have a current session to update
        current_session_id = getattr(st.session_state, 'current_session_id', None)
        
        if not current_session_id:
            st.warning("⚠️ No active session found. Generate a synthesis first to enable quality review.")
            return
        
        metrics = ["Accuracy", "Completeness", "Clarity", "Depth"]
        ratings = {}
        
        cols = st.columns(len(metrics))
        for i, metric in enumerate(metrics):
            with cols[i]:
                ratings[metric] = st.slider(metric, 1, 5, 3, key=f"rating_{metric}")
        
        # Optional review notes
        review_notes = st.text_area(
            "Review Notes (Optional)",
            placeholder="Add any additional comments about the synthesis quality...",
            key="review_notes"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Review", type="primary"):
                success = session_service.save_quality_review(
                    current_session_id, 
                    ratings, 
                    review_notes
                )
                
                if success:
                    st.success("✅ Quality review saved and session updated!")
                else:
                    st.error("❌ Failed to save quality review")
        
        with col2:
            if st.button("🔄 Reset Ratings"):
                # Clear the slider values by reinitializing them
                for metric in metrics:
                    if f"rating_{metric}" in st.session_state:
                        st.session_state[f"rating_{metric}"] = 3
                if "review_notes" in st.session_state:
                    st.session_state["review_notes"] = ""
                st.rerun() 