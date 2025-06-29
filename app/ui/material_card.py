import streamlit as st
from utils.helpers import format_file_size
import re

def render_material_card(material_key: str, material_content: str, col_index: int):
    """Render a single material card with type-specific styling."""
    
    # Determine material type from key
    material_type = _get_material_type(material_key)
    
    # Get card styling based on type
    icon, type_label, color = _get_card_styling(material_type)
    
    # Create card container
    with st.container():
        # Card styling
        st.markdown(f"""
        <style>
        .material-card-{col_index} {{
            background-color: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }}
        .material-card-{col_index}:hover {{
            border-color: {color};
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .card-header {{
            display: flex;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        .card-icon {{
            font-size: 2rem;
            margin-right: 0.5rem;
        }}
        .card-type {{
            color: {color};
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
        }}
        .card-title {{
            font-weight: 600;
            margin: 0.5rem 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .card-metadata {{
            color: #666;
            font-size: 0.875rem;
            margin: 0.25rem 0;
        }}
        .card-actions {{
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Card content
        st.markdown(f'<div class="material-card-{col_index}">', unsafe_allow_html=True)
        
        # Header with icon and type
        st.markdown(f"""
        <div class="card-header">
            <span class="card-icon">{icon}</span>
            <span class="card-type">{type_label}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Title (filename or URL)
        display_name = _get_display_name(material_key)
        st.markdown(f'<div class="card-title" title="{display_name}">{display_name}</div>', unsafe_allow_html=True)
        
        # Metadata
        metadata = _get_material_metadata(material_key, material_content)
        st.markdown(f'<div class="card-metadata">{metadata}</div>', unsafe_allow_html=True)
        
        # Tags placeholder (for future implementation)
        if material_type in ['image', 'pdf']:
            st.markdown('<div class="card-metadata" style="color: #1976d2;">📌 No tags yet</div>', unsafe_allow_html=True)
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👁️ Preview", key=f"preview_{material_key}_{col_index}", use_container_width=True):
                st.session_state[f"preview_{material_key}"] = True
                
        with col2:
            if st.button("🗑️ Remove", key=f"remove_{material_key}_{col_index}", use_container_width=True):
                if material_key in st.session_state.materials:
                    del st.session_state.materials[material_key]
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Preview modal (if activated)
        if st.session_state.get(f"preview_{material_key}", False):
            _render_preview_modal(material_key, material_content)

def render_material_grid():
    """Render all materials in a responsive grid layout."""
    if not st.session_state.materials:
        return
    
    # Add a simple search bar
    search_query = st.text_input("🔍 Search materials...", placeholder="Search by filename or content...")
    
    # Filter materials based on search
    filtered_materials = {}
    for key, content in st.session_state.materials.items():
        if not search_query or search_query.lower() in key.lower() or search_query.lower() in content.lower()[:200]:
            filtered_materials[key] = content
    
    if not filtered_materials:
        st.info("No materials found matching your search.")
        return
    
    # Display count
    st.caption(f"Showing {len(filtered_materials)} of {len(st.session_state.materials)} materials")
    
    # Create responsive grid (3 columns on desktop, 1 on mobile)
    num_cols = 3
    cols = st.columns(num_cols)
    
    # Render cards in grid
    for idx, (material_key, material_content) in enumerate(filtered_materials.items()):
        col_index = idx % num_cols
        with cols[col_index]:
            render_material_card(material_key, material_content, idx)

def _get_material_type(material_key: str) -> str:
    """Determine material type from key."""
    if material_key.startswith("url_"):
        return "url"
    elif material_key.startswith("youtube_"):
        return "youtube"
    elif material_key.endswith((".jpg", ".jpeg", ".png")):
        return "image"
    elif material_key.endswith(".pdf"):
        return "pdf"
    elif material_key.endswith(".txt"):
        return "text"
    else:
        return "unknown"

def _get_card_styling(material_type: str) -> tuple:
    """Get icon, label, and color for material type."""
    styling = {
        "image": ("🖼️", "IMAGE", "#4caf50"),
        "pdf": ("📄", "PDF", "#f44336"),
        "url": ("🌐", "WEB", "#2196f3"),
        "youtube": ("📺", "VIDEO", "#ff9800"),
        "text": ("📝", "TEXT", "#9c27b0"),
        "unknown": ("📎", "FILE", "#757575")
    }
    return styling.get(material_type, styling["unknown"])

def _get_display_name(material_key: str) -> str:
    """Get a clean display name from material key."""
    # Remove prefixes
    name = material_key
    for prefix in ["url_", "youtube_"]:
        if name.startswith(prefix):
            name = name[len(prefix):]
    
    # For URLs, try to extract domain or title
    if material_key.startswith("url_"):
        # This is simplified - in real implementation, you might store the actual URL
        return f"Web Content {name}"
    elif material_key.startswith("youtube_"):
        return f"YouTube Video {name}"
    
    # For files, return the filename
    return name

def _get_material_metadata(material_key: str, material_content: str) -> str:
    """Generate metadata string for material."""
    content_size = len(material_content)
    
    if material_key.endswith(".pdf"):
        # Estimate pages (very rough)
        estimated_pages = max(1, content_size // 3000)
        return f"{format_file_size(content_size)} • ~{estimated_pages} pages"
    elif material_key.endswith((".jpg", ".jpeg", ".png")):
        return f"Image • {format_file_size(content_size)}"
    elif material_key.startswith("url_"):
        word_count = len(material_content.split())
        return f"{word_count:,} words • Web content"
    elif material_key.startswith("youtube_"):
        word_count = len(material_content.split())
        # Estimate duration (very rough - 150 words per minute)
        estimated_minutes = max(1, word_count // 150)
        return f"~{estimated_minutes} min • {word_count:,} words"
    else:
        return format_file_size(content_size)

def _render_preview_modal(material_key: str, material_content: str):
    """Render a preview modal for the material."""
    with st.expander("📄 Material Preview", expanded=True):
        st.markdown(f"**{_get_display_name(material_key)}**")
        
        # Show content preview
        preview_length = 1000
        if len(material_content) > preview_length:
            st.text_area(
                "Content preview:",
                value=material_content[:preview_length] + "...\n\n[Content truncated]",
                height=300,
                disabled=True
            )
            st.caption(f"Showing first {preview_length} characters of {len(material_content):,} total")
        else:
            st.text_area(
                "Full content:",
                value=material_content,
                height=300,
                disabled=True
            )
        
        # Close button
        if st.button("Close Preview", key=f"close_preview_{material_key}"):
            st.session_state[f"preview_{material_key}"] = False
            st.rerun() 