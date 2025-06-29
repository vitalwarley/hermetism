"""
Services module initialization
"""

from .ai_service import ai_service
from .extraction import extraction_service
from .session import session_service
from .persistence import MaterialPersistenceService
persistence_service = MaterialPersistenceService()
from .project import project_service
from .material_library import material_library_service
from .prompt_management import prompt_workspace_service

__all__ = ['ai_service', 'extraction_service', 'session_service', 'persistence_service', 'project_service', 'material_library_service', 'prompt_workspace_service'] 