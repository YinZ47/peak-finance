#!/bin/bash
set -e

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Run the application
python -m app.main
