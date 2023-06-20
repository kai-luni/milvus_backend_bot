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

# Add poetry to PATH so its there after restart, and export it for now in command 2
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source export PATH="$HOME/.local/bin:$PATH"

# Set python version for poetry environment
poetry env use python3.10

# Activate poetry virtual environment
echo 'poetry shell'
poetry shell

# Install dependencies
echo 'poetry install'
poetry install

# Source variables
source ~/export_variables.sh

# Start the application
echo 'start poetry'
poetry run start

