#!/usr/bin/env python3

import argparse
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def download_content(url: str, output_path: str, extract_text: bool = False):
    """
    Download content from a URL and save it as a markdown file.
    
    Args:
        url: The URL to download content from
        output_path: Where to save the markdown file
        extract_text: If True, extract readable text from HTML. If False, save raw content.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        
        logging.info(f"Downloading content from {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        content = response.text
        
        if extract_text:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            content = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in content.splitlines())
            content = '\n'.join(line for line in lines if line)
        
        output_file = Path(output_path)
        
        # Ensure the parent directories exist
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # If no extension is provided, add .md
        if not output_file.suffix:
            output_file = output_file.with_suffix('.md')
        
        logging.info(f"Saving content to {output_file}")
        output_file.write_text(content)
        logging.info("Content saved successfully")
        
    except requests.RequestException as e:
        logging.error(f"Error downloading content: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Download content from a URL and save as markdown')
    parser.add_argument('url', help='URL to download content from')
    parser.add_argument('output', help='Output path for the markdown file')
    parser.add_argument('--extract-text', action='store_true', 
                      help='Extract readable text from HTML (useful for web pages)')
    
    args = parser.parse_args()
    download_content(args.url, args.output, args.extract_text)

if __name__ == '__main__':
    main() 