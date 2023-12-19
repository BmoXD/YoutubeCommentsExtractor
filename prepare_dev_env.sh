#!/bin/bash

echo "Script for preparing the development environment for Youtube Scraper"
echo "------------------------------------------------"

# Check if config.ini.template exists in the current working directory
echo "Checking if config.ini.template exists in the current working directory -->"
if test -f "config.ini.template"; then
    echo "exists"
else
    echo "Error: config.ini.template not found in the current working directory"
    exit 1
fi
echo "------------------------------------------------"

# Copy config.ini.template to config.ini if config.ini doesn't exist
echo "Copying config.ini.template to config.ini -->"
if [ ! -f "config.ini" ]; then
    cp config.ini.template config.ini
    if [ $? -eq 0 ]; then
        echo "OK"
    else
        echo "Error copying config.ini.template to config.ini"
        exit 1
    fi
else
    echo "config.ini already exists, skipping copy"
fi
echo "------------------------------------------------"


# Check if log_comments.yaml exists in the current working directory
echo "Checking if log_comments.yaml exists in the current working directory -->"
if test -f "log_comments.yaml"; then
    echo "exists"
else
    echo "Copying log config file from local dev template log_comments.yaml.dev"
    cp log_comments.yaml.dev log_comments.yaml
    if [ $? -eq 0 ]; then echo "OK"; else echo "Problem copying log_comments.yaml file"; exit 1; fi
fi
echo "------------------------------------------------"

# Check if log_migrate_db.yaml exists in the current working directory
echo "Checking if log_migratedb.yaml exists in the current working directory -->"
if test -f "log_migratedb.yaml"; then
    echo "exists"
else
    echo "Copying log config file from local dev template log_migratedb.yaml.dev"
    cp log_migratedb.yaml.dev log_migratedb.yaml
    if [ $? -eq 0 ]; then echo "OK"; else echo "Problem copying log_migratedb.yaml file"; exit 1; fi
fi
echo "------------------------------------------------"

# Get python3 executable location
echo "Getting python3 executable location -->"
python_exec_loc=$(where python)
if [ $? -eq 0 ]; then
    # Extracting the first line
    python_exec_loc=$(echo "$python_exec_loc" | head -n 1)
    echo "OK"
else
    echo "Problem getting python3 exec location"
    exit 1
fi
echo "$python_exec_loc"
echo "------------------------------------------------"

# Run config tests
echo "Running config tests"
$python_exec_loc test_config.py
if [ $? -eq 0 ]; then echo "OK"; else echo "Configuration test FAILED"; exit 1; fi
echo "------------------------------------------------"

echo "You're all ready to go! :]"
echo "To start the scraping Youtube video comments, execute:"
echo "$python_exec_loc get_comments.py"
