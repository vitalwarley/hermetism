from openai import OpenAI
import logging
from typing import Optional
from config.settings import (
    OPENROUTER_API_KEY, 
    OPENROUTER_BASE_URL, 
    MODEL_VISION, 
    MODEL_SYNTHESIS,
    SYNTHESIS_PROMPTS,
    MAX_TEXT_LENGTH,
    MAX_SYNTHESIS_LENGTH
)

class AIService:
    """Service for handling AI interactions."""
    
    def __init__(self):
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY
        )
        self.logger = logging.getLogger(__name__)
    
    def extract_from_image(self, base64_image: str, prompt: str) -> Optional[str]:
        """Extract content from base64 encoded image using Vision API."""
        try:
            response = self.client.chat.completions.create(
                model=MODEL_VISION,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Image extraction error: {str(e)}")
            return None
    
    def clean_text(self, text: str, context: str) -> str:
        """Clean and structure extracted text using LLM."""
        try:
            prompt = f"""Clean and structure this extracted text about {context}.
            Fix formatting issues but preserve all original content and meaning.
            
            Text: {text[:MAX_TEXT_LENGTH]}"""
            
            response = self.client.chat.completions.create(
                model=MODEL_SYNTHESIS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"LLM cleaning error: {str(e)}")
            return text  # Return original if cleaning fails
    
    def synthesize_content(self, materials: dict, artifact_type: str, custom_prompt: Optional[str] = None) -> Optional[str]:
        """Generate synthesis from combined materials."""
        try:
            # Combine all materials
            combined = "\n\n---\n\n".join([
                f"## {name}\n\n{content}" 
                for name, content in materials.items()
            ])
            
            # Build prompt based on artifact type
            if artifact_type in SYNTHESIS_PROMPTS:
                base_prompt = SYNTHESIS_PROMPTS[artifact_type]
            else:  # Custom
                base_prompt = custom_prompt or "Synthesize these materials:"
            
            full_prompt = f"{base_prompt}\n\nMaterials:\n{combined[:MAX_SYNTHESIS_LENGTH]}"
            
            response = self.client.chat.completions.create(
                model=MODEL_SYNTHESIS,
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Synthesis error: {str(e)}")
            return None

# Global instance
ai_service = AIService() 