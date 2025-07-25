"""
Synthesis Phase UI Component
Handles prompt creation, synthesis generation, and quality review
"""

import streamlit as st
from datetime import datetime
from urllib.parse import urlparse
from services.ai_service import ai_service
from services.session import session_service
from services.prompt_management import prompt_workspace_service
from services.materials_workspace import materials_workspace_service

def render_synthesis_phase(config: dict):
    """Render the synthesis phase interface."""
    st.header("✨ Phase 4: Synthesize")
    st.markdown("Create a hermetic synthesis from your extracted materials.")
    
    # Initialize synthesis state
    if 'workspace_extractions' not in st.session_state:
        st.session_state.workspace_extractions = {}
    
    # Tab selection for content source
    tab1, tab2 = st.tabs(["📚 Project Materials", "🔍 Materials Workspace"])
    
    with tab1:
        if not st.session_state.extracted_content:
            st.warning("⚠️ No extracted content found. Please extract materials in Phase 3 first.")
            return
        else:
            st.info(f"Using {len(st.session_state.extracted_content)} extractions from current project")
    
    with tab2:
        render_workspace_extraction_selector()
    
    # Check if we have any content to synthesize
    total_content = len(st.session_state.extracted_content) + len(st.session_state.workspace_extractions)
    if total_content == 0:
        st.warning("⚠️ No content selected for synthesis. Please select materials from either the current project or the Materials Workspace.")
        return
    
    st.divider()
    
    # Synthesis configuration
    render_synthesis_config()
    
    st.divider()
    
    # Generate synthesis
    render_synthesis_generation(config)
    
    # Display synthesis results in tabs
    if st.session_state.synthesis_results:
        st.divider()
        render_synthesis_tabs()

def render_workspace_extraction_selector():
    """Render extraction selector from Materials Workspace."""
    st.subheader("Select Extractions from Materials Workspace")
    
    # Get all extractions from workspace
    all_extractions = materials_workspace_service.list_extractions()
    
    if not all_extractions:
        st.info("No extractions available in the Materials Workspace. Add and extract materials there first.")
        return
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search extractions...", placeholder="Search by material name or content")
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Filter extractions based on search
    if search_query:
        filtered_extractions = []
        for ext in all_extractions:
            # Search in material name and content
            if (search_query.lower() in ext.get('material_name', '').lower() or
                search_query.lower() in ext.get('config_summary', '').lower()):
                filtered_extractions.append(ext)
            else:
                # Check content
                full_extraction = materials_workspace_service.get_extraction(ext['id'])
                if full_extraction and search_query.lower() in full_extraction.get('content', '').lower():
                    filtered_extractions.append(ext)
    else:
        filtered_extractions = all_extractions
    
    st.caption(f"Found {len(filtered_extractions)} extractions")
    
    # Display extractions with selection
    selected_count = len(st.session_state.workspace_extractions)
    if selected_count > 0:
        st.success(f"✅ {selected_count} extractions selected")
    
    # Bulk actions
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Select All", disabled=len(filtered_extractions) == 0):
            for ext in filtered_extractions:
                from ui.materials_workspace import get_extraction_for_synthesis
                extraction_data = get_extraction_for_synthesis(ext['id'])
                if extraction_data:
                    key = f"workspace_{ext['id']}"
                    st.session_state.workspace_extractions[key] = extraction_data
            st.rerun()
    
    with col2:
        if st.button("Clear Selection", disabled=selected_count == 0):
            st.session_state.workspace_extractions = {}
            st.rerun()
    
    # Display extractions
    for ext in filtered_extractions:
        with st.container():
            col1, col2, col3, col4 = st.columns([0.5, 3, 2, 1])
            
            key = f"workspace_{ext['id']}"
            is_selected = key in st.session_state.workspace_extractions
            
            with col1:
                # Checkbox for selection
                if st.checkbox("", value=is_selected, key=f"select_ext_{ext['id']}"):
                    if not is_selected:
                        # Add to selection
                        from ui.materials_workspace import get_extraction_for_synthesis
                        extraction_data = get_extraction_for_synthesis(ext['id'])
                        if extraction_data:
                            st.session_state.workspace_extractions[key] = extraction_data
                else:
                    if is_selected:
                        # Remove from selection
                        del st.session_state.workspace_extractions[key]
            
            with col2:
                st.markdown(f"**{ext.get('material_name', 'Unknown')}**")
                st.caption(f"{ext.get('config_summary', 'Default extraction')}")
            
            with col3:
                st.caption(f"{ext.get('word_count', 0):,} words")
                st.caption(f"Created: {ext.get('created_at', '')[:10]}")
            
            with col4:
                if st.button("👁️ Preview", key=f"preview_ext_{ext['id']}"):
                    with st.expander("Extraction Preview", expanded=True):
                        full_extraction = materials_workspace_service.get_extraction(ext['id'])
                        if full_extraction:
                            st.text_area("", full_extraction['content'][:1000] + "...", height=200, disabled=True)
                        else:
                            st.error("Could not load extraction")

