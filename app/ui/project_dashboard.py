"""
Project Dashboard UI - Landing page for managing hermetic workbench projects
"""

import streamlit as st
from datetime import datetime
from services.project import project_service
from utils.helpers import load_project_state

def render_project_dashboard():
    """Render the project dashboard with project cards and actions."""
    st.title("🔮 Hermetic Workbench - Projects")
    st.markdown("Manage your hermetic synthesis projects")
    
    # New project section
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader("📚 Your Projects")
        with col3:
            if st.button("➕ New Project", use_container_width=True, type="primary"):
                st.session_state.show_new_project_dialog = True
    
    # New project dialog
    if st.session_state.get('show_new_project_dialog', False):
        with st.container():
            st.divider()
            st.subheader("Create New Project")
            
            col1, col2 = st.columns(2)
            with col1:
                project_name = st.text_input("Project Name", placeholder="My Hermetic Synthesis")
            with col2:
                project_desc = st.text_area("Description (optional)", placeholder="Brief description of your project")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("Create", type="primary"):
                    if project_name:
                        # Create new project
                        new_project = project_service.create_project(project_name, project_desc)
                        st.session_state.current_project_id = new_project['id']
                        st.session_state.current_project = new_project
                        st.session_state.view_mode = 'workbench'
                        load_project_state(new_project['state'])
                        st.session_state.show_new_project_dialog = False
                        st.rerun()
                    else:
                        st.error("Please enter a project name")
            with col2:
                if st.button("Cancel"):
                    st.session_state.show_new_project_dialog = False
                    st.rerun()
            
            st.divider()
    
    # List existing projects
    projects = project_service.list_projects()
    
    if not projects:
        st.info("👋 Welcome! Create your first project to get started.")
    else:
        # Display projects in a grid
        num_cols = 3
        for i in range(0, len(projects), num_cols):
            cols = st.columns(num_cols)
            for j, col in enumerate(cols):
                if i + j < len(projects):
                    with col:
                        render_project_card(projects[i + j])

def render_project_card(project: dict):
    """Render a single project card with actions."""
    with st.container():
        # Card container with custom styling
        with st.container():
            # Project info
            st.markdown(f"### 📁 {project['name']}")
            
            if project['description']:
                st.caption(project['description'])
            
            # Project metadata
            created = datetime.fromisoformat(project['created_at'])
            updated = datetime.fromisoformat(project['updated_at'])
            
            st.markdown(f"**Last updated:** {updated.strftime('%Y-%m-%d %H:%M')}")
            st.markdown(f"**Phase:** {project_service.get_project_phase_name(project['current_phase'])}")
            st.markdown(f"**Materials:** {project['materials_count']}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📂 Open", key=f"open_{project['id']}", use_container_width=True):
                    # Load project
                    project_data = project_service.load_project(project['id'])
                    if project_data:
                        st.session_state.current_project_id = project['id']
                        st.session_state.current_project = project_data
                        st.session_state.view_mode = 'workbench'
                        load_project_state(project_data['state'])
                        st.rerun()
            
            with col2:
                if st.button("📋 Copy", key=f"copy_{project['id']}", use_container_width=True):
                    st.session_state[f"show_copy_dialog_{project['id']}"] = True
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{project['id']}", use_container_width=True):
                    st.session_state[f"confirm_delete_{project['id']}"] = True
            
            # Copy dialog
            if st.session_state.get(f"show_copy_dialog_{project['id']}", False):
                st.divider()
                new_name = st.text_input("New project name", value=f"{project['name']} (Copy)", 
                                       key=f"copy_name_{project['id']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Duplicate", key=f"confirm_copy_{project['id']}"):
                        if new_name:
                            new_project = project_service.duplicate_project(project['id'], new_name)
                            if new_project:
                                st.success(f"Project duplicated: {new_name}")
                                st.session_state[f"show_copy_dialog_{project['id']}"] = False
                                st.rerun()
                with col2:
                    if st.button("Cancel", key=f"cancel_copy_{project['id']}"):
                        st.session_state[f"show_copy_dialog_{project['id']}"] = False
                        st.rerun()
            
            # Delete confirmation
            if st.session_state.get(f"confirm_delete_{project['id']}", False):
                st.warning(f"⚠️ Delete '{project['name']}'? This cannot be undone.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Delete", key=f"yes_delete_{project['id']}", type="secondary"):
                        if project_service.delete_project(project['id']):
                            st.success("Project deleted")
                            st.session_state[f"confirm_delete_{project['id']}"] = False
                            st.rerun()
                with col2:
                    if st.button("Cancel", key=f"cancel_delete_{project['id']}"):
                        st.session_state[f"confirm_delete_{project['id']}"] = False
                        st.rerun()
        
        st.divider() 