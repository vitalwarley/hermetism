#!/usr/bin/env python3

import os
import argparse
from pathlib import Path
import base64
import logging
import json
import time
import signal
import requests
from typing import List, Optional, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_transcription.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

# Constants
MODEL_ID_VISION = 'openai/gpt-4o-mini'  # For vision tasks
MODEL_ID_PROCESSING = 'anthropic/claude-3.7-sonnet'  # For text processing
MAX_RETRIES = 3
RETRY_MIN_WAIT = 4
RETRY_MAX_WAIT = 10
REQUEST_TIMEOUT = 30

# Provider routing configuration
PROVIDER_ROUTING = {
    "Anthropic": {
        "priority": 1,
        "fallback": ["Google", "OpenAI"]
    },
    "Google": {
        "priority": 3,
        "fallback": ["Anthropic", "OpenAI"]
    },
    "OpenAI": {
        "priority": 2,
        "fallback": ["Anthropic", "Google"]
    }
}

def count_tokens(text):
    """Simple token counter (placeholder)."""
    # This is a simple approximation, for accurate counting, use tiktoken library
    return len(text.split())

def encode_image_to_base64(image_path: str) -> str:
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_files(directory: str, extensions: List[str] = ['.png', '.jpg', '.jpeg']) -> List[str]:
    """Get unique image files in the specified directory, excluding those with associated .md files."""
    image_files = set()
    md_files = {item.stem for item in Path(directory).rglob('*.md')}
    
    for item in Path(directory).rglob('*'):
        if item.is_file() and item.suffix in extensions and item.stem not in md_files:
            image_files.add(str(item))
    
    return list(image_files)

@retry(stop=stop_after_attempt(MAX_RETRIES), 
       wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT))
def transcribe_image(image_path: str) -> str:
    """Transcribe text from an image using vision model via OpenRouter."""
    logging.info(f"Transcribing image: {image_path}")
    base64_image = encode_image_to_base64(image_path)
    
    if not os.getenv('OPENROUTER_API_KEY'):
        logging.error("OPENROUTER_API_KEY not found in environment variables")
        return "Error: OPENROUTER_API_KEY not found in environment variables"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "HTTP-Referer": "https://github.com/warleydev/image-transcriber",
        "X-Title": "Image Transcriber",
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
                        "text": "Please transcribe any text you see in this image. Return only the transcribed text, nothing else."
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
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            error_message = response.text
            logging.error(f"API request failed: {error_message}")
            return f"Error processing {image_path}: {error_message}"
        
        response_data = response.json()
        if response_data and response_data.get('choices'):
            transcription = response_data['choices'][0]['message']['content']
            logging.info(f"Successfully transcribed image ({count_tokens(transcription)} tokens)")
            return transcription
        else:
            logging.error("Empty response from API")
            return f"Error: Empty response from API for {image_path}"
            
    except Exception as e:
        logging.error(f"Error transcribing image: {str(e)}")
        raise  # Re-raise to trigger retry

@retry(stop=stop_after_attempt(MAX_RETRIES), 
       wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT))