def render_synthesis_config():
    """Render synthesis configuration section."""
    st.subheader("📝 Synthesis Configuration")
    
    # Template selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Get active workspace
        active_workspace = prompt_workspace_service.get_active_workspace()
        
        template_options = {"Custom": ""}
        
        if active_workspace:
            # Get synthesis prompts from workspace
            synthesis_prompts = active_workspace["prompts"].get("synthesis", {})
            active_prompts = {pid: p for pid, p in synthesis_prompts.items() if p.get("active", True)}
            
            # Group prompts by category
            prompts_by_category = {}
            for pid, prompt in active_prompts.items():
                category = prompt.get("category", "Uncategorized") 
                prompt_name = f"[{category}] {prompt['name']}"
                template_options[prompt_name] = {
                    "content": prompt['content'],
                    "id": pid,
                    "metadata": prompt.get('metadata', {})
                }
        
        template_names = list(template_options.keys())
        selected_template = st.selectbox(
            "Prompt Template",
            template_names,
            help="Select a template from your workspace or choose 'Custom' to write your own"
        )
    
    with col2:
        st.info("💡 Use placeholders to reference specific materials")
        if not active_workspace:
            if st.button("Go to Prompts", key="goto_prompts_synthesis"):
                st.session_state.view_mode = 'prompts'
                st.rerun()
    
    # Load template if selected
    if selected_template != "Custom":
        template_data = template_options[selected_template]
        if isinstance(template_data, dict):
            template_text = template_data["content"]
            
            # Show metadata if available
            if template_data.get('metadata'):
                metadata = template_data['metadata']
                if metadata.get('author') or metadata.get('tags'):
                    with st.expander("Template Details", expanded=False):
                        if metadata.get('author'):
                            st.write(f"**Author:** {metadata['author']}")
                        if metadata.get('tags'):
                            tags = metadata['tags'] if isinstance(metadata['tags'], list) else [metadata['tags']]
                            st.write(f"**Tags:** {', '.join(tags)}")
                        if metadata.get('version_notes'):
                            st.write(f"**Notes:** {metadata['version_notes']}")
        else:
            template_text = template_data
            
        if st.button("Load Template", key="load_synthesis_template"):
            st.session_state.synthesis_config['custom_prompt'] = template_text
            if isinstance(template_data, dict):
                st.session_state.synthesis_config['prompt_id'] = template_data["id"]
                st.session_state.synthesis_config['prompt_workspace_id'] = active_workspace['id']
            st.rerun()
    
    # Generate material placeholders for both project and workspace materials
    material_placeholders = {}
    url_counters = {}  # Track URLs per site
    
    # Process project materials
    for i, (key, material) in enumerate(st.session_state.uploaded_materials.items()):
        if key in st.session_state.extracted_content:
            placeholder = _generate_placeholder_for_material(material, url_counters, material_placeholders)
            material_placeholders[placeholder] = key
    
    # Process workspace extractions
    for key, extraction_data in st.session_state.workspace_extractions.items():
        # Create a material-like structure for placeholder generation
        material = {
            'type': 'workspace',
            'name': extraction_data['material_name'],
            'display_name': extraction_data['material_name']
        }
        placeholder = _generate_placeholder_for_material(material, url_counters, material_placeholders)
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
                    source_names = combo_data.get('source_placeholders', [])
                    
                    # Create an expander for each combined placeholder
                    with st.expander(f"`{{{combo_name}}}` ({len(source_names)} placeholders)", expanded=True):
                        col1, col2 = st.columns([5, 1])
                        
                        with col1:
                            # Display format info
                            format_type = combo_data.get('format', 'Name + Content')
                            st.info(f"📋 Format: {format_type}")
                            
                            # Display source placeholders in a more readable format
                            st.markdown("**Source placeholders:**")
                            
                            # Show placeholders in a grid for better visibility
                            if len(source_names) <= 10:
                                # For smaller lists, show all in columns
                                cols_per_row = min(3, len(source_names))
                                rows = [source_names[i:i + cols_per_row] for i in range(0, len(source_names), cols_per_row)]
                                
                                for row in rows:
                                    cols = st.columns(len(row))
                                    for i, placeholder in enumerate(row):
                                        with cols[i]:
                                            st.code(f"{{{placeholder}}}", language=None)
                            else:
                                # For larger lists, show in a scrollable container
                                placeholder_display = "  \n".join([f"• `{{{p}}}`" for p in source_names])
                                st.markdown(placeholder_display, unsafe_allow_html=True)
                        
                        with col2:
                            if st.button("🗑️ Remove", key=f"remove_combo_{combo_name}", 
                                       help="Remove this combined placeholder", use_container_width=True):
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
        "google/gemini-2.5-pro",
        "x-ai/grok-4"
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
                
                # Save project state after clearing results
                if st.session_state.current_project_id:
                    from services.project import project_service
                    from utils.helpers import get_project_state
                    
                    project_service.save_project_state(
                        st.session_state.current_project_id,
                        get_project_state()
                    )
                
                st.rerun()

