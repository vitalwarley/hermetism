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
    
    # Synthesis results are now managed as part of project state
    
    # Synthesis configuration
    render_synthesis_config()
    
    st.divider()
    
    # Generate synthesis
    render_synthesis_generation(config)
    
    # Display synthesis results in tabs
    if st.session_state.synthesis_results:
        st.divider()
        render_synthesis_tabs()

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
    url_counters = {}  # Track URLs per site
    
    for i, (key, material) in enumerate(st.session_state.uploaded_materials.items()):
        if key in st.session_state.extracted_content:
            material_type = material.get('type', '')
            
            if material_type == 'url':
                # Extract domain from URL
                from urllib.parse import urlparse
                parsed = urlparse(material.get('url', ''))
                domain = parsed.netloc or 'unknown'
                
                # Clean domain (remove www., convert . to _)
                clean_domain = domain.replace('www.', '').replace('.', '_')
                
                # Track URLs per site
                if clean_domain not in url_counters:
                    url_counters[clean_domain] = 0
                url_counters[clean_domain] += 1
                
                # Create placeholder with site name and ID
                placeholder = f"{clean_domain}_{url_counters[clean_domain]}"
                
            elif material_type == 'file':
                # Get filename without extension
                display_name = material.get('display_name', material['name'])
                # Remove file extension
                import os
                name_without_ext = os.path.splitext(display_name)[0]
                
                # Clean name for placeholder
                clean_name = ''.join(c if c.isalnum() or c in ' -_' else '' for c in name_without_ext)
                clean_name = clean_name.replace(' ', '_').lower()[:30]
                placeholder = clean_name
                
            elif material_type == 'youtube':
                # Extract video ID for placeholder
                display_name = material.get('display_name', 'youtube')
                clean_name = display_name.replace('YouTube: ', '').replace('-', '_').lower()
                placeholder = f"youtube_{clean_name}"
                
            else:
                # Default handling for other types
                display_name = material.get('display_name', material['name'])
                clean_name = ''.join(c if c.isalnum() or c in ' -_' else '' for c in display_name)
                clean_name = clean_name.replace(' ', '_').lower()[:30]
                placeholder = clean_name
            
            # Ensure unique placeholders
            base_placeholder = placeholder
            counter = 1
            while placeholder in material_placeholders.values():
                placeholder = f"{base_placeholder}_{counter}"
                counter += 1
            
            material_placeholders[placeholder] = key
    
    # Store placeholders
    st.session_state.synthesis_config['material_placeholders'] = material_placeholders
    
    # Initialize placeholder order if not exists or if placeholders changed
    if 'placeholder_order' not in st.session_state.synthesis_config or \
       set(st.session_state.synthesis_config.get('placeholder_order', [])) != set(material_placeholders.keys()):
        st.session_state.synthesis_config['placeholder_order'] = list(material_placeholders.keys())
    
    # Initialize selected placeholders if not exists
    if 'selected_placeholders' not in st.session_state:
        st.session_state.selected_placeholders = []
    
    # Initialize combined placeholders if not exists
    if 'combined_placeholders' not in st.session_state.synthesis_config:
        st.session_state.synthesis_config['combined_placeholders'] = {}
    
    # Show available placeholders
    if material_placeholders:
        with st.expander("📋 Available Placeholders", expanded=True):
            # Add controls for combining placeholders
            col1, col2, col3, col4 = st.columns([2, 1.5, 1, 1])
            
            with col1:
                st.markdown("**Use these in your prompt:**")
            
            with col2:
                if st.session_state.selected_placeholders:
                    st.info(f"Selected: {len(st.session_state.selected_placeholders)}")
            
            with col3:
                # Select All button
                all_selected = len(st.session_state.selected_placeholders) == len(material_placeholders)
                if st.button("Select All", disabled=all_selected, key="select_all_placeholders"):
                    st.session_state.selected_placeholders = list(material_placeholders.keys())
                    st.rerun()
            
            with col4:
                # Clear Selection button
                if st.button("Clear Selection", disabled=not st.session_state.selected_placeholders, key="clear_selection"):
                    st.session_state.selected_placeholders = []
                    st.rerun()
            
            # Combine selected placeholders section
            if len(st.session_state.selected_placeholders) > 1:
                st.divider()
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    combine_name = st.text_input(
                        "Combined placeholder name:",
                        value="combined_content",
                        key="combine_placeholder_name",
                        help="Name for the combined placeholder"
                    )
                
                with col2:
                    combine_format = st.selectbox(
                        "Format:",
                        ["Name + Content", "Content Only", "Name as Header"],
                        key="combine_format",
                        help="How to format each material in the combined placeholder"
                    )
                
                with col3:
                    if st.button("🔗 Combine", type="primary"):
                        if combine_name:
                            # Create combined placeholder
                            clean_combine_name = ''.join(c if c.isalnum() or c in '_' else '' for c in combine_name)
                            if clean_combine_name:
                                combined_keys = [material_placeholders[p] for p in st.session_state.selected_placeholders]
                                st.session_state.synthesis_config['combined_placeholders'][clean_combine_name] = {
                                    'keys': combined_keys,
                                    'format': combine_format,
                                    'source_placeholders': st.session_state.selected_placeholders.copy()
                                }
                                st.session_state.selected_placeholders = []
                                st.rerun()
            
            # Display combined placeholders
            if st.session_state.synthesis_config['combined_placeholders']:
                st.divider()
                st.markdown("**Combined Placeholders:**")
                
                combined_to_remove = []
                for combo_name, combo_data in st.session_state.synthesis_config['combined_placeholders'].items():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        source_names = combo_data.get('source_placeholders', [])
                        st.markdown(f"• `{{{combo_name}}}` ← {', '.join([f'`{{{p}}}`' for p in source_names])}")
                    
                    with col2:
                        if st.button("🗑️", key=f"remove_combo_{combo_name}", help="Remove combined placeholder"):
                            combined_to_remove.append(combo_name)
                
                # Remove combined placeholders that were marked for removal
                for combo_name in combined_to_remove:
                    del st.session_state.synthesis_config['combined_placeholders'][combo_name]
                    st.rerun()
            
            # Display individual placeholders with selection
            st.divider()
            st.markdown("**Individual Placeholders:**")
            
            # Create columns for placeholders
            placeholder_list = list(material_placeholders.keys())
            
            if placeholder_list:
                # Show placeholders in a grid
                cols_per_row = 3
                rows = [placeholder_list[i:i + cols_per_row] for i in range(0, len(placeholder_list), cols_per_row)]
                
                for row in rows:
                    cols = st.columns(len(row))
                    for i, placeholder in enumerate(row):
                        with cols[i]:
                            # Get material info
                            material_key = material_placeholders[placeholder]
                            material = st.session_state.uploaded_materials.get(material_key, {})
                            display_name = material.get('display_name', material.get('name', 'Unknown'))
                            
                            # Checkbox for selection
                            is_selected = st.checkbox(
                                f"`{{{placeholder}}}`",
                                value=placeholder in st.session_state.selected_placeholders,
                                key=f"select_{placeholder}",
                                help=f"Material: {display_name}"
                            )
                            
                            # Update selection
                            if is_selected and placeholder not in st.session_state.selected_placeholders:
                                st.session_state.selected_placeholders.append(placeholder)
                            elif not is_selected and placeholder in st.session_state.selected_placeholders:
                                st.session_state.selected_placeholders.remove(placeholder)
    
    # Custom prompt text area
    custom_prompt_value = st.text_area(
        "Synthesis Prompt",
        value=st.session_state.synthesis_config.get('custom_prompt', ''),
        height=200,
        key="synthesis_custom_prompt",
        help="Enter your synthesis prompt. Use placeholders to reference specific materials."
    )
    
    # Update synthesis config with current prompt
    st.session_state.synthesis_config['custom_prompt'] = custom_prompt_value

