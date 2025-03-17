# Hermetism

A comprehensive guide to Hermetic knowledge.

## Setup

Run the setup script to install all dependencies:

```bash
./setup.sh
```

This will:
- Install uv (Python package manager)
- Install mdBook (if not already installed)
- Create a Python virtual environment
- Install Python dependencies

## Using mdBook

To build and serve the documentation locally:

```bash
mdbook serve
```

This will start a local server at http://localhost:3000 where you can view the documentation.

To build the documentation without serving:

```bash
mdbook build
```

The output will be in the `book` directory.

## Project Structure

- `src/`: Source files for the mdBook documentation
- `theme/`: Custom CSS and JavaScript for the documentation
- `data/`: Data files for the project