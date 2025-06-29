"""
Prompt Management service for creating and managing extraction, cleaning, and synthesis prompts
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List
import uuid

class PromptWorkspaceService:
    """Service for managing prompt workspaces with versioning and organization."""
    
    def __init__(self, base_dir: str = "prompt_workspaces"):
        self.logger = logging.getLogger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Create default workspace if none exists
        self._ensure_default_workspace()
    
    def create_workspace(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new prompt workspace.
        
        Args:
            name: Workspace name
            description: Optional workspace description
            
        Returns:
            Workspace data dictionary
        """
        workspace_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        workspace_data = {
            "id": workspace_id,
            "name": name,
            "description": description,
            "created_at": timestamp,
            "updated_at": timestamp,
            "prompts": {
                "extraction": {},
                "cleaning": {},
                "synthesis": {}
            },
            "categories": {
                "extraction": ["General", "Esoteric/Hermetic", "Academic", "Images", "Web Content", "Video/Audio"],
                "cleaning": ["General", "Formatting", "Esoteric", "Academic"],
                "synthesis": ["General", "Hermetic", "Tarot", "Astrological", "Alchemical", "Comparative"]
            },
            "active": False
        }
        
        # Create workspace directory
        workspace_dir = self.base_dir / workspace_id
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (workspace_dir / "versions").mkdir(exist_ok=True)
        (workspace_dir / "exports").mkdir(exist_ok=True)
        
        # Save workspace data
        self._save_workspace_data(workspace_id, workspace_data)
        
        self.logger.info(f"Created prompt workspace: {name} ({workspace_id})")
        return workspace_data
    
    def load_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """
        Load workspace data by ID.
        
        Args:
            workspace_id: Unique workspace identifier
            
        Returns:
            Workspace data dictionary or None if not found
        """
        try:
            workspace_file = self.base_dir / workspace_id / "workspace.json"
            if not workspace_file.exists():
                self.logger.info(f"Workspace {workspace_id} not found")
                return None
            
            with open(workspace_file, "r", encoding="utf-8") as f:
                workspace_data = json.load(f)
            
            return workspace_data
            
        except Exception as e:
            self.logger.error(f"Error loading workspace {workspace_id}: {e}")
            return None
    
    def save_workspace_data(self, workspace_id: str, workspace_data: Dict[str, Any]) -> bool:
        """
        Save the workspace data.
        
        Args:
            workspace_id: Unique workspace identifier
            workspace_data: Workspace data to save
            
        Returns:
            Success status
        """
        try:
            workspace_data["updated_at"] = datetime.now().isoformat()
            self._save_workspace_data(workspace_id, workspace_data)
            
            # Create version backup
            self._create_version_backup(workspace_id, workspace_data)
            
            self.logger.info(f"Saved workspace data: {workspace_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving workspace data: {e}")
            return False
    
    def add_prompt(self, workspace_id: str, prompt_type: str, category: str, 
                   name: str, content: str, metadata: Dict[str, Any] = None) -> Optional[str]:
        """
        Add a new prompt to the workspace.
        
        Args:
            workspace_id: Workspace ID
            prompt_type: Type of prompt (extraction, cleaning, synthesis)
            category: Prompt category
            name: Prompt name
            content: Prompt content
            metadata: Optional metadata
            
        Returns:
            Prompt ID or None if failed
        """
        try:
            workspace = self.load_workspace(workspace_id)
            if not workspace:
                return None
            
            prompt_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            prompt_data = {
                "id": prompt_id,
                "name": name,
                "content": content,
                "category": category,
                "created_at": timestamp,
                "updated_at": timestamp,
                "version": 1,
                "metadata": metadata or {},
                "active": True
            }
            
            # Add prompt to workspace
            if prompt_type not in workspace["prompts"]:
                workspace["prompts"][prompt_type] = {}
            
            workspace["prompts"][prompt_type][prompt_id] = prompt_data
            
            # Save workspace
            self.save_workspace_data(workspace_id, workspace)
            
            return prompt_id
            
        except Exception as e:
            self.logger.error(f"Error adding prompt: {e}")
            return None
    
    def update_prompt(self, workspace_id: str, prompt_type: str, prompt_id: str,
                      updates: Dict[str, Any]) -> bool:
        """
        Update an existing prompt.
        
        Args:
            workspace_id: Workspace ID
            prompt_type: Type of prompt
            prompt_id: Prompt ID
            updates: Dictionary of updates
            
        Returns:
            Success status
        """
        try:
            workspace = self.load_workspace(workspace_id)
            if not workspace:
                return False
            
            if prompt_type in workspace["prompts"] and prompt_id in workspace["prompts"][prompt_type]:
                prompt = workspace["prompts"][prompt_type][prompt_id]
                
                # Update fields
                for key, value in updates.items():
                    if key not in ["id", "created_at"]:  # Don't update these
                        prompt[key] = value
                
                prompt["updated_at"] = datetime.now().isoformat()
                prompt["version"] = prompt.get("version", 1) + 1
                
                # Save workspace
                self.save_workspace_data(workspace_id, workspace)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating prompt: {e}")
            return False
    
    def delete_prompt(self, workspace_id: str, prompt_type: str, prompt_id: str) -> bool:
        """
        Delete a prompt (soft delete by marking inactive).
        
        Args:
            workspace_id: Workspace ID
            prompt_type: Type of prompt
            prompt_id: Prompt ID
            
        Returns:
            Success status
        """
        try:
            workspace = self.load_workspace(workspace_id)
            if not workspace:
                return False
            
            if prompt_type in workspace["prompts"] and prompt_id in workspace["prompts"][prompt_type]:
                workspace["prompts"][prompt_type][prompt_id]["active"] = False
                workspace["prompts"][prompt_type][prompt_id]["deleted_at"] = datetime.now().isoformat()
                
                # Save workspace
                self.save_workspace_data(workspace_id, workspace)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting prompt: {e}")
            return False
    
    def list_workspaces(self) -> List[Dict[str, Any]]:
        """
        List all available workspaces.
        
        Returns:
            List of workspace summaries
        """
        workspaces = []
        
        try:
            for workspace_dir in self.base_dir.iterdir():
                if workspace_dir.is_dir():
                    workspace_file = workspace_dir / "workspace.json"
                    if workspace_file.exists():
                        with open(workspace_file, "r", encoding="utf-8") as f:
                            workspace_data = json.load(f)
                            
                            # Count active prompts
                            prompt_counts = {}
                            for prompt_type, prompts in workspace_data["prompts"].items():
                                active_count = sum(1 for p in prompts.values() if p.get("active", True))
                                prompt_counts[prompt_type] = active_count
                            
                            # Create summary
                            workspaces.append({
                                "id": workspace_data["id"],
                                "name": workspace_data["name"],
                                "description": workspace_data["description"],
                                "created_at": workspace_data["created_at"],
                                "updated_at": workspace_data["updated_at"],
                                "active": workspace_data.get("active", False),
                                "prompt_counts": prompt_counts
                            })
            
            # Sort by updated_at, newest first
            workspaces.sort(key=lambda x: x["updated_at"], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error listing workspaces: {e}")
        
        return workspaces
    
    def set_active_workspace(self, workspace_id: str) -> bool:
        """
        Set a workspace as the active one (deactivating others).
        
        Args:
            workspace_id: Workspace to activate
            
        Returns:
            Success status
        """
        try:
            # Deactivate all workspaces
            for ws in self.list_workspaces():
                ws_data = self.load_workspace(ws["id"])
                if ws_data:
                    ws_data["active"] = False
                    self._save_workspace_data(ws["id"], ws_data)
            
            # Activate the selected workspace
            workspace = self.load_workspace(workspace_id)
            if workspace:
                workspace["active"] = True
                self.save_workspace_data(workspace_id, workspace)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error setting active workspace: {e}")
            return False
    
    def get_active_workspace(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently active workspace.
        
        Returns:
            Active workspace data or None
        """
        for ws in self.list_workspaces():
            if ws.get("active", False):
                return self.load_workspace(ws["id"])
        
        # If no active workspace, return the default one
        default_ws = self._get_default_workspace()
        if default_ws:
            return self.load_workspace(default_ws["id"])
        
        return None
    
    def duplicate_workspace(self, workspace_id: str, new_name: str) -> Optional[Dict[str, Any]]:
        """
        Create a copy of an existing workspace.
        
        Args:
            workspace_id: Source workspace ID
            new_name: Name for the duplicated workspace
            
        Returns:
            New workspace data or None if failed
        """
        try:
            # Load source workspace
            source_workspace = self.load_workspace(workspace_id)
            if not source_workspace:
                return None
            
            # Create new workspace
            new_workspace = self.create_workspace(
                name=new_name,
                description=f"Copy of {source_workspace['name']}"
            )
            
            # Copy prompts and categories
            new_workspace["prompts"] = source_workspace["prompts"].copy()
            new_workspace["categories"] = source_workspace["categories"].copy()
            
            # Update all prompt IDs and timestamps
            for prompt_type in new_workspace["prompts"]:
                new_prompts = {}
                for old_id, prompt in new_workspace["prompts"][prompt_type].items():
                    new_id = str(uuid.uuid4())
                    prompt["id"] = new_id
                    prompt["created_at"] = datetime.now().isoformat()
                    prompt["updated_at"] = datetime.now().isoformat()
                    prompt["version"] = 1
                    new_prompts[new_id] = prompt
                new_workspace["prompts"][prompt_type] = new_prompts
            
            # Save the duplicated workspace
            self.save_workspace_data(new_workspace["id"], new_workspace)
            
            self.logger.info(f"Duplicated workspace {workspace_id} to {new_workspace['id']}")
            return new_workspace
            
        except Exception as e:
            self.logger.error(f"Error duplicating workspace: {e}")
            return None
    
    def export_workspace(self, workspace_id: str, export_path: Path) -> bool:
        """
        Export workspace as a JSON file.
        
        Args:
            workspace_id: Workspace to export
            export_path: Path for the export file
            
        Returns:
            Success status
        """
        try:
            workspace = self.load_workspace(workspace_id)
            if not workspace:
                return False
            
            # Save as JSON
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(workspace, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Exported workspace {workspace_id} to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting workspace: {e}")
            return False
    
    def import_workspace(self, import_path: Path, new_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Import a workspace from a JSON file.
        
        Args:
            import_path: Path to the import file
            new_name: Optional new name for the imported workspace
            
        Returns:
            Imported workspace data or None if failed
        """
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                workspace_data = json.load(f)
            
            # Create new workspace with imported data
            new_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            workspace_data["id"] = new_id
            workspace_data["name"] = new_name or f"Imported: {workspace_data['name']}"
            workspace_data["created_at"] = timestamp
            workspace_data["updated_at"] = timestamp
            workspace_data["active"] = False
            
            # Create workspace directory
            workspace_dir = self.base_dir / new_id
            workspace_dir.mkdir(parents=True, exist_ok=True)
            (workspace_dir / "versions").mkdir(exist_ok=True)
            (workspace_dir / "exports").mkdir(exist_ok=True)
            
            # Save workspace
            self._save_workspace_data(new_id, workspace_data)
            
            self.logger.info(f"Imported workspace: {workspace_data['name']} ({new_id})")
            return workspace_data
            
        except Exception as e:
            self.logger.error(f"Error importing workspace: {e}")
            return None
    
    def _save_workspace_data(self, workspace_id: str, workspace_data: Dict[str, Any]):
        """Save workspace data to JSON file."""
        workspace_file = self.base_dir / workspace_id / "workspace.json"
        
        with open(workspace_file, "w", encoding="utf-8") as f:
            json.dump(workspace_data, f, ensure_ascii=False, indent=2)
    
    def _create_version_backup(self, workspace_id: str, workspace_data: Dict[str, Any]):
        """Create a version backup of the workspace."""
        try:
            version_dir = self.base_dir / workspace_id / "versions"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            version_file = version_dir / f"workspace_{timestamp}.json"
            
            with open(version_file, "w", encoding="utf-8") as f:
                json.dump(workspace_data, f, ensure_ascii=False, indent=2)
            
            # Keep only last 10 versions
            versions = sorted(version_dir.glob("workspace_*.json"))
            if len(versions) > 10:
                for old_version in versions[:-10]:
                    old_version.unlink()
                    
        except Exception as e:
            self.logger.error(f"Error creating version backup: {e}")
    
    def _ensure_default_workspace(self):
        """Ensure a default workspace exists with initial prompts."""
        workspaces = self.list_workspaces()
        if not workspaces:
            # Create default workspace
            default_ws = self.create_workspace(
                name="Default Prompts",
                description="Default prompt workspace with standard prompts"
            )
            
            # Import default prompts from extraction_prompts.py
            from config.extraction_prompts import EXTRACTION_PROMPTS
            
            # Add extraction prompts
            for category, prompts in EXTRACTION_PROMPTS.items():
                for name, content in prompts.items():
                    self.add_prompt(
                        default_ws["id"],
                        "extraction",
                        category,
                        name,
                        content
                    )
            
            # Add default cleaning prompts
            cleaning_prompts = {
                "General": {
                    "Basic Cleaning": "Clean and format the extracted text, removing any artifacts or formatting issues.",
                    "Remove Metadata": "Remove all metadata, headers, footers, and non-content elements from the text.",
                },
                "Formatting": {
                    "Preserve Structure": "Clean the text while preserving its original structure, headings, and formatting.",
                    "Plain Text": "Convert to plain text, removing all formatting while maintaining readability.",
                },
                "Esoteric": {
                    "Preserve Symbols": "Clean the text while carefully preserving all esoteric symbols, sigils, and special characters.",
                    "Standardize Terms": "Clean and standardize esoteric terminology while preserving original meanings.",
                }
            }
            
            for category, prompts in cleaning_prompts.items():
                for name, content in prompts.items():
                    self.add_prompt(
                        default_ws["id"],
                        "cleaning",
                        category,
                        name,
                        content
                    )
            
            # Add default synthesis prompts
            synthesis_prompts = {
                "Hermetic": {
                    "Hermetic Synthesis": "Create a hermetic synthesis that weaves together the esoteric principles and wisdom found in the materials. Focus on:\n1. Hidden connections between materials\n2. Deeper symbolic meanings\n3. Practical applications of the wisdom\n4. Universal principles that emerge",
                },
                "Tarot": {
                    "Tarot Reading": "Provide a comprehensive tarot reading based on the materials:\n1. Card meanings and positions\n2. Relationships between cards\n3. Overall narrative and message\n4. Guidance for the querent",
                },
                "Astrological": {
                    "Astrological Analysis": "Analyze the astrological content:\n1. Planetary influences and aspects\n2. House placements and their meanings\n3. Timing and cycles\n4. Practical life applications",
                },
                "Alchemical": {
                    "Alchemical Interpretation": "Interpret through an alchemical lens:\n1. Stages of transformation present\n2. Symbolic elements and their meanings\n3. The Great Work as reflected in the materials\n4. Personal transformation insights",
                },
                "Comparative": {
                    "Comparative Analysis": "Compare and contrast the materials:\n{material1} - Primary source\n{material2} - Secondary source\n\nAnalyze:\n1. Common themes\n2. Contrasting viewpoints\n3. Synthesis of ideas\n4. Unified insights"
                }
            }
            
            for category, prompts in synthesis_prompts.items():
                for name, content in prompts.items():
                    self.add_prompt(
                        default_ws["id"],
                        "synthesis",
                        category,
                        name,
                        content
                    )
            
            # Set as active
            self.set_active_workspace(default_ws["id"])
    
    def _get_default_workspace(self) -> Optional[Dict[str, Any]]:
        """Get the default workspace."""
        for ws in self.list_workspaces():
            if ws["name"] == "Default Prompts":
                return ws
        return None

# Global instance
prompt_workspace_service = PromptWorkspaceService() 