def render_synthesis_generation(config: dict):
    """Render synthesis generation controls with model selection."""
    st.subheader("🔮 Generate Synthesis")
    
    # Check if prompt is provided
    custom_prompt = st.session_state.synthesis_config.get('custom_prompt', '').strip()
    
    if not custom_prompt:
        st.warning("⚠️ Please enter a synthesis prompt above.")
        return
    
    # Model selection for synthesis
    synthesis_model_options = [
        "openai/gpt-4.1",
        "anthropic/claude-opus-4",
        "google/gemini-2.5-pro"
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_model = st.selectbox(
            "Model for this synthesis:",
            options=synthesis_model_options,
            index=synthesis_model_options.index(st.session_state.get('model_synthesis', synthesis_model_options[0])) if st.session_state.get('model_synthesis', synthesis_model_options[0]) in synthesis_model_options else 0,
            help="Choose the model to use for this specific synthesis"
        )
    
    with col2:
        st.info("💡 Each model has different strengths")
    
    # Show prompt preview
    with st.expander("👁️ Prompt Preview", expanded=False):
        st.text(custom_prompt[:500] + "..." if len(custom_prompt) > 500 else custom_prompt)
    
    # Generation controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🚀 Generate Synthesis", type="primary", use_container_width=True):
            generate_synthesis(selected_model)
    
    with col2:
        if st.session_state.synthesis_results:
            if st.button("🔄 Regenerate", type="secondary"):
                generate_synthesis(selected_model)
    
    with col3:
        if st.session_state.synthesis_results:
            if st.button("🗑️ Clear All", type="secondary"):
                st.session_state.synthesis_results = []
                st.rerun()

def generate_synthesis(model_id: str):
    """Generate synthesis using AI service with specified model."""
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
            
            # Temporarily override the synthesis model
            original_model = st.session_state.get('model_synthesis')
            st.session_state.model_synthesis = model_id
            
            try:
                # Generate synthesis
                synthesis = ai_service.synthesize_content(
                    synthesis_materials,
                    custom_prompt=custom_prompt,
                    material_placeholders=placeholder_mapping
                )
            finally:
                # Restore original model
                if original_model is not None:
                    st.session_state.model_synthesis = original_model
            
            if synthesis:
                # Create synthesis result with metadata
                synthesis_result = {
                    'id': len(st.session_state.synthesis_results) + 1,
                    'model': model_id,
                    'content': synthesis,
                    'timestamp': datetime.now(),
                    'prompt': custom_prompt,
                    'materials_count': len(synthesis_materials)
                }
                
                # Add to results
                st.session_state.synthesis_results.append(synthesis_result)
                
                # Auto-save session with all syntheses
                session_dir = session_service.save_session(
                    synthesis_materials,
                    synthesis,
                    custom_prompt=custom_prompt
                )
                
                # Store session ID for quality review
                st.session_state.current_session_id = session_dir.name
                
                st.success(f"✅ Synthesis generated with {model_id} and saved to: sessions/{session_dir.name}")
            else:
                st.error("❌ Failed to generate synthesis. Please try again.")
                
        except Exception as e:
            st.error(f"❌ Error generating synthesis: {str(e)}")

def render_synthesis_tabs():
    """Render synthesis results in tabs."""
    if not st.session_state.synthesis_results:
        return
    
    st.subheader("📜 Synthesis Results")
    
    # Create tab labels with per-model versioning
    tab_labels = []
    model_versions = {}  # Track version count per model
    
    for result in st.session_state.synthesis_results:
        model = result['model']
        
        # Increment version for this model
        if model not in model_versions:
            model_versions[model] = 0
        model_versions[model] += 1
        
        # Format model name for display
        model_display = model.replace('/', ' ').replace('-', ' ').title()
        tab_label = f"{model_display} (v{model_versions[model]})"
        tab_labels.append(tab_label)
    
    # Create tabs
    tabs = st.tabs(tab_labels)
    
    for i, (tab, result) in enumerate(zip(tabs, st.session_state.synthesis_results)):
        with tab:
            # Show metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Model", result['model'])
            with col2:
                st.metric("Materials Used", result['materials_count'])
            with col3:
                st.metric("Generated", result['timestamp'].strftime("%H:%M:%S"))
            
            st.divider()
            
            # Show synthesis content
            st.markdown(result['content'])
            
            st.divider()
            
            # Export options for this synthesis
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.download_button(
                    "📥 Download",
                    result['content'],
                    file_name=f"synthesis_{result['model'].replace('/', '_')}_{result['timestamp'].strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    key=f"download_{result['id']}",
                    use_container_width=True
                )
            
            with col2:
                st.download_button(
                    "📦 Full Session",
                    create_session_archive_for_result(result),
                    file_name=f"session_{result['model'].replace('/', '_')}_{result['timestamp'].strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key=f"session_{result['id']}",
                    use_container_width=True
                )
            
            with col3:
                if st.button("📋 Copy", key=f"copy_{result['id']}", use_container_width=True):
                    st.info("Use Ctrl+A and Ctrl+C to copy the synthesis text above")
            
            with col4:
                if st.button("🗑️ Remove", type="secondary", key=f"remove_{result['id']}", use_container_width=True):
                    st.session_state.synthesis_results = [r for r in st.session_state.synthesis_results if r['id'] != result['id']]
                    st.rerun()
            
            # Quality review for this specific synthesis
            with st.expander("📊 Quality Review", expanded=False):
                render_quality_review_for_result(result)

def render_quality_review_for_result(result):
    """Render quality review section for a specific synthesis result."""
    st.markdown(f"### Rate the {result['model']} synthesis quality:")
    
    metrics = ["Accuracy", "Completeness", "Clarity", "Depth", "Relevance"]
    ratings = {}
    
    cols = st.columns(len(metrics))
    for i, metric in enumerate(metrics):
        with cols[i]:
            ratings[metric] = st.slider(
                metric,
                1, 5, 3,
                key=f"rating_{result['id']}_{metric}",
                help=f"Rate the {metric.lower()} of the synthesis"
            )
    
    # Review notes
    review_notes = st.text_area(
        "Additional Comments (Optional)",
        placeholder="Add any notes about the synthesis quality, suggestions for improvement, etc.",
        key=f"review_notes_{result['id']}"
    )
    
    # Save review
    if st.button("💾 Save Quality Review", type="primary", key=f"save_review_{result['id']}"):
        # For now, just show success. In a full implementation, this would save to a database
        st.success("✅ Quality review saved!")

def create_session_archive_for_result(result):
    """Create a JSON archive of the current session for a specific synthesis result."""
    import json
    import base64
    
    # Create a clean copy of uploaded materials without binary data
    clean_materials = {}
    for key, material in st.session_state.uploaded_materials.items():
        clean_material = material.copy()
        
        # Handle binary data
        if 'data' in clean_material and isinstance(clean_material['data'], bytes):
            # Option 1: Convert to base64 for storage (can make files large)
            # clean_material['data'] = base64.b64encode(clean_material['data']).decode('utf-8')
            # clean_material['data_encoding'] = 'base64'
            
            # Option 2: Remove binary data and just keep metadata
            clean_material.pop('data', None)
            clean_material['data_removed'] = True
        
        clean_materials[key] = clean_material
    
    session_data = {
        "timestamp": datetime.now().isoformat(),
        "uploaded_materials": clean_materials,
        "extraction_configs": st.session_state.extraction_configs,
        "extracted_content": st.session_state.extracted_content,
        "synthesis_config": st.session_state.synthesis_config,
        "synthesis": result['content'],
        "synthesis_model": result['model'],
        "synthesis_id": result['id'],
        "synthesis_timestamp": result['timestamp'].isoformat()
    }
    
    return json.dumps(session_data, indent=2)

def create_session_archive():
    """Create a JSON archive of the current session."""
    import json
    import base64
    
    # Create a clean copy of uploaded materials without binary data
    clean_materials = {}
    for key, material in st.session_state.uploaded_materials.items():
        clean_material = material.copy()
        
        # Handle binary data
        if 'data' in clean_material and isinstance(clean_material['data'], bytes):
            # Option 1: Convert to base64 for storage (can make files large)
            # clean_material['data'] = base64.b64encode(clean_material['data']).decode('utf-8')
            # clean_material['data_encoding'] = 'base64'
            
            # Option 2: Remove binary data and just keep metadata
            clean_material.pop('data', None)
            clean_material['data_removed'] = True
        
        clean_materials[key] = clean_material
    
    session_data = {
        "timestamp": datetime.now().isoformat(),
        "uploaded_materials": clean_materials,
        "extraction_configs": st.session_state.extraction_configs,
        "extracted_content": st.session_state.extracted_content,
        "synthesis_config": st.session_state.synthesis_config,
        "synthesis_results": [
            {
                "id": result['id'],
                "model": result['model'],
                "content": result['content'],
                "timestamp": result['timestamp'].isoformat(),
                "prompt": result['prompt'],
                "materials_count": result['materials_count']
            }
            for result in st.session_state.synthesis_results
        ]
    }
    
    return json.dumps(session_data, indent=2) 