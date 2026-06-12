#!/bin/bash
echo "Running cmaputils commit script!"

# run the macros before commiting so that any changes will not stop commit
uv run pre-commit run --hook-stage manual cmaputils-macros

read -r -p "Which files would you like to stage? (git add __): " files_to_add
git add "$files_to_add"

read -r -p "Enter your commit message: " git_commit_message
git commit -m "$git_commit_message"
