# Materials Workspace Feature

## Overview

The Materials Workspace is a centralized hub for managing materials and their extractions across all your hermetic projects. This powerful feature enables you to:

- **Manage materials independently** of specific projects
- **Create multiple extractions** per material with different configurations
- **Reuse extractions** across different projects for synthesis
- **Import existing materials** from all your projects automatically

## Key Features

### 1. Centralized Material Management
- Upload and organize materials (PDFs, images, URLs, YouTube videos) in one place
- Tag materials for easy organization and search
- Preview materials directly in the workspace
- Delete materials and their associated extractions

### 2. Multiple Extractions per Material
- Create different extractions from the same material using various methods:
  - Different page ranges for PDFs
  - Different extraction prompts
  - Different processing methods (text vs. vision for PDFs)
- Store extraction metadata and configuration for reference
- Compare different extraction approaches

### 3. Cross-Project Extraction Reuse
- Access workspace extractions from any project's synthesis phase
- Select and combine extractions from both the current project and workspace
- Mix and match different extraction versions for optimal synthesis results

### 4. Automatic Project Import
- One-click import of all materials and extractions from existing projects
- Preserves original extraction configurations and metadata
- Tags imported materials with their source project for tracking

## Navigation

### Accessing the Materials Workspace

1. Click the **"📚 Materials Workspace"** button in the sidebar (available from any view)
2. The workspace opens with four main sections:
   - **📊 Overview**: Statistics and recent activity
   - **📄 Materials**: Material management and extraction
   - **🔍 Extractions**: Browse and search all extractions
   - **🔄 Import**: Import from existing projects

### Workspace Navigation
- Use the top navigation buttons to switch between sections
- Your current section is highlighted with a primary button style
- The workspace maintains its own state independent of projects

## Usage Guide

### Adding Materials

1. Navigate to the **Materials** section
2. Click **"➕ Add New Material"** to expand the form
3. Choose material type:
   - **File**: Upload PDFs, images, or text files
   - **URL**: Add web page content
   - **YouTube**: Add video transcripts
4. Click the appropriate "Add" button

### Creating Extractions

1. In the **Materials** section, find your material
2. Click **"🔍 Extract"** on the material card
3. Configure extraction settings:
   - For PDFs: Choose pages or use AI vision
   - For URLs: Select content extraction method
   - For YouTube: Choose transcript type
4. Optionally add a custom extraction prompt
5. Click **"🔍 Extract"** to process

### Using Extractions in Synthesis

1. Open any project and navigate to the **Synthesis phase**
2. Click the **"🔍 Materials Workspace"** tab
3. Search or browse available extractions
4. Select extractions using checkboxes
5. Selected extractions will be included in your synthesis

### Managing Tags

1. Click **"👁️ View"** on any material
2. Expand the **"🏷️ Tags"** section
3. Edit tags as comma-separated values
4. Click **"Update Tags"** to save

## Technical Details

### Storage Structure

```
materials_workspace/
├── materials/
│   ├── mat_[id].json     # Material metadata
│   └── mat_[id].bin      # Binary data (for files)
├── extractions/
│   └── ext_[id].json     # Extraction content and config
└── workspace_index.json  # Central index of all items
```

### Material Types Supported

- **PDF Files**: Text extraction with page selection, AI vision for scanned PDFs
- **Images**: AI vision extraction with custom prompts
- **Text Files**: Direct text extraction
- **URLs**: Web scraping with configurable content selection
- **YouTube**: Transcript extraction (manual/auto-generated)

### Extraction Configuration

Each extraction stores:
- Source material reference
- Extraction method and parameters
- Custom prompts (if used)
- Creation timestamp
- Word and character counts
- Optional metadata/notes

## Best Practices

1. **Organize with Tags**: Use consistent tagging conventions (e.g., "source:book-name", "topic:alchemy")
2. **Multiple Extractions**: Create different extractions for different purposes (summary vs. detailed)
3. **Descriptive Notes**: Add metadata notes to extractions for future reference
4. **Regular Imports**: Periodically import from projects to keep workspace current
5. **Clean Up**: Delete unused materials and extractions to maintain performance

## Benefits

- **Efficiency**: Avoid re-uploading and re-processing the same materials
- **Flexibility**: Try different extraction approaches without affecting projects
- **Consistency**: Use the same high-quality extractions across multiple syntheses
- **Organization**: Central location for all your hermetic research materials
- **Experimentation**: Test different extraction methods and prompts easily 