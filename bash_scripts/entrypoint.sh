#!/bin/sh

set -e

# update system
apt-get update
apt-get upgrade -y

# install wget and unzip
echo "Installing wget and unzip..."
apt-get install wget unzip -y

# Browser to selenium folders
echo "Setting up browser..."
mkdir -p browser
mkdir -p browser/chrome
# Determine the latest Chromedriver version
CHROMEDRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")

# Download chromedriver
echo "Downloading Chromedriver..."

cd browser/chrome
wget "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"

# extract and move to bin
echo "Extracting Chromedriver..."
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Install google chrome with all dependencies
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Check the installed version of Google Chrome
GOOGLE_CHROME_VERSION=$(google-chrome --version)
echo "Installed Google Chrome version: ${GOOGLE_CHROME_VERSION}"

# Check the installed version of Chromedriver
CHROMEDRIVER_VERSION=$(chromedriver --version)
echo "Installed Chromedriver version: ${CHROMEDRIVER_VERSION}"

#test if chromedriver and google chrome is installed and working
echo "Testing Chromedriver and Google Chrome..."
if chromedriver --version && google-chrome --version > /dev/null; then
    echo "Chromedriver and Google Chrome are installed and working."
else
    echo "Chromedriver and Google Chrome are not installed or not working."
    exit 1
fi

# Clean browser files installers
echo "Cleaning up browser files..."
cd ../../
rm -rf browser/

# Setup alembic
./bash_scripts/setup_alembic.sh

# Install main dependencies with poetry
echo "Installing main dependencies..."
poetry install --only main --no-interaction --no-ansi

# Run the Taskipy tasks for generating new migrations and applying them
echo "Running Alembic migrations..."
poetry run task makemigrations
poetry run task migrate

# Start the FastAPI application
echo "Starting FastAPI application..."
poetry run uvicorn kami_pricing_analytics.interface.api.fastapi.app:app --host 0.0.0.0 --port 8001 --reload --log-level debug
