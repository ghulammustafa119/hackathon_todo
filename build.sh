#!/bin/bash

# Build script for the todo application
set -e

echo "Building frontend..."
cd frontend
npm install
npm run build
npm run export  # Export for static serving
cd ..

echo "Building complete!"