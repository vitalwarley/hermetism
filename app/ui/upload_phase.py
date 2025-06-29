"""
Upload Phase UI Component
Handles material upload without extraction processing
"""

import streamlit as st
import re
import os
import mimetypes
from datetime import datetime
from utils.helpers import format_file_size
from config.settings import SUPPORTED_FILE_TYPES
from services.persistence import persistence_service
from services.material_library import material_library_service
from urllib.parse import urlparse

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📁 Files", "🌐 URL", "📺 YouTube", "💾 Saved Materials", "📚 Material Library"])
    
    with tab1:
        render_file_upload_tab()
    
    with tab2:
        render_url_input_tab()
    
    with tab3:
        render_youtube_input_tab()
    
    with tab4:
        render_saved_materials_tab()
    
    with tab5:
        render_material_library_tab()
    
    # Display uploaded materials
    if st.session_state.uploaded_materials:
        st.divider()
        render_uploaded_materials()

def render_file_upload_tab():
    """Render file upload interface with folder structure support."""
    
    # Create two columns for upload methods
    upload_method = st.radio(
        "Choose upload method:",
        ["📂 Select Folder (Recommended)", "📄 Select Individual Files"],
        index=0,
        horizontal=True
    )
    
    st.divider()
    
    if upload_method == "📂 Select Folder (Recommended)":
        render_folder_import()
    else:
        render_individual_file_upload()

def render_folder_import():
    """Render the folder import interface."""
    st.markdown("### 📂 Import from Folder")
    st.info("💡 Select a folder to import all files recursively. Folder structure will be preserved in file names.")
    
    # Add helpful tips
    with st.expander("💡 Tips for folder import", expanded=False):
        st.markdown("""
        **How to use folder import:**
        1. Place your materials in the `data/` folder in your project
        2. Organize them in subfolders (e.g., `data/signs/taurus/`)
        3. Select a folder below to import all files at once
        4. File names will preserve folder structure (e.g., `signs/taurus/1.jpg` → `signs_taurus_1.jpg`)
        
        **Note:** Due to browser security restrictions, you cannot directly select folders from your file system. 
        Instead, place your materials in the `data/` directory first.
        
        **Alternative methods:**
        - Use the command line to copy folders: `cp -r /source/folder ./data/`
        - Drag and drop folders into the `data/` directory using your file explorer
        """)
    
    # Get the data directory path
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    # Create a folder browser
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Show current data path
        st.caption(f"📍 Base directory: `{os.path.relpath(data_path)}`")
    
    with col2:
        if st.button("🔄 Refresh Folders"):
            st.rerun()
    
    if os.path.exists(data_path):
        # Build folder tree structure
        folder_tree = build_folder_tree(data_path)
        
        if folder_tree:
            # Folder selection with tree view
            st.markdown("#### Select a folder to import:")
            
            # Create an expandable tree view
            selected_folder_path = render_folder_tree(folder_tree, data_path)
            
            if selected_folder_path:
                # Show folder contents preview
                st.divider()
                st.markdown("#### 📋 Folder Contents Preview")
                
                # Count files
                file_count, file_list = count_files_in_folder(selected_folder_path, recursive=True)
                
                if file_count > 0:
                    # Import options
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        recursive = st.checkbox(
                            "Include subfolders",
                            value=True,
                            help="Import files from all subfolders recursively"
                        )
                    
                    with col2:
                        preserve_structure = st.checkbox(
                            "Preserve folder structure",
                            value=True,
                            help="Convert folder paths to underscored names"
                        )
                    
                    with col3:
                        st.metric("Files found", file_count if recursive else len([f for f in file_list if os.path.dirname(f) == selected_folder_path]))
                    
                    # Preview naming
                    with st.expander(f"📄 Preview file naming ({min(10, file_count)} of {file_count} files)", expanded=True):
                        preview_files = file_list[:10] if recursive else [f for f in file_list if os.path.dirname(f) == selected_folder_path][:10]
                        
                        for file_path in preview_files:
                            rel_path = os.path.relpath(file_path, data_path)
                            if preserve_structure:
                                display_name = convert_path_to_underscore_name(rel_path)
                            else:
                                display_name = os.path.basename(file_path)
                            
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                st.caption(f"📁 {rel_path}")
                            with col2:
                                st.caption(f"➡️ {display_name}")
                    
                    # Import button
                    st.divider()
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button(
                            f"📥 Import {file_count if recursive else len([f for f in file_list if os.path.dirname(f) == selected_folder_path])} Files",
                            type="primary",
                            use_container_width=True
                        ):
                            # Determine relative base
                            relative_base = os.path.relpath(selected_folder_path, data_path)
                            if relative_base == ".":
                                relative_base = ""
                            
                            # Import files
                            imported_count = import_files_from_folder(
                                selected_folder_path,
                                relative_base,
                                recursive=recursive,
                                preserve_structure=preserve_structure
                            )
                            
                            st.success(f"✅ Successfully imported {imported_count} files!")
                            st.balloons()
                            st.rerun()
                else:
                    st.warning("No supported files found in this folder.")
        else:
            st.info("No folders found in the data directory. Please add folders with your materials to the `data/` directory.")
    else:
        # Provide instructions for creating data directory
        st.warning("Data directory not found.")
        st.markdown("""
        **To use folder import:**
        1. Create a `data/` folder in your project root
        2. Add your material folders inside (e.g., `data/signs/`, `data/tarot/`)
        3. Click refresh to see available folders
        """)

