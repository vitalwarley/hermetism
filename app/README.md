# 🔮 Hermetic Workbench

A modular Streamlit application for transforming esoteric materials into hermetic syntheses using AI.

## ✨ Features

### 📥 Multi-Source Content Extraction
- **Multi-format File Processing**: Support for PDF, images (JPG/PNG), and text files
- **Web Content Scraping**: Extract content from any web page with multiple extraction methods:
  - Main content extraction (smart content detection)
  - Full page extraction
  - Custom CSS selector targeting
- **YouTube Transcription**: Get transcripts from YouTube videos with:
  - Auto-generated transcript support
  - Manual transcript preference
  - Multi-language support
  - Optional content summarization
- **AI-Powered Image Analysis**: Extract text and symbolic elements from images using vision models
- **Intelligent Text Cleaning**: LLM-based text cleaning and structuring with custom context

### 🎯 Advanced Synthesis Capabilities
- **Custom Prompt System**: Create fully customizable synthesis prompts with:
  - Material placeholder substitution (e.g., `{material1}`, `{pdf_content}`)
  - Pre-built template library (Tarot, Hermetic, Astrological, Alchemical)
  - Dynamic placeholder generation from uploaded materials
- **Multiple Synthesis Types**:
  - Tarot Readings with harmonic/disharmonic interpretations
  - Hermetic Synthesis exploring esoteric connections
  - Astrological Analysis with planetary influences
  - Alchemical Interpretation focusing on transformation stages
  - Custom prompts for specialized analysis

### 📊 Enhanced Session Management
- **Automatic Session Saving**: Every synthesis is automatically saved with:
  - Source materials and extraction settings
  - Custom prompts and configurations
  - Generated synthesis content
  - Timestamps and metadata
- **Quality Review System**: Built-in assessment tools with:
  - Multi-metric rating system (Accuracy, Completeness, Clarity, Depth)
  - Review notes and comments
  - Session update tracking
- **Export Options**: 
  - Download syntheses in Markdown format
  - Auto-generated session reports
  - Material preservation for future reference

### 🎨 Modern User Interface
- **Tabbed Input System**: Organized interface with separate tabs for:
  - File uploads with drag-and-drop support
  - URL scraping with validation and options
  - YouTube transcription with language preferences
- **Real-time Material Management**: 
  - Live preview of extracted content
  - Individual material removal
  - File size and metadata display
- **Interactive Configuration**: 
  - PDF page range selection
  - Image extraction prompt customization
  - AI cleaning toggle options

## 🏗️ Architecture

The application follows a modular architecture for better maintainability and extensibility:

```
app/
├── app.py                      # Main application entry point
├── config/
│   └── settings.py            # Configuration and constants
├── services/
│   ├── ai_service.py          # AI interactions (OpenAI/OpenRouter)
│   ├── extraction.py          # Multi-source content extraction
│   └── session.py             # Enhanced session management
├── ui/
│   ├── sidebar.py             # Configuration sidebar
│   ├── input_panel.py         # Multi-tab input interface
│   └── synthesis_panel.py     # Synthesis generation and review
└── utils/
    └── helpers.py             # Common utilities
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenRouter API key (for AI services)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hermetic-workbench
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app/app.py
   ```

## 📋 Dependencies

