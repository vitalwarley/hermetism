"""
Materials Workspace Service - Central hub for materials and their extractions
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import uuid
import shutil
from services.extraction import extraction_service
from services.ai_service import ai_service

class MaterialsWorkspaceService:
    """Service for managing materials and their extractions independently of projects."""
    
    def __init__(self, workspace_dir: str = "materials_workspace"):
        self.logger = logging.getLogger(__name__)
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.materials_dir = self.workspace_dir / "materials"
        self.extractions_dir = self.workspace_dir / "extractions"
        self.materials_dir.mkdir(exist_ok=True)
        self.extractions_dir.mkdir(exist_ok=True)
        
        # Load workspace index
        self.index_file = self.workspace_dir / "workspace_index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load the workspace index that tracks all materials and extractions."""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading workspace index: {e}")
        
        # Initialize empty index
        return {
            "materials": {},
            "extractions": {},
            "updated_at": datetime.now().isoformat()
        }
    
    def _save_index(self):
        """Save the workspace index."""
        self.index["updated_at"] = datetime.now().isoformat()
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self.index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving workspace index: {e}")
    
    def add_material(self, material_data: Dict[str, Any], material_key: Optional[str] = None) -> str:
        """
        Add a material to the workspace.
        
        Args:
            material_data: Material data including type, name, content, etc.
            material_key: Optional key for the material (auto-generated if not provided)
            
        Returns:
            Material ID
        """
        # Generate material ID
        if material_key:
            material_id = material_key
        else:
            material_id = f"mat_{uuid.uuid4().hex[:8]}"
        
        # Prepare material metadata
        material_meta = {
            "id": material_id,
            "type": material_data.get("type", "unknown"),
            "name": material_data.get("name", "Unknown"),
            "display_name": material_data.get("display_name", material_data.get("name", "Unknown")),
            "file_type": material_data.get("file_type"),
            "size": material_data.get("size"),
            "url": material_data.get("url"),
            "added_at": datetime.now().isoformat(),
            "extraction_ids": [],
            "tags": material_data.get("tags", []),
            "imported_from": material_data.get("imported_from")
        }
        
        # Save material metadata
        material_file = self.materials_dir / f"{material_id}.json"
        with open(material_file, "w", encoding="utf-8") as f:
            json.dump(material_meta, f, ensure_ascii=False, indent=2)
        
        # Save binary data if present
        if "data" in material_data:
            data_file = self.materials_dir / f"{material_id}.bin"
            with open(data_file, "wb") as f:
                data = material_data["data"]
                if isinstance(data, str):
                    data = data.encode('utf-8')
                f.write(data)
        
        # Update index
        self.index["materials"][material_id] = material_meta
        self._save_index()
        
        self.logger.info(f"Added material to workspace: {material_id}")
        return material_id
    
    def add_extraction(self, material_id: str, extraction_content: str, 
                      extraction_config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an extraction for a material.
        
        Args:
            material_id: ID of the material
            extraction_content: The extracted content
            extraction_config: Configuration used for extraction
            metadata: Additional metadata for the extraction
            
        Returns:
            Extraction ID
        """
        if material_id not in self.index["materials"]:
            raise ValueError(f"Material {material_id} not found")
        
        # Generate extraction ID
        extraction_id = f"ext_{uuid.uuid4().hex[:8]}"
        
        # Prepare extraction data
        extraction_data = {
            "id": extraction_id,
            "material_id": material_id,
            "content": extraction_content,
            "config": extraction_config,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "word_count": len(extraction_content.split()),
            "char_count": len(extraction_content)
        }
        
        # Save extraction
        extraction_file = self.extractions_dir / f"{extraction_id}.json"
        with open(extraction_file, "w", encoding="utf-8") as f:
            json.dump(extraction_data, f, ensure_ascii=False, indent=2)
        
        # Update material's extraction list
        self.index["materials"][material_id]["extraction_ids"].append(extraction_id)
        
        # Update extraction index
        self.index["extractions"][extraction_id] = {
            "id": extraction_id,
            "material_id": material_id,
            "created_at": extraction_data["created_at"],
            "config_summary": self._get_config_summary(extraction_config),
            "word_count": extraction_data["word_count"]
        }
        
        self._save_index()
        self.logger.info(f"Added extraction {extraction_id} for material {material_id}")
        return extraction_id
    
    def get_material(self, material_id: str) -> Optional[Dict[str, Any]]:
        """Get material data by ID."""
        if material_id not in self.index["materials"]:
            return None
        
        # Load material metadata
        material_file = self.materials_dir / f"{material_id}.json"
        if not material_file.exists():
            return None
        
        with open(material_file, "r", encoding="utf-8") as f:
            material_data = json.load(f)
        
        # Load binary data if exists
        data_file = self.materials_dir / f"{material_id}.bin"
        if data_file.exists():
            with open(data_file, "rb") as f:
                material_data["data"] = f.read()
        
        return material_data
    
    def get_extraction(self, extraction_id: str) -> Optional[Dict[str, Any]]:
        """Get extraction data by ID."""
        if extraction_id not in self.index["extractions"]:
            return None
        
        extraction_file = self.extractions_dir / f"{extraction_id}.json"
        if not extraction_file.exists():
            return None
        
        with open(extraction_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def list_materials(self, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all materials in the workspace."""
        materials = []
        
        for material_id, material_meta in self.index["materials"].items():
            if filter_type and material_meta.get("type") != filter_type:
                continue
            
            # Add extraction count
            material_info = material_meta.copy()
            material_info["extraction_count"] = len(material_meta.get("extraction_ids", []))
            materials.append(material_info)
        
        # Sort by added date, newest first
        materials.sort(key=lambda x: x.get("added_at", ""), reverse=True)
        return materials
    
    def list_extractions(self, material_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List extractions, optionally filtered by material."""
        extractions = []
        
        for ext_id, ext_meta in self.index["extractions"].items():
            if material_id and ext_meta.get("material_id") != material_id:
                continue
            
            extraction_info = ext_meta.copy()
            
            # Add material info
            mat_id = ext_meta.get("material_id")
            if mat_id and mat_id in self.index["materials"]:
                extraction_info["material_name"] = self.index["materials"][mat_id].get("display_name", "Unknown")
            
            extractions.append(extraction_info)
        
        # Sort by creation date, newest first
        extractions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return extractions
    
    def delete_material(self, material_id: str) -> bool:
        """Delete a material and all its extractions."""
        if material_id not in self.index["materials"]:
            return False
        
        try:
            # Delete all extractions
            extraction_ids = self.index["materials"][material_id].get("extraction_ids", [])
            for ext_id in extraction_ids:
                self.delete_extraction(ext_id)
            
            # Delete material files
            material_file = self.materials_dir / f"{material_id}.json"
            data_file = self.materials_dir / f"{material_id}.bin"
            
            if material_file.exists():
                material_file.unlink()
            if data_file.exists():
                data_file.unlink()
            
            # Remove from index
            del self.index["materials"][material_id]
            self._save_index()
            
            self.logger.info(f"Deleted material {material_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting material {material_id}: {e}")
            return False
    
    def delete_extraction(self, extraction_id: str) -> bool:
        """Delete an extraction."""
        if extraction_id not in self.index["extractions"]:
            return False
        
        try:
            # Get material ID
            material_id = self.index["extractions"][extraction_id].get("material_id")
            
            # Delete extraction file
            extraction_file = self.extractions_dir / f"{extraction_id}.json"
            if extraction_file.exists():
                extraction_file.unlink()
            
            # Remove from material's extraction list
            if material_id and material_id in self.index["materials"]:
                extraction_ids = self.index["materials"][material_id].get("extraction_ids", [])
                if extraction_id in extraction_ids:
                    extraction_ids.remove(extraction_id)
            
            # Remove from index
            del self.index["extractions"][extraction_id]
            self._save_index()
            
            self.logger.info(f"Deleted extraction {extraction_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting extraction {extraction_id}: {e}")
            return False
    
    def search_materials(self, query: str) -> List[Dict[str, Any]]:
        """Search materials by name or content."""
        query_lower = query.lower()
        results = []
        
        for material in self.list_materials():
            # Check name
            if query_lower in material.get("name", "").lower():
                results.append(material)
                continue
            
            # Check display name
            if query_lower in material.get("display_name", "").lower():
                results.append(material)
                continue
            
            # Check URL
            if material.get("url") and query_lower in material["url"].lower():
                results.append(material)
                continue
            
            # Check tags
            if any(query_lower in tag.lower() for tag in material.get("tags", [])):
                results.append(material)
                continue
        
        return results
    
    def search_extractions(self, query: str) -> List[Dict[str, Any]]:
        """Search extractions by content."""
        query_lower = query.lower()
        results = []
        
        for ext_meta in self.list_extractions():
            # Load full extraction to search content
            extraction = self.get_extraction(ext_meta["id"])
            if extraction and query_lower in extraction.get("content", "").lower():
                results.append(ext_meta)
        
        return results
    
    def import_from_projects(self, projects_dir: str = "projects") -> Tuple[int, int]:
        """
        Import all materials and extractions from existing projects.
        
        Returns:
            Tuple of (materials_imported, extractions_imported)
        """
        materials_imported = 0
        extractions_imported = 0
        projects_path = Path(projects_dir)
        
        if not projects_path.exists():
            return 0, 0
        
        try:
            # Scan all project directories
            for project_dir in projects_path.iterdir():
                if not project_dir.is_dir():
                    continue
                
                # Load project data
                project_file = project_dir / "project.json"
                if not project_file.exists():
                    continue
                
                try:
                    with open(project_file, "r", encoding="utf-8") as f:
                        project_data = json.load(f)
                    
                    project_name = project_data.get("name", "Unknown Project")
                    project_id = project_data.get("id", project_dir.name)
                    
                    # Import materials
                    materials_dir = project_dir / "materials"
                    if materials_dir.exists():
                        for material_file in materials_dir.glob("*.json"):
                            try:
                                # Load material
                                with open(material_file, "r", encoding="utf-8") as f:
                                    material_data = json.load(f)
                                
                                material_key = material_file.stem
                                
                                # Check if binary data exists
                                data_file = materials_dir / f"{material_key}.bin"
                                if data_file.exists():
                                    with open(data_file, "rb") as f:
                                        material_data["data"] = f.read()
                                
                                # Add import metadata
                                material_data["imported_from"] = f"{project_name} ({project_id})"
                                material_data["tags"] = [f"project:{project_name}"]
                                
                                # Add material to workspace
                                material_id = self.add_material(material_data)
                                materials_imported += 1
                                
                                # Check for extracted content
                                if "state" in project_data and "extracted_content" in project_data["state"]:
                                    if material_key in project_data["state"]["extracted_content"]:
                                        extraction_content = project_data["state"]["extracted_content"][material_key]
                                        
                                        # Get extraction config if available
                                        extraction_config = {}
                                        if "extraction_configs" in project_data["state"]:
                                            extraction_config = project_data["state"]["extraction_configs"].get(material_key, {})
                                        
                                        # Add extraction
                                        self.add_extraction(
                                            material_id,
                                            extraction_content,
                                            extraction_config,
                                            metadata={
                                                "imported_from": f"{project_name} ({project_id})",
                                                "original_key": material_key
                                            }
                                        )
                                        extractions_imported += 1
                                
                            except Exception as e:
                                self.logger.error(f"Error importing material {material_file}: {e}")
                                continue
                
                except Exception as e:
                    self.logger.error(f"Error loading project {project_dir}: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error during project import: {e}")
        
        self.logger.info(f"Imported {materials_imported} materials and {extractions_imported} extractions")
        return materials_imported, extractions_imported
    
    def _get_config_summary(self, config: Dict[str, Any]) -> str:
        """Generate a summary of extraction configuration."""
        parts = []
        
        if config.get("method"):
            parts.append(f"Method: {config['method']}")
        
        if config.get("prompt"):
            prompt_preview = config['prompt'][:50] + "..." if len(config['prompt']) > 50 else config['prompt']
            parts.append(f"Prompt: {prompt_preview}")
        
        if config.get("page_range"):
            parts.append(f"Pages: {config['page_range']}")
        
        return " | ".join(parts) if parts else "Default extraction"
    
    def update_material_tags(self, material_id: str, tags: List[str]) -> bool:
        """Update tags for a material."""
        if material_id not in self.index["materials"]:
            return False
        
        try:
            # Update in index
            self.index["materials"][material_id]["tags"] = tags
            
            # Update in file
            material_file = self.materials_dir / f"{material_id}.json"
            if material_file.exists():
                with open(material_file, "r", encoding="utf-8") as f:
                    material_data = json.load(f)
                
                material_data["tags"] = tags
                
                with open(material_file, "w", encoding="utf-8") as f:
                    json.dump(material_data, f, ensure_ascii=False, indent=2)
            
            self._save_index()
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating material tags: {e}")
            return False

# Global instance
materials_workspace_service = MaterialsWorkspaceService() 