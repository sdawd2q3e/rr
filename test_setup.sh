#!/bin/bash

# Quick test to make sure everything works
echo "🧪 Testing GeyserMC PackConverter..."

# Test basic functionality
if python3 --version > /dev/null 2>&1; then
    echo "✅ Python 3 is available"
else
    echo "❌ Python 3 is required but not found"
    exit 1
fi

# Test converter import
if python3 -c "import geyser_pack_converter" 2>/dev/null; then
    echo "✅ Converter module loads correctly"
else
    echo "❌ Error loading converter module"
    exit 1
fi

# Check for input files
zip_files=$(ls *.zip 2>/dev/null | wc -l)
if [ $zip_files -gt 0 ]; then
    echo "✅ Found $zip_files ZIP resource pack files"
else
    echo "⚠️  No ZIP files found to convert"
fi

# Test help
if python3 geyser_pack_converter.py --help > /dev/null 2>&1; then
    echo "✅ Help system works"
else
    echo "❌ Error with help system"
    exit 1
fi

echo ""
echo "🎉 All tests passed! Ready to convert resource packs."
echo ""
echo "Usage:"
echo "  ./convert_all.sh          # Convert all packs"
echo "  python3 demo_results.py   # Show conversion results"