#!/usr/bin/env python3

import os
import json
import base64
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
import time
import argparse
# Add new imports for PDF and web extraction
try:
    from PyPDF2 import PdfReader
except ImportError:
    logging.error("PyPDF2 is required for PDF extraction. Install with: pip install PyPDF2")
    PdfReader = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    logging.error("BeautifulSoup is required for web extraction. Install with: pip install beautifulsoup4")
    BeautifulSoup = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hermetic_synthesis.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

# Constants
MODEL_ID_VISION = 'openai/gpt-4o-mini'  # For vision tasks
MODEL_ID_SYNTHESIS = 'openai/gpt-4.1'  # For synthesis
REQUEST_TIMEOUT = 30

# PDF page mappings for Crowley books
BOOK_OF_THOTH_PAGES = {
    "emperor": (49, 50),
}

LIBER_THETA_PAGES = {
    "emperor": 35,
}

# Configuration for Sol em Áries
CONFIG = {
    "project": "sol_em_aries",
    "base_path": "data/images",
    "categories": {
        "zodiac": {
            "path": "zodiac/aries", 
            "type": "sign",
            "prompt": "Extract all astrological information about Aries from this image, including characteristics, symbols, ruling planets, elements, qualities, and any other relevant details. Preserve all original text. If you see any related images interspersed in the input image (like symbols, glyphs, or illustrations), add your analysis of these visual elements at the end of the raw extraction."
        },
        "planet": {
            "path": "planets/sun", 
            "type": "planet",
            "prompt": "Extract all information about the Sun as a planet/celestial body, including astronomical data, astrological meanings, mythological associations, and influences. Preserve all original text. If you see any related images interspersed in the input image (like symbols, glyphs, or illustrations), add your analysis of these visual elements at the end of the raw extraction."
        },
        "synthesis": {
            "path": "planets-zodiac/sun_aries", 
            "type": "synthesis",
            "prompt": "Extract the synthesis content that describes how the Sun expresses itself in Aries. Include all interpretations, meanings, and practical applications. If you see any related images interspersed in the input image (like symbols, glyphs, or illustrations), add your analysis of these visual elements at the end of the raw extraction."
        },
        "angels": {
            "path": "angels/aries", 
            "type": "angel",
            "prompt": "Extract all information about the kabbalistic angel from this image, including name, correspondences, sphere associations, time periods, and spiritual attributes. Preserve Hebrew text and translations. If you see any related images interspersed in the input image (like symbols, sigils, or illustrations), add your analysis of these visual elements at the end of the raw extraction."
        },
        "tarot": {
            "path": "tarot/aries", 
            "type": "tarot",
            "prompt": "Extract all information about this tarot card, including symbolism, meanings, elemental associations, and interpretive guidance. If you see any related images interspersed in the input image (like card illustrations, symbols, or visual elements), add your analysis of these visual elements at the end of the raw extraction."
        },
        # New web extraction categories
        "esoteric_meanings": {
            "type": "web_tarot",
            "sources": {
                "emperor": "https://www.esotericmeanings.com/thoth-emperor-tarot-card-tutorial/",
                "two_of_wands": "https://www.esotericmeanings.com/two-of-wands-thoth-tarot-card-tutorial/",
                "three_of_wands": "https://www.esotericmeanings.com/three-of-wands-thoth-tarot-card-tutorial/",
                "four_of_wands": "https://www.esotericmeanings.com/four-of-wands-thoth-tarot-card-tutorial/",
                "prince_of_disks": "https://www.esotericmeanings.com/prince-of-disks-thoth-tarot-card-tutorial/",
                "queen_of_wands": "https://www.esotericmeanings.com/queen-of-wands-thoth-tarot-card-tutorial/"
            },
            "save_path": "data/webpages/sun_in_aries"
        },
        "crowley_books": {
            "type": "pdf_tarot",
            "sources": {
                "emperor": {
                    "book_of_thoth": (49, 50),
                    "liber_theta": 35
                }
            },
            "save_path": "data/books/sun_in_aries",
            "pdf_paths": {
                "book_of_thoth": "src/scripts/tarot/data/Aleister Crowley - The book of Thoth.pdf",
                "liber_theta": "src/scripts/tarot/data/Liber Theta - Tarot Symbolism & Divination.pdf"
            }
        },
        "inacchio_base": {
            "type": "web_base",
            "sources": {
                "schemhammephorasch": "https://inaciovacchiano.com/a-cabala-de-hakash-ba-hakash/a-cabala-de-hakash-ba-hakash-filosofia-metafisica-quantica-cabalistica-tomo-iii/",
                "os_72_anjos": "https://inaciovacchiano.com/a-cabala-de-hakash-ba-hakash/a-cabala-de-hakash-ba-hakash-filosofia-metafisica-quantica-cabalistica-tomo-iii/6-os-72-anjos/"
            },
            "save_path": "data/webpages/inacchio/base"
        },
        "inacchio_angels": {
            "type": "web_angels",
            "sources": {
                "vehuiah": "https://inaciovacchiano.com/a-cabala-de-hakash-ba-hakash/a-cabala-de-hakash-ba-hakash-filosofia-metafisica-quantica-cabalistica-tomo-iii/1-1-1-vehuiah/",
                "jeliel": "https://inaciovacchiano.com/a-cabala-de-hakash-ba-hakash/a-cabala-de-hakash-ba-hakash-filosofia-metafisica-quantica-cabalistica-tomo-iii/2-1-2-jeliel/",
                "sitael": "https://inaciovacchiano.com/a-cabala-de-hakash-ba-hakash/a-cabala-de-hakash-ba-hakash-filosofia-metafisica-quantica-cabalistica-tomo-iii/3-1-3-sitael/",
                "elemiah": "http://inaciovacchiano.com/a-cabala-de-hakash-ba-hakash/a-cabala-de-hakash-ba-hakash-filosofia-metafisica-quantica-cabalistica-tomo-iii/4-1-4-elemiah/",
                "mahasiah": "https://inaciovacchiano.com/a-cabala-de-hakash-ba-hakash/a-cabala-de-hakash-ba-hakash-filosofia-metafisica-quantica-cabalistica-tomo-iii/5-1-5-mahasiah/",
                "lehahel": "https://inaciovacchiano.com/a-cabala-de-hakash-ba-hakash/a-cabala-de-hakash-ba-hakash-filosofia-metafisica-quantica-cabalistica-tomo-iii/6-1-6-lelahel/"
            },
            "save_path": "data/webpages/inacchio/sun_in_aries"
        },
        "local_docs": {
            "type": "local_files",
            "sources": {
                "dignidades_planetarias": "data/custom/dignidades_planetárias.md"
            },
            "save_path": "data/local/astrology/base"
        }
    },
    "output": "output/sol_em_aries_synthesis.md",
    "raw_extractions_dir": "output/sol_em_aries_raw_extractions"
}

