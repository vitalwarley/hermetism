import os
import json
import argparse
import logging
from openai import OpenAI
from dotenv import load_dotenv

from utils import count_tokens

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('astrology.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('OPENROUTER_API_KEY')
)
if not os.getenv('OPENROUTER_API_KEY'):
    logging.error("OPENROUTER_API_KEY not found in environment variables")

# Define models to use
MODELS = {
    # 'claude_3_7_sonnet': 'anthropic/claude-3.7-sonnet',
    'gpt4.1': 'openai/gpt-4.1',
    # 'claude_3_7_sonnet_thinking': 'anthropic/claude-3.7-sonnet:thinking',
}

def load_astrological_point_data(point_name):
    """Load data for an astrological point from the raw files.
    
    Args:
        point_name: Name of the astrological point (e.g., 'ascendente', 'meio_do_ceu')
        
    Returns:
        str: Content of the point's markdown file
    """
    logging.info(f"Loading data for astrological point: {point_name}")
    file_path = os.path.join('src', 'astrology', 'raw', 'planets', 'others', f"{point_name}.md")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logging.info(f"Successfully loaded data for {point_name}")
        return content
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Error loading data for {point_name}: {str(e)}")
        return None

def load_zodiac_signs_data(zodiac_dir=None):
    """Load data for all zodiac signs from the specified directory.
    
    Args:
        zodiac_dir: Directory containing zodiac sign files
        
    Returns:
        dict: Dictionary with sign names as keys and content as values
    """
    if not zodiac_dir:
        logging.info("No zodiac directory specified, skipping zodiac data loading")
        return {}
    
    logging.info(f"Loading zodiac signs data from: {zodiac_dir}")
    zodiac_data = {}
    
    try:
        for filename in os.listdir(zodiac_dir):
            if filename.endswith('.md'):
                sign_name = os.path.splitext(filename)[0]
                file_path = os.path.join(zodiac_dir, filename)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    zodiac_data[sign_name] = f.read()
                
        logging.info(f"Successfully loaded data for {len(zodiac_data)} zodiac signs")
        return zodiac_data
    except Exception as e:
        logging.error(f"Error loading zodiac signs data: {str(e)}")
        return {}

def load_synthesis_prompt_template():
    """Load the prompt template for planet synthesis."""
    logging.info("Loading planet synthesis prompt template")
    try:
        with open(os.path.join('src', 'prompts', 'planet_synthesis_others.md'), 'r', encoding='utf-8') as f:
            template = f.read()
        logging.info("Successfully loaded synthesis template")
        return template
    except FileNotFoundError:
        logging.error("Synthesis prompt template file not found")
        return None
    except Exception as e:
        logging.error(f"Error loading synthesis template: {str(e)}")
        return None

def create_prompt(point_name, point_data, template, zodiac_data=None):
    """Create a prompt for the LLM to analyze the astrological point.
    
    Args:
        point_name: Name of the astrological point
        point_data: Content of the point's markdown file
        template: Prompt template for synthesis
        zodiac_data: Optional dictionary containing zodiac sign data
        
    Returns:
        str: The complete prompt for the LLM
    """
    logging.info(f"Creating prompt for point: {point_name}")
    
    # Extract just the name without file extension for display
    display_name = point_name.replace('_', ' ').title()
    
    # Base prompt with point data
    prompt = f"""# Análise do Ponto Astrológico: {display_name}

Dados do ponto astrológico:
{point_data}
"""

    # Add zodiac sign data if available
    if zodiac_data and len(zodiac_data) > 0:
        prompt += "\n## Dados dos Signos do Zodíaco:\n"
        for sign_name, sign_data in zodiac_data.items():
            display_sign = sign_name.replace('_', ' ').title()
            prompt += f"\n### {display_sign}:\n{sign_data}\n"
    
    # Add template instructions
    prompt += f"""
Utilize o template abaixo para criar uma síntese completa deste ponto astrológico com todos os 12 signos do zodíaco:

{template}

É essencial manter a estrutura e formatação exatas do template acima, incluindo:
1. Todas as seções e subseções na ordem correta
2. Análise detalhada do ponto em cada um dos 12 signos do zodíaco
3. Respeito pelo formato de títulos, subtítulos, negrito, itálico e citações
4. Conteúdo em português do Brasil

Sua análise deve integrar completamente as informações fornecidas sobre o ponto astrológico, apresentando uma síntese coerente, profunda e prática que segue o formato do template."""
    
    total_tokens = count_tokens(prompt)
    logging.info(f"Total prompt tokens: {total_tokens}")
    
    return prompt

