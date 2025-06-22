"""
Project management service for handling multiple hermetic workbench projects
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List
import uuid
from config.settings import SESSIONS_DIR, MODEL_VISION, MODEL_SYNTHESIS

class ProjectService:
    """Service for managing projects with isolated workbench states."""
    
    def __init__(self, base_dir: str = "projects"):
        self.logger = logging.getLogger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def create_project(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new project with initial state.
        
        Args:
            name: Project name
            description: Optional project description
            
        Returns:
            Project data dictionary
        """
        project_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        project_data = {
            "id": project_id,
            "name": name,
            "description": description,
            "created_at": timestamp,
            "updated_at": timestamp,
            "state": {
                "current_phase": 0,
                "uploaded_materials": {},
                "extraction_configs": {},
                "extracted_content": {},
                "synthesis_config": {
                    "custom_prompt": "",
                    "material_placeholders": {}
                },
                "synthesis": "",
                "temperature": 0.7,
                "model_vision": MODEL_VISION,
                "model_synthesis": MODEL_SYNTHESIS,
                "model": MODEL_SYNTHESIS  # Legacy support
            }
        }
        
        # Create project directory
        project_dir = self.base_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (project_dir / "materials").mkdir(exist_ok=True)
        (project_dir / "outputs").mkdir(exist_ok=True)
        (project_dir / "sessions").mkdir(exist_ok=True)
        
        # Save project data
        self._save_project_data(project_id, project_data)
        
        self.logger.info(f"Created project: {name} ({project_id})")
        return project_data
    
    def load_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Load project data by ID.
        
        Args:
            project_id: Unique project identifier
            
        Returns:
            Project data dictionary or None if not found
        """
        try:
            project_file = self.base_dir / project_id / "project.json"
            if not project_file.exists():
                self.logger.info(f"Project {project_id} not found")
                return None
            
            with open(project_file, "r", encoding="utf-8") as f:
                project_data = json.load(f)
            
            # Ensure backward compatibility - add model settings if missing
            if 'model_vision' not in project_data.get('state', {}):
                project_data['state']['model_vision'] = MODEL_VISION
            if 'model_synthesis' not in project_data.get('state', {}):
                project_data['state']['model_synthesis'] = MODEL_SYNTHESIS
            
            # Load materials data if they exist
            materials_dir = self.base_dir / project_id / "materials"
            if materials_dir.exists():
                # Load any persisted material files
                for material_file in materials_dir.glob("*.json"):
                    try:
                        with open(material_file, "r", encoding="utf-8") as f:
                            material_data = json.load(f)
                            key = material_file.stem
                            
                            # Check if there's a corresponding binary data file
                            data_file = materials_dir / f"{key}.bin"
                            if data_file.exists():
                                with open(data_file, "rb") as f:
                                    material_data["data"] = f.read()
                            
                            if "uploaded_materials" not in project_data["state"]:
                                project_data["state"]["uploaded_materials"] = {}
                            
                            project_data["state"]["uploaded_materials"][key] = material_data
                    except Exception as e:
                        self.logger.error(f"Error loading material {material_file}: {e}")
            
            return project_data
            
        except Exception as e:
            self.logger.error(f"Error loading project {project_id}: {e}")
            return None
    
    def save_project_state(self, project_id: str, state: Dict[str, Any]) -> bool:
        """
        Save the current project state.
        
        Args:
            project_id: Unique project identifier
            state: Current session state to save
            
        Returns:
            Success status
        """
        try:
            import copy
            
            project_data = self.load_project(project_id)
            if not project_data:
                return False
            
            # Make a deep copy of the state to avoid modifying the original
            state_copy = copy.deepcopy(state)
            
            # Update state and timestamp
            project_data["state"] = state_copy
            project_data["updated_at"] = datetime.now().isoformat()
            
            # Save project data (binary data will be excluded by _save_project_data)
            self._save_project_data(project_id, project_data)
            
            # Save materials separately
            self._save_project_materials(project_id, state.get("uploaded_materials", {}))
            
            self.logger.info(f"Saved project state: {project_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving project state: {e}")
            return False
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all available projects.
        
        Returns:
            List of project summaries
        """
        projects = []
        
        try:
            for project_dir in self.base_dir.iterdir():
                if project_dir.is_dir():
                    project_file = project_dir / "project.json"
                    if project_file.exists():
                        with open(project_file, "r", encoding="utf-8") as f:
                            project_data = json.load(f)
                            
                            # Create summary
                            projects.append({
                                "id": project_data["id"],
                                "name": project_data["name"],
                                "description": project_data["description"],
                                "created_at": project_data["created_at"],
                                "updated_at": project_data["updated_at"],
                                "current_phase": project_data["state"]["current_phase"],
                                "materials_count": len(project_data["state"].get("uploaded_materials", {}))
                            })
            
            # Sort by updated_at, newest first
            projects.sort(key=lambda x: x["updated_at"], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error listing projects: {e}")
        
        return projects
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project and all its data.
        
        Args:
            project_id: Unique project identifier
            
        Returns:
            Success status
        """
        try:
            project_dir = self.base_dir / project_id
            if project_dir.exists():
                shutil.rmtree(project_dir)
                self.logger.info(f"Deleted project: {project_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting project {project_id}: {e}")
            return False
    
    def duplicate_project(self, project_id: str, new_name: str) -> Optional[Dict[str, Any]]:
        """
        Create a copy of an existing project.
        
        Args:
            project_id: Source project ID
            new_name: Name for the duplicated project
            
        Returns:
            New project data or None if failed
        """
        try:
            # Load source project
            source_project = self.load_project(project_id)
            if not source_project:
                return None
            
            # Create new project
            new_project = self.create_project(
                name=new_name,
                description=f"Copy of {source_project['name']}"
            )
            
            # Copy state
            new_project["state"] = source_project["state"].copy()
            
            # Save the duplicated project
            self._save_project_data(new_project["id"], new_project)
            
            # Copy materials directory
            source_materials = self.base_dir / project_id / "materials"
            dest_materials = self.base_dir / new_project["id"] / "materials"
            if source_materials.exists():
                shutil.copytree(source_materials, dest_materials, dirs_exist_ok=True)
            
            self.logger.info(f"Duplicated project {project_id} to {new_project['id']}")
            return new_project
            
        except Exception as e:
            self.logger.error(f"Error duplicating project: {e}")
            return None
    
    def export_project(self, project_id: str, export_path: Path) -> bool:
        """
        Export project as a zip file.
        
        Args:
            project_id: Project to export
            export_path: Path for the export file
            
        Returns:
            Success status
        """
        try:
            project_dir = self.base_dir / project_id
            if not project_dir.exists():
                return False
            
            # Create zip file
            shutil.make_archive(
                str(export_path.with_suffix('')),
                'zip',
                project_dir
            )
            
            self.logger.info(f"Exported project {project_id} to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting project: {e}")
            return False
    
    def _save_project_data(self, project_id: str, project_data: Dict[str, Any]):
        """Save project data to JSON file."""
        project_file = self.base_dir / project_id / "project.json"
        
        # Create a copy to avoid modifying the original
        data_to_save = project_data.copy()
        
        # If there are uploaded materials in the state, remove binary data before saving
        if "state" in data_to_save and "uploaded_materials" in data_to_save["state"]:
            materials_copy = {}
            for key, material in data_to_save["state"]["uploaded_materials"].items():
                # Copy material without the binary data
                material_copy = material.copy()
                if "data" in material_copy:
                    del material_copy["data"]
                materials_copy[key] = material_copy
            data_to_save["state"]["uploaded_materials"] = materials_copy
        
        with open(project_file, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    
    def _save_project_materials(self, project_id: str, materials: Dict[str, Any]):
        """Save project materials to separate files."""
        materials_dir = self.base_dir / project_id / "materials"
        materials_dir.mkdir(exist_ok=True)
        
        for key, material in materials.items():
            try:
                # Save material metadata (without actual file data for efficiency)
                material_meta = {
                    "type": material.get("type"),
                    "name": material.get("name"),
                    "display_name": material.get("display_name"),
                    "file_type": material.get("file_type"),
                    "size": material.get("size"),
                    "url": material.get("url")
                }
                
                # Save metadata
                material_file = materials_dir / f"{key}.json"
                with open(material_file, "w", encoding="utf-8") as f:
                    json.dump(material_meta, f, ensure_ascii=False, indent=2)
                
                # Save binary data separately if it's a file with data
                if material.get("type") == "file" and "data" in material:
                    data_file = materials_dir / f"{key}.bin"
                    with open(data_file, "wb") as f:
                        # Handle both bytes and string data
                        data = material["data"]
                        if isinstance(data, str):
                            data = data.encode('utf-8')
                        f.write(data)
                        
            except Exception as e:
                self.logger.error(f"Error saving material {key}: {e}")
                continue
    
    def get_project_phase_name(self, phase: int) -> str:
        """Get human-readable phase name."""
        phases = ["📥 Upload", "⚙️ Configure", "🔍 Extract", "✨ Synthesize"]
        return phases[phase] if 0 <= phase < len(phases) else "Unknown"

# Global instance
project_service = ProjectService() 