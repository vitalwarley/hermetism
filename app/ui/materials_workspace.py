"""
Materials Workspace UI - Central hub for managing materials and extractions
"""

import streamlit as st
from typing import Dict, List, Optional, Any
from datetime import datetime
from services.materials_workspace import materials_workspace_service
from services.extraction import extraction_service
from services.ai_service import ai_service
from utils.helpers import format_file_size
from ui.material_card import _get_material_type, _get_card_styling
import base64
from urllib.parse import urlparse

def render_materials_workspace():
    """Main function to render the Materials Workspace interface."""
    st.title("📚 Materials Workspace")
    st.markdown("Central hub for managing materials and their extractions across all projects")
    
    # Initialize workspace state
    if 'workspace_mode' not in st.session_state:
        st.session_state.workspace_mode = 'overview'
    if 'selected_material' not in st.session_state:
        st.session_state.selected_material = None
    if 'selected_extraction' not in st.session_state:
        st.session_state.selected_extraction = None
    
    # Top navigation
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        if st.button("📊 Overview", use_container_width=True, 
                    type="primary" if st.session_state.workspace_mode == 'overview' else "secondary"):
            st.session_state.workspace_mode = 'overview'
            st.rerun()
    
    with col2:
        if st.button("📄 Materials", use_container_width=True,
                    type="primary" if st.session_state.workspace_mode == 'materials' else "secondary"):
            st.session_state.workspace_mode = 'materials'
            st.rerun()
    
    with col3:
        if st.button("🔍 Extractions", use_container_width=True,
                    type="primary" if st.session_state.workspace_mode == 'extractions' else "secondary"):
            st.session_state.workspace_mode = 'extractions'
            st.rerun()
    
    with col4:
        if st.button("🔄 Import", use_container_width=True,
                    type="primary" if st.session_state.workspace_mode == 'import' else "secondary"):
            st.session_state.workspace_mode = 'import'
            st.rerun()
    
    st.divider()
    
    # Render based on mode
    if st.session_state.workspace_mode == 'overview':
        render_workspace_overview()
    elif st.session_state.workspace_mode == 'materials':
        render_materials_view()
    elif st.session_state.workspace_mode == 'extractions':
        render_extractions_view()
    elif st.session_state.workspace_mode == 'import':
        render_import_view()

def render_workspace_overview():
    """Render the workspace overview with statistics and recent items."""
    # Statistics
    materials = materials_workspace_service.list_materials()
    extractions = materials_workspace_service.list_extractions()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Materials", len(materials))
    
    with col2:
        st.metric("Total Extractions", len(extractions))
    
    with col3:
        # Count materials by type
        type_counts = {}
        for mat in materials:
            mat_type = mat.get('type', 'unknown')
            type_counts[mat_type] = type_counts.get(mat_type, 0) + 1
        most_common_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else "none"
        st.metric("Most Common Type", most_common_type.title())
    
    with col4:
        # Average extractions per material
        avg_extractions = len(extractions) / len(materials) if materials else 0
        st.metric("Avg Extractions/Material", f"{avg_extractions:.1f}")
    
    st.divider()
    
    # Recent materials and extractions
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Recent Materials")
        recent_materials = materials[:5]  # Already sorted by date
        
        if recent_materials:
            for mat in recent_materials:
                with st.container():
                    icon, type_label, color = _get_card_styling(mat.get('type', 'unknown'))
                    
                    subcol1, subcol2 = st.columns([3, 1])
                    with subcol1:
                        st.markdown(f"{icon} **{mat['display_name']}**")
                        st.caption(f"Type: {type_label} | Extractions: {mat.get('extraction_count', 0)}")
                    with subcol2:
                        if st.button("View", key=f"view_mat_{mat['id']}"):
                            st.session_state.selected_material = mat['id']
                            st.session_state.workspace_mode = 'materials'
                            st.rerun()
        else:
            st.info("No materials yet. Add some materials to get started!")
    
    with col2:
        st.subheader("🔍 Recent Extractions")
        recent_extractions = extractions[:5]  # Already sorted by date
        
        if recent_extractions:
            for ext in recent_extractions:
                with st.container():
                    subcol1, subcol2 = st.columns([3, 1])
                    with subcol1:
                        st.markdown(f"**{ext.get('material_name', 'Unknown')}**")
                        st.caption(f"{ext.get('config_summary', 'Default extraction')} | {ext.get('word_count', 0):,} words")
                    with subcol2:
                        if st.button("View", key=f"view_ext_{ext['id']}"):
                            st.session_state.selected_extraction = ext['id']
                            st.session_state.workspace_mode = 'extractions'
                            st.rerun()
        else:
            st.info("No extractions yet. Extract content from your materials!")

