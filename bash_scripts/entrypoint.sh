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

# Check if Chromedriver is installed and if the latest version is available
CHROMEDRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
if [ chromedriver --version ]; then
    echo "Chromedriver is already installed."
else
    echo "Chromedriver is not installed. Installing Chromedriver version: ${CHROMEDRIVER_VERSION}"
    echo "Downloading Chromedriver version: ${CHROMEDRIVER_VERSION}..."
    cd browser/chrome
    wget "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
    # extract and move to bin
    echo "Extracting Chromedriver..."
    unzip chromedriver_linux64.zip
    mv chromedriver /usr/local/bin/
    chmod +x /usr/local/bin/chromedriver
fi 

# Google Chrome installation

# Check if Google Chrome is installed
echo "Checking if Google Chrome is installed..."
if google-chrome --version > /dev/null; then
    echo "Google Chrome is already installed."
else
    echo "Google Chrome is not installed., Installing Google Chrome..."
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    apt-get install -y ./google-chrome-stable_current_amd64.deb

fi

# Check the installed version of Google Chrome
GOOGLE_CHROME_VERSION=$(google-chrome --version)
if [ "$GOOGLE_CHROME_VERSION" ]; then
    echo "Google Chrome Version: ${GOOGLE_CHROME_VERSION} is successfull installed."
else
    echo "Google Chrome is not installed."
    exit 1
fi

# Check the installed version of Chromedriver
CHROMEDRIVER_VERSION=$(chromedriver --version)
echo "Installed Chromedriver version: ${CHROMEDRIVER_VERSION}"
if [ "$CHROMEDRIVER_VERSION" ]; then
    echo "Chromedriver Version: ${CHROMEDRIVER_VERSION} is successfull installed."
else
    echo "Chromedriver is not installed."
    exit 1
fi


# Clean browser files installers
echo "Cleaning up browser files..."
cd ../../
rm -rf browser/

# Install main dependencies with poetry
echo "Installing main dependencies..."
poetry install --only main --no-interaction --no-ansi

echo "Applying database migrations if exists..."

echo "Creating migrations"
poetry run task makemigrations -m "Initial migration"

poetry run task migrate || { echo "Database migration failed"; exit 1; }

# Start the FastAPI application
echo "Starting FastAPI application..."
poetry run uvicorn kami_pricing_analytics.interface.api.fastapi.app:app --host 0.0.0.0 --port 8001 --reload --log-level debug