def get_llm_responses(prompt, point_name, output_dir=None, overwrite_models=None):
    """Get responses from multiple LLMs using OpenRouter.
    
    Args:
        prompt: The prompt to send to the LLMs
        point_name: Name of the astrological point
        output_dir: Optional custom output directory
        overwrite_models: List of model IDs to overwrite. If None, no models will be overwritten.
    """
    logging.info("Getting LLM responses")
    responses = {}
    
    # Create point-specific output directory
    if output_dir is None:
        point_dir = os.path.join('output', 'astrology', 'points', point_name)
    else:
        point_dir = output_dir
    
    os.makedirs(point_dir, exist_ok=True)
    
    # Check which models already have responses
    existing_files = set(os.listdir(point_dir)) if os.path.exists(point_dir) else set()
    existing_models = {f.replace('.md', '') for f in existing_files if f.endswith('.md')}
    
    for model_name, model_id in MODELS.items():
        # Skip if we already have a response and this model is not in overwrite list
        if model_name in existing_models and (overwrite_models is None or model_name not in overwrite_models):
            logging.info(f"Skipping {model_name} - response already exists")
            continue
            
        try:
            logging.info(f"Requesting response from {model_name}")
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}]
            )
            responses[model_name] = response.choices[0].message.content
            logging.info(f"Successfully received response from {model_name}")
        except Exception as e:
            logging.error(f"Error with {model_name}: {str(e)}")
            responses[model_name] = None
    
    return responses

def save_responses(responses, point_name, output_dir=None):
    """Save LLM responses to files.
    
    Args:
        responses: Dictionary of model names and their responses
        point_name: Name of the astrological point
        output_dir: Optional custom output directory. If None, uses default path.
    """
    if output_dir is None:
        output_dir = os.path.join('output', 'astrology', 'points')
    
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Saving responses to {output_dir}")
    
    # Use only point name for the single output file
    output_file = os.path.join(output_dir, f'{point_name}.md')
    
    try:
        # Write all model responses to a single file
        with open(output_file, 'w', encoding='utf-8') as f:
            # For each model, add its response to the file with a header
            for model, response in responses.items():
                if response:
                    # Add response content first, then model info with italics
                    f.write(response + "\n\n" + "---\n\n" + "*Análise gerada pelo modelo: " + model + "*\n\n")
        
        logging.info(f"Saved all responses to {output_file}")
    except Exception as e:
        logging.error(f"Error saving responses: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Process astrological points')
    parser.add_argument('point', help='Name of the astrological point to process (e.g., ascendente, meio_do_ceu)')
    parser.add_argument('--overwrite', nargs='*', help='Models to overwrite (space-separated, or "all" for all models)')
    parser.add_argument('--output-dir', help='Custom output directory path')
    parser.add_argument('--zodiac-dir', help='Directory containing zodiac signs files')
    
    args = parser.parse_args()
    point_name = args.point.lower()
    output_dir = args.output_dir
    zodiac_dir = args.zodiac_dir
    
    logging.info(f"Starting process for astrological point: {point_name}")
    if output_dir:
        logging.info(f"Using custom output directory: {output_dir}")
    if zodiac_dir:
        logging.info(f"Using zodiac signs from directory: {zodiac_dir}")
    
    # Determine which models to overwrite
    overwrite_models = None
    if args.overwrite:
        if 'all' in args.overwrite:
            logging.info("Will overwrite responses for all models")
        else:
            overwrite_models = args.overwrite
            # Validate model names
            invalid_models = [model for model in overwrite_models if model not in MODELS]
            if invalid_models:
                logging.error(f"Invalid model names: {', '.join(invalid_models)}")
                return
            logging.info(f"Will overwrite responses for models: {', '.join(overwrite_models)}")
    
    # Load data for the astrological point
    point_data = load_astrological_point_data(point_name)
    if not point_data:
        logging.error(f"Failed to load data for {point_name}")
        return
    
    # Load zodiac signs data if directory specified
    zodiac_data = load_zodiac_signs_data(zodiac_dir)
    
    # Load synthesis prompt template
    template = load_synthesis_prompt_template()
    if not template:
        logging.error("Failed to load synthesis prompt template")
        return
    
    # Create prompt
    prompt = create_prompt(point_name, point_data, template, zodiac_data)
    
    # Get LLM responses
    responses = get_llm_responses(prompt, point_name, output_dir, overwrite_models)
    
    # Save responses
    save_responses(responses, point_name, output_dir)
    
    logging.info(f"Completed processing for {point_name}")

if __name__ == "__main__":
    main() 