def generate_synthesis(model_id: str):
    """Generate synthesis using AI service with specified model."""
    with st.spinner("🌟 Consulting the cosmic wisdom..."):
        try:
            # Prepare materials for synthesis
            synthesis_materials = {}
            name_counters = {}  # Track duplicate names to ensure uniqueness
            
            # Map extracted content from project to material display names
            for key, content in st.session_state.extracted_content.items():
                material = st.session_state.uploaded_materials.get(key, {})
                # Use display_name for consistency
                base_name = material.get('display_name', material.get('name', key))
                
                # For URLs, include more context in the name if it's just a domain
                if material.get('type') == 'url' and material.get('url'):
                    # If display_name is just a domain, append path info
                    parsed_url = urlparse(material['url'])
                    
                    # Check if display_name is just the domain
                    if base_name == parsed_url.netloc:
                        # Extract meaningful path or query info
                        path_parts = parsed_url.path.strip('/').split('/')
                        if path_parts and path_parts[0]:
                            # For very long paths, include more segments to ensure uniqueness
                            if len(path_parts) >= 3:
                                # Include at least 2 path segments for deep URLs
                                base_name = f"{base_name}/{path_parts[0]}/{path_parts[1]}"
                                if len(path_parts) > 2:
                                    # Add the last segment if it's different from the second
                                    if path_parts[-1] != path_parts[1]:
                                        base_name += f"/.../{path_parts[-1]}"
                                    else:
                                        base_name += "/..."
                            else:
                                # Use the first meaningful path segment
                                base_name = f"{base_name}/{path_parts[0]}"
                                if len(path_parts) > 1:
                                    base_name += "/..."
                        elif parsed_url.query:
                            # Use query parameter if no path
                            base_name = f"{base_name}?{parsed_url.query[:30]}..."
                
                # Ensure unique names
                material_name = base_name
                if material_name in synthesis_materials:
                    # Track how many times we've seen this name
                    if material_name not in name_counters:
                        name_counters[material_name] = 1
                    name_counters[material_name] += 1
                    # Append counter to make it unique
                    material_name = f"{base_name} ({name_counters[material_name]})"
                
                synthesis_materials[material_name] = content
            
            # Add workspace extractions
            for key, extraction_data in st.session_state.workspace_extractions.items():
                base_name = extraction_data['material_name']
                
                # Ensure unique names
                material_name = base_name
                if material_name in synthesis_materials:
                    # Track how many times we've seen this name
                    if material_name not in name_counters:
                        name_counters[material_name] = 1
                    name_counters[material_name] += 1
                    # Append identifier to make it unique
                    material_name = f"{base_name} (Workspace {name_counters[material_name]})"
                
                synthesis_materials[material_name] = extraction_data['content']
            
            # Get synthesis configuration
            custom_prompt = st.session_state.synthesis_config.get('custom_prompt', '')
            material_placeholders = st.session_state.synthesis_config.get('material_placeholders', {})
            
            # Create placeholder mapping for AI service
            placeholder_mapping = {}
            name_counters_for_placeholders = {}  # Track duplicate names for placeholder mapping
            
            for placeholder, key in material_placeholders.items():
                if key.startswith('workspace_'):
                    # Handle workspace extractions
                    extraction_data = st.session_state.workspace_extractions.get(key, {})
                    base_name = extraction_data.get('material_name', key)
                else:
                    # Handle project materials
                    material = st.session_state.uploaded_materials.get(key, {})
                    base_name = material.get('display_name', material.get('name', key))
                    
                    # For URLs, include more context in the name if it's just a domain
                    if material.get('type') == 'url' and material.get('url'):
                        parsed_url = urlparse(material['url'])
                        
                        # Check if display_name is just the domain
                        if base_name == parsed_url.netloc:
                            # Extract meaningful path or query info
                            path_parts = parsed_url.path.strip('/').split('/')
                            if path_parts and path_parts[0]:
                                # For very long paths, include more segments to ensure uniqueness
                                if len(path_parts) >= 3:
                                    # Include at least 2 path segments for deep URLs
                                    base_name = f"{base_name}/{path_parts[0]}/{path_parts[1]}"
                                    if len(path_parts) > 2:
                                        # Add the last segment if it's different from the second
                                        if path_parts[-1] != path_parts[1]:
                                            base_name += f"/.../{path_parts[-1]}"
                                        else:
                                            base_name += "/..."
                                else:
                                    # Use the first meaningful path segment
                                    base_name = f"{base_name}/{path_parts[0]}"
                                    if len(path_parts) > 1:
                                        base_name += "/..."
                            elif parsed_url.query:
                                # Use query parameter if no path
                                base_name = f"{base_name}?{parsed_url.query[:30]}..."
                
                # Find the actual unique name used in synthesis_materials
                material_name = None
                for name in synthesis_materials.keys():
                    # Check if this is the material we're looking for
                    if name == base_name or name.startswith(f"{base_name} ("):
                        # Additional check to ensure it's the right material
                        if key.startswith('workspace_'):
                            if 'Workspace' in name:
                                material_name = name
                                break
                        else:
                            material_name = name
                            # Don't break here, keep looking for exact match
                            if name == base_name:
                                break
                
                if material_name:
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
                    'materials_count': len(synthesis_materials),
                    'workspace_extractions_count': len(st.session_state.workspace_extractions)
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
                
                # Save project state to persist synthesis results
                if st.session_state.current_project_id:
                    from services.project import project_service
                    from utils.helpers import get_project_state
                    
                    project_service.save_project_state(
                        st.session_state.current_project_id,
                        get_project_state()
                    )
                
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
                    
                    # Save project state after removing a result
                    if st.session_state.current_project_id:
                        from services.project import project_service
                        from utils.helpers import get_project_state
                        
                        project_service.save_project_state(
                            st.session_state.current_project_id,
                            get_project_state()
                        )
                    
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

