"""
Upload Phase UI Component
Handles material upload without extraction processing
"""

import streamlit as st
import re
from datetime import datetime
from utils.helpers import format_file_size
from config.settings import SUPPORTED_FILE_TYPES
from services.persistence import persistence_service

def render_upload_phase():
    """Render the upload phase interface."""
    st.header("📥 Phase 1: Upload Materials")
    st.markdown("Upload your source materials. You'll configure extraction settings in the next phase.")
    
    # Save/Load controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("💾 Save All", help="Save all current materials to disk"):
            saved = persistence_service.save_all_materials()
            st.success(f"Saved {saved} materials to disk")
            st.rerun()
    
    # Create tabs for different input types
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Files", "🌐 URL", "📺 YouTube", "💾 Saved Materials"])
    
    with tab1:
        render_file_upload_tab()
    
    with tab2:
        render_url_input_tab()
    
    with tab3:
        render_youtube_input_tab()
    
    with tab4:
        render_saved_materials_tab()
    
    # Display uploaded materials
    if st.session_state.uploaded_materials:
        st.divider()
        render_uploaded_materials()

def render_file_upload_tab():
    """Render file upload interface."""
    uploaded_files = st.file_uploader(
        "Drop your files here",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        key="file_uploader"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_key = f"file_{uploaded_file.name}"
            
            if file_key not in st.session_state.uploaded_materials:
                # Store file info without processing
                st.session_state.uploaded_materials[file_key] = {
                    'type': 'file',
                    'name': uploaded_file.name,
                    'display_name': uploaded_file.name,  # Add display name
                    'file_type': uploaded_file.type,
                    'size': len(uploaded_file.getvalue()),
                    'data': uploaded_file.getvalue()  # Store file data
                }
                st.success(f"✅ Uploaded: {uploaded_file.name}")

def render_url_input_tab():
    """Render URL input interface."""
    st.subheader("🌐 Web Page URL")
    
    url = st.text_input(
        "Enter URL:",
        placeholder="https://example.com/article",
        help="Enter a web page URL to extract content from"
    )
    
    if url:
        # Validate URL format
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if url_pattern.match(url):
            url_key = f"url_{hash(url) % 10000}"
            
            if st.button("➕ Add URL", type="primary", key="add_url"):
                if url_key not in st.session_state.uploaded_materials:
                    # Extract domain name for display
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc or 'Web Page'
                    st.session_state.uploaded_materials[url_key] = {
                        'type': 'url',
                        'name': url,
                        'display_name': domain,  # Add display name
                        'url': url,
                        'data': None
                    }
                    st.success(f"✅ Added URL: {url}")
                    st.rerun()
                else:
                    st.warning("This URL has already been added.")
        else:
            st.error("Please enter a valid URL starting with http:// or https://")

def render_youtube_input_tab():
    """Render YouTube input interface."""
    st.subheader("📺 YouTube Video")
    
    youtube_url = st.text_input(
        "Enter YouTube URL:",
        placeholder="https://www.youtube.com/watch?v=VIDEO_ID",
        help="Enter a YouTube video URL to extract transcript"
    )
    
    if youtube_url:
        # Validate YouTube URL
        youtube_pattern = re.compile(
            r'(https?://)?(www\.)?(youtube\.com/(watch\?v=|embed/)|youtu\.be/)'
            r'([a-zA-Z0-9_-]{11})', re.IGNORECASE)
        
        if youtube_pattern.match(youtube_url):
            yt_key = f"youtube_{hash(youtube_url) % 10000}"
            
            if st.button("➕ Add YouTube Video", type="primary", key="add_youtube"):
                if yt_key not in st.session_state.uploaded_materials:
                    # Extract video ID for display name
                    match = youtube_pattern.search(youtube_url)
                    video_id = match.group(5) if match else 'YouTube Video'
                    st.session_state.uploaded_materials[yt_key] = {
                        'type': 'youtube',
                        'name': f"YouTube: {youtube_url}",
                        'display_name': f"YouTube: {video_id}",  # Add display name
                        'url': youtube_url,
                        'data': None
                    }
                    st.success(f"✅ Added YouTube video")
                    st.rerun()
                else:
                    st.warning("This YouTube video has already been added.")
        else:
            st.error("Please enter a valid YouTube URL")

def render_saved_materials_tab():
    """Render saved materials loading interface."""
    st.subheader("💾 Load Saved Materials")
    
    saved_materials = persistence_service.list_saved_materials()
    
    if not saved_materials:
        st.info("No saved materials found. Upload and save materials to see them here.")
        return
    
    # Display saved materials
    st.markdown(f"Found **{len(saved_materials)}** saved materials:")
    
    for material_meta in saved_materials:
        with st.expander(f"{material_meta['display_name']} - {material_meta['type']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Original name:** {material_meta['name']}")
                st.write(f"**Type:** {material_meta['type']}")
                if material_meta.get('size'):
                    st.write(f"**Size:** {format_file_size(material_meta['size'])}")
                if material_meta.get('url'):
                    st.write(f"**URL:** {material_meta['url']}")
                
                saved_date = datetime.fromisoformat(material_meta['saved_at'])
                st.write(f"**Saved:** {saved_date.strftime('%Y-%m-%d %H:%M')}")
                
                # Status indicators
                status_cols = st.columns(3)
                with status_cols[0]:
                    if material_meta.get('has_config'):
                        st.success("✓ Configured")
                    else:
                        st.warning("○ Not configured")
                
                with status_cols[1]:
                    if material_meta.get('has_extracted_content'):
                        st.success("✓ Extracted")
                    else:
                        st.warning("○ Not extracted")
            
            with col2:
                # Load options
                load_content = st.checkbox(
                    "Load extracted content",
                    value=True,
                    key=f"load_content_{material_meta['key']}",
                    help="Load previously extracted content (uncheck to re-extract)"
                )
                
                if st.button("📥 Load", key=f"load_{material_meta['key']}", type="primary"):
                    # Load the material
                    loaded = persistence_service.load_material(material_meta['key'], load_content)
                    
                    if loaded:
                        # Add to session state
                        st.session_state.uploaded_materials[material_meta['key']] = loaded['material']
                        
                        if loaded['config']:
                            st.session_state.extraction_configs[material_meta['key']] = loaded['config']
                        
                        if loaded['extracted_content'] and load_content:
                            st.session_state.extracted_content[material_meta['key']] = loaded['extracted_content']
                        
                        st.success(f"✅ Loaded: {material_meta['display_name']}")
                        st.rerun()
                    else:
                        st.error("Failed to load material")
                
                if st.button("🗑️ Delete", key=f"delete_saved_{material_meta['key']}"):
                    if persistence_service.delete_material(material_meta['key']):
                        st.success("Deleted saved material")
                        st.rerun()
                    else:
                        st.error("Failed to delete material")

def render_uploaded_materials():
    """Display uploaded materials in a grid layout."""
    st.subheader("📚 Uploaded Materials")
    
    # View options
    col1, col2 = st.columns([3, 1])
    with col2:
        view_mode = st.selectbox(
            "View",
            ["Grid", "List"],
            key="upload_view_mode",
            label_visibility="collapsed"
        )
    
    if view_mode == "Grid":
        # Grid view
        cols = st.columns(3)
        for i, (key, material) in enumerate(st.session_state.uploaded_materials.items()):
            with cols[i % 3]:
                render_material_card(key, material)
    else:
        # List view
        for key, material in st.session_state.uploaded_materials.items():
            render_material_list_item(key, material)

def render_material_card(key: str, material: dict):
    """Render a material card."""
    with st.container():
        # Card header
        if material['type'] == 'file':
            icon = "📄" if "pdf" in material.get('file_type', '') else "🖼️" if "image" in material.get('file_type', '') else "📝"
            # Use display_name if available, otherwise original name
            display_name = material.get('display_name', material['name'])
            st.markdown(f"### {icon} {display_name}")
            if material.get('display_name') and material['display_name'] != material['name']:
                st.caption(f"Original: {material['name']}")
            st.caption(f"Size: {format_file_size(material['size'])}")
        elif material['type'] == 'url':
            st.markdown(f"### 🌐 {material.get('display_name', 'Web Page')}")
            st.caption(material['url'][:50] + "..." if len(material['url']) > 50 else material['url'])
        elif material['type'] == 'youtube':
            st.markdown(f"### 📺 {material.get('display_name', 'YouTube')}")
            st.caption(material['url'][:50] + "..." if len(material['url']) > 50 else material['url'])
        
        # Action buttons in columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Rename button
            if st.button("✏️ Rename", key=f"rename_{key}", use_container_width=True):
                st.session_state[f"renaming_{key}"] = True
                st.rerun()
        
        with col2:
            # Remove button
            if st.button("🗑️ Remove", key=f"remove_{key}", use_container_width=True):
                del st.session_state.uploaded_materials[key]
                # Also remove any associated configs if they exist
                if key in st.session_state.extraction_configs:
                    del st.session_state.extraction_configs[key]
                if key in st.session_state.extracted_content:
                    del st.session_state.extracted_content[key]
                st.rerun()
        
        # Rename dialog
        if st.session_state.get(f"renaming_{key}", False):
            with st.container():
                st.divider()
                new_name = st.text_input(
                    "New name:",
                    value=material.get('display_name', material.get('name', 'Untitled')),
                    key=f"new_name_{key}"
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Save", key=f"save_rename_{key}", type="primary"):
                        material['display_name'] = new_name
                        st.session_state[f"renaming_{key}"] = False
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", key=f"cancel_rename_{key}"):
                        st.session_state[f"renaming_{key}"] = False
                        st.rerun()

def render_material_list_item(key: str, material: dict):
    """Render a material list item."""
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        display_name = material.get('display_name', material['name'])
        if material['type'] == 'file':
            st.write(f"📄 {display_name}")
        elif material['type'] == 'url':
            st.write(f"🌐 {display_name}")
        elif material['type'] == 'youtube':
            st.write(f"📺 {display_name}")
    
    with col2:
        if material['type'] == 'file':
            st.caption(format_file_size(material['size']))
    
    with col3:
        if st.button("Rename", key=f"rename_list_{key}"):
            st.session_state[f"renaming_list_{key}"] = True
            st.rerun()
    
    with col4:
        if st.button("Remove", key=f"remove_list_{key}"):
            del st.session_state.uploaded_materials[key]
            # Also remove any associated configs if they exist
            if key in st.session_state.extraction_configs:
                del st.session_state.extraction_configs[key]
            if key in st.session_state.extracted_content:
                del st.session_state.extracted_content[key]
            st.rerun()
    
    # Rename dialog for list view
    if st.session_state.get(f"renaming_list_{key}", False):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            new_name = st.text_input(
                "New name:",
                value=material.get('display_name', material.get('name', 'Untitled')),
                key=f"new_name_list_{key}",
                label_visibility="collapsed"
            )
        with col2:
            if st.button("Save", key=f"save_rename_list_{key}"):
                material['display_name'] = new_name
                st.session_state[f"renaming_list_{key}"] = False
                st.rerun()
        with col3:
            if st.button("Cancel", key=f"cancel_rename_list_{key}"):
                st.session_state[f"renaming_list_{key}"] = False
                st.rerun() 