# Hermetic Synthesis System - 2-Hour Implementation Plan

## 🎯 Simplified Objective

Create **ONE main script** that processes all images in your current structure and generates a complete "Sol em Áries" synthesis document.

## 📁 Work With Current Structure (No Changes Needed)

```
raw_images/
├── zodiac/aries/          # 4 images ✅
├── planets/sun/           # 2 images ✅ 
├── planets-zodiac/sun_aries/  # 2 images ✅
├── angels/aries/          # ADD angel images
└── tarot/aries/           # ADD tarot images
```

## 🚀 Single Script Approach: `hermetic_synthesis.py`

### Core Function Flow
```
1. Load simple config (hardcoded or JSON)
2. Process all images in batch by directory
3. Combine extracted content
4. Generate final synthesis
5. Save complete document
```

### Script Structure (60 minutes)

#### Part 1: Configuration (5 minutes)
- Simple dictionary with paths and expected content
- Hardcode the structure for "sol_em_aries"
- No complex YAML needed

#### Part 2: Batch Image Processor (20 minutes)
- Enhance your existing `image_transcriber.py`
- Add directory-aware processing
- Process all images in each category at once
- Generate one markdown file per category

#### Part 3: Content Combiner (15 minutes)
- Simple function to read all extracted markdown files
- Basic content validation (file exists, not empty)
- Combine into structured sections

#### Part 4: Synthesis Generator (15 minutes)
- Use your existing `astro_synth.py` approach
- Create one comprehensive prompt
- Generate final synthesis document

#### Part 5: Output Handler (5 minutes)
- Save final document
- Basic logging
- Simple error reporting

## 🔧 Implementation Steps

### Step 1: Prepare Content (15 minutes)
1. Add missing angel images to `angels/aries/` (if empty, return mock content)
2. Add missing tarot images to `tarot/aries/` (if empty, return mock content)
3. Verify all directories have content (if empty, return mock content)

### Step 2: Create Main Script (45 minutes)

**Key Functions Needed:**
```python
def process_category(category_path, content_type):
    """Process all images in a category directory"""
    
def extract_content(image_path, content_type):
    """Extract content from single image with type-specific prompt"""
    
def combine_content(extracted_files):
    """Combine extracted content into structured sections"""
    
def generate_synthesis(combined_content):
    """Generate final comprehensive synthesis"""
    
def main():
    """Run complete pipeline"""
```

### Step 3: Configuration (15 minutes)

**Simple Config Dictionary:**
```python
CONFIG = {
    "project": "sol_em_aries",
    "base_path": "raw_images",
    "categories": {
        "zodiac": {"path": "zodiac/aries", "type": "sign"},
        "planet": {"path": "planets/sun", "type": "planet"},
        "synthesis": {"path": "planets-zodiac/sun_aries", "type": "synthesis"},
        "angels": {"path": "angels/aries", "type": "angel"},
        "tarot": {"path": "tarot/aries", "type": "tarot"}
    },
    "output": "sol_em_aries_synthesis.md"
}
```

### Step 4: Processing Logic (30 minutes)

**Processing Order:**
1. **Zodiac** → Extract Aries characteristics
2. **Planet** → Extract Sun characteristics  
3. **Synthesis** → Extract Sol em Aries base content
4. **Angels** → Extract individual angel profiles
5. **Tarot** → Extract individual card meanings
6. **Combine** → Merge all content into sections
7. **Synthesize** → Generate final comprehensive document

### Step 5: Testing and Refinement (15 minutes)

**Quick Validation:**
- Run on current structure
- Check output quality
- Fix immediate issues
- Generate final document

## 📝 Simple Synthesis Template

```markdown
# Sol em Áries - Síntese Hermética

## Fundamentos Astrológicos

### O Signo de Áries
[Zodiac content]

### O Planeta Sol
[Planet content]

### Sol em Áries
[Synthesis session content]

## Correspondências Cabalísticas

### Anjos de Áries
[Angel profiles]

## Correspondências do Tarô

### Cartas Associadas
[Tarot meanings]

## Síntese Hermética Completa

[Integrated synthesis combining all elements]
```

## ⚡ Execution Plan (2 Hours Total)

### Hour 1: Setup and Core Development
- **0-15 min**: Prepare missing images and validate structure
- **15-45 min**: Create main script with core functions
- **45-60 min**: Implement extraction and combination logic

### Hour 2: Integration and Output
- **60-90 min**: Implement synthesis generation
- **90-105 min**: Test and debug pipeline
- **105-120 min**: Generate final Sol em Áries document

## 🎯 Minimal Viable Product

**Input**: Current directory structure with all images
**Output**: Single comprehensive markdown document
**Features**: 
- Batch image processing
- Content combination
- Basic synthesis generation
- Error logging

## 🚫 What to Skip (For Now)

- Complex configuration systems
- Advanced quality control
- Multiple model comparisons
- Detailed error recovery
- Performance optimization
- Complex templates
- Metadata tracking

## ✅ Success Criteria

1. **Script runs without errors** on your current structure
2. **Processes all image categories** (zodiac, planet, synthesis, angels, tarot)
3. **Generates readable synthesis** with all content integrated
4. **Produces final markdown** ready for review
5. **Takes less than 10 minutes** to execute complete pipeline

## 🔧 Code Reuse Strategy

**Leverage existing scripts:**
- Use `image_transcriber.py` extraction logic
- Adapt `astro_synth.py` synthesis approach
- Use `utils.py` token counting
- Keep existing API configuration

**New additions:**
- Directory batch processing
- Content combination logic
- Simple synthesis template
- Output formatting

This simplified approach gets you a working hermetic synthesis system in 2 hours that can immediately process your "Sol em Áries" content and be easily extended later.