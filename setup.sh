#!/bin/bash

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add uv to PATH for this session
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install mdBook if not already installed
if ! command -v mdbook &> /dev/null; then
    echo "Installing mdBook..."
    # Check if cargo is installed
    if ! command -v cargo &> /dev/null; then
        echo "Cargo not found. Installing Rust and Cargo using pacman..."
        sudo pacman -S --noconfirm rust
    fi
    
    # Ensure Cargo bin directory is in PATH
    if [[ ":$PATH:" != *":$HOME/.cargo/bin:"* ]]; then
        echo "Adding ~/.cargo/bin to PATH for this session"
        export PATH="$HOME/.cargo/bin:$PATH"
        
        # Add to shell profile if not already there
        if ! grep -q "export PATH=\"\$HOME/.cargo/bin:\$PATH\"" ~/.bashrc; then
            echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
            echo "Added ~/.cargo/bin to PATH permanently in ~/.bashrc"
        fi
        
        if [ -f ~/.zshrc ] && ! grep -q "export PATH=\"\$HOME/.cargo/bin:\$PATH\"" ~/.zshrc; then
            echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
            echo "Added ~/.cargo/bin to PATH permanently in ~/.zshrc"
        fi
    fi
    
    cargo install mdbook
    echo "mdBook installed successfully!"
fi

# Create virtual environment and install dependencies in one go
uv venv --python=3.13 .venv
source .venv/bin/activate

# Install dependencies from pyproject.toml
uv pip install -r pyproject.toml

echo "Setup completed successfully!" 