def _generate_placeholder_for_material(material, url_counters, existing_placeholders):
    """Generate a unique placeholder for a material."""
    material_type = material.get('type', '')
    
    if material_type == 'url':
        # Extract domain from URL
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
        # Remove the 30 character limit to preserve uniqueness
        clean_name = clean_name.replace(' ', '_').lower()
        placeholder = clean_name
        
    elif material_type == 'youtube':
        # Extract video ID for placeholder
        display_name = material.get('display_name', 'youtube')
        clean_name = display_name.replace('YouTube: ', '').replace('-', '_').lower()
        # Clean name for placeholder consistency
        clean_name = ''.join(c if c.isalnum() or c in ' -_' else '' for c in clean_name)
        clean_name = clean_name.replace(' ', '_')
        placeholder = f"youtube_{clean_name}"
        
    elif material_type == 'workspace':
        # Handle workspace extractions
        display_name = material.get('display_name', material.get('name', 'workspace'))
        clean_name = ''.join(c if c.isalnum() or c in ' -_' else '' for c in display_name)
        clean_name = clean_name.replace(' ', '_').lower()
        placeholder = f"ws_{clean_name}"
        
    else:
        # Default handling for other types
        display_name = material.get('display_name', material['name'])
        clean_name = ''.join(c if c.isalnum() or c in ' -_' else '' for c in display_name)
        clean_name = clean_name.replace(' ', '_').lower()
        placeholder = clean_name
    
    # Ensure unique placeholders
    base_placeholder = placeholder
    counter = 1
    while placeholder in existing_placeholders:
        placeholder = f"{base_placeholder}_{counter}"
        counter += 1
    
    return placeholder 