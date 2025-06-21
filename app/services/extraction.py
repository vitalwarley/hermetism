import PyPDF2
import base64
import logging
from typing import Optional, Tuple
import streamlit as st
from services.ai_service import ai_service

class ExtractionService:
    """Service for extracting content from various file types."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_pdf_info(self, pdf_file) -> Optional[dict]:
        """Get basic information about a PDF file."""
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(reader.pages)
            
            # Get basic metadata if available
            metadata = {}
            if reader.metadata:
                metadata.update({
                    'title': reader.metadata.get('/Title', 'Unknown'),
                    'author': reader.metadata.get('/Author', 'Unknown'),
                    'creator': reader.metadata.get('/Creator', 'Unknown'),
                })
            
            return {
                'total_pages': total_pages,
                'metadata': metadata
            }
        except Exception as e:
            self.logger.error(f"Error getting PDF info: {str(e)}")
            return None
    
    def extract_text_from_pdf(self, pdf_file, page_range: Optional[Tuple[int, int]] = None) -> Optional[str]:
        """Extract text from uploaded PDF file with improved error handling."""
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(reader.pages)
            text = ""
            
            if page_range:
                start, end = page_range
                
                # Validate page range
                if start < 1 or end < 1:
                    raise ValueError("Page numbers must be positive")
                if start > total_pages:
                    raise ValueError(f"Start page {start} exceeds total pages ({total_pages})")
                if end > total_pages:
                    st.warning(f"End page {end} exceeds total pages ({total_pages}). Using page {total_pages} as end.")
                    end = total_pages
                if start > end:
                    raise ValueError(f"Start page ({start}) cannot be greater than end page ({end})")
                
                # Extract text from specified range
                extracted_pages = 0
                for page_num in range(start-1, min(end, total_pages)):
                    try:
                        page_text = reader.pages[page_num].extract_text()
                        if page_text.strip():  # Only add non-empty pages
                            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                            extracted_pages += 1
                    except Exception as e:
                        self.logger.warning(f"Error extracting page {page_num + 1}: {str(e)}")
                        continue
                
                if extracted_pages == 0:
                    st.warning("No text content found in the selected page range.")
                else:
                    st.info(f"Successfully extracted text from {extracted_pages} pages (range: {start}-{min(end, total_pages)})")
                    
            else:
                # Extract all pages
                extracted_pages = 0
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():  # Only add non-empty pages
                            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                            extracted_pages += 1
                    except Exception as e:
                        self.logger.warning(f"Error extracting page {page_num + 1}: {str(e)}")
                        continue
                
                if extracted_pages == 0:
                    st.warning("No text content found in the PDF.")
                else:
                    st.info(f"Successfully extracted text from {extracted_pages} out of {total_pages} pages")
            
            return text.strip() if text.strip() else None
            
        except ValueError as e:
            st.error(f"Page range error: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"PDF extraction error: {str(e)}")
            st.error(f"PDF extraction error: {str(e)}")
            return None
    
    def extract_from_image(self, image_file, prompt: str) -> Optional[str]:
        """Extract content from image using Vision API."""
        try:
            # Read image and encode to base64
            image_bytes = image_file.read()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Reset file pointer for potential reuse
            image_file.seek(0)
            
            return ai_service.extract_from_image(base64_image, prompt)
        except Exception as e:
            self.logger.error(f"Image processing error: {str(e)}")
            st.error(f"Image processing error: {str(e)}")
            return None
    
    def extract_from_text_file(self, text_file) -> Optional[str]:
        """Extract content from text file."""
        try:
            content = text_file.read().decode('utf-8')
            if not content.strip():
                st.warning("Text file appears to be empty")
                return None
            return content
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                text_file.seek(0)
                content = text_file.read().decode('latin-1')
                st.warning("File encoding detected as Latin-1 instead of UTF-8")
                return content
            except Exception as e:
                self.logger.error(f"Text file encoding error: {str(e)}")
                st.error(f"Could not decode text file. Please ensure it's a valid text file.")
                return None
        except Exception as e:
            self.logger.error(f"Text file extraction error: {str(e)}")
            st.error(f"Text file extraction error: {str(e)}")
            return None
    
    def clean_extracted_text(self, text: str, context: str) -> str:
        """Clean and structure extracted text using LLM."""
        try:
            return ai_service.clean_text(text, context)
        except Exception as e:
            self.logger.error(f"Text cleaning error: {str(e)}")
            st.error(f"Text cleaning failed: {str(e)}")
            return text  # Return original text if cleaning fails

# Global instance
extraction_service = ExtractionService() 