def render_individual_file_upload():
    """Render individual file upload interface."""
    st.markdown("### 📄 Upload Individual Files")
    
    # Add option to preserve folder structure
    preserve_paths = st.checkbox(
        "Preserve folder structure in names",
        value=True,
        help="When enabled, folder paths will be converted to underscored names (e.g., signs/taurus/1.jpg → signs_taurus_1.jpg)"
    )
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Drop your files here (you can select multiple files)",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        key="file_uploader",
        help="Tip: For folder uploads, use the 'Select Folder' option above"
    )
    
    if uploaded_files:
        # Process uploaded files
        processed_count = 0
        skipped_count = 0
        
        for uploaded_file in uploaded_files:
            # Process the filename
            original_name = uploaded_file.name
            
            if preserve_paths and '/' in original_name:
                # Convert folder separators to underscores
                display_name = convert_path_to_underscore_name(original_name)
            else:
                # Just use the filename without path
                display_name = original_name.split('/')[-1] if '/' in original_name else original_name
            
            # Generate unique key
            file_key = f"file_{display_name}"
            
            if file_key not in st.session_state.uploaded_materials:
                # Store file info
                st.session_state.uploaded_materials[file_key] = {
                    'type': 'file',
                    'name': original_name,  # Keep original name for reference
                    'display_name': display_name,  # Use processed name for display
                    'file_type': uploaded_file.type,
                    'size': len(uploaded_file.getvalue()),
                    'data': uploaded_file.getvalue()
                }
                processed_count += 1
            else:
                skipped_count += 1
        
        # Show summary
        if processed_count > 0:
            st.success(f"✅ Uploaded {processed_count} file(s)")
        if skipped_count > 0:
            st.info(f"ℹ️ Skipped {skipped_count} duplicate file(s)")

