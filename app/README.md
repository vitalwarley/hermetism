# 🔮 Hermetic Workbench

A modular Streamlit application for transforming esoteric materials into hermetic syntheses using AI.

## ✨ Features

- **Multi-format File Processing**: Support for PDF, images (JPG/PNG), and text files
- **AI-Powered Extraction**: Extract text and symbolic elements from images using vision models
- **Intelligent Text Cleaning**: LLM-based text cleaning and structuring
- **Hermetic Synthesis**: Generate comprehensive syntheses with multiple artifact types:
  - Tarot Readings
  - Hermetic Synthesis
  - Astrological Analysis
  - Custom prompts
- **Session Management**: Automatic saving and loading of work sessions
- **Quality Review**: Built-in quality assessment tools
- **Export Options**: Download syntheses in Markdown format

## 🏗️ Architecture

The application follows a modular architecture for better maintainability and extensibility:

```
app/
├── app.py                      # Main application entry point
├── config/
│   └── settings.py            # Configuration and constants
├── services/
│   ├── ai_service.py          # AI interactions (OpenAI/OpenRouter)
│   ├── extraction.py          # File processing services
│   └── session.py             # Session management
├── ui/
│   ├── sidebar.py             # Configuration sidebar
│   ├── input_panel.py         # File upload interface
│   └── synthesis_panel.py     # Synthesis generation UI
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

### Supported File Types

- **PDF**: Text extraction with optional page range selection
- **Images**: JPG, PNG with OCR and symbolic analysis
- **Text**: Plain text files (.txt)

## 📖 Usage Guide

### 1. Upload Materials

- Use the file uploader in the left panel
- Select multiple files of supported types
- Configure extraction options for each file:
  - **PDF**: Choose page ranges, enable LLM cleaning
  - **Images**: Customize extraction prompts
  - **Text**: Direct import

### 2. Configure Synthesis

- Choose artifact type from the sidebar:
  - **Tarot Reading**: Comprehensive tarot interpretation
  - **Hermetic Synthesis**: Esoteric connections and insights
  - **Astrological Analysis**: Planetary and sign influences
  - **Custom**: Use your own synthesis prompt

### 3. Generate Synthesis

- Click "🔮 Generate Synthesis" once materials are loaded
- Review the generated synthesis
- Use export options to save results
- Provide quality ratings for improvement

### 4. Session Management

- Sessions are automatically saved after synthesis
- Each session includes:
  - Source materials
  - Generated synthesis
  - Configuration settings
  - Timestamps and metadata

## 🔌 Extending the Application

### Adding New File Types

1. Update `SUPPORTED_FILE_TYPES` in `config/settings.py`
2. Add processing logic in `services/extraction.py`
3. Update UI handling in `ui/input_panel.py`

### Adding New Synthesis Types

1. Add prompt template to `SYNTHESIS_PROMPTS` in `config/settings.py`
2. Update the artifact type selector in `ui/sidebar.py`

### Custom AI Models

1. Modify model constants in `config/settings.py`
2. Ensure compatibility with OpenAI API format

## 🧪 Development

### Project Structure

- **`config/`**: Application configuration and constants
- **`services/`**: Business logic and external service integrations
- **`ui/`**: Streamlit UI components
- **`utils/`**: Common utilities and helpers

### Key Design Principles

- **Separation of Concerns**: Each module has a single responsibility
- **Dependency Injection**: Services are injected where needed
- **Error Handling**: Consistent error handling across all modules
- **Logging**: Comprehensive logging for debugging and monitoring

### Running Tests

```bash
# Unit tests (when implemented)
python -m pytest tests/

# Linting
flake8 app/
black app/
```

## 📊 Session Data Structure

Sessions are saved as JSON files with the following structure:

```json
{
  "timestamp": "2024-01-01T12:00:00.000000",
  "artifact_type": "Hermetic Synthesis",
  "materials": {
    "document1.pdf": "extracted text content...",
    "image1.jpg": "extracted image content..."
  },
  "synthesis": "generated synthesis content...",
  "metadata": {
    "quality_ratings": {
      "accuracy": 4,
      "completeness": 5,
      "clarity": 4,
      "depth": 5
    }
  }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure `OPENROUTER_API_KEY` is set in your `.env` file
   - Verify the API key is valid and has sufficient credits

2. **File Processing Errors**
   - Check file formats are supported
   - Ensure files are not corrupted
   - Try smaller files if hitting token limits

3. **Import Errors**
   - Verify all dependencies are installed
   - Check Python version compatibility
   - Ensure you're running from the correct directory

### Debug Mode

Enable debug logging by modifying `utils/helpers.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section above
- Review the code documentation in each module

---

**Built with ❤️ for the esoteric community** 