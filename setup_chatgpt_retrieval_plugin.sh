#!/bin/bash

# Create directory for git repositories
mkdir -p ~/git

# Navigate to git directory
cd ~/git

# Clone chatgpt-retrieval-plugin repository
git clone https://github.com/openai/chatgpt-retrieval-plugin.git

# Navigate to the cloned repository
cd chatgpt-retrieval-plugin/

# Install poetry
pip install poetry

# Install poetry script to path
curl -sSL https://install.python-poetry.org | python3 -

# Add poetry to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Refresh bashrc to apply changes
source ~/.bashrc

# Set python version for poetry environment
poetry env use python3.10

# Activate poetry virtual environment
poetry shell

# Install dependencies
poetry install

# Source variables
source ~/export_variables.sh

# Start the application
poetry run start

