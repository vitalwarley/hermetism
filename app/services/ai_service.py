from openai import OpenAI
import logging
from typing import Optional
import streamlit as st
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
    
    def _get_vision_model(self) -> str:
        """Get the vision model from session state or fall back to config."""
        return st.session_state.get('model_vision', MODEL_VISION)
    
    def _get_synthesis_model(self) -> str:
        """Get the synthesis model from session state or fall back to config."""
        return st.session_state.get('model_synthesis', MODEL_SYNTHESIS)
    
    def extract_from_image(self, base64_image: str, prompt: str) -> Optional[str]:
        """Extract content from base64 encoded image using Vision API."""
        try:
            response = self.client.chat.completions.create(
                model=self._get_vision_model(),
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
                model=self._get_synthesis_model(),
                messages=[{"role": "user", "content": prompt}],
                temperature=st.session_state.get('temperature', 0.7)
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"LLM cleaning error: {str(e)}")
            return text  # Return original if cleaning fails
    
    def summarize_text(self, text: str, context: str) -> str:
        """Summarize text content using LLM."""
        try:
            prompt = f"""Create a comprehensive summary of this {context}.
            Preserve all key information, concepts, and insights while making it more concise and structured.
            Include main points, key takeaways, and important details.
            
            Content: {text[:MAX_SYNTHESIS_LENGTH]}"""
            
            response = self.client.chat.completions.create(
                model=self._get_synthesis_model(),
                messages=[{"role": "user", "content": prompt}],
                temperature=st.session_state.get('temperature', 0.7)
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"LLM summarization error: {str(e)}")
            return text  # Return original if summarization fails
    
    def apply_custom_prompt(self, text: str, prompt: str) -> str:
        """Apply a custom extraction prompt to text using LLM."""
        try:
            # Combine the custom prompt with the text
            full_prompt = f"""{prompt}

Text to process:
{text[:MAX_TEXT_LENGTH]}"""
            
            response = self.client.chat.completions.create(
                model=self._get_synthesis_model(),
                messages=[{"role": "user", "content": full_prompt}],
                temperature=st.session_state.get('temperature', 0.7)
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Custom prompt processing error: {str(e)}")
            return text  # Return original if processing fails
    
    def synthesize_content(self, materials: dict, custom_prompt: str, material_placeholders: Optional[dict] = None) -> Optional[str]:
        """Generate synthesis from combined materials using custom prompt with placeholder support."""
        try:
            # Get combined placeholders from session state
            combined_placeholders = st.session_state.synthesis_config.get('combined_placeholders', {})
            
            # Check if prompt contains placeholders (individual or combined)
            all_placeholders = []
            if material_placeholders:
                all_placeholders.extend(material_placeholders.values())
            all_placeholders.extend(combined_placeholders.keys())
            
            has_placeholders = any(f"{{{placeholder}}}" in custom_prompt for placeholder in all_placeholders)
            
            if has_placeholders:
                # Use placeholder substitution
                full_prompt = self._substitute_placeholders(custom_prompt, materials, material_placeholders, combined_placeholders)
            else:
                # Fallback to original behavior - append all materials at the end
                combined = "\n\n---\n\n".join([
                    f"## {name}\n\n{content}" 
                    for name, content in materials.items()
                ])
                full_prompt = f"{custom_prompt}\n\nMaterials:\n{combined[:MAX_SYNTHESIS_LENGTH]}"
            
            response = self.client.chat.completions.create(
                model=self._get_synthesis_model(),
                messages=[{"role": "user", "content": full_prompt}],
                temperature=st.session_state.get('temperature', 0.7)
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Synthesis error: {str(e)}")
            return None
    
    def _substitute_placeholders(self, prompt: str, materials: dict, material_placeholders: dict, combined_placeholders: dict = None) -> str:
        """Substitute material placeholders in the prompt with actual content."""
        full_prompt = prompt
        
        # Create reverse mapping from placeholder to material name
        placeholder_to_material = {placeholder: material_name for material_name, placeholder in material_placeholders.items()} if material_placeholders else {}
        
        # Find all placeholders in the prompt and substitute them
        import re
        
        # Find all {placeholder} patterns in the prompt
        placeholder_pattern = r'\{([^}]+)\}'
        placeholders_in_prompt = re.findall(placeholder_pattern, prompt)
        
        for placeholder in placeholders_in_prompt:
            # Check if it's a combined placeholder
            if combined_placeholders and placeholder in combined_placeholders:
                combo_data = combined_placeholders[placeholder]
                # Get the material keys for this combined placeholder
                material_keys = combo_data['keys']
                format_type = combo_data.get('format', 'Name + Content')
                source_placeholders = combo_data.get('source_placeholders', [])
                
                # Build combined content using the source placeholders
                combined_parts = []
                
                # Use the source placeholders to get the correct material names
                for source_placeholder in source_placeholders:
                    if source_placeholder in placeholder_to_material:
                        material_name = placeholder_to_material[source_placeholder]
                        if material_name in materials:
                            content = materials[material_name]
                            
                            if format_type == "Name + Content":
                                combined_parts.append(f"### {material_name}\n\n{content}")
                            elif format_type == "Content Only":
                                combined_parts.append(content)
                            elif format_type == "Name as Header":
                                combined_parts.append(f"# {material_name}\n\n{content}")
                        else:
                            self.logger.warning(f"Material '{material_name}' not found in materials dict")
                    else:
                        self.logger.warning(f"Source placeholder '{source_placeholder}' not found in placeholder mapping")
                
                # Join all parts with line breaks
                if combined_parts:
                    combined_content = "\n\n---\n\n".join(combined_parts)
                    
                    # Limit content length
                    content_limit = MAX_SYNTHESIS_LENGTH // len(placeholders_in_prompt) if len(placeholders_in_prompt) > 1 else MAX_SYNTHESIS_LENGTH
                    limited_content = combined_content[:content_limit]
                    full_prompt = full_prompt.replace(f"{{{placeholder}}}", limited_content)
                else:
                    self.logger.warning(f"No content found for combined placeholder: {{{placeholder}}}")
                    full_prompt = full_prompt.replace(f"{{{placeholder}}}", f"[Combined placeholder '{placeholder}' has no content]")
                
            elif placeholder in placeholder_to_material:
                # Handle individual placeholder
                material_name = placeholder_to_material[placeholder]
                material_content = materials.get(material_name, f"[Material '{material_name}' not found]")
                # Limit content length per placeholder to avoid token overflow
                content_limit = MAX_SYNTHESIS_LENGTH // len(placeholders_in_prompt) if len(placeholders_in_prompt) > 1 else MAX_SYNTHESIS_LENGTH
                limited_content = material_content[:content_limit]
                full_prompt = full_prompt.replace(f"{{{placeholder}}}", limited_content)
            else:
                # Keep unknown placeholders as-is or mark them
                self.logger.warning(f"Unknown placeholder: {{{placeholder}}}")
        
        return full_prompt

# Global instance
ai_service = AIService() 