```txt
streamlit>=1.28.0
openai>=1.3.0
python-dotenv>=1.0.0
PyPDF2>=3.0.0
Pillow>=10.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
youtube-transcript-api>=0.6.0
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key for AI services | Yes |

### Model Configuration

Default models can be changed in `config/settings.py`:

```python
MODEL_VISION = "openai/gpt-4o-mini"      # For image processing
MODEL_SYNTHESIS = "openai/gpt-4.1"       # For text synthesis
```

### Supported Content Sources

- **PDF Files**: Text extraction with optional page range selection
- **Images**: JPG, PNG with OCR and symbolic analysis
- **Text Files**: Plain text files (.txt)
- **Web Pages**: Any HTTP/HTTPS URL with smart content extraction
- **YouTube Videos**: Automatic transcript extraction with language support

## 📖 Usage Guide

### 1. Input Materials

#### File Upload Tab
- Use the file uploader with drag-and-drop support
- Configure extraction options for each file type:
  - **PDF**: Choose page ranges, enable LLM cleaning with context
  - **Images**: Customize extraction prompts for specific content
  - **Text**: Direct import with encoding detection

#### URL Scraping Tab
- Enter any web page URL for content extraction
- Choose extraction method:
  - **Main Content**: Smart detection of primary content
  - **Full Page**: Complete page text extraction
  - **Custom Selector**: Target specific elements with CSS selectors
- Optional AI cleaning and structuring

#### YouTube Transcription Tab
- Enter YouTube video URLs for transcript extraction
- Configure transcript preferences:
  - **Auto**: Use auto-generated transcripts
  - **Manual**: Prefer human-created transcripts
  - **Any**: Accept any available transcript
- Specify language codes (en, es, fr, etc.)
- Optional content summarization

### 2. Create Custom Synthesis Prompts

- **Template Selection**: Choose from pre-built templates:
  - Tarot Reading with comprehensive interpretations
  - Hermetic Synthesis for esoteric connections
  - Astrological Analysis with planetary influences
  - Alchemical Interpretation focusing on transformation
  - Structured Analysis with placeholders
- **Material Placeholders**: Use dynamic placeholders like:
  - `{material1}` - First uploaded material
  - `{pdf_content}` - Specific PDF content
  - `{youtube_transcript}` - YouTube video transcript
- **Custom Prompts**: Write completely custom synthesis instructions

### 3. Generate Synthesis

- Review loaded materials and custom prompt
- Click "🔮 Generate Synthesis" to create analysis
- AI processes all materials according to your prompt
- Results are automatically saved as a session

### 4. Quality Review & Export

- **Rate Synthesis Quality**: Use 5-star rating system for:
  - Accuracy of information
  - Completeness of analysis
  - Clarity of presentation
  - Depth of insights
- **Add Review Notes**: Provide detailed feedback
- **Export Options**: Download as Markdown with full session data
- **Session Management**: All sessions automatically saved with timestamps

## 🔌 Extending the Application

### Adding New Content Sources

1. Update `SUPPORTED_FILE_TYPES` in `config/settings.py`
2. Add extraction logic in `services/extraction.py`
3. Update UI handling in `ui/input_panel.py`
4. Add validation and error handling

### Adding New Synthesis Templates

1. Add prompt template to `SYNTHESIS_PROMPTS` in `config/settings.py`
2. Update template selector in `ui/input_panel.py`
3. Consider placeholder requirements

### Custom AI Models

1. Modify model constants in `config/settings.py`
2. Ensure compatibility with OpenAI API format
3. Test with different content types

## 🧪 Development

### Project Structure

- **`config/`**: Application configuration and constants
- **`services/`**: Business logic and external service integrations
  - `ai_service.py`: AI model interactions and prompt processing
  - `extraction.py`: Multi-source content extraction (files, URLs, YouTube)
  - `session.py`: Session persistence and quality review management
- **`ui/`**: Streamlit UI components
  - `input_panel.py`: Multi-tab input interface with validation
  - `synthesis_panel.py`: Synthesis generation and quality review
  - `sidebar.py`: Configuration and settings panel
- **`utils/`**: Common utilities and helpers

### Key Design Principles

- **Separation of Concerns**: Each module has a single responsibility
- **Extensible Architecture**: Easy to add new content sources and synthesis types
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Session Persistence**: All work is automatically saved and recoverable
- **User Experience**: Intuitive interface with real-time feedback

### Recent Enhancements

- **URL & YouTube Integration**: Full web content extraction capabilities
- **Custom Prompt System**: Flexible synthesis with material placeholders
- **Enhanced Session Management**: Quality reviews and markdown export
- **Improved UI**: Tabbed interface with better validation and feedback

## 📊 Session Data Structure

Sessions are saved as JSON files with comprehensive metadata:

```json
{
  "timestamp": "2024-01-01T12:00:00.000000",
  "custom_prompt": "Your custom synthesis prompt with placeholders...",
  "materials": {
    "document1.pdf": "extracted text content...",
    "webpage_content": "scraped web content...",
    "youtube_transcript": "video transcript content..."
  },
  "synthesis": "generated synthesis content...",
  "metadata": {
    "quality_ratings": {
      "accuracy": 4,
      "completeness": 5,
      "clarity": 4,
      "depth": 5
    },
    "review_notes": "Excellent synthesis with deep insights...",
    "review_timestamp": "2024-01-01T12:30:00.000000"
  }
}
```

Each session also generates a human-readable Markdown file with:
- Formatted timestamp and title
- Complete custom prompt
- All source materials
- Generated synthesis
- Quality review data with star ratings
- Review notes and comments

## 🎯 Future Roadmap

Based on current development priorities:

- **Project Management**: Card-based project organization
- **Enhanced State Management**: Persistent project saving
- **Deployment Options**: Cloud deployment configurations
- **Model Comparison**: Side-by-side synthesis comparison
- **Template Enhancement**: Pre-filled cleaning templates
- **Advanced Analytics**: Synthesis quality tracking over time

---

*Transform wisdom through AI synthesis - Hermetic Workbench* 