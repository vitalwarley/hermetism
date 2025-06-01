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
            # Save raw extraction
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
            combined.append("\n")
    
    # Angels content
    if "angels" in all_extractions and all_extractions["angels"]:
        combined.append("\n## Correspondências Angélicas\n")
        for key, content in all_extractions["angels"].items():
            combined.append(content)
            combined.append("\n")
    
    # Tarot content
    if "tarot" in all_extractions and all_extractions["tarot"]:
        combined.append("\n## Correspondências do Tarô\n")
        for key, content in all_extractions["tarot"].items():
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

CONTEÚDO EXTRAÍDO:
{combined_content}

TEMPLATE A SEGUIR:

<!--
╔════════════════════════════════════════════════════════════════════════╗
║  TEMPLATE GENÉRICO – SÍNTESE HERMÉTICA (Sol em Áries)                 ║
║  • Texto 100 % em português; nomes angelicais em hebraico             ║
║  • Cada decanato possui 2 cartas menores + 2 anjos correspondentes    ║
║  • 1 Carta da Corte "primária" abrange os dois primeiros decanatos    ║
║  • 1 Carta da Corte "secundária" abrange o terceiro decanato          ║
╚════════════════════════════════════════════════════════════════════════╝
-->

## 0 Instruções de Uso
1. **Integração total** – discuta astrologia + Cabala + Tarô em conjunto.  
2. **Personalize** – troque `Sol`, `Áries`, anjos, cartas e graus conforme necessário.  
3. **Âncoras de realidade** – justifique cada associação (cor, elemento, símbolo).  
4. **Objetivo** – compreender **como** anjos e cartas refletem o arquétipo `Sol-Áries` e **inspiram** soluções para desafios cotidianos (sem instruções rituais).

---

## 1 Fundamentos Astrológicos

### 1.1 O Signo de Áries
<!-- Elemento, modalidade, mitologia, palavras-chave -->

### 1.2 O Planeta Sol
<!-- Função arquetípica, esfera de experiência -->

### 1.3 Sol em Áries
<!-- Pontos fortes, desafios, expressão natal -->

---

## 2 Correspondências Herméticas (Cabala & Tarô)

### 2.1 Cartas Menores e Anjos (6 entradas)

| Decanato | Sub-posição | Graus | Anjo (hebraico) | Carta Menor | Virtudes / Domínios | Salmo | Cor | Perfume / Incenso | Manifestação na Vida* |
|---------|-------------|-------|-----------------|-------------|----------------------|-------|-----|-------------------|-----------------------|
| **1º** | **1A** | <GRAUS> | <ANJO> | <CARTA-MENOR> | <VIRTUDES> | <SALMO> | <COR> | <PERFUME> | _Ex.: "Estimula iniciativa para superar obstáculos profissionais."_ |
|  | **1B** | <GRAUS> | <ANJO> | <CARTA-MENOR> | <VIRTUDES> | <SALMO> | <COR> | <PERFUME> | _Ex.: "Favorece coragem emocional em novos relacionamentos."_ |
| **2º** | **2A** | <GRAUS> | <ANJO> | <CARTA-MENOR> | <VIRTUDES> | <SALMO> | <COR> | <PERFUME> | _Ex.: "Promove visão estratégica em projetos de longo prazo."_ |
|  | **2B** | <GRAUS> | <ANJO> | <CARTA-MENOR> | <VIRTUDES> | <SALMO> | <COR> | <PERFUME> | _Ex.: "Desperta diplomacia durante negociações difíceis."_ |
| **3º** | **3A** | <GRAUS> | <ANJO> | <CARTA-MENOR> | <VIRTUDES> | <SALMO> | <COR> | <PERFUME> | _Ex.: "Apoia resiliência frente a mudanças inesperadas."_ |
|  | **3B** | <GRAUS> | <ANJO> | <CARTA-MENOR> | <VIRTUDES> | <SALMO> | <COR> | <PERFUME> | _Ex.: "Inspira criatividade na solução de problemas complexos."_ |

*Forneça frases-modelo (1–2 linhas) mostrando **como** cada anjo + carta expressa o arquétipo `Sol-Áries` na vida diária.

---

### 2.2 Cartas da Corte

| Escopo | Carta da Corte | Decanatos Abrangidos | Papel Arquetípico | Observações |
|--------|----------------|----------------------|-------------------|-------------|
| **Primária** | <CARTA-CORTE-PRIMÁRIA> | 1º & 2º | Síntese das qualidades iniciais do signo (impulso, desenvolvimento) | _Ex.: "Atua como força motivadora que integra as virtudes dos quatro anjos iniciais."_ |
| **Secundária** | <CARTA-CORTE-SECUNDÁRIA> | 3º | Culmina as qualidades finais (maturação, estabilização) | _Ex.: "Consolida sabedoria prática e resiliência do anjo do 3º decanato."_ |

---

## 3 Síntese Hermética Integrada
<!--
Escreva 1–2 parágrafos que:
• Relacionem Sol, Áries, as 6 cartas menores, 6 anjos e as duas cartas da corte.
• Expliquem padrões de comportamento ou desafios de vida que emergem dessa teia simbólica.
• Incluam 2–3 perguntas reflexivas para analisar o arquétipo no mapa natal ou em problemas concretos.
-->

> _Exemplo de pergunta reflexiva:_ "Quais projetos atuais exigem a visão estratégica sintetizada pela carta da corte primária e seus anjos subjacentes?"

---

IMPORTANTE: Preencha TODOS os campos do template com informações precisas baseadas no conteúdo extraído. Use as informações sobre anjos, cartas e correspondências fornecidas. Mantenha o formato da tabela e a estrutura do template."""
    
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

def main():
    """Run the complete hermetic synthesis pipeline."""
    parser = argparse.ArgumentParser(description='Hermetic Synthesis Pipeline')
    parser.add_argument('--synthesis-only', action='store_true', 
                       help='Run only the synthesis step using existing combined content')
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
    else:
        # Run full pipeline
        all_extractions = {}
        
        for category_name, category_config in CONFIG["categories"].items():
            logging.info(f"\n--- Processing {category_name} ---")
            
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
        if not args.synthesis_only:
            # Save combined content as fallback
            save_output(combined_content, CONFIG["output"])
            logging.info("Saved combined content as fallback")

if __name__ == "__main__":
    main() 