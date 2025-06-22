"""
Predefined extraction prompts for different material types
"""

EXTRACTION_PROMPTS = {
    "General": {
        "Basic Text Extraction": "Extract all text content from this material.",
        "Detailed Analysis": "Extract and analyze all text content, identifying key themes, concepts, and important passages.",
        "Summary Extraction": "Extract the main points and create a concise summary of the content.",
    },
    "Esoteric/Hermetic": {
        "Hermetic Symbols": "Extract all text and identify hermetic symbols, correspondences, and esoteric meanings. Pay special attention to alchemical, astrological, and mystical references.",
        "Ritual Content": "Extract ritual instructions, invocations, and ceremonial procedures. Identify tools, timing, and symbolic elements.",
        "Correspondences": "Extract and organize all correspondences including planetary, elemental, color, number, and symbolic associations.",
        "Sacred Geometry": "Identify and describe geometric patterns, sacred symbols, and their esoteric significance.",
    },
    "Academic": {
        "Research Paper": "Extract the abstract, methodology, findings, and conclusions. Identify key citations and references.",
        "Lecture Notes": "Extract main topics, key points, examples, and important definitions or formulas.",
        "Technical Documentation": "Extract technical specifications, procedures, parameters, and implementation details.",
    },
    "Images": {
        "Text in Image": "Extract all visible text from the image, maintaining the original formatting and layout where possible.",
        "Symbol Description": "Describe all symbols, sigils, and geometric patterns in detail, including their positions and relationships.",
        "Full Description": "Provide a comprehensive description of the image including text, symbols, colors, composition, and any esoteric or symbolic elements.",
        "Tarot/Oracle Card": "Describe the card imagery, symbols, colors, and any text. Include traditional meanings and symbolic interpretations.",
    },
    "Web Content": {
        "Article Extraction": "Extract the main article content, removing navigation, ads, and other non-content elements.",
        "Blog Post": "Extract the blog post content including title, author, date, and main text.",
        "Forum Discussion": "Extract the discussion thread, preserving the conversation structure and participant contributions.",
    },
    "Video/Audio": {
        "Full Transcript": "Provide a complete transcript of all spoken content.",
        "Key Points": "Extract and summarize the main points and key takeaways from the video/audio.",
        "Quotes and Timestamps": "Extract notable quotes with their timestamps for reference.",
    }
}

def get_prompt_categories():
    """Get all prompt categories."""
    return list(EXTRACTION_PROMPTS.keys())

def get_prompts_for_category(category: str):
    """Get all prompts for a specific category."""
    return EXTRACTION_PROMPTS.get(category, {})

def get_all_prompts_flat():
    """Get all prompts as a flat list of tuples (category, name, prompt)."""
    prompts = []
    for category, prompt_dict in EXTRACTION_PROMPTS.items():
        for name, prompt in prompt_dict.items():
            prompts.append((category, name, prompt))
    return prompts 