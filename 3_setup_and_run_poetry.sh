# Install dependencies
echo '>>> poetry install'
poetry install

# Source variables
source ~/export_variables.sh

# Start the application
echo '>>> start poetry'
poetry run start