def render_materials_view():
    """Render the materials management view."""
    # Add new material section
    with st.expander("➕ Add New Material", expanded=False):
        render_add_material_form()
    
    # Search and filter
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search materials...", placeholder="Search by name, URL, or tags")
    
    with col2:
        filter_type = st.selectbox("Filter by type", ["all", "file", "url", "youtube", "image", "pdf", "text"])
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Get materials
    if search_query:
        materials = materials_workspace_service.search_materials(search_query)
    else:
        materials = materials_workspace_service.list_materials(
            filter_type=None if filter_type == "all" else filter_type
        )
    
    # Display materials
    if materials:
        st.caption(f"Showing {len(materials)} materials")
        
        # Check if a material is selected
        if st.session_state.selected_material:
            # Show selected material detail
            render_material_detail(st.session_state.selected_material)
        else:
            # Show materials grid
            render_materials_grid(materials)
    else:
        st.info("No materials found. Add some materials to get started!")

def render_add_material_form():
    """Render form to add new material."""
    material_type = st.radio("Material Type", ["file", "url", "youtube"], horizontal=True)
    
    if material_type == "file":
        uploaded_file = st.file_uploader(
            "Choose a file",
            accept_multiple_files=False,
            help="Upload PDF, images, or text files"
        )
        
        if uploaded_file and st.button("Add File", type="primary"):
            with st.spinner("Adding material..."):
                try:
                    # Prepare material data
                    material_data = {
                        "type": "file",
                        "name": uploaded_file.name,
                        "display_name": uploaded_file.name,
                        "file_type": uploaded_file.type,
                        "size": uploaded_file.size,
                        "data": uploaded_file.read()
                    }
                    
                    # Determine specific type
                    if uploaded_file.type.startswith("image/"):
                        material_data["type"] = "image"
                    elif uploaded_file.type == "application/pdf":
                        material_data["type"] = "pdf"
                    elif uploaded_file.type.startswith("text/"):
                        material_data["type"] = "text"
                    
                    # Add to workspace
                    material_id = materials_workspace_service.add_material(material_data)
                    st.success(f"Added material: {uploaded_file.name}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error adding material: {str(e)}")
    
    elif material_type == "url":
        url = st.text_input("Enter URL")
        
        if url and st.button("Add URL", type="primary"):
            with st.spinner("Adding URL..."):
                try:
                    # Parse URL for better display name
                    parsed_url = urlparse(url)
                    domain = parsed_url.netloc or 'Web Page'
                    
                    # Create a more descriptive display name
                    if parsed_url.path and parsed_url.path != '/':
                        # Include first meaningful path segment
                        path_parts = parsed_url.path.strip('/').split('/')
                        if path_parts and path_parts[0]:
                            # For very long paths, include more segments to ensure uniqueness
                            if len(path_parts) >= 3:
                                # Include at least 2 path segments for deep URLs
                                display_name = f"{domain}/{path_parts[0]}/{path_parts[1]}"
                                if len(path_parts) > 2:
                                    # Add the last segment if it's different from the second
                                    if path_parts[-1] != path_parts[1]:
                                        display_name += f"/.../{path_parts[-1]}"
                                    else:
                                        display_name += "/..."
                            else:
                                display_name = f"{domain}/{path_parts[0]}"
                                # If there are more path parts, indicate it
                                if len(path_parts) > 1:
                                    display_name += "/..."
                        else:
                            display_name = domain
                    elif parsed_url.query:
                        # Include query hint if no meaningful path
                        display_name = f"{domain}?..."
                    else:
                        display_name = domain
                    
                    material_data = {
                        "type": "url",
                        "url": url,
                        "name": url,
                        "display_name": display_name
                    }
                    
                    material_id = materials_workspace_service.add_material(material_data)
                    st.success(f"Added URL: {url}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error adding URL: {str(e)}")
    
    elif material_type == "youtube":
        youtube_url = st.text_input("Enter YouTube URL")
        
        if youtube_url and st.button("Add YouTube Video", type="primary"):
            with st.spinner("Adding YouTube video..."):
                try:
                    # Extract video ID for display name
                    import re
                    video_id_match = re.search(r'(?:v=|/)([a-zA-Z0-9_-]{11})', youtube_url)
                    video_id = video_id_match.group(1) if video_id_match else "video"
                    
                    material_data = {
                        "type": "youtube",
                        "url": youtube_url,
                        "name": youtube_url,
                        "display_name": f"YouTube: {video_id}"
                    }
                    
                    material_id = materials_workspace_service.add_material(material_data)
                    st.success(f"Added YouTube video")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error adding YouTube video: {str(e)}")

