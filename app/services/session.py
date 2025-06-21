import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
from config.settings import SESSIONS_DIR

class SessionService:
    """Service for managing session data persistence."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sessions_dir = Path(SESSIONS_DIR)
        self.sessions_dir.mkdir(exist_ok=True)
    
    def save_session(self, materials: Dict[str, str], synthesis: str, 
                    artifact_type: str, metadata: Optional[Dict[str, Any]] = None) -> Path:
        """Save session data for future reference."""
        timestamp = datetime.now().isoformat()
        session_id = timestamp.replace(":", "-").replace(".", "-")
        
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save session data
        session_data = {
            "timestamp": timestamp,
            "artifact_type": artifact_type,
            "materials": materials,
            "synthesis": synthesis,
            "metadata": metadata or {}
        }
        
        try:
            with open(session_dir / "session.json", "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Session saved to {session_dir}")
            return session_dir
        except Exception as e:
            self.logger.error(f"Error saving session: {str(e)}")
            raise e
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data by ID."""
        try:
            session_file = self.sessions_dir / session_id / "session.json"
            if session_file.exists():
                with open(session_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.error(f"Error loading session {session_id}: {str(e)}")
            return None
    
    def list_sessions(self) -> list:
        """List all available sessions."""
        try:
            sessions = []
            for session_dir in self.sessions_dir.iterdir():
                if session_dir.is_dir():
                    session_file = session_dir / "session.json"
                    if session_file.exists():
                        with open(session_file, "r", encoding="utf-8") as f:
                            session_data = json.load(f)
                            sessions.append({
                                "id": session_dir.name,
                                "timestamp": session_data.get("timestamp"),
                                "artifact_type": session_data.get("artifact_type"),
                                "materials_count": len(session_data.get("materials", {}))
                            })
            
            # Sort by timestamp, newest first
            sessions.sort(key=lambda x: x["timestamp"], reverse=True)
            return sessions
        except Exception as e:
            self.logger.error(f"Error listing sessions: {str(e)}")
            return []

# Global instance
session_service = SessionService() 