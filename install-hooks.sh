#!/bin/bash

# Make hooks directory in .git if not exists
mkdir -p .git/hooks

# Copy all custom hooks from hooks/ directory to .git/hooks
cp hooks/* .git/hooks/

# Ensure the hooks are executable
chmod +x .git/hooks/*
