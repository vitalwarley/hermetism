"""
Synthesis Phase UI Component
Handles prompt creation, synthesis generation, and quality review
"""

import streamlit as st
from datetime import datetime
from services.ai_service import ai_service
from services.session import session_service

def render_synthesis_phase(config: dict):
    """Render the synthesis phase interface."""
    st.header("✨ Phase 4: Synthesize")
    st.markdown("Create a hermetic synthesis from your extracted materials.")
    
    if not st.session_state.extracted_content:
        st.warning("⚠️ No extracted content found. Please extract materials in Phase 3 first.")
        return
    
    # Synthesis configuration
    render_synthesis_config()
    
    st.divider()
    
    # Generate synthesis
    render_synthesis_generation(config)
    
    # Display synthesis results
    if st.session_state.synthesis:
        st.divider()
        render_synthesis_results()

def render_synthesis_config():
    """Render synthesis configuration section."""
    st.subheader("📝 Synthesis Configuration")
    
    # Template selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        template_options = {
            "Custom": "",
            "Hermetic Synthesis": "Create a hermetic synthesis that weaves together the esoteric principles and wisdom found in the materials. Focus on:\n1. Hidden connections between materials\n2. Deeper symbolic meanings\n3. Practical applications of the wisdom\n4. Universal principles that emerge",
            "Tarot Reading": "Provide a comprehensive tarot reading based on the materials:\n1. Card meanings and positions\n2. Relationships between cards\n3. Overall narrative and message\n4. Guidance for the querent",
            "Astrological Analysis": "Analyze the astrological content:\n1. Planetary influences and aspects\n2. House placements and their meanings\n3. Timing and cycles\n4. Practical life applications",
            "Alchemical Interpretation": "Interpret through an alchemical lens:\n1. Stages of transformation present\n2. Symbolic elements and their meanings\n3. The Great Work as reflected in the materials\n4. Personal transformation insights",
            "Comparative Analysis": "Compare and contrast the materials:\n{material1} - Primary source\n{material2} - Secondary source\n\nAnalyze:\n1. Common themes\n2. Contrasting viewpoints\n3. Synthesis of ideas\n4. Unified insights"
        }
        
        selected_template = st.selectbox(
            "Prompt Template",
            list(template_options.keys()),
            help="Select a template or choose 'Custom' to write your own"
        )
    
    with col2:
        st.info("💡 Use placeholders to reference specific materials")
    
    # Load template if selected
    if selected_template != "Custom":
        template_text = template_options[selected_template]
        if st.button("Load Template", key="load_synthesis_template"):
            st.session_state.synthesis_config['custom_prompt'] = template_text
            st.rerun()
    
    # Generate material placeholders
    material_placeholders = {}
    for i, (key, material) in enumerate(st.session_state.uploaded_materials.items()):
        if key in st.session_state.extracted_content:
            # Use display_name for more readable placeholders
            display_name = material.get('display_name', material['name'])
            # Create clean placeholder from display name
            clean_name = ''.join(c if c.isalnum() or c in ' -_' else '' for c in display_name)
            clean_name = clean_name.replace(' ', '_').lower()[:30]  # Limit length
            placeholder = f"{clean_name}"
            
            # Ensure unique placeholders
            if placeholder in material_placeholders.values():
                placeholder = f"{clean_name}_{i+1}"
            
            material_placeholders[placeholder] = key
    
    # Store placeholders
    st.session_state.synthesis_config['material_placeholders'] = material_placeholders
    
    # Show available placeholders
    if material_placeholders:
        with st.expander("📋 Available Placeholders", expanded=True):
            st.markdown("**Use these in your prompt:**")
            
            for placeholder, key in material_placeholders.items():
                material = st.session_state.uploaded_materials[key]
                display_name = material.get('display_name', material['name'])
                col1, col2 = st.columns([2, 3])
                with col1:
                    st.code(f"{{{placeholder}}}")
                with col2:
                    st.write(f"→ {display_name}")
            
            st.success(f"✅ {len(material_placeholders)} placeholders available")
    
    # Custom prompt editor
    st.markdown("### ✍️ Synthesis Prompt")
    
    current_prompt = st.session_state.synthesis_config.get('custom_prompt', '')
    custom_prompt = st.text_area(
        "Enter your synthesis prompt:",
        value=current_prompt,
        height=300,
        placeholder="Write your custom synthesis prompt here...\n\nYou can use placeholders like {material1}, {material2}, etc. to reference specific materials.\n\nIf you don't use placeholders, all materials will be included automatically.",
        help="Craft your prompt to guide the AI synthesis"
    )
    
    # Update synthesis config
    st.session_state.synthesis_config['custom_prompt'] = custom_prompt

