#!/usr/bin/env python3

import os
import argparse
from pathlib import Path
import shutil

def ensure_directory(path: Path):
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)

def aggregate_md_files(files: list[Path]) -> str:
    """Combine multiple markdown files into one, preserving headers."""
    content = []
    for file in sorted(files):  # Sort to ensure consistent order (_1, _2, etc.)
        with open(file, 'r') as f:
            content.append(f.read().strip())
    return '\n\n'.join(content)

def process_sign_files(sign: str):
    """Process the main sign markdown files."""
    sign_dir = Path('images') / sign / 'sign'
    if not sign_dir.exists():
        print(f"Sign directory not found: {sign_dir}")
        return
    
    # Get all markdown files for the sign
    sign_files = list(sign_dir.glob('*.md'))
    if not sign_files:
        print(f"No markdown files found in {sign_dir}")
        return
    
    # Combine all sign markdown files
    combined_content = aggregate_md_files(sign_files)
    
    # Create target directory and save
    target_file = Path('src') / 'raw' / f'{sign}.md'
    ensure_directory(target_file.parent)
    with open(target_file, 'w') as f:
        f.write(combined_content)
    print(f"Created {target_file}")

def process_tarot_files(sign: str):
    """Process tarot card files."""
    source_dir = Path('images') / sign / 'tarot'
    if not source_dir.exists():
        print(f"Tarot directory not found: {source_dir}")
        return
    
    # Create target directory
    target_dir = Path('src') / 'tarot' / sign
    ensure_directory(target_dir)
    
    # Get all base names (without _1, _2, etc.)
    base_names = set()
    for f in source_dir.glob('*.md'):
        # Handle both formats: 'seven_swords_1.md' and 'prince_swords.md'
        if '_' in f.stem and f.stem[-2] == '_' and f.stem[-1].isdigit():
            base_names.add(f.stem.rsplit('_', 1)[0])
        else:
            base_names.add(f.stem)
    
    # Process each base name
    for base in base_names:
        # Try both numbered and non-numbered files
        files = list(source_dir.glob(f'{base}_*.md'))
        if not files:
            # If no numbered files found, try direct match
            direct_file = source_dir / f'{base}.md'
            if direct_file.exists():
                files = [direct_file]
        
        if not files:
            continue
            
        # Combine content from all files
        combined_content = aggregate_md_files(files)
        
        # Save to target directory
        target_file = target_dir / f'{base}.md'
        with open(target_file, 'w') as f:
            f.write(combined_content)
        print(f"Created {target_file}")

def process_angel_files(sign: str):
    """Process angel files."""
    source_dir = Path('images') / sign / 'angels'
    if not source_dir.exists():
        print(f"Angels directory not found: {source_dir}")
        return
    
    # Create target directory
    target_dir = Path('src') / 'angels' / sign
    ensure_directory(target_dir)
    
    # Get all base names (without _1, _2, etc.)
    base_names = {
        f.stem.rsplit('_', 1)[0] 
        for f in source_dir.glob('*.md')
        if '_' in f.stem and f.stem[-2] == '_' and f.stem[-1].isdigit()
    }
    
    # Process each base name
    for base in base_names:
        # Get all files for this angel
        files = list(source_dir.glob(f'{base}_*.md'))
        if not files:
            continue
            
        # Combine content from all files
        combined_content = aggregate_md_files(files)
        
        # Save to target directory
        target_file = target_dir / f'{base}.md'
        with open(target_file, 'w') as f:
            f.write(combined_content)
        print(f"Created {target_file}")

def main():
    parser = argparse.ArgumentParser(description='Organize and aggregate markdown files from images to src directory')
    parser.add_argument('sign', help='Zodiac sign to process (e.g., aquarius)')
    args = parser.parse_args()
    
    sign = args.sign.lower()
    
    # Process main sign files
    process_sign_files(sign)
    
    # Process angels and tarot
    process_angel_files(sign)
    process_tarot_files(sign)
    
    print(f"Finished processing files for {sign}")

if __name__ == "__main__":
    main() 