def encode_image_to_base64(image_path: str) -> str:
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_content(image_path: str, content_type: str, prompt: str) -> Optional[str]:
    """Extract content from a single image using OpenRouter API."""
    logging.info(f"Extracting content from: {image_path}")
    
    if not os.getenv('OPENROUTER_API_KEY'):
        logging.error("OPENROUTER_API_KEY not found")
        return None
    
    try:
        base64_image = encode_image_to_base64(image_path)
        
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "HTTP-Referer": "https://github.com/warleydev/hermetism",
            "X-Title": "Hermetic Synthesis",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": MODEL_ID_VISION,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data and response_data.get('choices'):
                content = response_data['choices'][0]['message']['content']
                logging.info(f"Successfully extracted content from {Path(image_path).name}")
                return content
        else:
            logging.error(f"API error: {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"Error extracting from {image_path}: {str(e)}")
        return None

def save_raw_extraction(category: str, filename: str, content: str):
    """Save raw extraction to a separate file."""
    raw_dir = Path(CONFIG["raw_extractions_dir"]) / category
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = raw_dir / f"{filename}.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Raw Extraction: {filename}\n\n")
        f.write(content)
    
    logging.info(f"Saved raw extraction to: {output_path}")

def extract_text_from_pdf(pdf_path: str, start_page: int = None, end_page: int = None) -> Optional[str]:
    """Extract text from a PDF file between specified pages."""
    if PdfReader is None:
        logging.error("PyPDF2 is not available. Cannot extract PDF content.")
        return None
        
    logging.info(f"Extracting text from {pdf_path} (pages {start_page}-{end_page})")
    try:
        if not os.path.exists(pdf_path):
            logging.error(f"PDF file not found: {pdf_path}")
            return None

        reader = PdfReader(pdf_path)
        text = ""
        
        if start_page is not None and end_page is not None:
            logging.debug(f"Extracting pages {start_page} to {end_page}")
            for page_num in range(start_page - 1, end_page):
                if page_num >= len(reader.pages):
                    logging.warning(f"Page {page_num + 1} not found in PDF")
                    continue
                page_text = reader.pages[page_num].extract_text()
                text += page_text
        elif start_page is not None:
            logging.debug(f"Extracting single page {start_page}")
            if start_page - 1 >= len(reader.pages):
                logging.warning(f"Page {start_page} not found in PDF")
                return None
            text = reader.pages[start_page - 1].extract_text()
        
        if not text.strip():
            logging.warning("No text extracted from PDF")
            return None
            
        logging.info(f"Successfully extracted text from PDF")
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        return None

