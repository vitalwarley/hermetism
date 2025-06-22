import PyPDF2
import base64
import logging
from typing import Optional, Tuple
from services.ai_service import ai_service
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import re
import xml.etree.ElementTree as ET
from urllib.parse import quote
import traceback

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
                    self.logger.warning(f"End page {end} exceeds total pages ({total_pages}). Using page {total_pages} as end.")
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
                    self.logger.warning("No text content found in the selected page range.")
                else:
                    self.logger.info(f"Successfully extracted text from {extracted_pages} pages (range: {start}-{min(end, total_pages)})")
                    
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
                    self.logger.warning("No text content found in the PDF.")
                else:
                    self.logger.info(f"Successfully extracted text from {extracted_pages} out of {total_pages} pages")
            
            return text.strip() if text.strip() else None
            
        except ValueError as e:
            self.logger.error(f"Page range error: {str(e)}")
            raise ValueError(f"Page range error: {str(e)}")
        except Exception as e:
            self.logger.error(f"PDF extraction error: {str(e)}")
            raise Exception(f"PDF extraction error: {str(e)}")
    
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
            raise Exception(f"Image processing error: {str(e)}")
    
    def extract_from_text_file(self, text_file) -> Optional[str]:
        """Extract content from text file."""
        try:
            content = text_file.read().decode('utf-8')
            if not content.strip():
                self.logger.warning("Text file appears to be empty")
                return None
            return content
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                text_file.seek(0)
                content = text_file.read().decode('latin-1')
                self.logger.warning("File encoding detected as Latin-1 instead of UTF-8")
                return content
            except Exception as e:
                self.logger.error(f"Text file encoding error: {str(e)}")
                raise Exception("Could not decode text file. Please ensure it's a valid text file.")
        except Exception as e:
            self.logger.error(f"Text file extraction error: {str(e)}")
            raise Exception(f"Text file extraction error: {str(e)}")
    
    def clean_extracted_text(self, text: str, context: str) -> str:
        """Clean and structure extracted text using LLM."""
        try:
            return ai_service.clean_text(text, context)
        except Exception as e:
            self.logger.error(f"Text cleaning error: {str(e)}")
            raise Exception(f"Text cleaning failed: {str(e)}")
    
    def extract_from_url(self, url: str, extract_option: str = "main_content", css_selector: str = None) -> Optional[str]:
        """Extract content from a web URL."""
        try:
            # Set up headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Fetch the webpage
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Extract content based on the selected option
            if extract_option == "custom_selector" and css_selector:
                elements = soup.select(css_selector)
                if elements:
                    content = '\n\n'.join([elem.get_text(strip=True) for elem in elements])
                else:
                    # Fallback to main content if selector doesn't match
                    content = self._extract_main_content(soup)
                    self.logger.warning(f"CSS selector '{css_selector}' didn't match any elements. Using main content extraction.")
            
            elif extract_option == "full_page":
                content = soup.get_text(separator='\n', strip=True)
            
            else:  # main_content
                content = self._extract_main_content(soup)
            
            # Clean up whitespace
            content = re.sub(r'\n\s*\n', '\n\n', content)
            content = re.sub(r' +', ' ', content)
            
            if not content.strip():
                return None
            
            # Add metadata
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else "Unknown Title"
            
            return f"URL: {url}\nTitle: {title_text}\n\n{content.strip()}"
            
        except requests.RequestException as e:
            self.logger.error(f"URL request error: {str(e)}")
            raise Exception(f"Failed to fetch URL: {str(e)}")
        except Exception as e:
            self.logger.error(f"URL extraction error: {str(e)}")
            raise Exception(f"Failed to extract content: {str(e)}")
    
    def _extract_main_content(self, soup) -> str:
        """Extract main content from HTML soup using common content selectors."""
        # Common content selectors ordered by priority
        content_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.main-content',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '#content',
            '#main',
            '.container',
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                # Use the first matching element
                content = elements[0].get_text(separator='\n', strip=True)
                if len(content.strip()) > 100:  # Ensure we got substantial content
                    return content
        
        # Fallback to body content
        body = soup.find('body')
        if body:
            return body.get_text(separator='\n', strip=True)
        
        # Last resort
        return soup.get_text(separator='\n', strip=True)
    
    def extract_from_youtube(self, youtube_url: str, transcript_type: str = "any", language: str = None) -> Optional[str]:
        """Extract transcript from YouTube video."""
        try:
            # Import youtube-transcript-api here to make it optional
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
                from youtube_transcript_api.formatters import TextFormatter
                from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
            except ImportError:
                raise ImportError("youtube-transcript-api is required for YouTube transcription. Install it with: pip install youtube-transcript-api")
            
            # Extract video ID from URL
            video_id = self._extract_youtube_video_id(youtube_url)
            if not video_id:
                raise ValueError("Invalid YouTube URL or unable to extract video ID")
            
            self.logger.info(f"Attempting to get transcript for video ID: {video_id}")
            
            # Get transcript with the updated API
            try:
                # First, check what transcripts are available
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # Log available transcripts for debugging
                available_transcripts = []
                for transcript in transcript_list:
                    transcript_info = {
                        'language': transcript.language,
                        'language_code': transcript.language_code,
                        'is_generated': transcript.is_generated,
                        'is_translatable': transcript.is_translatable
                    }
                    available_transcripts.append(transcript_info)
                
                self.logger.info(f"Available transcripts: {available_transcripts}")
                
                # Try to get the best transcript based on preferences
                transcript = None
                
                if language:
                    # Try specific language first
                    if transcript_type == "manual":
                        transcript = transcript_list.find_manually_created_transcript([language])
                    elif transcript_type == "auto":
                        transcript = transcript_list.find_generated_transcript([language]) 
                    else:  # any
                        try:
                            transcript = transcript_list.find_manually_created_transcript([language])
                        except (NoTranscriptFound, AttributeError):
                            transcript = transcript_list.find_generated_transcript([language])
                else:
                    # Auto-detect language - try common languages
                    common_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh']
                    
                    if transcript_type == "manual":
                        transcript = transcript_list.find_manually_created_transcript(common_languages)
                    elif transcript_type == "auto":
                        transcript = transcript_list.find_generated_transcript(common_languages)
                    else:  # any
                        # Try manual first, then auto
                        try:
                            transcript = transcript_list.find_manually_created_transcript(common_languages)
                        except (NoTranscriptFound, AttributeError):
                            transcript = transcript_list.find_generated_transcript(common_languages)
                
                if not transcript:
                    raise NoTranscriptFound("No suitable transcript found")
                
                # Fetch and format transcript
                self.logger.info(f"Using transcript: {transcript.language} ({'manual' if not transcript.is_generated else 'auto'})")
                
                transcript_data = transcript.fetch()
                
                if not transcript_data:
                    raise Exception("Transcript data is empty")
                
                formatter = TextFormatter()
                formatted_text = formatter.format_transcript(transcript_data)
                
                # Add metadata
                video_title = self._get_youtube_title(youtube_url)
                
                result = f"YouTube Video: {youtube_url}\nTitle: {video_title}\nLanguage: {transcript.language}\nType: {'Manual' if not transcript.is_generated else 'Auto-generated'}\n\n{formatted_text}"
                
                self.logger.info(f"Successfully extracted transcript ({len(formatted_text)} characters)")
                return result
                
            except TranscriptsDisabled:
                raise Exception("Transcripts are disabled for this video")
            except VideoUnavailable:
                raise Exception("Video is unavailable or private")
            except NoTranscriptFound:
                raise Exception("No transcripts found for this video")
            except Exception as transcript_error:
                self.logger.error(f"Transcript extraction error: {str(transcript_error)}")
                raise Exception(f"Failed to get transcript: {str(transcript_error)}")
                
        except ImportError as e:
            self.logger.error(f"YouTube transcript dependency error: {str(e)}")
            raise e
        except Exception as e:
            self.logger.error(f"YouTube extraction error: {str(e)}")
            raise e
    
    def _extract_youtube_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        # Clean up the URL
        url = url.strip()
        
        patterns = [
            # Standard youtube.com URLs
            r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
            # Shortened youtu.be URLs  
            r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
            # Embedded URLs
            r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            # Old format
            r'(?:youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
            # Mobile URLs
            r'(?:m\.youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
            # Gaming URLs
            r'(?:gaming\.youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                # Validate video ID format (11 characters, alphanumeric + _ -)
                if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]+$', video_id):
                    self.logger.info(f"Extracted video ID: {video_id} from URL: {url}")
                    return video_id
        
        # Try to extract from URL parameters as fallback
        try:
            parsed_url = urlparse(url)
            if 'v' in parse_qs(parsed_url.query):
                video_id = parse_qs(parsed_url.query)['v'][0]
                if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]+$', video_id):
                    self.logger.info(f"Extracted video ID from params: {video_id}")
                    return video_id
        except:
            pass
        
        self.logger.error(f"Could not extract video ID from URL: {url}")
        return None
    
    def _get_youtube_title(self, url: str) -> str:
        """Get YouTube video title."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            # Extract title from HTML
            title_match = re.search(r'<title>([^<]+)</title>', response.text)
            if title_match:
                title = title_match.group(1)
                # Clean up YouTube title
                title = title.replace(' - YouTube', '').strip()
                return title
        except:
            pass
        
        return "Unknown Title"
    
    def summarize_content(self, content: str, context: str) -> str:
        """Summarize content using AI."""
        try:
            return ai_service.summarize_text(content, context)
        except Exception as e:
            self.logger.error(f"Content summarization error: {str(e)}")
            raise Exception(f"Content summarization failed: {str(e)}")

    def apply_extraction_prompt(self, text: str, prompt: str) -> str:
        """Apply a custom extraction prompt to the text using AI."""
        try:
            if not text or not prompt:
                return text
            
            # Use AI service to process the text with the custom prompt
            return ai_service.apply_custom_prompt(text, prompt)
        except Exception as e:
            self.logger.error(f"Failed to apply extraction prompt: {str(e)}")
            # Return original text if processing fails
            return text

# Global instance
extraction_service = ExtractionService() 