def render_materials_grid(materials: List[Dict[str, Any]]):
    """Render materials in a grid layout."""
    cols = st.columns(3)
    
    for idx, mat in enumerate(materials):
        col_idx = idx % 3
        with cols[col_idx]:
            render_material_card_workspace(mat, idx)

def render_material_card_workspace(material: Dict[str, Any], idx: int):
    """Render a material card in the workspace."""
    icon, type_label, color = _get_card_styling(material.get('type', 'unknown'))
    
    with st.container():
        # Card content
        st.markdown(f"""
        <div style="background-color: #f8f9fa; border: 1px solid #e0e0e0; 
                    border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 2rem; margin-right: 0.5rem;">{icon}</span>
                <span style="color: {color}; font-weight: 600; font-size: 0.875rem; text-transform: uppercase;">{type_label}</span>
            </div>
            <div style="font-weight: 600; margin: 0.5rem 0;">{material['display_name']}</div>
            <div style="color: #666; font-size: 0.875rem;">
                Extractions: {material.get('extraction_count', 0)} | 
                Added: {material.get('added_at', 'Unknown')[:10]}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👁️ View", key=f"view_{material['id']}_{idx}", use_container_width=True):
                st.session_state.selected_material = material['id']
                st.rerun()
        
        with col2:
            if st.button("🔍 Extract", key=f"extract_{material['id']}_{idx}", use_container_width=True):
                st.session_state.selected_material = material['id']
                st.session_state.show_extraction_form = True
                st.rerun()
        
        with col3:
            if st.button("🗑️", key=f"delete_{material['id']}_{idx}", use_container_width=True):
                if materials_workspace_service.delete_material(material['id']):
                    st.success("Material deleted")
                    st.rerun()

def render_material_detail(material_id: str):
    """Render detailed view of a material."""
    material = materials_workspace_service.get_material(material_id)
    if not material:
        st.error("Material not found")
        return
    
    # Back button
    if st.button("← Back to Materials"):
        st.session_state.selected_material = None
        st.session_state.show_extraction_form = False
        st.rerun()
    
    # Material info
    icon, type_label, color = _get_card_styling(material.get('type', 'unknown'))
    
    st.markdown(f"## {icon} {material['display_name']}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Type", type_label)
    with col2:
        st.metric("Extractions", len(material.get('extraction_ids', [])))
    with col3:
        if material.get('size'):
            st.metric("Size", format_file_size(material['size']))
    with col4:
        st.metric("Added", material.get('added_at', 'Unknown')[:10])
    
    # Tags management
    with st.expander("🏷️ Tags", expanded=True):
        current_tags = material.get('tags', [])
        
        # Display current tags
        if current_tags:
            st.write("Current tags:")
            for tag in current_tags:
                st.caption(f"🏷️ {tag}")
        
        # Add/edit tags
        new_tags = st.text_input("Edit tags (comma-separated)", value=", ".join(current_tags))
        if st.button("Update Tags"):
            tags = [tag.strip() for tag in new_tags.split(",") if tag.strip()]
            if materials_workspace_service.update_material_tags(material_id, tags):
                st.success("Tags updated")
                st.rerun()
    
    # Preview section
    with st.expander("📄 Material Preview", expanded=True):
        if material.get('type') == 'image' and 'data' in material:
            # Display image
            st.image(material['data'])
        elif material.get('url'):
            st.write(f"**URL:** {material['url']}")
        elif 'data' in material:
            # Text preview
            try:
                text_preview = material['data'].decode('utf-8') if isinstance(material['data'], bytes) else str(material['data'])
                st.text_area("Content preview", text_preview[:1000] + "..." if len(text_preview) > 1000 else text_preview, height=200)
            except:
                st.info("Binary content - cannot preview as text")
    
    # Extraction section
    st.divider()
    
    if st.session_state.get('show_extraction_form'):
        render_extraction_form(material)
    else:
        # Show extractions
        st.subheader("🔍 Extractions")
        
        if st.button("➕ New Extraction", type="primary"):
            st.session_state.show_extraction_form = True
            st.rerun()
        
        extractions = materials_workspace_service.list_extractions(material_id)
        
        if extractions:
            for ext in extractions:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{ext.get('config_summary', 'Default extraction')}**")
                        st.caption(f"Created: {ext['created_at'][:16]} | {ext.get('word_count', 0):,} words")
                    
                    with col2:
                        if st.button("View", key=f"view_ext_{ext['id']}"):
                            st.session_state.selected_extraction = ext['id']
                            st.session_state.workspace_mode = 'extractions'
                            st.rerun()
                    
                    with col3:
                        if st.button("🗑️", key=f"del_ext_{ext['id']}"):
                            if materials_workspace_service.delete_extraction(ext['id']):
                                st.success("Extraction deleted")
                                st.rerun()
        else:
            st.info("No extractions yet. Click 'New Extraction' to create one.")

def render_extraction_form(material: Dict[str, Any]):
    """Render form for creating new extraction."""
    st.subheader("🔍 Create New Extraction")
    
    # Extraction configuration
    extraction_config = {}
    
    if material['type'] == 'pdf':
        # PDF-specific options
        total_pages = st.number_input("Total pages (estimate)", min_value=1, value=10)
        
        extract_option = st.radio("Extract:", ["All pages", "Page range", "AI Vision (for scanned PDFs)"])
        
        if extract_option == "Page range":
            col1, col2 = st.columns(2)
            with col1:
                start_page = st.number_input("Start page", min_value=1, value=1)
            with col2:
                end_page = st.number_input("End page", min_value=1, value=min(10, total_pages))
            extraction_config['page_range'] = (start_page, end_page)
            extraction_config['method'] = 'text_range'
        elif extract_option == "AI Vision (for scanned PDFs)":
            extraction_config['method'] = 'vision'
        else:
            extraction_config['method'] = 'text_all'
    
    elif material['type'] == 'image':
        extraction_config['method'] = 'vision'
    
    elif material['type'] == 'url':
        extract_option = st.selectbox("Extract method:", ["Main content", "Full page", "Custom CSS selector"])
        extraction_config['method'] = extract_option.lower().replace(" ", "_")
        
        if extract_option == "Custom CSS selector":
            css_selector = st.text_input("CSS Selector", placeholder="e.g., .main-content, #article")
            extraction_config['css_selector'] = css_selector
    
    elif material['type'] == 'youtube':
        transcript_type = st.selectbox("Transcript type:", ["Any available", "Manual only", "Auto-generated only"])
        extraction_config['transcript_type'] = transcript_type.lower().replace(" ", "_")
        
        language = st.text_input("Language code (optional)", placeholder="e.g., en, es, fr")
        if language:
            extraction_config['language'] = language
    
    # Custom prompt
    use_custom_prompt = st.checkbox("Use custom extraction prompt")
    if use_custom_prompt:
        custom_prompt = st.text_area(
            "Extraction prompt",
            placeholder="Enter instructions for how to extract or process the content...",
            height=100
        )
        extraction_config['prompt'] = custom_prompt
    
    # Metadata
    metadata_text = st.text_input("Metadata/Notes (optional)", placeholder="Add any notes about this extraction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_extraction_form = False
            st.rerun()
    
    with col2:
        if st.button("🔍 Extract", type="primary", use_container_width=True):
            with st.spinner("Extracting content..."):
                try:
                    # Perform extraction based on material type
                    extracted_content = None
                    
                    if material['type'] == 'pdf' and 'data' in material:
                        if extraction_config.get('method') == 'vision':
                            # AI Vision extraction for PDFs would need to be implemented
                            st.error("AI Vision for PDFs not yet implemented")
                            return
                        else:
                            # Create file-like object from bytes
                            import io
                            pdf_file = io.BytesIO(material['data'])
                            page_range = extraction_config.get('page_range')
                            extracted_content = extraction_service.extract_text_from_pdf(pdf_file, page_range)
                    
                    elif material['type'] == 'image' and 'data' in material:
                        # Use vision API
                        base64_image = base64.b64encode(material['data']).decode('utf-8')
                        prompt = extraction_config.get('prompt', "Extract all text and describe the content of this image.")
                        extracted_content = ai_service.extract_from_image(base64_image, prompt)
                    
                    elif material['type'] == 'url':
                        extracted_content = extraction_service.extract_from_url(
                            material['url'],
                            extraction_config.get('method', 'main_content'),
                            extraction_config.get('css_selector')
                        )
                    
                    elif material['type'] == 'youtube':
                        extracted_content = extraction_service.extract_from_youtube(
                            material['url'],
                            extraction_config.get('transcript_type', 'any'),
                            extraction_config.get('language')
                        )
                    
                    elif material['type'] == 'text' and 'data' in material:
                        extracted_content = material['data'].decode('utf-8') if isinstance(material['data'], bytes) else str(material['data'])
                    
                    if extracted_content:
                        # Apply custom prompt if specified
                        if use_custom_prompt and custom_prompt:
                            extracted_content = extraction_service.apply_extraction_prompt(
                                extracted_content, custom_prompt
                            )
                        
                        # Save extraction
                        metadata = {}
                        if metadata_text:
                            metadata['notes'] = metadata_text
                        
                        extraction_id = materials_workspace_service.add_extraction(
                            material['id'],
                            extracted_content,
                            extraction_config,
                            metadata
                        )
                        
                        st.success("Extraction completed!")
                        st.session_state.show_extraction_form = False
                        st.rerun()
                    else:
                        st.error("No content extracted")
                
                except Exception as e:
                    st.error(f"Extraction failed: {str(e)}")

def render_extractions_view():
    """Render the extractions view."""
    # Search
    search_query = st.text_input("🔍 Search extractions...", placeholder="Search in content")
    
    # Get extractions
    if search_query:
        extractions = materials_workspace_service.search_extractions(search_query)
    else:
        extractions = materials_workspace_service.list_extractions()
    
    # Check if an extraction is selected
    if st.session_state.selected_extraction:
        render_extraction_detail(st.session_state.selected_extraction)
    else:
        # Display extractions list
        if extractions:
            st.caption(f"Showing {len(extractions)} extractions")
            
            for ext in extractions:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{ext.get('material_name', 'Unknown Material')}**")
                    
                    with col2:
                        st.caption(ext.get('config_summary', 'Default extraction'))
                    
                    with col3:
                        st.caption(f"{ext.get('word_count', 0):,} words")
                    
                    with col4:
                        if st.button("View", key=f"view_ext_{ext['id']}"):
                            st.session_state.selected_extraction = ext['id']
                            st.rerun()
                    
                    st.caption(f"Created: {ext['created_at'][:16]}")
                    st.divider()
        else:
            st.info("No extractions found. Extract content from your materials first!")

def render_extraction_detail(extraction_id: str):
    """Render detailed view of an extraction."""
    extraction = materials_workspace_service.get_extraction(extraction_id)
    if not extraction:
        st.error("Extraction not found")
        return
    
    # Back button
    if st.button("← Back to Extractions"):
        st.session_state.selected_extraction = None
        st.rerun()
    
    # Get material info
    material = materials_workspace_service.get_material(extraction['material_id'])
    material_name = material['display_name'] if material else "Unknown Material"
    
    st.markdown(f"## 🔍 Extraction: {material_name}")
    
    # Metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Words", f"{extraction['word_count']:,}")
    with col2:
        st.metric("Characters", f"{extraction['char_count']:,}")
    with col3:
        st.metric("Created", extraction['created_at'][:16])
    
    # Configuration details
    with st.expander("⚙️ Extraction Configuration", expanded=False):
        st.json(extraction['config'])
        
        if extraction.get('metadata'):
            st.subheader("Metadata")
            st.json(extraction['metadata'])
    
    # Content
    st.subheader("📄 Extracted Content")
    
    # Copy button
    if st.button("📋 Copy to Clipboard"):
        # This would need JavaScript implementation in real Streamlit
        st.info("Content copied! (Note: Copy functionality requires JavaScript implementation)")
    
    # Content display
    st.text_area("", extraction['content'], height=500, disabled=True)
    
    # Actions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Delete Extraction", type="secondary", use_container_width=True):
            if materials_workspace_service.delete_extraction(extraction_id):
                st.success("Extraction deleted")
                st.session_state.selected_extraction = None
                st.rerun()
    
    with col2:
        if material:
            if st.button("👁️ View Material", type="primary", use_container_width=True):
                st.session_state.selected_material = material['id']
                st.session_state.selected_extraction = None
                st.session_state.workspace_mode = 'materials'
                st.rerun()

def render_import_view():
    """Render the import from projects view."""
    st.subheader("🔄 Import from Projects")
    st.markdown("Import all materials and extractions from existing projects into the Materials Workspace.")
    
    # Import status
    if 'import_status' not in st.session_state:
        st.session_state.import_status = None
    
    if st.session_state.import_status:
        if st.session_state.import_status['success']:
            st.success(
                f"✅ Import completed! Imported {st.session_state.import_status['materials']} materials "
                f"and {st.session_state.import_status['extractions']} extractions."
            )
        else:
            st.error(st.session_state.import_status['message'])
    
    # Current statistics
    current_materials = len(materials_workspace_service.list_materials())
    current_extractions = len(materials_workspace_service.list_extractions())
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Materials", current_materials)
    with col2:
        st.metric("Current Extractions", current_extractions)
    
    st.divider()
    
    # Import options
    st.info(
        "This will scan all projects and import their materials and extractions. "
        "Duplicates will be created as new entries in the workspace."
    )
    
    if st.button("🚀 Start Import", type="primary", use_container_width=True):
        with st.spinner("Importing materials and extractions from all projects..."):
            try:
                materials_imported, extractions_imported = materials_workspace_service.import_from_projects()
                
                st.session_state.import_status = {
                    'success': True,
                    'materials': materials_imported,
                    'extractions': extractions_imported
                }
                st.rerun()
                
            except Exception as e:
                st.session_state.import_status = {
                    'success': False,
                    'message': f"Import failed: {str(e)}"
                }
                st.rerun()
    
    # Manual refresh
    if st.button("🔄 Refresh Statistics"):
        st.session_state.import_status = None
        st.rerun()

def get_extraction_for_synthesis(extraction_id: str) -> Optional[Dict[str, Any]]:
    """Get extraction data formatted for synthesis phase."""
    extraction = materials_workspace_service.get_extraction(extraction_id)
    if not extraction:
        return None
    
    material = materials_workspace_service.get_material(extraction['material_id'])
    if not material:
        return None
    
    return {
        'material_id': material['id'],
        'material_name': material['display_name'],
        'extraction_id': extraction['id'],
        'content': extraction['content'],
        'config_summary': extraction.get('config_summary', 'Default extraction'),
        'metadata': extraction.get('metadata', {})
    } 