"""
Extraction Phase UI Component
Executes the extraction process based on configured settings
"""

import streamlit as st
import io
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.extraction import extraction_service

def render_extraction_phase():
    """Render the extraction phase interface."""
    st.header("🔍 Phase 3: Extract Content")
    st.markdown("Extract content from your materials using the configured settings.")
    
    if not st.session_state.uploaded_materials:
        st.warning("⚠️ No materials uploaded. Please start from Phase 1.")
        return
    
    if not st.session_state.extraction_configs:
        st.warning("⚠️ No extraction configurations found. Please configure in Phase 2.")
        return
    
    # Extraction control panel
    render_extraction_controls()
    
    st.divider()
    
    # Extraction status and results
    render_extraction_results()

def render_extraction_controls():
    """Render extraction control panel."""
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        # Count materials ready for extraction
        total_configured = len([
            key for key in st.session_state.uploaded_materials
            if key in st.session_state.extraction_configs
        ])
        
        disabled_count = len([
            key for key in st.session_state.uploaded_materials
            if key in st.session_state.extraction_configs
            and st.session_state.extraction_configs[key].get('disabled', False)
        ])
        
        ready_count = total_configured - disabled_count
        extracted_count = len(st.session_state.extracted_content)
        
        st.metric(
            "Ready for Extraction",
            f"{ready_count - extracted_count} materials",
            f"{extracted_count} extracted, {disabled_count} disabled"
        )
    
    with col2:
        extract_all = st.button(
            "🚀 Extract All",
            type="primary",
            disabled=(ready_count == extracted_count),
            help="Extract content from all configured materials (excluding disabled ones)"
        )
    
    with col3:
        parallel_extraction = st.checkbox(
            "⚡ Parallel",
            value=True,
            help="Extract materials in parallel for faster processing"
        )
    
    with col4:
        if extracted_count > 0:
            if st.button("🔄 Re-extract All", type="secondary"):
                st.session_state.extracted_content.clear()
                st.rerun()
    
    # Handle extraction
    if extract_all:
        if parallel_extraction:
            extract_all_materials_parallel()
        else:
            extract_all_materials()

def extract_all_materials():
    """Extract content from all configured materials sequentially."""
    progress_container = st.container()
    
    with progress_container:
        materials_to_extract = [
            (key, material) for key, material in st.session_state.uploaded_materials.items()
            if key in st.session_state.extraction_configs 
            and key not in st.session_state.extracted_content
            and not st.session_state.extraction_configs[key].get('disabled', False)
        ]
        
        if not materials_to_extract:
            st.info("All materials have already been extracted or are disabled.")
            return
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (key, material) in enumerate(materials_to_extract):
            display_name = material.get('display_name', material['name'])
            status_text.text(f"Extracting: {display_name}...")
            
            # Extract based on material type
            extracted_text = extract_single_material(key, material)
            
            if extracted_text:
                st.session_state.extracted_content[key] = extracted_text
                st.success(f"✅ Extracted: {display_name}")
            else:
                st.error(f"❌ Failed to extract: {display_name}")
            
            # Update progress
            progress = (i + 1) / len(materials_to_extract)
            progress_bar.progress(progress)
        
        status_text.text("✅ Extraction complete!")
        time.sleep(1)
        st.rerun()