def render_url_input_tab():
    """Render URL input interface."""
    st.subheader("🌐 Web Page URL")
    
    # Add toggle for bulk mode
    input_mode = st.radio(
        "Input mode:",
        ["Single URL", "Bulk URLs"],
        horizontal=True,
        help="Choose between adding one URL or multiple URLs at once"
    )
    
    if input_mode == "Single URL":
        # Single URL input
        url = st.text_input(
            "Enter URL:",
            placeholder="https://example.com/article",
            help="Enter a web page URL to extract content from"
        )
        urls_to_process = [url] if url else []
    else:
        # Bulk URL input
        urls_text = st.text_area(
            "Enter URLs (one per line):",
            placeholder="https://example.com/article1\nhttps://example.com/article2\nhttps://example.com/article3",
            help="Enter multiple URLs, each on a new line",
            height=150
        )
        # Split by newlines and clean up
        urls_to_process = [url.strip() for url in urls_text.split('\n') if url.strip()]
    
    if urls_to_process:
        # Validate URL format
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        # Validate all URLs
        valid_urls = []
        invalid_urls = []
        
        for url in urls_to_process:
            if url_pattern.match(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
        
        # Show validation results
        if invalid_urls:
            st.error(f"Invalid URLs found ({len(invalid_urls)}):")
            for invalid_url in invalid_urls:
                st.caption(f"❌ {invalid_url}")
        
        if valid_urls:
            # Show valid URLs count
            st.info(f"Ready to add {len(valid_urls)} valid URL(s)")
            
            # Add button
            button_text = f"➕ Add {len(valid_urls)} URL{'s' if len(valid_urls) > 1 else ''}"
            if st.button(button_text, type="primary", key="add_urls"):
                added_count = 0
                duplicate_count = 0
                
                for url in valid_urls:
                    url_key = f"url_{hash(url) % 10000}"
                    
                    if url_key not in st.session_state.uploaded_materials:
                        # Extract domain and path for display
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
                        
                        st.session_state.uploaded_materials[url_key] = {
                            'type': 'url',
                            'name': url,
                            'display_name': display_name,
                            'url': url,
                            'data': None
                        }
                        added_count += 1
                    else:
                        duplicate_count += 1
                
                # Show results
                if added_count > 0:
                    st.success(f"✅ Added {added_count} URL{'s' if added_count > 1 else ''}")
                if duplicate_count > 0:
                    st.warning(f"⚠️ Skipped {duplicate_count} duplicate URL{'s' if duplicate_count > 1 else ''}")
                
                st.rerun()

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
                    st.write(f"**URL:**")
                    # Display full URL in a code block for better formatting
                    st.code(material_meta['url'], language=None)
                
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

def render_material_library_tab():
    """Render material library interface for cross-project material reuse."""
    st.subheader("📚 Material Library")
    st.markdown("Browse and import materials from other projects. You can choose to reuse existing extractions or reprocess them.")
    
    # Search and filter controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Search materials",
            placeholder="Search by name, URL, or content...",
            key="material_library_search"
        )
    
    with col2:
        filter_type = st.selectbox(
            "Filter by type",
            ["All", "file", "url", "youtube"],
            key="material_library_filter"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("🔄 Refresh", key="refresh_material_library"):
            st.rerun()
    
    # Get materials from library
    if search_query:
        all_materials = material_library_service.search_materials(search_query)
    elif filter_type != "All":
        all_materials = material_library_service.get_materials_by_type(filter_type)
    else:
        all_materials = material_library_service.get_all_project_materials()
    
    if not all_materials:
        st.info("No materials found in other projects. Materials will appear here once you create and save them in projects.")
        return
    
    # Group materials by project
    materials_by_project = {}
    for material in all_materials:
        project_name = material["project_name"]
        if project_name not in materials_by_project:
            materials_by_project[project_name] = []
        materials_by_project[project_name].append(material)
    
    # Display materials grouped by project
    st.markdown(f"Found **{len(all_materials)}** materials across **{len(materials_by_project)}** projects:")
    
    for project_name, project_materials in materials_by_project.items():
        with st.expander(f"📁 {project_name} ({len(project_materials)} materials)", expanded=True):
            for material in project_materials:
                # Material container
                with st.container():
                    col1, col2, col3 = st.columns([4, 1, 1])
                    
                    with col1:
                        # Material info
                        icon = "📄" if material["type"] == "file" else "🌐" if material["type"] == "url" else "📺"
                        st.markdown(f"**{icon} {material['display_name']}**")
                        
                        # Show additional info
                        info_parts = []
                        if material["type"] == "file" and material.get("file_type"):
                            info_parts.append(f"Type: {material['file_type']}")
                        if material.get("size"):
                            info_parts.append(f"Size: {format_file_size(material['size'])}")
                        if material.get("url"):
                            st.code(material["url"], language=None)
                        
                        if info_parts:
                            st.caption(" | ".join(info_parts))
                        
                        # Status badges
                        status_cols = st.columns(4)
                        with status_cols[0]:
                            if material["has_binary"]:
                                st.success("✓ Has data")
                            else:
                                st.warning("○ No data")
                        
                        with status_cols[1]:
                            if material["has_extraction"]:
                                st.success("✓ Extracted")
                            else:
                                st.warning("○ Not extracted")
                    
                    with col2:
                        # Reuse extraction option
                        reuse_key = f"reuse_{material['key']}_{material['project_id']}"
                        reuse_extraction = st.checkbox(
                            "Reuse extraction",
                            value=material["has_extraction"],
                            key=reuse_key,
                            disabled=not material["has_extraction"],
                            help="Use existing extraction or reprocess the material"
                        )
                    
                    with col3:
                        # Import button
                        import_key = f"import_{material['key']}_{material['project_id']}"
                        if st.button("📥 Import", key=import_key, type="primary"):
                            # Check if material already exists
                            existing_keys = list(st.session_state.uploaded_materials.keys())
                            material_exists = False
                            
                            for existing_key in existing_keys:
                                existing_material = st.session_state.uploaded_materials[existing_key]
                                # Check if it's the same material
                                if (existing_material.get("name") == material["name"] and 
                                    existing_material.get("type") == material["type"]):
                                    material_exists = True
                                    break
                            
                            if material_exists:
                                st.warning("This material is already in your current project.")
                            else:
                                # Import the material
                                imported_data = material_library_service.import_material_from_project(
                                    material, 
                                    include_extraction=reuse_extraction
                                )
                                
                                if imported_data:
                                    # Generate a new key for this material
                                    import uuid
                                    new_key = f"{material['type']}_{str(uuid.uuid4())[:8]}"
                                    
                                    # Add to session state
                                    st.session_state.uploaded_materials[new_key] = imported_data["material"]
                                    
                                    # Add extracted content if available
                                    if imported_data["extracted_content"] and reuse_extraction:
                                        st.session_state.extracted_content[new_key] = imported_data["extracted_content"]
                                    
                                    st.success(f"✅ Imported: {material['display_name']}")
                                    st.rerun()
                                else:
                                    st.error("Failed to import material")
                    
                    st.divider()

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
            # Display full URL in a code block for better formatting
            st.code(material['url'], language=None)
        elif material['type'] == 'youtube':
            st.markdown(f"### 📺 {material.get('display_name', 'YouTube')}")
            # Display full URL in a code block for better formatting
            st.code(material['url'], language=None)
        
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
            # Show full URL below the display name
            st.caption(material['url'])
        elif material['type'] == 'youtube':
            st.write(f"📺 {display_name}")
            # Show full URL below the display name
            st.caption(material['url'])
    
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

def convert_path_to_underscore_name(path: str) -> str:
    """Convert a file path to underscore-separated name.
    
    Examples:
        signs/taurus/1.jpg → signs_taurus_1.jpg
        folder/subfolder/file.pdf → folder_subfolder_file.pdf
    """
    # Replace forward slashes and backslashes with underscores
    return path.replace('/', '_').replace('\\', '_')

def import_files_from_folder(folder_path: str, relative_base: str = "", recursive: bool = True, preserve_structure: bool = True) -> int:
    """Import files from a local folder into the upload materials.
    
    Args:
        folder_path: Absolute path to the folder
        relative_base: Base path for relative naming (e.g., "signs/taurus")
        recursive: Whether to import files from subfolders
        preserve_structure: Whether to preserve folder structure in file names
    
    Returns:
        Number of files imported
    """
    imported_count = 0
    
    if recursive:
        # Walk through all subdirectories
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Get relative path from the base folder
                rel_path = os.path.relpath(file_path, folder_path)
                if relative_base:
                    full_rel_path = os.path.join(relative_base, rel_path)
                else:
                    full_rel_path = rel_path
                
                # Determine display name based on preserve_structure setting
                if preserve_structure:
                    display_name = convert_path_to_underscore_name(full_rel_path)
                else:
                    display_name = os.path.basename(file)
                
                # Check if it's a supported file type
                ext = os.path.splitext(file)[1].lower().replace('.', '')
                mime_type, _ = mimetypes.guess_type(file)
                
                if ext in SUPPORTED_FILE_TYPES or ext in ['jpg', 'jpeg', 'png', 'pdf', 'txt']:
                    file_key = f"file_{display_name}"
                    
                    if file_key not in st.session_state.uploaded_materials:
                        # Read file data
                        try:
                            with open(file_path, 'rb') as f:
                                file_data = f.read()
                            
                            # Store file info
                            st.session_state.uploaded_materials[file_key] = {
                                'type': 'file',
                                'name': full_rel_path,  # Original path
                                'display_name': display_name,  # Processed name
                                'file_type': mime_type or f'application/{ext}',
                                'size': len(file_data),
                                'data': file_data
                            }
                            imported_count += 1
                        except Exception as e:
                            st.error(f"Failed to import {file}: {str(e)}")
    else:
        # Only import files from the specified folder (not subfolders)
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            
            if os.path.isfile(file_path):
                # Build the relative path
                if relative_base:
                    full_rel_path = os.path.join(relative_base, file)
                else:
                    full_rel_path = file
                
                # Determine display name based on preserve_structure setting
                if preserve_structure and relative_base:
                    display_name = convert_path_to_underscore_name(full_rel_path)
                else:
                    display_name = file
                
                # Check if it's a supported file type
                ext = os.path.splitext(file)[1].lower().replace('.', '')
                mime_type, _ = mimetypes.guess_type(file)
                
                if ext in SUPPORTED_FILE_TYPES or ext in ['jpg', 'jpeg', 'png', 'pdf', 'txt']:
                    file_key = f"file_{display_name}"
                    
                    if file_key not in st.session_state.uploaded_materials:
                        # Read file data
                        try:
                            with open(file_path, 'rb') as f:
                                file_data = f.read()
                            
                            # Store file info
                            st.session_state.uploaded_materials[file_key] = {
                                'type': 'file',
                                'name': full_rel_path,  # Original path
                                'display_name': display_name,  # Processed name
                                'file_type': mime_type or f'application/{ext}',
                                'size': len(file_data),
                                'data': file_data
                            }
                            imported_count += 1
                        except Exception as e:
                            st.error(f"Failed to import {file}: {str(e)}")
    
    return imported_count

def build_folder_tree(base_path):
    """Build a folder tree structure."""
    folder_tree = {}
    
    for root, dirs, files in os.walk(base_path):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        rel_path = os.path.relpath(root, base_path)
        
        # Count supported files in this directory
        supported_files = []
        for file in files:
            ext = os.path.splitext(file)[1].lower().replace('.', '')
            if ext in SUPPORTED_FILE_TYPES or ext in ['jpg', 'jpeg', 'png', 'pdf', 'txt']:
                supported_files.append(file)
        
        if rel_path == '.':
            # Root directory
            if supported_files or dirs:
                folder_tree['_root'] = {
                    'path': base_path,
                    'name': 'data/ (root)',
                    'file_count': len(supported_files),
                    'has_subdirs': len(dirs) > 0
                }
        else:
            # Subdirectory
            if supported_files or dirs:
                folder_tree[rel_path] = {
                    'path': root,
                    'name': os.path.basename(root),
                    'file_count': len(supported_files),
                    'has_subdirs': len(dirs) > 0,
                    'level': rel_path.count(os.sep)
                }
    
    return folder_tree

def render_folder_tree(folder_tree, base_path):
    """Render folder tree and return selected path."""
    # Sort folders by path for hierarchical display
    sorted_folders = sorted(folder_tree.items(), key=lambda x: x[0] if x[0] != '_root' else '')
    
    selected_folder = None
    
    for folder_key, folder_info in sorted_folders:
        # Determine indentation based on folder level
        if folder_key == '_root':
            indent = ""
            display_name = "📁 **data/** (root)"
        else:
            level = folder_info.get('level', 0)
            indent = "&nbsp;" * (level * 4)
            folder_name = folder_info['name']
            display_name = f"{indent}📁 **{folder_name}/**"
        
        # Add file count
        file_count = folder_info['file_count']
        if file_count > 0:
            display_name += f" ({file_count} files)"
        
        # Create selectable button
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(display_name, unsafe_allow_html=True)
        with col2:
            if st.button("Select", key=f"select_{folder_key}", use_container_width=True):
                selected_folder = folder_info['path']
    
    # Store selected folder in session state
    if selected_folder:
        st.session_state['selected_folder_path'] = selected_folder
    
    # Return the selected folder from session state
    return st.session_state.get('selected_folder_path')

def count_files_in_folder(folder_path, recursive=True):
    """Count supported files in a folder."""
    file_count = 0
    file_list = []
    
    if recursive:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower().replace('.', '')
                if ext in SUPPORTED_FILE_TYPES or ext in ['jpg', 'jpeg', 'png', 'pdf', 'txt']:
                    file_count += 1
                    file_list.append(os.path.join(root, file))
    else:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower().replace('.', '')
                if ext in SUPPORTED_FILE_TYPES or ext in ['jpg', 'jpeg', 'png', 'pdf', 'txt']:
                    file_count += 1
                    file_list.append(file_path)
    
    return file_count, file_list 