def render_synthesis_generation(config: dict):
    """Render synthesis generation controls."""
    st.subheader("🔮 Generate Synthesis")
    
    # Check if prompt is provided
    custom_prompt = st.session_state.synthesis_config.get('custom_prompt', '').strip()
    
    if not custom_prompt:
        st.warning("⚠️ Please enter a synthesis prompt above.")
        return
    
    # Show prompt preview
    with st.expander("👁️ Prompt Preview", expanded=False):
        st.text(custom_prompt[:500] + "..." if len(custom_prompt) > 500 else custom_prompt)
    
    # Generation controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🚀 Generate Synthesis", type="primary", use_container_width=True):
            generate_synthesis()
    
    with col2:
        if st.session_state.synthesis:
            if st.button("🔄 Regenerate", type="secondary"):
                generate_synthesis()
    
    with col3:
        if st.session_state.synthesis:
            if st.button("🗑️ Clear", type="secondary"):
                st.session_state.synthesis = ""
                st.rerun()

def generate_synthesis():
    """Generate synthesis using AI service."""
    with st.spinner("🌟 Consulting the cosmic wisdom..."):
        try:
            # Prepare materials for synthesis
            synthesis_materials = {}
            
            # Map extracted content to material display names
            for key, content in st.session_state.extracted_content.items():
                material = st.session_state.uploaded_materials.get(key, {})
                # Use display_name for consistency
                material_name = material.get('display_name', material.get('name', key))
                synthesis_materials[material_name] = content
            
            # Get synthesis configuration
            custom_prompt = st.session_state.synthesis_config.get('custom_prompt', '')
            material_placeholders = st.session_state.synthesis_config.get('material_placeholders', {})
            
            # Create placeholder mapping for AI service
            placeholder_mapping = {}
            for placeholder, key in material_placeholders.items():
                material = st.session_state.uploaded_materials.get(key, {})
                material_name = material.get('display_name', material.get('name', key))
                placeholder_mapping[material_name] = placeholder
            
            # Generate synthesis
            synthesis = ai_service.synthesize_content(
                synthesis_materials,
                custom_prompt=custom_prompt,
                material_placeholders=placeholder_mapping
            )
            
            if synthesis:
                st.session_state.synthesis = synthesis
                
                # Auto-save session
                session_dir = session_service.save_session(
                    synthesis_materials,
                    synthesis,
                    custom_prompt=custom_prompt
                )
                
                # Store session ID for quality review
                st.session_state.current_session_id = session_dir.name
                
                st.success(f"✅ Synthesis generated and saved to: sessions/{session_dir.name}")
            else:
                st.error("❌ Failed to generate synthesis. Please try again.")
                
        except Exception as e:
            st.error(f"❌ Error generating synthesis: {str(e)}")

def render_synthesis_results():
    """Render synthesis results and options."""
    st.subheader("📜 Synthesis Results")
    
    # Display synthesis
    st.markdown(st.session_state.synthesis)
    
    # Export options
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "📥 Download Synthesis",
            st.session_state.synthesis,
            file_name=f"synthesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col2:
        st.download_button(
            "📦 Download Full Session",
            create_session_archive(),
            file_name=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.info("Use Ctrl+A and Ctrl+C to copy the synthesis text above")
    
    # Quality review
    st.divider()
    render_quality_review()

def render_quality_review():
    """Render quality review section."""
    with st.expander("📊 Quality Review", expanded=False):
        current_session_id = getattr(st.session_state, 'current_session_id', None)
        
        if not current_session_id:
            st.warning("⚠️ No active session found.")
            return
        
        st.markdown("### Rate the synthesis quality:")
        
        metrics = ["Accuracy", "Completeness", "Clarity", "Depth", "Relevance"]
        ratings = {}
        
        cols = st.columns(len(metrics))
        for i, metric in enumerate(metrics):
            with cols[i]:
                ratings[metric] = st.slider(
                    metric,
                    1, 5, 3,
                    key=f"phase4_rating_{metric}",
                    help=f"Rate the {metric.lower()} of the synthesis"
                )
        
        # Review notes
        review_notes = st.text_area(
            "Additional Comments (Optional)",
            placeholder="Add any notes about the synthesis quality, suggestions for improvement, etc.",
            key="phase4_review_notes"
        )
        
        # Save review
        if st.button("💾 Save Quality Review", type="primary"):
            success = session_service.save_quality_review(
                current_session_id,
                ratings,
                review_notes
            )
            
            if success:
                st.success("✅ Quality review saved!")
            else:
                st.error("❌ Failed to save quality review")

def create_session_archive():
    """Create a JSON archive of the current session."""
    import json
    
    session_data = {
        "timestamp": datetime.now().isoformat(),
        "uploaded_materials": st.session_state.uploaded_materials,
        "extraction_configs": st.session_state.extraction_configs,
        "extracted_content": st.session_state.extracted_content,
        "synthesis_config": st.session_state.synthesis_config,
        "synthesis": st.session_state.synthesis
    }
    
    return json.dumps(session_data, indent=2) 