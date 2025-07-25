"""
Extraction Configuration Phase UI Component
Allows users to configure extraction settings for each uploaded material
"""

import streamlit as st
import io
from services.extraction import extraction_service
from PIL import Image
from config.extraction_prompts import get_prompt_categories, get_prompts_for_category
from services.prompt_management import prompt_workspace_service

def render_extraction_config_phase():
    """Render the extraction configuration phase interface."""
    st.header("⚙️ Phase 2: Configure Extraction")
    st.markdown("Configure how each material should be processed and extracted.")
    
    if not st.session_state.uploaded_materials:
        st.warning("⚠️ No materials uploaded. Please upload materials in Phase 1 first.")
        return
    
    # Global extraction settings
    with st.expander("🌐 Global Extraction Settings", expanded=False):
        render_global_settings()
    
    st.divider()
    
    # Material-specific configurations
    st.subheader("📋 Material-Specific Settings")
    
    # Process each uploaded material
    for key, material in st.session_state.uploaded_materials.items():
        display_name = material.get('display_name', material['name'])
        with st.expander(f"⚙️ {display_name}", expanded=True):
            render_material_config(key, material)
    
    # Configuration summary
    st.divider()
    render_config_summary()

def render_global_settings():
    """Render global extraction settings."""
    col1, col2 = st.columns(2)
    
    with col1:
        use_ai_cleaning = st.checkbox(
            "🧹 Use AI cleaning for all materials",
            value=True,
            help="Apply AI cleaning to improve text quality"
        )
    
    # Store global settings
    if 'global_extraction_settings' not in st.session_state:
        st.session_state.global_extraction_settings = {}
    
    st.session_state.global_extraction_settings.update({
        'use_ai_cleaning': use_ai_cleaning
    })

def render_material_config(key: str, material: dict):
    """Render configuration options for a specific material."""
    material_type = material['type']
    
    # Initialize config if not exists
    if key not in st.session_state.extraction_configs:
        st.session_state.extraction_configs[key] = {}
    
    config = st.session_state.extraction_configs[key]
    
    # Add disable toggle at the top
    st.markdown("**🔧 Extraction Settings**")
    disabled = st.checkbox(
        "🚫 Skip extraction for this material",
        value=config.get('disabled', False),
        key=f"disable_{key}",
        help="When enabled, this material will be skipped during extraction"
    )
    config['disabled'] = disabled
    
    if disabled:
        st.info("⚠️ This material will be skipped during extraction. You can still include it in synthesis.")
        st.divider()
        return
    
    # Check if this is an image file
    is_image = (material_type == 'file' and 
                'image' in material.get('file_type', ''))
    
    if is_image:
        # Create two columns for side-by-side layout
        col1, col2 = st.columns([0.1, 0.9])
        
        with col1:
            # Display the image
            st.markdown("**🖼️ Image**")
            try:
                image = Image.open(io.BytesIO(material['data']))
                # Resize image if too large while maintaining aspect ratio
                max_width = 500
                width, height = image.size
                if width > max_width:
                    ratio = max_width / width
                    new_height = int(height * ratio)
                    image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                st.image(image, caption=material.get('display_name', material['name']))
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")
        
        with col2:
            # Display extraction options
            st.markdown("**📝 Extraction Instructions**")
            render_extraction_prompt_options(key, config)
            
            # Other common options
            st.markdown("---")
            render_ai_cleaning_options(key, config)
    else:
        # Original layout for non-image materials
        if material_type == 'file':
            render_file_config(key, material, config)
        elif material_type == 'url':
            render_url_config(key, material, config)
        elif material_type == 'youtube':
            render_youtube_config(key, material, config)
        
        # Common options for all non-image types
        st.markdown("---")
        render_common_options(key, config)

