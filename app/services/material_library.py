"""
Material Library Service for cross-project material management
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil

class MaterialLibraryService:
    """Service for managing materials across all projects."""
    
    def __init__(self, projects_dir: str = "projects"):
        self.logger = logging.getLogger(__name__)
        self.projects_dir = Path(projects_dir)
    
    def get_all_project_materials(self) -> List[Dict[str, Any]]:
        """
        Scan all projects and return available materials with their metadata.
        
        Returns:
            List of material entries with project information
        """
        all_materials = []
        
        try:
            # Scan all project directories
            for project_dir in self.projects_dir.iterdir():
                if not project_dir.is_dir():
                    continue
                
                # Load project metadata
                project_file = project_dir / "project.json"
                if not project_file.exists():
                    continue
                
                try:
                    with open(project_file, "r", encoding="utf-8") as f:
                        project_data = json.load(f)
                    
                    project_name = project_data.get("name", "Unknown Project")
                    project_id = project_data.get("id", project_dir.name)
                    
                    # Check materials directory
                    materials_dir = project_dir / "materials"
                    if not materials_dir.exists():
                        continue
                    
                    # Load each material
                    for material_file in materials_dir.glob("*.json"):
                        try:
                            with open(material_file, "r", encoding="utf-8") as f:
                                material_data = json.load(f)
                            
                            material_key = material_file.stem
                            
                            # Check if binary data exists
                            has_binary = (materials_dir / f"{material_key}.bin").exists()
                            
                            # Check if extracted content exists
                            extracted_content = None
                            has_extraction = False
                            
                            # Check in project state for extracted content
                            if "extracted_content" in project_data.get("state", {}):
                                if material_key in project_data["state"]["extracted_content"]:
                                    extracted_content = project_data["state"]["extracted_content"][material_key]
                                    has_extraction = True
                            
                            # Create material entry
                            material_entry = {
                                "key": material_key,
                                "project_id": project_id,
                                "project_name": project_name,
                                "type": material_data.get("type", "unknown"),
                                "name": material_data.get("name", "Unknown"),
                                "display_name": material_data.get("display_name", material_data.get("name", "Unknown")),
                                "file_type": material_data.get("file_type"),
                                "size": material_data.get("size"),
                                "url": material_data.get("url"),
                                "has_binary": has_binary,
                                "has_extraction": has_extraction,
                                "extracted_content": extracted_content,
                                "material_path": str(material_file),
                                "binary_path": str(materials_dir / f"{material_key}.bin") if has_binary else None,
                                "added_date": project_data.get("created_at", "Unknown")
                            }
                            
                            all_materials.append(material_entry)
                            
                        except Exception as e:
                            self.logger.error(f"Error loading material {material_file}: {e}")
                            continue
                
                except Exception as e:
                    self.logger.error(f"Error loading project {project_dir}: {e}")
                    continue
            
            # Sort by project name and then material name
            all_materials.sort(key=lambda x: (x["project_name"], x["display_name"]))
            
        except Exception as e:
            self.logger.error(f"Error scanning project materials: {e}")
        
        return all_materials
    
    def import_material_from_project(self, material_entry: Dict[str, Any], 
                                   include_extraction: bool = True) -> Optional[Dict[str, Any]]:
        """
        Import a material from another project.
        
        Args:
            material_entry: Material entry from get_all_project_materials
            include_extraction: Whether to include extracted content
            
        Returns:
            Material data ready for session state
        """
        try:
            # Load material metadata
            with open(material_entry["material_path"], "r", encoding="utf-8") as f:
                material_data = json.load(f)
            
            # Create material dict for session state
            material = {
                "type": material_data.get("type"),
                "name": material_data.get("name"),
                "display_name": material_data.get("display_name", material_data.get("name")),
                "file_type": material_data.get("file_type"),
                "size": material_data.get("size"),
                "url": material_data.get("url"),
                "imported_from": material_entry["project_name"]
            }
            
            # Load binary data if exists
            if material_entry.get("binary_path") and os.path.exists(material_entry["binary_path"]):
                with open(material_entry["binary_path"], "rb") as f:
                    material["data"] = f.read()
            
            # Include extraction if requested and available
            extracted_content = None
            if include_extraction and material_entry.get("has_extraction"):
                extracted_content = material_entry.get("extracted_content")
            
            return {
                "material": material,
                "extracted_content": extracted_content
            }
            
        except Exception as e:
            self.logger.error(f"Error importing material: {e}")
            return None
    
    def get_materials_by_type(self, material_type: str) -> List[Dict[str, Any]]:
        """
        Get all materials of a specific type across all projects.
        
        Args:
            material_type: Type of material (file, url, youtube)
            
        Returns:
            Filtered list of materials
        """
        all_materials = self.get_all_project_materials()
        return [m for m in all_materials if m["type"] == material_type]
    
    def search_materials(self, query: str) -> List[Dict[str, Any]]:
        """
        Search materials by name or content across all projects.
        
        Args:
            query: Search query
            
        Returns:
            List of matching materials
        """
        query_lower = query.lower()
        all_materials = self.get_all_project_materials()
        
        results = []
        for material in all_materials:
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
            
            # Check extracted content
            if material.get("extracted_content") and query_lower in material["extracted_content"].lower():
                results.append(material)
        
        return results

# Global instance
material_library_service = MaterialLibraryService() 