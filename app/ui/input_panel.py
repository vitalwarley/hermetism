import streamlit as st
from config.settings import SUPPORTED_FILE_TYPES
from services.extraction import extraction_service
from utils.helpers import format_file_size

def render_input_panel():
    """Render the input materials panel."""
    st.header("📥 Input Materials")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Drop your files here",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True
    )
    
    # Process uploaded files
    for uploaded_file in uploaded_files:
        file_key = uploaded_file.name
        
        if file_key not in st.session_state.materials:
            _handle_file_upload(uploaded_file, file_key)
    
    # Display current materials
    if st.session_state.materials:
        st.subheader("📚 Loaded Materials")
        for name, content in st.session_state.materials.items():
            with st.expander(name):
                st.text(content[:500] + "..." if len(content) > 500 else content)
                if st.button(f"Remove {name}", key=f"remove_{name}"):
                    del st.session_state.materials[name]
                    st.rerun()

def _handle_file_upload(uploaded_file, file_key: str):
    """Handle file upload and show processing options."""
    file_type = uploaded_file.type
    
    # PDF files need special handling for page range selection
    if file_type == "application/pdf":
        _handle_pdf_upload(uploaded_file, file_key)
    else:
        # Process other file types immediately
        with st.spinner(f"Processing {uploaded_file.name}..."):
            _process_file(uploaded_file, file_key)

def _handle_pdf_upload(uploaded_file, file_key: str):
    """Handle PDF upload with page range configuration."""
    st.subheader(f"📄 Configure PDF: {uploaded_file.name}")
    
    # Get PDF info first
    try:
        pdf_info = extraction_service.get_pdf_info(uploaded_file)
        uploaded_file.seek(0)  # Reset file pointer
        
        if pdf_info:
            total_pages = pdf_info['total_pages']
            metadata = pdf_info.get('metadata', {})
            
            # Display PDF information
            col_info, col_meta = st.columns([1, 1])
            
            with col_info:
                st.info(f"📊 **Total pages:** {total_pages}")
                st.caption(f"File size: {format_file_size(len(uploaded_file.getvalue()))}")
            
            with col_meta:
                if any(v != 'Unknown' for v in metadata.values()):
                    with st.expander("📋 PDF Metadata", expanded=False):
                        for key, value in metadata.items():
                            if value and value != 'Unknown':
                                st.text(f"{key.title()}: {value}")
                else:
                    st.caption("No metadata available")
            
            # Page range selection
            st.markdown("---")
            use_range = st.checkbox(
                "📑 Specify page range",
                key=f"use_range_{file_key}",
                help="Select specific pages to extract. Leave unchecked to extract all pages."
            )
            
            page_range = None
            if use_range:
                st.markdown("**Page Selection:**")
                col_start, col_end, col_preview = st.columns([1, 1, 1])
                
                with col_start:
                    start_page = st.number_input(
                        "Start page",
                        min_value=1,
                        max_value=total_pages,
                        value=1,
                        key=f"start_{file_key}"
                    )
                with col_end:
                    end_page = st.number_input(
                        "End page",
                        min_value=1,  # Fixed: Don't use dynamic min_value
                        max_value=total_pages,
                        value=min(10, total_pages),
                        key=f"end_{file_key}"
                    )
                
                with col_preview:
                    if start_page <= end_page:
                        pages_count = end_page - start_page + 1
                        st.metric("Pages to extract", pages_count)
                        if pages_count > 50:
                            st.warning("⚠️ Large page range may take longer to process")
                    else:
                        st.error("❌ Invalid range")
                
                # Validation and range setup
                if start_page > end_page:
                    st.error(f"❌ Start page ({start_page}) cannot be greater than end page ({end_page})!")
                    st.info("💡 **Tip:** Adjust the page numbers so that start ≤ end")
                    page_range = None  # Don't set page_range if invalid
                else:
                    page_range = (start_page, end_page)
                    st.success(f"✅ Will extract pages {start_page} to {end_page}")
            else:
                if total_pages > 50:
                    st.warning(f"⚠️ This PDF has {total_pages} pages. Processing may take some time.")
            
            # LLM cleaning option
            st.markdown("---")
            use_cleaning = st.checkbox(
                "🧹 Clean text with AI",
                key=f"clean_{file_key}",
                help="Use AI to clean and structure the extracted text"
            )
            
            cleaning_context = None
            if use_cleaning:
                cleaning_context = st.text_input(
                    "Context for cleaning",
                    value="hermetic text",
                    key=f"context_{file_key}",
                    help="Provide context to help the AI understand the type of content",
                    placeholder="e.g., hermetic text, tarot cards, astrological charts"
                )
            
            # Process button
            st.markdown("---")
            process_button_col = st.columns([1, 2, 1])[1]  # Center the button
            with process_button_col:
                # Disable button if page range is invalid
                button_disabled = use_range and page_range is None
                button_help = "Fix the page range first" if button_disabled else None
                
                if st.button(
                    f"📖 Process {uploaded_file.name}", 
                    type="primary", 
                    key=f"process_{file_key}",
                    use_container_width=True,
                    disabled=button_disabled,
                    help=button_help
                ):
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        _process_pdf_with_config(uploaded_file, file_key, page_range, use_cleaning, cleaning_context)
        else:
            st.error("❌ Unable to read PDF information. The file may be corrupted or password-protected.")
            
    except Exception as e:
        st.error(f"❌ Error reading PDF: {str(e)}")
        # Fallback option
        if st.button(f"Try Basic Processing for {uploaded_file.name}", key=f"fallback_{file_key}"):
            with st.spinner(f"Processing {uploaded_file.name}..."):
                _process_file(uploaded_file, file_key)

def _process_pdf_with_config(uploaded_file, file_key: str, page_range, use_cleaning: bool, cleaning_context: str):
    """Process PDF with the specified configuration."""
    # Extract text
    raw_text = extraction_service.extract_text_from_pdf(uploaded_file, page_range)
    
    if raw_text:
        if use_cleaning and cleaning_context:
            cleaned_text = extraction_service.clean_extracted_text(raw_text, cleaning_context)
            st.session_state.materials[file_key] = cleaned_text
            st.success(f"✅ {uploaded_file.name} processed and cleaned successfully!")
        else:
            st.session_state.materials[file_key] = raw_text
            st.success(f"✅ {uploaded_file.name} processed successfully!")
    else:
        st.error(f"❌ Failed to extract text from {uploaded_file.name}")

def _process_file(uploaded_file, file_key: str):
    """Process a single uploaded file based on its type (legacy method for non-PDF files)."""
    file_type = uploaded_file.type
    
    # Image extraction
    if file_type in ["image/jpeg", "image/png"]:
        _process_image(uploaded_file, file_key)
    
    # Text files
    elif file_type == "text/plain":
        _process_text_file(uploaded_file, file_key)

def _process_image(uploaded_file, file_key: str):
    """Process image file with custom extraction prompt."""
    extraction_prompt = st.text_area(
        f"Extraction prompt for {uploaded_file.name}",
        "Extract all text and describe symbolic elements from this image."
    )
    
    extracted = extraction_service.extract_from_image(uploaded_file, extraction_prompt)
    if extracted:
        st.session_state.materials[file_key] = extracted

def _process_text_file(uploaded_file, file_key: str):
    """Process text file."""
    text_content = extraction_service.extract_from_text_file(uploaded_file)
    if text_content:
        st.session_state.materials[file_key] = text_content 