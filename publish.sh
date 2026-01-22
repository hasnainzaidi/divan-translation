#!/bin/bash

# Publish Divan-e Kabir to GitHub Pages
# Run this from the divan-translation folder

set -e

echo "Initializing git repository..."
git init

echo "Adding all files..."
git add .

echo "Creating initial commit..."
git commit -m "Initial commit: Divan-e Kabir translation project"

echo "Creating GitHub repository and pushing..."
gh repo create divan-translation --public --source=. --push

echo "Enabling GitHub Pages..."
sleep 2  # Give GitHub a moment to set up the repo
gh repo edit --enable-pages --branch main --path /

echo ""
echo "Done! Your site will be live in 1-2 minutes at:"
gh repo view --json url -q '.url' | sed 's|github.com/|github.io/|; s|github.io/\([^/]*\)/|github.io/\1/|; s|$|/|'
echo ""
echo "You can also check the deployment status at:"
gh repo view --web
