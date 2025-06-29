"""
Prompt Workspace UI Component
Handles prompt creation, editing, and organization for extraction, cleaning, and synthesis
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
import json
from services.prompt_management import prompt_workspace_service

def render_prompt_workspace():
    """Render the prompt workspace interface."""
    # Navigation header
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("← Back to Projects", use_container_width=True):
            st.session_state.view_mode = 'dashboard'
            st.rerun()
    
    with col2:
        st.header("📝 Prompt Management Workspace")
    
    st.markdown("Create and manage prompts for extraction, cleaning, and synthesis operations.")
    
    # Workspace selection and management in sidebar
    with st.sidebar:
        render_workspace_sidebar()
    
    # Main content area
    active_workspace = prompt_workspace_service.get_active_workspace()
    if active_workspace:
        render_workspace_content(active_workspace)
    else:
        st.warning("No active workspace found. Please create or select a workspace.")

def render_workspace_sidebar():
    """Render workspace management sidebar."""
    st.subheader("🗂️ Workspaces")
    
    # List workspaces
    workspaces = prompt_workspace_service.list_workspaces()
    
    if workspaces:
        # Workspace selector
        workspace_names = [ws["name"] + (" ✓" if ws["active"] else "") for ws in workspaces]
        workspace_ids = [ws["id"] for ws in workspaces]
        
        # Get current active workspace index
        active_idx = next((i for i, ws in enumerate(workspaces) if ws["active"]), 0)
        
        selected_idx = st.selectbox(
            "Select Workspace",
            range(len(workspace_names)),
            format_func=lambda x: workspace_names[x],
            index=active_idx,
            key="workspace_selector"
        )
        
        selected_workspace_id = workspace_ids[selected_idx]
        selected_workspace = workspaces[selected_idx]
        
        # Activate button if not active
        if not selected_workspace["active"]:
            if st.button("Activate", key="activate_workspace"):
                if prompt_workspace_service.set_active_workspace(selected_workspace_id):
                    st.success("Workspace activated!")
                    st.rerun()
        
        # Workspace info
        with st.expander("Workspace Info", expanded=False):
            st.write(f"**Description:** {selected_workspace['description']}")
            st.write(f"**Created:** {selected_workspace['created_at'][:10]}")
            st.write(f"**Updated:** {selected_workspace['updated_at'][:10]}")
            
            prompt_counts = selected_workspace.get('prompt_counts', {})
            if prompt_counts:
                st.write("**Prompts:**")
                for ptype, count in prompt_counts.items():
                    st.write(f"- {ptype.capitalize()}: {count}")
    
    st.divider()
    
    # Create new workspace
    with st.expander("➕ New Workspace", expanded=False):
        new_name = st.text_input("Workspace Name", key="new_workspace_name")
        new_desc = st.text_area("Description", key="new_workspace_desc", height=80)
        
        if st.button("Create Workspace", key="create_workspace"):
            if new_name:
                workspace = prompt_workspace_service.create_workspace(new_name, new_desc)
                if workspace:
                    st.success(f"Created workspace: {new_name}")
                    st.rerun()
            else:
                st.error("Please enter a workspace name")
    
    # Workspace operations
    if workspaces:
        st.divider()
        st.subheader("🔧 Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Duplicate workspace
            if st.button("📋 Duplicate", key="duplicate_workspace"):
                new_name = f"{selected_workspace['name']} (Copy)"
                new_ws = prompt_workspace_service.duplicate_workspace(selected_workspace_id, new_name)
                if new_ws:
                    st.success("Workspace duplicated!")
                    st.rerun()
        
        with col2:
            # Export workspace
            if st.button("💾 Export", key="export_workspace"):
                export_path = Path("exports") / f"{selected_workspace['name']}_export.json"
                export_path.parent.mkdir(exist_ok=True)
                
                if prompt_workspace_service.export_workspace(selected_workspace_id, export_path):
                    with open(export_path, "r") as f:
                        st.download_button(
                            label="Download Export",
                            data=f.read(),
                            file_name=export_path.name,
                            mime="application/json"
                        )
        
        # Import workspace
        uploaded_file = st.file_uploader(
            "Import Workspace",
            type=["json"],
            key="import_workspace_file"
        )
        
        if uploaded_file:
            if st.button("Import", key="import_workspace"):
                # Save uploaded file temporarily
                temp_path = Path("temp_import.json")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Import workspace
                imported_ws = prompt_workspace_service.import_workspace(temp_path)
                if imported_ws:
                    st.success(f"Imported workspace: {imported_ws['name']}")
                    temp_path.unlink()  # Clean up
                    st.rerun()

def render_workspace_content(workspace: dict):
    """Render the main workspace content area."""
    # Tabs for different prompt types
    tab1, tab2, tab3 = st.tabs(["🔍 Extraction Prompts", "🧹 Cleaning Prompts", "✨ Synthesis Prompts"])
    
    with tab1:
        render_prompt_section(workspace, "extraction")
    
    with tab2:
        render_prompt_section(workspace, "cleaning")
    
    with tab3:
        render_prompt_section(workspace, "synthesis")

def render_prompt_section(workspace: dict, prompt_type: str):
    """Render a section for a specific prompt type."""
    st.subheader(f"{prompt_type.capitalize()} Prompts")
    
    # Get prompts for this type
    prompts = workspace["prompts"].get(prompt_type, {})
    active_prompts = {pid: p for pid, p in prompts.items() if p.get("active", True)}
    
    # Categories for this prompt type
    categories = workspace["categories"].get(prompt_type, [])
    
    # Add new prompt button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button(f"➕ New {prompt_type.capitalize()}", key=f"new_{prompt_type}_prompt"):
            st.session_state[f"creating_{prompt_type}_prompt"] = True
    
    # Create new prompt form
    if st.session_state.get(f"creating_{prompt_type}_prompt", False):
        with st.container():
            st.markdown("### Create New Prompt")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                new_name = st.text_input("Prompt Name", key=f"new_{prompt_type}_name")
            
            with col2:
                new_category = st.selectbox("Category", categories, key=f"new_{prompt_type}_category")
            
            new_content = st.text_area(
                "Prompt Content",
                height=150,
                key=f"new_{prompt_type}_content",
                placeholder="Enter the prompt instructions..."
            )
            
            # Metadata section
            with st.expander("Metadata (Optional)", expanded=False):
                metadata = {}
                
                col1, col2 = st.columns(2)
                with col1:
                    metadata["author"] = st.text_input("Author", key=f"new_{prompt_type}_author")
                    metadata["tags"] = st.text_input("Tags (comma-separated)", key=f"new_{prompt_type}_tags")
                
                with col2:
                    metadata["version_notes"] = st.text_area("Version Notes", key=f"new_{prompt_type}_notes", height=68)
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("Save", key=f"save_{prompt_type}_prompt"):
                    if new_name and new_content:
                        # Process tags
                        if metadata.get("tags"):
                            metadata["tags"] = [tag.strip() for tag in metadata["tags"].split(",")]
                        
                        prompt_id = prompt_workspace_service.add_prompt(
                            workspace["id"],
                            prompt_type,
                            new_category,
                            new_name,
                            new_content,
                            metadata
                        )
                        
                        if prompt_id:
                            st.success("Prompt created successfully!")
                            st.session_state[f"creating_{prompt_type}_prompt"] = False
                            st.rerun()
                    else:
                        st.error("Please provide both name and content")
            
            with col2:
                if st.button("Cancel", key=f"cancel_{prompt_type}_prompt"):
                    st.session_state[f"creating_{prompt_type}_prompt"] = False
                    st.rerun()
        
        st.divider()
    
    # Display prompts by category
    if active_prompts:
        # Group prompts by category
        prompts_by_category = {}
        for pid, prompt in active_prompts.items():
            category = prompt.get("category", "Uncategorized")
            if category not in prompts_by_category:
                prompts_by_category[category] = []
            prompts_by_category[category].append((pid, prompt))
        
        # Display each category
        for category in categories:
            if category in prompts_by_category:
                with st.expander(f"📁 {category} ({len(prompts_by_category[category])})", expanded=True):
                    for prompt_id, prompt in prompts_by_category[category]:
                        render_prompt_card(workspace["id"], prompt_type, prompt_id, prompt)
    else:
        st.info(f"No {prompt_type} prompts yet. Click the button above to create one.")

def render_prompt_card(workspace_id: str, prompt_type: str, prompt_id: str, prompt: dict):
    """Render a single prompt card with edit/delete options."""
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"**{prompt['name']}**")
            
            # Show metadata if available
            metadata_items = []
            if prompt.get("metadata", {}).get("author"):
                metadata_items.append(f"👤 {prompt['metadata']['author']}")
            if prompt.get("metadata", {}).get("tags"):
                tags = prompt['metadata']['tags']
                if isinstance(tags, list):
                    metadata_items.append(f"🏷️ {', '.join(tags)}")
            if metadata_items:
                st.caption(" | ".join(metadata_items))
        
        with col2:
            st.caption(f"v{prompt.get('version', 1)}")
            st.caption(prompt['updated_at'][:10])
        
        with col3:
            col_edit, col_del = st.columns(2)
            
            with col_edit:
                if st.button("✏️", key=f"edit_{prompt_id}", help="Edit prompt"):
                    st.session_state[f"editing_{prompt_id}"] = True
            
            with col_del:
                if st.button("🗑️", key=f"delete_{prompt_id}", help="Delete prompt"):
                    if prompt_workspace_service.delete_prompt(workspace_id, prompt_type, prompt_id):
                        st.rerun()
        
        # Show content preview or edit form
        if st.session_state.get(f"editing_{prompt_id}", False):
            # Edit form
            updated_name = st.text_input("Name", value=prompt['name'], key=f"edit_name_{prompt_id}")
            updated_category = st.selectbox(
                "Category",
                prompt_workspace_service.load_workspace(workspace_id)["categories"][prompt_type],
                index=prompt_workspace_service.load_workspace(workspace_id)["categories"][prompt_type].index(prompt['category']),
                key=f"edit_category_{prompt_id}"
            )
            updated_content = st.text_area(
                "Content",
                value=prompt['content'],
                height=150,
                key=f"edit_content_{prompt_id}"
            )
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if st.button("Save Changes", key=f"save_edit_{prompt_id}"):
                    updates = {
                        "name": updated_name,
                        "category": updated_category,
                        "content": updated_content
                    }
                    
                    if prompt_workspace_service.update_prompt(workspace_id, prompt_type, prompt_id, updates):
                        st.success("Prompt updated!")
                        st.session_state[f"editing_{prompt_id}"] = False
                        st.rerun()
            
            with col2:
                if st.button("Cancel", key=f"cancel_edit_{prompt_id}"):
                    st.session_state[f"editing_{prompt_id}"] = False
                    st.rerun()
        else:
            # Show content preview
            with st.expander("View Content", expanded=False):
                st.text(prompt['content'])
                
                # Copy to clipboard button
                if st.button("📋 Copy", key=f"copy_{prompt_id}"):
                    st.code(prompt['content'], language=None)
                    st.info("Content displayed above. Select and copy manually.")
        
        st.divider()

def render_prompt_statistics(workspace: dict):
    """Render statistics about the prompts in the workspace."""
    st.subheader("📊 Workspace Statistics")
    
    # Count prompts by type and category
    stats = {}
    for prompt_type in ["extraction", "cleaning", "synthesis"]:
        prompts = workspace["prompts"].get(prompt_type, {})
        active_prompts = [p for p in prompts.values() if p.get("active", True)]
        
        stats[prompt_type] = {
            "total": len(active_prompts),
            "by_category": {}
        }
        
        for prompt in active_prompts:
            category = prompt.get("category", "Uncategorized")
            stats[prompt_type]["by_category"][category] = stats[prompt_type]["by_category"].get(category, 0) + 1
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Extraction Prompts", stats["extraction"]["total"])
        for cat, count in stats["extraction"]["by_category"].items():
            st.caption(f"{cat}: {count}")
    
    with col2:
        st.metric("Cleaning Prompts", stats["cleaning"]["total"])
        for cat, count in stats["cleaning"]["by_category"].items():
            st.caption(f"{cat}: {count}")
    
    with col3:
        st.metric("Synthesis Prompts", stats["synthesis"]["total"])
        for cat, count in stats["synthesis"]["by_category"].items():
            st.caption(f"{cat}: {count}") 