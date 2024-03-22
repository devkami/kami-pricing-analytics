#!/bin/bash

# Function to check if Alembic is installed
check_alembic_installed() {
    poetry show alembic > /dev/null 2>&1
    return $?
}

# Function to check if Alembic is initialized
check_alembic_initialized() {
    if [ -d "./alembic" ] && [ -f "./alembic.ini" ]; then
        return 0
    else
        return 1
    fi
}

# Function to check if env.py is correctly modified for dynamic database settings
check_env_py_modified() {
    # Check if the last line of env.py is "Alembic setup and configuration complete."
    tail -n 1 alembic/env.py | grep -q "# Alembic setup and configuration complete."
    return $?
}

# Function to modify env.py with dynamic database settings
modify_env_py() {
    echo "Modifying env.py for dynamic database settings..."
    
    # Insert the required imports at the beginning of the file, before 'from alembic import context'
    sed -i "1i import os\nimport configparser\nfrom kami_pricing_analytics.data_storage.modes.sql_storage.models import Base\nfrom kami_pricing_analytics.data_storage.settings import (\n    PostgreSQLSettings,\n    SQLiteSettings,\n)\nfrom kami_pricing_analytics.schemas.options import StorageOptions\n" alembic/env.py
    
    # Remove existing block from '# add your model's MetaData object here' until '# ... etc.'
    # Then insert the new dynamic configuration block
    sed -i "/# add your model's MetaData object here/,/# ... etc./c\
# Load storage configuration\n\
storage_config_path = os.path.join('config', 'storage.cfg')\n\n\
storage_config = configparser.ConfigParser()\n\
storage_config.read(storage_config_path)\n\
storage_mode = storage_config.getint('storage', 'MODE')\n\n\
# Dynamically set database settings based on storage mode\n\
if storage_mode == StorageOptions.SQLITE.value:\n\
    database_settings = SQLiteSettings()\n\
elif storage_mode == StorageOptions.POSTGRESQL.value:\n\
    # Ensuring the db_driver is correctly set for PostgreSQLSettings\n\
    database_settings = PostgreSQLSettings(db_driver='postgresql')\n\
else:\n\
    raise ValueError(f\"Unsupported STORAGE_MODE: {storage_mode}\")\n\n\
# Dynamically set the SQLAlchemy URL\n\
config.set_main_option('sqlalchemy.url', database_settings.db_url)\n\n\
target_metadata = Base.metadata\n" alembic/env.py

 echo "# Alembic setup and configuration complete." >> alembic/env.py
}


# Function to check if Taskipy tasks are added
check_taskipy_tasks() {
    grep -q "makemigrations = \"alembic revision --autogenerate" pyproject.toml &&
    grep -q "migrate = \"alembic upgrade head" pyproject.toml
    return $?
}

# Install Alembic if not installed
if ! check_alembic_installed; then
    echo "Installing Alembic..."
    poetry add alembic
fi

# Initialize Alembic if not initialized
if ! check_alembic_initialized; then
    echo "Initializing Alembic..."
    poetry run alembic init alembic
fi

# Check if env.py modifications are needed and apply them
if ! check_env_py_modified; then
    echo "Configuring Alembic for dynamic database settings..."
    modify_env_py
else
    echo "Alembic env.py already configured for dynamic database settings."
fi

# Add Taskipy tasks if not added
if ! check_taskipy_tasks; then
    echo "Adding Taskipy tasks..."
    if grep -q "\[tool.taskipy.tasks\]" pyproject.toml; then
        sed -i "/\[tool.taskipy.tasks\]/a makemigrations = \"alembic revision --autogenerate -m 'auto_migration'\"" pyproject.toml
        sed -i "/\[tool.taskipy.tasks\]/a migrate = \"alembic upgrade head\"" pyproject.toml
    else
        echo -e "\n[tool.taskipy.tasks]\nmakemigrations = \"alembic revision --autogenerate -m 'auto_migration'\"\nmigrate = \"alembic upgrade head\"" >> pyproject.toml
    fi
fi

echo "Alembic setup and configuration complete."
