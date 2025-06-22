# Material Library Feature

## Overview

The Material Library feature enables cross-project material reuse in the Hermetic Workbench. This allows users to access and import materials (files, URLs, YouTube videos) that have been uploaded and processed in other projects, saving time and avoiding duplicate processing.

## Key Features

### 1. Cross-Project Material Discovery
- Browse all materials from all projects in one centralized location
- Materials are grouped by their source project for easy navigation
- See material metadata including type, size, and processing status

### 2. Smart Import with Extraction Reuse
- Import materials from other projects into your current project
- Choose whether to reuse existing extractions or reprocess the material
- The "Reuse extraction" checkbox is automatically enabled for materials that have been extracted
- If disabled, the material will be imported but marked for re-extraction

### 3. Search and Filter Capabilities
- **Search**: Find materials by name, URL, or even within extracted content
- **Filter by Type**: Quickly filter to show only files, URLs, or YouTube videos
- **Refresh**: Update the library view to see newly added materials

### 4. Material Status Indicators
- **Has data**: Indicates if the material's binary data is available
- **Extracted**: Shows if the material has been processed and extracted

## Usage

### Accessing the Material Library

1. Navigate to the **Upload Phase** (Phase 1)
2. Click on the **"📚 Material Library"** tab
3. The library will automatically scan all projects and display available materials

### Importing Materials

1. Browse or search for the material you want to import
2. Check/uncheck "Reuse extraction" based on your needs:
   - **Checked**: Import with existing extraction (faster, no reprocessing)
   - **Unchecked**: Import material only, will need to extract again
3. Click the **"📥 Import"** button
4. The material will be added to your current project

### Search Functionality

The search feature looks through:
- Material names and display names
- URLs (for web and YouTube materials)
- Extracted content (if available)

This makes it easy to find materials even if you only remember part of the content.

## Technical Details

### Storage Structure

Materials are stored in individual project directories:
```
projects/
├── [project-id]/
│   ├── materials/
│   │   ├── [material-key].json  # Material metadata
│   │   └── [material-key].bin   # Binary data (for files)
│   └── project.json             # Project data including extracted content
```

### Material Import Process

When importing a material:
1. The system loads the material metadata from the source project
2. If binary data exists (for files), it's loaded into memory
3. If "Reuse extraction" is selected and extraction exists, it's imported
4. A new unique key is generated for the imported material
5. The material is added to the current project's session state

### Duplicate Prevention

The system checks for duplicate materials by comparing:
- Material name
- Material type (file, url, youtube)

If a material with the same name and type already exists in the current project, the import is prevented with a warning message.

## Benefits

1. **Time Savings**: Avoid re-uploading and re-processing materials you've already worked with
2. **Consistency**: Reuse the same extractions across projects for consistent results
3. **Flexibility**: Choose whether to reuse extractions or process materials differently
4. **Organization**: See all your materials across projects in one place
5. **Discovery**: Search through all your processed content to find relevant materials 