def render_file_config(key: str, material: dict, config: dict):
    """Render configuration for file materials."""
    file_type = material.get('file_type', '')
    
    if 'pdf' in file_type:
        st.markdown("**📄 PDF Extraction Settings**")
        
        # Get PDF info
        try:
            pdf_data = io.BytesIO(material['data'])
            pdf_info = extraction_service.get_pdf_info(pdf_data)
            
            if pdf_info:
                total_pages = pdf_info['total_pages']
                st.info(f"Total pages: {total_pages}")
                
                # Page range selection
                use_range = st.checkbox(
                    "Select specific pages",
                    key=f"use_range_{key}",
                    value=config.get('use_page_range', False)
                )
                
                if use_range:
                    # Initialize page ranges if not exists
                    if 'page_ranges' not in config:
                        config['page_ranges'] = [(1, min(10, total_pages))]
                    
                    st.markdown("**Page Ranges** (e.g., 1-10, 15-20, 25)")
                    
                    # Display existing ranges
                    ranges_to_remove = []
                    for i, (start, end) in enumerate(config['page_ranges']):
                        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                        with col1:
                            new_start = st.number_input(
                                f"Start",
                                min_value=1,
                                max_value=total_pages,
                                value=start,
                                key=f"start_{key}_{i}"
                            )
                        with col2:
                            new_end = st.number_input(
                                f"End",
                                min_value=new_start,
                                max_value=total_pages,
                                value=end,
                                key=f"end_{key}_{i}"
                            )
                        with col3:
                            st.write(f"Pages: {new_end - new_start + 1}")
                        with col4:
                            if st.button("❌", key=f"remove_range_{key}_{i}"):
                                ranges_to_remove.append(i)
                        
                        # Update range
                        config['page_ranges'][i] = (new_start, new_end)
                    
                    # Remove marked ranges
                    for i in reversed(ranges_to_remove):
                        config['page_ranges'].pop(i)
                    
                    # Add new range button
                    if st.button("➕ Add Page Range", key=f"add_range_{key}"):
                        last_end = config['page_ranges'][-1][1] if config['page_ranges'] else 0
                        new_start = min(last_end + 1, total_pages)
                        new_end = min(new_start + 9, total_pages)
                        config['page_ranges'].append((new_start, new_end))
                        st.rerun()
                    
                    # Quick presets
                    st.markdown("**Quick Presets:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("First 10 pages", key=f"preset1_{key}"):
                            config['page_ranges'] = [(1, min(10, total_pages))]
                            st.rerun()
                    with col2:
                        if st.button("First 50 pages", key=f"preset2_{key}"):
                            config['page_ranges'] = [(1, min(50, total_pages))]
                            st.rerun()
                    with col3:
                        if st.button("All pages", key=f"preset3_{key}"):
                            config['page_ranges'] = [(1, total_pages)]
                            st.rerun()
                    
                    # Show total pages to be extracted
                    total_pages_to_extract = sum(end - start + 1 for start, end in config['page_ranges'])
                    st.success(f"Total pages to extract: {total_pages_to_extract}")
                    
                    config['use_page_range'] = True
                else:
                    config['use_page_range'] = False
                    config.pop('page_ranges', None)
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
    
    elif 'text' in file_type:
        st.markdown("**📝 Text File Settings**")
        st.info("Text files will be processed as-is")

def render_url_config(key: str, material: dict, config: dict):
    """Render configuration for URL materials."""
    st.markdown("**🌐 Web Scraping Settings**")
    
    extraction_method = st.selectbox(
        "Content extraction method",
        ["main_content", "full_page", "custom_selector"],
        index=["main_content", "full_page", "custom_selector"].index(
            config.get('extraction_method', 'main_content')
        ),
        key=f"url_method_{key}",
        help="Choose how to extract content from the webpage"
    )
    config['extraction_method'] = extraction_method
    
    if extraction_method == "custom_selector":
        css_selector = st.text_input(
            "CSS selector",
            value=config.get('css_selector', ''),
            placeholder="article, .content, #main",
            key=f"css_{key}",
            help="Enter CSS selector to target specific content"
        )
        config['css_selector'] = css_selector

def render_youtube_config(key: str, material: dict, config: dict):
    """Render configuration for YouTube materials."""
    st.markdown("**📺 YouTube Transcript Settings**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        transcript_type = st.selectbox(
            "Transcript preference",
            ["any", "manual", "auto"],
            index=["any", "manual", "auto"].index(
                config.get('transcript_type', 'any')
            ),
            key=f"yt_type_{key}",
            help="Choose transcript type preference"
        )
        config['transcript_type'] = transcript_type
    
    with col2:
        language = st.text_input(
            "Language code (optional)",
            value=config.get('language', ''),
            placeholder="en, es, fr, etc.",
            key=f"yt_lang_{key}",
            help="Specify language code for transcript"
        )
        config['language'] = language
    
    summarize = st.checkbox(
        "📝 Summarize transcript",
        value=config.get('summarize', False),
        key=f"yt_summarize_{key}",
        help="Create a summary instead of full transcript"
    )
    config['summarize'] = summarize

def render_extraction_prompt_options(key: str, config: dict):
    """Render extraction prompt selection options."""
    prompt_mode = st.radio(
        "Prompt mode",
        ["Workspace Prompts", "Custom"],
        key=f"prompt_mode_{key}",
        horizontal=True,
        help="Choose prompts from your workspace or write your own"
    )
    
    if prompt_mode == "Workspace Prompts":
        # Get active workspace
        active_workspace = prompt_workspace_service.get_active_workspace()
        
        if not active_workspace:
            st.warning("No active prompt workspace. Please create or activate a workspace first.")
            if st.button("Go to Prompt Workspace", key=f"goto_prompts_{key}"):
                st.session_state.view_mode = 'prompts'
                st.rerun()
            return
        
        # Get extraction prompts from workspace
        extraction_prompts = active_workspace["prompts"].get("extraction", {})
        active_prompts = {pid: p for pid, p in extraction_prompts.items() if p.get("active", True)}
        
        if not active_prompts:
            st.info("No extraction prompts in the active workspace. Add some in the Prompt Workspace.")
            return
        
        # Group prompts by category
        prompts_by_category = {}
        for pid, prompt in active_prompts.items():
            category = prompt.get("category", "Uncategorized")
            if category not in prompts_by_category:
                prompts_by_category[category] = []
            prompts_by_category[category].append((pid, prompt))
        
        # Category selection
        categories = list(prompts_by_category.keys())
        material = st.session_state.uploaded_materials[key]
        
        # Auto-select category based on material type
        default_category = "General"
        if material['type'] == 'file' and 'image' in material.get('file_type', ''):
            default_category = "Images" if "Images" in categories else default_category
        elif material['type'] == 'url':
            default_category = "Web Content" if "Web Content" in categories else default_category
        elif material['type'] == 'youtube':
            default_category = "Video/Audio" if "Video/Audio" in categories else default_category
        
        category = st.selectbox(
            "Category",
            categories,
            index=categories.index(default_category) if default_category in categories else 0,
            key=f"prompt_category_{key}"
        )
        
        # Prompt selection within category
        prompts_in_category = prompts_by_category[category]
        if prompts_in_category:
            prompt_names = [p[1]['name'] for p in prompts_in_category]
            prompt_ids = [p[0] for p in prompts_in_category]
            
            selected_idx = st.selectbox(
                "Select prompt",
                range(len(prompt_names)),
                format_func=lambda x: prompt_names[x],
                key=f"prompt_select_{key}"
            )
            
            selected_prompt_id = prompt_ids[selected_idx]
            selected_prompt = prompts_in_category[selected_idx][1]
            
            # Show the actual prompt
            st.info(f"**Prompt:** {selected_prompt['content']}")
            
            # Show metadata if available
            if selected_prompt.get('metadata'):
                metadata = selected_prompt['metadata']
                if metadata.get('author') or metadata.get('tags'):
                    with st.expander("Prompt Details", expanded=False):
                        if metadata.get('author'):
                            st.write(f"**Author:** {metadata['author']}")
                        if metadata.get('tags'):
                            tags = metadata['tags'] if isinstance(metadata['tags'], list) else [metadata['tags']]
                            st.write(f"**Tags:** {', '.join(tags)}")
                        if metadata.get('version_notes'):
                            st.write(f"**Notes:** {metadata['version_notes']}")
            
            # Store the prompt
            config['extraction_prompt'] = selected_prompt['content']
            config['prompt_category'] = category
            config['prompt_name'] = selected_prompt['name']
            config['prompt_id'] = selected_prompt_id
            config['prompt_workspace_id'] = active_workspace['id']
    else:
        # Custom prompt
        custom_prompt = st.text_area(
            "Custom extraction prompt",
            value=config.get('extraction_prompt', "Extract all relevant content from this material."),
            key=f"custom_prompt_{key}",
            help="Write your own extraction instructions",
            height=100
        )
        config['extraction_prompt'] = custom_prompt
        config.pop('prompt_category', None)
        config.pop('prompt_name', None)
        config.pop('prompt_id', None)
        config.pop('prompt_workspace_id', None)

def render_ai_cleaning_options(key: str, config: dict):
    """Render AI cleaning options."""
    global_settings = st.session_state.get('global_extraction_settings', {})
    
    use_ai_cleaning = st.checkbox(
        "🧹 Clean with AI",
        value=config.get('use_ai_cleaning', global_settings.get('use_ai_cleaning', True)),
        key=f"clean_{key}",
        help="Use AI to clean and structure the extracted text"
    )
    config['use_ai_cleaning'] = use_ai_cleaning
    
    # Hard-code the context for hermetic and esoteric text
    if use_ai_cleaning:
        config['context'] = 'hermetic and esoteric text'
    
    # Save config
    st.session_state.extraction_configs[key] = config

def render_common_options(key: str, config: dict):
    """Render common extraction options."""
    # Extraction prompt selection
    st.markdown("**📝 Extraction Instructions**")
    render_extraction_prompt_options(key, config)
    
    st.markdown("---")
    
    # AI cleaning options
    render_ai_cleaning_options(key, config)

def render_config_summary():
    """Render configuration summary."""
    st.subheader("📊 Configuration Summary")
    
    configured = len(st.session_state.extraction_configs)
    total = len(st.session_state.uploaded_materials)
    disabled_count = sum(
        1 for config in st.session_state.extraction_configs.values()
        if config.get('disabled', False)
    )
    enabled_count = configured - disabled_count
    
    if configured == total:
        if disabled_count == 0:
            st.success(f"✅ All {total} materials configured and enabled")
        else:
            st.success(f"✅ All {total} materials configured ({enabled_count} enabled, {disabled_count} disabled)")
    else:
        st.warning(f"⚠️ {configured}/{total} materials configured ({enabled_count} enabled, {disabled_count} disabled)")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ai_cleaning_count = sum(
            1 for config in st.session_state.extraction_configs.values()
            if config.get('use_ai_cleaning', False) and not config.get('disabled', False)
        )
        st.metric("AI Cleaning", f"{ai_cleaning_count} materials")
    
    with col2:
        pdf_count = sum(
            1 for key, material in st.session_state.uploaded_materials.items()
            if material['type'] == 'file' and 'pdf' in material.get('file_type', '')
            and key in st.session_state.extraction_configs
            and not st.session_state.extraction_configs[key].get('disabled', False)
        )
        st.metric("PDFs", f"{pdf_count} files")
    
    with col3:
        web_count = sum(
            1 for key, material in st.session_state.uploaded_materials.items()
            if material['type'] in ['url', 'youtube']
            and key in st.session_state.extraction_configs
            and not st.session_state.extraction_configs[key].get('disabled', False)
        )
        st.metric("Web Sources", f"{web_count} sources")
    
    with col4:
        st.metric("Disabled", f"{disabled_count} materials") 