def extract_all_materials_parallel():
    """Extract content from all configured materials in parallel."""
    progress_container = st.container()
    
    with progress_container:
        materials_to_extract = [
            (key, material) for key, material in st.session_state.uploaded_materials.items()
            if key in st.session_state.extraction_configs 
            and key not in st.session_state.extracted_content
            and not st.session_state.extraction_configs[key].get('disabled', False)
        ]
        
        if not materials_to_extract:
            st.info("All materials have already been extracted or are disabled.")
            return
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text(f"Starting parallel extraction of {len(materials_to_extract)} materials...")
        
        # Create a placeholder for status updates
        status_placeholder = st.empty()
        extraction_status = {key: "⏳ Pending" for key, _ in materials_to_extract}
        
        def update_status_display():
            """Update the status display."""
            status_html = "<div style='font-family: monospace;'>"
            for key, material in materials_to_extract:
                display_name = material.get('display_name', material['name'])
                status = extraction_status.get(key, "⏳ Pending")
                status_html += f"{status} {display_name}<br>"
            status_html += "</div>"
            status_placeholder.markdown(status_html, unsafe_allow_html=True)
        
        # Initial status display
        update_status_display()
        
        # Execute extractions in parallel
        successful_extractions = 0
        failed_extractions = 0
        
        # Prepare data for threads (avoiding session state access in threads)
        extraction_configs = {key: st.session_state.extraction_configs.get(key, {}) 
                            for key, _ in materials_to_extract}
        
        # Define a wrapper function that doesn't use Streamlit or session state
        def extract_material_wrapper(key: str, material: dict, config: dict) -> tuple:
            """Wrapper that returns result without using Streamlit."""
            try:
                material_type = material['type']
                
                # Extract based on type (without using st.error)
                if material_type == 'file':
                    result = extract_file_content(material, config)
                elif material_type == 'url':
                    result = extract_url_content(material, config)
                elif material_type == 'youtube':
                    result = extract_youtube_content(material, config)
                else:
                    result = None
                
                return (key, result, None)
            except Exception as e:
                return (key, None, str(e))
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all extraction tasks with configs
            future_to_key = {
                executor.submit(extract_material_wrapper, key, material, extraction_configs[key]): (key, material)
                for key, material in materials_to_extract
            }
            
            # Process completed extractions
            for future in as_completed(future_to_key):
                key, material = future_to_key[future]
                display_name = material.get('display_name', material['name'])
                
                try:
                    key, extracted_text, error = future.result()
                    if extracted_text:
                        st.session_state.extracted_content[key] = extracted_text
                        extraction_status[key] = "✅ Complete"
                        successful_extractions += 1
                    else:
                        extraction_status[key] = f"❌ Failed{': ' + error[:30] + '...' if error else ''}"
                        failed_extractions += 1
                except Exception as e:
                    extraction_status[key] = f"❌ Error: {str(e)[:30]}..."
                    failed_extractions += 1
                
                # Update progress
                completed = successful_extractions + failed_extractions
                progress = completed / len(materials_to_extract)
                progress_bar.progress(progress)
                
                # Update status display
                update_status_display()
        
        # Final status
        status_text.text(f"✅ Extraction complete! Success: {successful_extractions}, Failed: {failed_extractions}")
        
        if successful_extractions > 0:
            st.success(f"Successfully extracted {successful_extractions} materials")
        
        if failed_extractions > 0:
            st.warning(f"{failed_extractions} materials failed to extract")
        
        time.sleep(2)
        st.rerun()

def extract_single_material(key: str, material: dict) -> str:
    """Extract content from a single material based on its type and configuration."""
    config = st.session_state.extraction_configs.get(key, {})
    material_type = material['type']
    
    if material_type == 'file':
        return extract_file_content(material, config)
    elif material_type == 'url':
        return extract_url_content(material, config)
    elif material_type == 'youtube':
        return extract_youtube_content(material, config)
    else:
        return None

def extract_file_content(material: dict, config: dict) -> str:
    """Extract content from uploaded files."""
    file_type = material.get('file_type', '')
    
    if 'pdf' in file_type:
        # Extract PDF
        pdf_data = io.BytesIO(material['data'])
        
        if config.get('use_page_range') and config.get('page_ranges'):
            # Extract multiple page ranges
            all_text = []
            for start, end in config['page_ranges']:
                page_text = extraction_service.extract_text_from_pdf(pdf_data, (start, end))
                if page_text:
                    all_text.append(f"[Pages {start}-{end}]\n{page_text}")
                pdf_data.seek(0)  # Reset stream position for next extraction
            raw_text = "\n\n".join(all_text) if all_text else None
        else:
            # Extract all pages
            raw_text = extraction_service.extract_text_from_pdf(pdf_data, None)
        
        # Apply extraction prompt if available
        if raw_text and config.get('extraction_prompt'):
            raw_text = extraction_service.apply_extraction_prompt(raw_text, config['extraction_prompt'])
        
    elif 'image' in file_type:
        # Extract from image - use configured prompt
        image_data = io.BytesIO(material['data'])
        extraction_prompt = config.get('extraction_prompt', 'Extract all text and describe symbolic elements.')
        raw_text = extraction_service.extract_from_image(image_data, extraction_prompt)
        
    elif 'text' in file_type:
        # Extract text file
        text_data = io.BytesIO(material['data'])
        raw_text = extraction_service.extract_from_text_file(text_data)
        
        # Apply extraction prompt if available
        if raw_text and config.get('extraction_prompt'):
            raw_text = extraction_service.apply_extraction_prompt(raw_text, config['extraction_prompt'])
    else:
        raw_text = None
    
    # Apply AI cleaning if configured
    if raw_text and config.get('use_ai_cleaning', False):
        context = 'hermetic and esoteric text'  # Hard-coded context
        return extraction_service.clean_extracted_text(raw_text, context)
    
    return raw_text

def extract_url_content(material: dict, config: dict) -> str:
    """Extract content from URLs."""
    url = material['url']
    extraction_method = config.get('extraction_method', 'main_content')
    css_selector = config.get('css_selector') if extraction_method == 'custom_selector' else None
    
    raw_text = extraction_service.extract_from_url(url, extraction_method, css_selector)
    
    # Apply extraction prompt if available
    if raw_text and config.get('extraction_prompt'):
        raw_text = extraction_service.apply_extraction_prompt(raw_text, config['extraction_prompt'])
    
    # Apply AI cleaning if configured
    if raw_text and config.get('use_ai_cleaning', False):
        context = 'hermetic and esoteric text'  # Hard-coded context
        return extraction_service.clean_extracted_text(raw_text, context)
    
    return raw_text