def process_with_llm(text: str, image_name: str) -> str:
    """Process transcribed text with LLM to clean up and preserve content."""
    logging.info(f"Processing transcription for image: {image_name}")
    
    if not text:
        logging.error("No text provided for LLM processing")
        return None
    
    prompt = f"""You are processing text that was transcribed from an image. The transcription may contain errors, artifacts, or formatting issues.

Your task is to:
1. Fix any syntax and grammar issues
2. Remove any artifacts or formatting issues
3. Preserve ALL original content and meaning
4. Maintain the original structure and flow
5. Do not add any new interpretations or analysis
6. Output only the cleaned up text, no other text or commentary

Text to clean up:
{text}"""

    logging.info(f"Sending request to LLM: {count_tokens(prompt)} tokens (transcription is {count_tokens(text)} tokens)")
    
    # Try each provider in order of priority
    for provider, config in sorted(PROVIDER_ROUTING.items(), key=lambda x: x[1]["priority"]):
        try:
            logging.info(f"Attempting with provider: {provider}")
            
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "HTTP-Referer": "https://github.com/vitalwarley/hermetism",
                "X-Title": "Hermetism",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": MODEL_ID_PROCESSING,
                "messages": [{"role": "user", "content": prompt}],
                "provider": {
                    "order": [provider],
                    "allow_fallbacks": False
                }
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                error_message = response.text
                if 'blocked by content filtering policy' in error_message.lower():
                    logging.warning(f"Content blocked by {provider}, trying next provider...")
                    continue
                raise Exception(f"API request failed: {error_message}")
            
            response_data = response.json()
            if response_data and response_data.get('choices'):
                logging.info(f"Successfully processed with provider: {provider}")
                return response_data['choices'][0]['message']['content']
            else:
                logging.warning(f"Empty response from {provider}, trying next provider...")
                continue
                
        except Exception as e:
            error_message = str(e)
            if 'blocked by content filtering policy' in error_message.lower():
                logging.warning(f"Content blocked by {provider}, trying next provider...")
                continue
            logging.warning(f"Provider {provider} failed: {error_message}")
            continue
    
    # If all providers fail, try with default OpenRouter request
    try:
        logging.info("All providers failed, trying with default OpenRouter request")
        
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "HTTP-Referer": "https://github.com/vitalwarley/hermetism",
            "X-Title": "Hermetism",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": MODEL_ID_PROCESSING,
            "messages": [{"role": "user", "content": prompt}]
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
                return response_data['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Default request also failed: {str(e)}")
    
    raise Exception("All providers and default request failed to process the transcription")

def main():
    parser = argparse.ArgumentParser(description='Transcribe and process text from images using LLM models via OpenRouter')
    parser.add_argument('directory', help='Directory containing images to transcribe')
    parser.add_argument('--raw', action='store_true', help='Save raw transcription without processing')
    args = parser.parse_args()

    # Check if OPENROUTER_API_KEY is set
    if 'OPENROUTER_API_KEY' not in os.environ:
        logging.error("OPENROUTER_API_KEY environment variable is not set")
        return

    # Get all image files
    image_files = get_image_files(args.directory)
    
    if not image_files:
        logging.info(f"No image files found in {args.directory}")
        return

    logging.info(f"Found {len(image_files)} image(s) to process...")

    # Set up signal handler for graceful interruption
    def signal_handler(signum, frame):
        logging.warning("Received interrupt signal. Stopping gracefully...")
        exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)

    # Process each image
    for image_path in image_files:
        logging.info(f"Processing {image_path}...")
        
        try:
            # Step 1: Transcribe the image
            transcription = transcribe_image(image_path)
            
            # Create markdown file paths
            md_file = str(Path(image_path).with_suffix('.md'))
            raw_md_file = str(Path(image_path).with_suffix('_raw.md'))
            
            # Step 2: Process the transcription if not raw mode
            if args.raw:
                processed_text = transcription
                logging.info(f"Saving raw transcription (skipping processing)")
            else:
                try:
                    processed_text = process_with_llm(transcription, Path(image_path).name)
                    logging.info(f"Transcription processed successfully")
                except Exception as e:
                    logging.error(f"Failed to process transcription after retries: {str(e)}")
                    processed_text = transcription
                    logging.info(f"Falling back to raw transcription")
            
            # Save to markdown file
            with open(md_file, 'w') as f:
                # Add a header with the original image name
                f.write(f"# Transcription of {Path(image_path).name}\n\n")
                f.write(processed_text)
            
            # Save raw transcription to separate file
            with open(raw_md_file, 'w') as f:
                f.write(f"# Raw Transcription of {Path(image_path).name}\n\n")
                f.write("```\n")
                f.write(transcription)
                f.write("\n```")
            
            logging.info(f"Transcription saved to {md_file}")
            logging.info(f"Raw transcription saved to {raw_md_file}")
            
        except Exception as e:
            logging.error(f"Failed to process {image_path}: {str(e)}")

if __name__ == "__main__":
    main() 