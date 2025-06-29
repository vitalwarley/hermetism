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
                    custom_prompt: str, metadata: Optional[Dict[str, Any]] = None) -> Path:
        """Save session data for future reference."""
        timestamp = datetime.now().isoformat()
        session_id = timestamp.replace(":", "-").replace(".", "-")
        
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save session data
        session_data = {
            "timestamp": timestamp,
            "custom_prompt": custom_prompt,
            "materials": materials,
            "synthesis": synthesis,
            "output": synthesis,  # Add output field for consistency
            "metadata": metadata or {}
        }
        
        try:
            with open(session_dir / "session.json", "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            # Generate markdown file
            self._generate_session_markdown(session_dir, session_data)
            
            self.logger.info(f"Session saved to {session_dir}")
            return session_dir
        except Exception as e:
            self.logger.error(f"Error saving session: {str(e)}")
            raise e
    
    def _generate_session_markdown(self, session_dir: Path, session_data: Dict[str, Any]):
        """Generate a markdown file from session data."""
        try:
            # Parse timestamp for readable format
            timestamp = datetime.fromisoformat(session_data["timestamp"])
            formatted_datetime = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            # Generate title from materials or timestamp
            materials_names = list(session_data.get("materials", {}).keys())
            if materials_names:
                title = f"Session: {', '.join(materials_names[:2])}"
                if len(materials_names) > 2:
                    title += f" and {len(materials_names) - 2} more"
            else:
                title = f"Session {timestamp.strftime('%Y-%m-%d %H:%M')}"
            
            # Build markdown content
            markdown_content = f"""# {title}

**Date & Time:** {formatted_datetime}

## Custom Prompt

{session_data.get('custom_prompt', 'No custom prompt provided')}

## Materials

"""
            
            # Add materials section
            materials = session_data.get("materials", {})
            if materials:
                for material_name, content in materials.items():
                    markdown_content += f"### {material_name}\n\n"
                    # Include full content without truncation
                    markdown_content += f"{content}\n\n"
            else:
                markdown_content += "No materials provided.\n\n"
            
            # Add output section
            markdown_content += f"""## Output

{session_data.get('output', session_data.get('synthesis', 'No output generated'))}

"""
            
            # Add quality review section if available
            metadata = session_data.get("metadata", {})
            if "quality_ratings" in metadata:
                markdown_content += """## Quality Review

"""
                ratings = metadata["quality_ratings"]
                review_timestamp = metadata.get("review_timestamp", "")
                
                if review_timestamp:
                    review_datetime = datetime.fromisoformat(review_timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    markdown_content += f"**Reviewed on:** {review_datetime}\n\n"
                
                markdown_content += "**Ratings:**\n\n"
                for metric, rating in ratings.items():
                    stars = "★" * rating + "☆" * (5 - rating)
                    markdown_content += f"- **{metric}:** {stars} ({rating}/5)\n"
                
                review_notes = metadata.get("review_notes", "")
                if review_notes.strip():
                    markdown_content += f"\n**Notes:**\n\n{review_notes}\n"
                
                markdown_content += "\n"
            
            markdown_content += f"""---

*Generated on {formatted_datetime}*
"""
            
            # Write markdown file
            with open(session_dir / "session.md", "w", encoding="utf-8") as f:
                f.write(markdown_content)
                
            self.logger.info(f"Markdown file generated at {session_dir / 'session.md'}")
            
        except Exception as e:
            self.logger.error(f"Error generating markdown file: {str(e)}")
            # Don't raise exception - markdown generation failure shouldn't break session saving
    
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
                            
                            # Handle both old (custom_prompt_preview) and new (custom_prompt) format
                            prompt_preview = session_data.get("custom_prompt_preview", 
                                           session_data.get("custom_prompt", ""))
                            if len(prompt_preview) > 100:
                                prompt_preview = prompt_preview[:100] + "..."
                            
                            sessions.append({
                                "id": session_dir.name,
                                "timestamp": session_data.get("timestamp"),
                                "custom_prompt_preview": prompt_preview,
                                "materials_count": len(session_data.get("materials", {}))
                            })
            
            # Sort by timestamp, newest first
            sessions.sort(key=lambda x: x["timestamp"], reverse=True)
            return sessions
        except Exception as e:
            self.logger.error(f"Error listing sessions: {str(e)}")
            return []

    def update_session_metadata(self, session_id: str, metadata_updates: Dict[str, Any]) -> bool:
        """Update session metadata and regenerate markdown."""
        try:
            session_file = self.sessions_dir / session_id / "session.json"
            if not session_file.exists():
                self.logger.error(f"Session {session_id} not found")
                return False
            
            # Load existing session data
            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            
            # Update metadata
            if "metadata" not in session_data:
                session_data["metadata"] = {}
            
            session_data["metadata"].update(metadata_updates)
            
            # Save updated session data
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            # Regenerate markdown with updated data
            session_dir = self.sessions_dir / session_id
            self._generate_session_markdown(session_dir, session_data)
            
            self.logger.info(f"Session {session_id} metadata updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating session metadata: {str(e)}")
            return False

    def save_quality_review(self, session_id: str, ratings: Dict[str, int], 
                           review_notes: str = "") -> bool:
        """Save quality review ratings to session."""
        try:
            timestamp = datetime.now().isoformat()
            quality_review = {
                "quality_ratings": ratings,
                "review_notes": review_notes,
                "review_timestamp": timestamp
            }
            
            return self.update_session_metadata(session_id, quality_review)
            
        except Exception as e:
            self.logger.error(f"Error saving quality review: {str(e)}")
            return False

# Global instance
session_service = SessionService() 