def extract_youtube_content(material: dict, config: dict) -> str:
    """Extract content from YouTube videos."""
    youtube_url = material['url']
    transcript_type = config.get('transcript_type', 'any')
    language = config.get('language', None)
    
    transcript = extraction_service.extract_from_youtube(youtube_url, transcript_type, language)
    
    if transcript and config.get('summarize', False):
        # Summarize the transcript
        return extraction_service.summarize_content(transcript, 'YouTube video transcript')
    
    # Apply AI cleaning if configured (and not summarized)
    if transcript and not config.get('summarize') and config.get('use_ai_cleaning', False):
        context = 'hermetic and esoteric text'  # Hard-coded context
        return extraction_service.clean_extracted_text(transcript, context)
    
    return transcript

def render_extraction_results():
    """Render extraction results and previews."""
    st.subheader("📋 Extracted Content")
    
    # Check for disabled materials
    disabled_materials = [
        (key, material) for key, material in st.session_state.uploaded_materials.items()
        if key in st.session_state.extraction_configs
        and st.session_state.extraction_configs[key].get('disabled', False)
    ]
    
    if disabled_materials:
        with st.expander(f"🚫 Disabled Materials ({len(disabled_materials)})", expanded=False):
            for key, material in disabled_materials:
                display_name = material.get('display_name', material.get('name', 'Unknown'))
                st.info(f"**{display_name}** - Extraction disabled")
    
    if not st.session_state.extracted_content:
        st.info("No content extracted yet. Click 'Extract All' to begin.")
        return
    
    # View options
    col1, col2 = st.columns([3, 1])
    with col2:
        view_mode = st.selectbox(
            "View",
            ["Expanded", "Compact"],
            key="extraction_view_mode",
            label_visibility="collapsed"
        )
    
    # Display extracted content
    for key, content in st.session_state.extracted_content.items():
        material = st.session_state.uploaded_materials.get(key, {})
        display_name = material.get('display_name', material.get('name', 'Unknown'))
        
        with st.expander(f"📄 {display_name}", expanded=(view_mode == "Expanded")):
            # Content preview
            preview_length = 1000 if view_mode == "Expanded" else 500
            preview_text = content[:preview_length] + "..." if len(content) > preview_length else content
            
            st.text_area(
                "Extracted content",
                value=preview_text,
                height=200 if view_mode == "Expanded" else 100,
                disabled=True,
                key=f"preview_{key}"
            )
            
            # Content stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Characters", f"{len(content):,}")
            with col2:
                st.metric("Words", f"{len(content.split()):,}")
            with col3:
                st.metric("Lines", f"{len(content.splitlines()):,}")
            
            # Actions
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button(f"🔄 Re-extract", key=f"reextract_{key}"):
                    # Remove from extracted content to allow re-extraction
                    del st.session_state.extracted_content[key]
                    st.rerun()
            
            with action_col2:
                # Download extracted content
                st.download_button(
                    "📥 Download",
                    data=content,
                    file_name=f"extracted_{display_name.replace(' ', '_')}.txt",
                    mime="text/plain",
                    key=f"download_{key}"
                )
    
    # Summary stats
    st.divider()
    render_extraction_summary()

def render_extraction_summary():
    """Render extraction summary statistics."""
    st.subheader("📊 Extraction Summary")
    
    total_materials = len(st.session_state.uploaded_materials)
    total_configured = len([
        key for key in st.session_state.uploaded_materials
        if key in st.session_state.extraction_configs
    ])
    disabled_count = len([
        key for key in st.session_state.uploaded_materials
        if key in st.session_state.extraction_configs
        and st.session_state.extraction_configs[key].get('disabled', False)
    ])
    extracted_count = len(st.session_state.extracted_content)
    
    total_content = extracted_count
    total_chars = sum(len(content) for content in st.session_state.extracted_content.values())
    total_words = sum(len(content.split()) for content in st.session_state.extracted_content.values())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Materials", total_materials)
    
    with col2:
        st.metric("Configured", total_configured)
    
    with col3:
        st.metric("Disabled", disabled_count)
    
    with col4:
        st.metric("Extracted", extracted_count)
    
    # Additional stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Characters", f"{total_chars:,}")
    
    with col2:
        st.metric("Total Words", f"{total_words:,}")
    
    with col3:
        avg_words = total_words // extracted_count if extracted_count > 0 else 0
        st.metric("Avg Words/Material", f"{avg_words:,}")
    
    if extracted_count > 0:
        st.success(f"✅ Ready for synthesis! {extracted_count} materials have been extracted.")
    
    # Migrate to legacy format button (for backward compatibility)
    if st.button("🔄 Migrate to Legacy Format", help="Copy extracted content to legacy materials format"):
        st.session_state.materials = st.session_state.extracted_content.copy()
        st.success("✅ Content migrated to legacy format!") 