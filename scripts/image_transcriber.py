#!/usr/bin/env python3

import os
import argparse
from pathlib import Path
from openai import OpenAI
import base64
from typing import List, Optional

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

def transcribe_image(client: OpenAI, image_path: str) -> str:
    """Transcribe text from an image using OpenAI's Vision API."""
    base64_image = encode_image_to_base64(image_path)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
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
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error processing {image_path}: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Transcribe text from images using OpenAI Vision API')
    parser.add_argument('directory', help='Directory containing images to transcribe')
    args = parser.parse_args()

    # Check if OPENAI_API_KEY is set
    if 'OPENAI_API_KEY' not in os.environ:
        print("Error: OPENAI_API_KEY environment variable is not set")
        return

    # Initialize OpenAI client
    client = OpenAI()

    # Get all image files
    image_files = get_image_files(args.directory)
    
    if not image_files:
        print(f"No image files found in {args.directory}")
        return

    print(f"Found {len(image_files)} image(s) to process...")

    # Process each image
    for image_path in image_files:
        print(f"Processing {image_path}...")
        transcription = transcribe_image(client, image_path)
        
        # Create markdown file path with same name as image but .md extension
        md_file = str(Path(image_path).with_suffix('.md'))
        
        # Save transcription to markdown file
        with open(md_file, 'w') as f:
            # Add a header with the original image name
            f.write(f"# Transcription of {Path(image_path).name}\n\n")
            f.write(transcription)
        
        print(f"Transcription saved to {md_file}")

if __name__ == "__main__":
    main() 