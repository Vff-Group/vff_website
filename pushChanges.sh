#!/bin/bash

# GitHub credentials
USERNAME="Vff-Group"
PASSWORD="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"

# Repository URL
REPO_URL="https://github.com/Vff-Group/vff_website.git"

# Function to handle errors
handle_error() {
    echo "Error: $1"
    exit 1
}

# Pull new changes
echo "Pulling new changes..."
git pull || handle_error "Failed to pull changes."

# Prompt for commit message
read -p "Enter commit message: " COMMIT_MSG

# Add changes
echo "Adding changes..."
git add . || handle_error "Failed to add changes."

# Commit changes
echo "Committing changes..."
git commit -m "$COMMIT_MSG" || handle_error "Failed to commit changes."

# Push changes
echo "Pushing changes..."
git push $USERNAME:$PASSWORD@$REPO_URL || handle_error "Failed to push changes."

echo "Operation completed successfully."

