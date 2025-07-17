#!/bin/bash
# Simple conversion script for the resource packs in this repository

echo "🎮 GeyserMC PackConverter - Auto Converter"
echo "=========================================="

# Make the Python script executable
chmod +x geyser_pack_converter.py

# Create output directory
mkdir -p converted_packs

echo "📦 Converting all resource packs in the repository..."

# Convert all ZIP files in the current directory
python3 geyser_pack_converter.py . --convert-all --output converted_packs

echo ""
echo "✅ Conversion completed!"
echo "📁 Check the 'converted_packs' directory for your Bedrock resource packs"
echo "🔧 Use the geyser_mappings.json files with your GeyserMC server"
echo ""
echo "Usage with GeyserMC:"
echo "1. Copy the .mcpack files to your Bedrock client"
echo "2. Copy the geyser_mappings.json to your Geyser plugin folder"
echo "3. Restart your server and enjoy cross-platform resource packs!"