def download_web_content(url: str, extract_text: bool = True) -> Optional[str]:
    """Download content from a URL and return as text."""
    if extract_text and BeautifulSoup is None:
        logging.error("BeautifulSoup is not available. Cannot extract HTML content.")
        return None
        
    logging.info(f"Downloading content from {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        if extract_text:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            content = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in content.splitlines())
            content = '\n'.join(line for line in lines if line)
            return content
        else:
            return response.text
            
    except Exception as e:
        logging.error(f"Error downloading content from {url}: {str(e)}")
        return None

def save_extracted_content(content: str, save_path: str, filename: str):
    """Save extracted content to specified path."""
    output_dir = Path(save_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{filename}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logging.info(f"Saved content to: {output_file}")

def process_web_extraction(category_name: str, category_config: dict) -> Dict[str, str]:
    """Process web content extraction for a category."""
    logging.info(f"Processing web extraction for: {category_name}")
    
    extracted_content = {}
    sources = category_config.get("sources", {})
    save_path = category_config.get("save_path", "")
    
    for key, url in sources.items():
        logging.info(f"Downloading {key} from {url}")
        content = download_web_content(url)
        
        if content:
            # Save to specified path
            save_extracted_content(content, save_path, key)
            
            # Also save raw extraction
            save_raw_extraction(category_name, key, content)
            
            extracted_content[key] = content
        
        # Add delay to avoid rate limiting
        time.sleep(2)
    
    return extracted_content

def process_pdf_extraction(category_name: str, category_config: dict) -> Dict[str, str]:
    """Process PDF content extraction for a category."""
    logging.info(f"Processing PDF extraction for: {category_name}")
    
    extracted_content = {}
    sources = category_config.get("sources", {})
    save_path = category_config.get("save_path", "")
    pdf_paths = category_config.get("pdf_paths", {})
    
    for card_key, pdf_info in sources.items():
        logging.info(f"Processing PDF content for: {card_key}")
        
        combined_content = []
        
        # Process Book of Thoth if specified
        if "book_of_thoth" in pdf_info and "book_of_thoth" in pdf_paths:
            pdf_path = pdf_paths["book_of_thoth"]
            if isinstance(pdf_info["book_of_thoth"], tuple):
                start_page, end_page = pdf_info["book_of_thoth"]
                content = extract_text_from_pdf(pdf_path, start_page, end_page)
            else:
                page = pdf_info["book_of_thoth"]
                content = extract_text_from_pdf(pdf_path, page, page)
            
            if content:
                combined_content.append(f"## Book of Thoth\n\n{content}")
        
        # Process Liber Theta if specified
        if "liber_theta" in pdf_info and "liber_theta" in pdf_paths:
            pdf_path = pdf_paths["liber_theta"]
            page = pdf_info["liber_theta"]
            content = extract_text_from_pdf(pdf_path, page, page)
            
            if content:
                combined_content.append(f"## Liber Theta\n\n{content}")
        
        if combined_content:
            final_content = "\n\n".join(combined_content)
            
            # Save to specified path
            save_extracted_content(final_content, save_path, card_key)
            
            # Also save raw extraction
            save_raw_extraction(category_name, card_key, final_content)
            
            extracted_content[card_key] = final_content
    
    return extracted_content

def process_local_files(category_name: str, category_config: dict) -> Dict[str, str]:
    """Process local file reading for a category."""
    logging.info(f"Processing local files for: {category_name}")
    
    extracted_content = {}
    sources = category_config.get("sources", {})
    save_path = category_config.get("save_path", "")
    
    for key, file_path in sources.items():
        logging.info(f"Reading local file {key} from {file_path}")
        
        try:
            if not os.path.exists(file_path):
                logging.warning(f"File not found: {file_path}")
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content:
                # Save to specified path
                save_extracted_content(content, save_path, key)
                
                # Also save raw extraction
                save_raw_extraction(category_name, key, content)
                
                extracted_content[key] = content
                logging.info(f"Successfully read {key}: {len(content)} characters")
            else:
                logging.warning(f"Empty file: {file_path}")Sol em Áries
                
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {str(e)}")
    
    return extracted_content

def process_category(category_path: str, category_name: str, content_type: str, prompt: str) -> Dict[str, str]:
    """Process all images in a category directory."""
    logging.info(f"Processing category: {category_path}")
    
    full_path = Path(CONFIG["base_path"]) / category_path
    extracted_content = {}
    
    # Check if directory exists and has images
    if not full_path.exists():
        logging.warning(f"Directory {category_path} does not exist")
        return {}
    
    image_files = list(full_path.glob("*.jpg")) + list(full_path.glob("*.jpeg")) + list(full_path.glob("*.png"))
    
    if not image_files:
        logging.warning(f"No images found in {category_path}")
        return {}
    
    # Process each image
    for image_file in sorted(image_files):
        content = extract_content(str(image_file), content_type, prompt)
        if content:
            extracted_content[image_file.stem] = content
            # Save raw extractionSol em Áries
            save_raw_extraction(category_name, image_file.stem, content)
        # Add small delay to avoid rate limiting
        time.sleep(1)
    
    return extracted_content

def combine_content(all_extractions: Dict[str, Dict[str, str]]) -> str:
    """Combine all extracted content into structured sections."""
    logging.info("Combining extracted content")
    
    combined = []
    
    # Zodiac content
    if "zodiac" in all_extractions and all_extractions["zodiac"]:
        combined.append("## O Signo de Áries\n")
        for key, content in all_extractions["zodiac"].items():
            combined.append(content)
            combined.append("\n")
    
    # Planet content
    if "planet" in all_extractions and all_extractions["planet"]:
        combined.append("\n## O Planeta Sol\n")
        for key, content in all_extractions["planet"].items():
            combined.append(content)
            combined.append("\n")
    
    # Synthesis content
    if "synthesis" in all_extractions and all_extractions["synthesis"]:
        combined.append("\n## Sol em Áries - Síntese Base\n")
        for key, content in all_extractions["synthesis"].items():
            combined.append(content)
            combined.append("\n")Sol em Áries
            combined.append(content)
            combined.append("\n")
    
    # Tarot content
    if "tarot" in all_extractions and all_extractions["tarot"]:
        combined.append("\n## Correspondências do Tarô\n")
        for key, content in all_extractions["tarot"].items():
            combined.append(content)
            combined.append("\n")
    
    # Esoteric Meanings (web tarot content)
    if "esoteric_meanings" in all_extractions and all_extractions["esoteric_meanings"]:
        combined.append("\n## Interpretações Esotéricas - Cartas do Tarô\n")
        for key, content in all_extractions["esoteric_meanings"].items():
            combined.append(f"### {key.replace('_', ' ').title()}\n")
            combined.append(content)
            combined.append("\n")
    
    # Crowley Books (PDF content)
    if "crowley_books" in all_extractions and all_extractions["crowley_books"]:
        combined.append("\n## Textos de Crowley - Livros Originais\n")
        for key, content in all_extractions["crowley_books"].items():
            combined.append(f"### {key.replace('_', ' ').title()}\n")
            combined.append(content)
            combined.append("\n")
    
    # # Inacchio Base (fundamental concepts)
    # if "inacchio_base" in all_extractions and all_extractions["inacchio_base"]:
    #     combined.append("\n## Fundamentos Cabalísticos - Inácio Vacchiano\n")
    #     for key, content in all_extractions["inacchio_base"].items():
    #         combined.append(f"### {key.replace('_', ' ').title()}\n")
    #         combined.append(content)
    #         combined.append("\n")
    
    # Inacchio Angels (specific angels)
    if "inacchio_angels" in all_extractions and all_extractions["inacchio_angels"]:
        combined.append("\n## Anjos de Sol em Áries - Inácio Vacchiano\n")
        for key, content in all_extractions["inacchio_angels"].items():
            combined.append(f"### Anjo {key.title()}\n")
            combined.append(content)
            combined.append("\n")
    
    # Local Documents (custom documents)
    if "local_docs" in all_extractions and all_extractions["local_docs"]:
        combined.append("\n## Documentos Locais - Material de Referência\n")
        for key, content in all_extractions["local_docs"].items():
            combined.append(f"### {key.replace('_', ' ').title()}\n")
            combined.append(content)
            combined.append("\n")
    
    return "\n".join(combined)

def generate_synthesis(combined_content: str) -> Optional[str]:
    """Generate final comprehensive synthesis using GPT-4."""
    logging.info("Generating final synthesis")
    
    if not os.getenv('OPENROUTER_API_KEY'):
        logging.error("OPENROUTER_API_KEY not found")
        return None
    
    prompt = f"""Você é um especialista em astrologia hermética, cabala e tarô. Com base no conteúdo extraído abaixo, crie uma síntese hermética completa sobre Sol em Áries usando o template fornecido.


1. Fundamentos Astrológicos: Planeta e Signo
2. Correspondências Angélicas 
- Organize-os 2 a 2: cada anjo é meia carta do tarô, logo 2 anjos = 1 carta do tarô. Por exemplo, Vehuhiah e Eliel estão associados com a carta 2 de paus. Deve-se expor: o que os anjos tem a ver com a carta, as virtudes e domínios de cada anjo, e como essas virtudes se manifestam na vida prática.
- Para cada decanato, traga também uma explicação sob a ótica dos dois anjos relacionados.
- Tal exposição deve refletir os poderes concedidos de cada anjo. Esses poderes precisam ser modulados de acordo com questões e situações do planeta em específico. Por exemplo, em assuntos relacionados ao planeta Sol, Vehuhiah serve para que? E assim para os demais anjos.
- Usar todo o arranjo dos anjos para elaborar sobre o arcano maior.
3. Conclusão
- Sumarize o que foi exposto sobre os anjos e as cartas do tarô.

CONTEÚDO EXTRAÍDO:
{combined_content}


ATENÇÃO:

1. Quanto ao material do Inácio, use apenas os poderes concedidos de cada anjo. 
2. Quanto ao restante do material, use-os integralmente.
3. Ao elaborar a síntese, priorize fortemente (cerca de 80%) as informações sobre anjos (com ênfase especial no conteúdo de Inácio Vacchiano, focando apenas nos poderes concedidos de cada anjo) e cartas do tarô (menores, corte e maiores). Os conteúdos sobre signo e planeta devem ser considerados secundários (cerca de 20%), servindo apenas como base contextual. 
4. Estruture a síntese de modo que a análise dos anjos e do tarô seja o foco central, justificando as correspondências e relações herméticas, enquanto as informações astrológicas gerais (signo/planeta) apenas contextualizam e fundamentam as associações principais.

"""
    
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "HTTP-Referer": "https://github.com/warleydev/hermetism",
            "X-Title": "Hermetic Synthesis",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": MODEL_ID_SYNTHESIS,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60  # Longer timeout for synthesis
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data and response_data.get('choices'):
                synthesis = response_data['choices'][0]['message']['content']
                logging.info("Successfully generated synthesis")
                return synthesis
        else:
            logging.error(f"API error: {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"Error generating synthesis: {str(e)}")
        return None

def save_output(content: str, filename: str):
    """Save the final synthesis to a markdown file."""
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logging.info(f"Saved synthesis to: {output_path}")

def load_combined_content(filepath: str) -> Optional[str]:
    """Load previously saved combined content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        logging.info(f"Loaded combined content from: {filepath}")
        return content
    except Exception as e:
        logging.error(f"Error loading combined content: {str(e)}")
        return None

def load_raw_extractions() -> Dict[str, Dict[str, str]]:
    """Load all raw extractions from the filesystem."""
    logging.info("Loading raw extractions from filesystem")
    
    raw_dir = Path(CONFIG["raw_extractions_dir"])
    if not raw_dir.exists():
        logging.error(f"Raw extractions directory not found: {raw_dir}")
        return {}
    
    all_extractions = {}
    
    # Iterate through category directories
    for category_dir in raw_dir.iterdir():
        if not category_dir.is_dir():
            continue
            
        category_name = category_dir.name
        category_extractions = {}
        
        # Load all .md files in the category directory
        for extraction_file in category_dir.glob("*.md"):
            try:
                with open(extraction_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove the header that was added during save_raw_extraction
                if content.startswith(f"# Raw Extraction: {extraction_file.stem}\n\n"):
                    content = content[len(f"# Raw Extraction: {extraction_file.stem}\n\n"):]
                
                category_extractions[extraction_file.stem] = content
                logging.info(f"Loaded {extraction_file.stem} from {category_name}")
                
            except Exception as e:
                logging.error(f"Error loading {extraction_file}: {str(e)}")
        
        if category_extractions:
            all_extractions[category_name] = category_extractions
            logging.info(f"Loaded {len(category_extractions)} extractions from {category_name}")
    
    return all_extractions

def main():
    """Run the complete hermetic synthesis pipeline."""
    parser = argparse.ArgumentParser(description='Hermetic Synthesis Pipeline')
    parser.add_argument('--synthesis-only', action='store_true', 
                       help='Run only the synthesis step using existing combined content')
    parser.add_argument('--from-raw', action='store_true',
                       help='Load content from raw extractions and combine again (skip extraction)')
    args = parser.parse_args()
    
    logging.info("=== Starting Hermetic Synthesis Pipeline ===")
    logging.info(f"Project: {CONFIG['project']}")
    
    # Check API key
    if not os.getenv('OPENROUTER_API_KEY'):
        logging.error("OPENROUTER_API_KEY environment variable not set")
        return
    
    combined_content = None
    
    if args.synthesis_only:
        # Load existing combined content
        intermediate_path = CONFIG["output"].replace(".md", "_combined.md")
        combined_content = load_combined_content(intermediate_path)
        
        if not combined_content:
            logging.error("Could not load combined content. Run full pipeline first.")
            return
            
        logging.info("Using existing combined content for synthesis")
    elif args.from_raw:
        # Load content from raw extractions and combine
        logging.info("\n--- Loading Raw Extractions ---")
        all_extractions = load_raw_extractions()
        
        if not all_extractions:
            logging.error("No raw extractions found. Run extraction first.")
            return
        
        # Combine all content
        logging.info("\n--- Combining Content ---")
        combined_content = combine_content(all_extractions)
        
        # Save intermediate combined content
        intermediate_path = CONFIG["output"].replace(".md", "_combined.md")
        save_output(combined_content, intermediate_path)
    else:
        # Run full pipeline
        all_extractions = {}
        
        for category_name, category_config in CONFIG["categories"].items():
            logging.info(f"\n--- Processing {category_name} ---")
            
            category_type = category_config.get("type", "")
            
            if category_type in ["web_tarot", "web_base", "web_angels"]:
                # Process web content
                extracted = process_web_extraction(category_name, category_config)
            elif category_type == "pdf_tarot":
                # Process PDF content
                extracted = process_pdf_extraction(category_name, category_config)
            elif category_type == "local_files":
                # Process local files
                extracted = process_local_files(category_name, category_config)
            else:
                # Process image content (original functionality)
                extracted = process_category(
                    category_config["path"],
                    category_name,
                    category_config["type"],
                    category_config["prompt"]
                )
            
            if extracted:
                all_extractions[category_name] = extracted
                logging.info(f"Extracted {len(extracted)} items from {category_name}")
            else:
                logging.warning(f"No content extracted from {category_name}")
        
        # Combine all content
        logging.info("\n--- Combining Content ---")
        combined_content = combine_content(all_extractions)
        
        # Save intermediate combined content
        intermediate_path = CONFIG["output"].replace(".md", "_combined.md")
        save_output(combined_content, intermediate_path)
    
    # Generate final synthesis
    logging.info("\n--- Generating Final Synthesis ---")
    final_synthesis = generate_synthesis(combined_content)
    
    if final_synthesis:
        # Save final synthesis
        save_output(final_synthesis, CONFIG["output"])
        logging.info("\n=== Synthesis Complete! ===")
        logging.info(f"Final document saved to: {CONFIG['output']}")
    else:
        logging.error("Failed to generate final synthesis")
        if not args.synthesis_only and not args.from_raw:
            # Save combined content as fallback
            save_output(combined_content, CONFIG["output"])
            logging.info("Saved combined content as fallback")

if __name__ == "__main__":
    main() 