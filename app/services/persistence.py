"""
Material persistence service for saving and loading materials with metadata
"""

import os
import json
import pickle
import base64
from datetime import datetime
from typing import Dict, Any, Optional, List
import streamlit as st

class MaterialPersistenceService:
    def __init__(self, base_dir: str = "saved_materials"):
        """Initialize the persistence service."""
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def save_material(self, key: str, material: dict, config: Optional[dict] = None, 
                     extracted_content: Optional[str] = None) -> bool:
        """
        Save a material with its configuration and extracted content.
        
        Args:
            key: Unique identifier for the material
            material: Material data dictionary
            config: Extraction configuration (optional)
            extracted_content: Extracted text content (optional)
        
        Returns:
            bool: Success status
        """
        try:
            # Create material directory
            material_dir = os.path.join(self.base_dir, key)
            os.makedirs(material_dir, exist_ok=True)
            
            # Prepare metadata
            metadata = {
                'key': key,
                'type': material['type'],
                'name': material['name'],
                'display_name': material.get('display_name', material['name']),
                'file_type': material.get('file_type'),
                'size': material.get('size'),
                'url': material.get('url'),
                'saved_at': datetime.now().isoformat(),
                'has_config': config is not None,
                'has_extracted_content': extracted_content is not None
            }
            
            # Save metadata
            with open(os.path.join(material_dir, 'metadata.json'), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Save material data (for files)
            if material['type'] == 'file' and 'data' in material:
                with open(os.path.join(material_dir, 'data.bin'), 'wb') as f:
                    f.write(material['data'])
            
            # Save configuration
            if config:
                with open(os.path.join(material_dir, 'config.json'), 'w') as f:
                    json.dump(config, f, indent=2)
            
            # Save extracted content
            if extracted_content:
                with open(os.path.join(material_dir, 'extracted_content.txt'), 'w', encoding='utf-8') as f:
                    f.write(extracted_content)
            
            return True
            
        except Exception as e:
            st.error(f"Error saving material {key}: {str(e)}")
            return False
    
    def load_material(self, key: str, load_content: bool = True) -> Optional[Dict[str, Any]]:
        """
        Load a material with its configuration and extracted content.
        
        Args:
            key: Unique identifier for the material
            load_content: Whether to load extracted content
        
        Returns:
            Dict containing material, config, and extracted_content
        """
        try:
            material_dir = os.path.join(self.base_dir, key)
            
            if not os.path.exists(material_dir):
                return None
            
            # Load metadata
            with open(os.path.join(material_dir, 'metadata.json'), 'r') as f:
                metadata = json.load(f)
            
            # Reconstruct material
            material = {
                'type': metadata['type'],
                'name': metadata['name'],
                'display_name': metadata.get('display_name', metadata['name']),
                'file_type': metadata.get('file_type'),
                'size': metadata.get('size'),
                'url': metadata.get('url')
            }
            
            # Load file data if exists
            data_path = os.path.join(material_dir, 'data.bin')
            if os.path.exists(data_path):
                with open(data_path, 'rb') as f:
                    material['data'] = f.read()
            
            # Load configuration
            config = None
            config_path = os.path.join(material_dir, 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
            
            # Load extracted content
            extracted_content = None
            if load_content:
                content_path = os.path.join(material_dir, 'extracted_content.txt')
                if os.path.exists(content_path):
                    with open(content_path, 'r', encoding='utf-8') as f:
                        extracted_content = f.read()
            
            return {
                'material': material,
                'config': config,
                'extracted_content': extracted_content,
                'metadata': metadata
            }
            
        except Exception as e:
            st.error(f"Error loading material {key}: {str(e)}")
            return None
    
    def list_saved_materials(self) -> List[Dict[str, Any]]:
        """
        List all saved materials with their metadata.
        
        Returns:
            List of metadata dictionaries
        """
        materials = []
        
        if not os.path.exists(self.base_dir):
            return materials
        
        for key in os.listdir(self.base_dir):
            material_dir = os.path.join(self.base_dir, key)
            if os.path.isdir(material_dir):
                metadata_path = os.path.join(material_dir, 'metadata.json')
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                            metadata['key'] = key
                            materials.append(metadata)
                    except Exception:
                        continue
        
        # Sort by saved date (newest first)
        materials.sort(key=lambda x: x.get('saved_at', ''), reverse=True)
        
        return materials
    
    def delete_material(self, key: str) -> bool:
        """
        Delete a saved material.
        
        Args:
            key: Unique identifier for the material
        
        Returns:
            bool: Success status
        """
        try:
            material_dir = os.path.join(self.base_dir, key)
            if os.path.exists(material_dir):
                import shutil
                shutil.rmtree(material_dir)
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting material {key}: {str(e)}")
            return False
    
    def save_all_materials(self) -> int:
        """
        Save all materials from current session state.
        
        Returns:
            int: Number of materials saved
        """
        saved_count = 0
        
        for key, material in st.session_state.uploaded_materials.items():
            config = st.session_state.extraction_configs.get(key)
            extracted_content = st.session_state.extracted_content.get(key)
            
            if self.save_material(key, material, config, extracted_content):
                saved_count += 1
        
        return saved_count

# Create a global instance
persistence_service = MaterialPersistenceService() 