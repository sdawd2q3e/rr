#!/usr/bin/env python3
"""
Demo script for GeyserMC PackConverter
Shows what the converter can do with actual results
"""

import os
import json
from pathlib import Path

def analyze_converted_pack(pack_dir):
    """Analyze a converted pack to show what was created"""
    pack_path = Path(pack_dir)
    
    if not pack_path.exists():
        print(f"❌ Pack directory not found: {pack_dir}")
        return
        
    print(f"📦 Analyzing converted pack: {pack_path.name}")
    print("=" * 60)
    
    # Check manifest
    manifest_file = pack_path / "manifest.json"
    if manifest_file.exists():
        with open(manifest_file) as f:
            manifest = json.load(f)
        print(f"✅ Pack Name: {manifest['header']['name']}")
        print(f"✅ Description: {manifest['header']['description']}")
        print(f"✅ UUID: {manifest['header']['uuid']}")
    
    # Count files
    textures_count = len(list((pack_path / "textures").rglob("*.png"))) if (pack_path / "textures").exists() else 0
    models_count = len(list((pack_path / "models" / "entity").glob("*.geo.json"))) if (pack_path / "models" / "entity").exists() else 0
    animations_count = len(list((pack_path / "animations").glob("*.json"))) if (pack_path / "animations").exists() else 0
    render_controllers_count = len(list((pack_path / "render_controllers").glob("*.json"))) if (pack_path / "render_controllers").exists() else 0
    
    print(f"📊 Conversion Results:")
    print(f"   🖼️  Textures: {textures_count}")
    print(f"   🎨 Geometry files: {models_count}")
    print(f"   🎬 Animations: {animations_count}")  
    print(f"   🎮 Render controllers: {render_controllers_count}")
    
    # Check Geyser mappings
    geyser_file = pack_path / "geyser_mappings.json"
    if geyser_file.exists():
        with open(geyser_file) as f:
            mappings = json.load(f)
        
        total_items = sum(len(items) for items in mappings.get("items", {}).values())
        unique_base_items = len(mappings.get("items", {}))
        
        print(f"🔧 Geyser Mappings:")
        print(f"   📋 Base items: {unique_base_items}")
        print(f"   🎯 Total custom variants: {total_items}")
        
        # Show some examples
        print(f"📝 Example mappings:")
        for base_item, variants in list(mappings.get("items", {}).items())[:3]:
            print(f"   {base_item}: {len(variants)} variants")
            for variant in variants[:2]:
                cmd = variant.get("custom_model_data", "?")
                name = variant.get("display_name", "Unknown")
                print(f"     └─ CMD {cmd}: {name}")
            if len(variants) > 2:
                print(f"     └─ ... and {len(variants) - 2} more")
    
    print()

def main():
    """Demo the converted packs"""
    print("🎮 GeyserMC PackConverter - Results Demo")
    print("=" * 60)
    
    converted_dir = Path("converted_packs")
    if not converted_dir.exists():
        print("❌ No converted packs found. Run the converter first!")
        print("   python3 geyser_pack_converter.py . --convert-all")
        return
    
    # Find all converted pack directories
    pack_dirs = [d for d in converted_dir.iterdir() if d.is_dir() and d.name.endswith("_bedrock")]
    
    if not pack_dirs:
        print("❌ No Bedrock pack directories found in converted_packs/")
        return
    
    print(f"📦 Found {len(pack_dirs)} converted packs:\n")
    
    for pack_dir in pack_dirs:
        analyze_converted_pack(pack_dir)
    
    # Show .mcpack files
    mcpack_files = list(converted_dir.glob("*.mcpack"))
    print(f"📱 Ready-to-use .mcpack files: {len(mcpack_files)}")
    for mcpack in mcpack_files:
        size_mb = mcpack.stat().st_size / (1024 * 1024)
        print(f"   📦 {mcpack.name} ({size_mb:.1f} MB)")
    
    print("\n🚀 Next Steps:")
    print("1. 📱 Install .mcpack files on Bedrock clients")
    print("2. 🔧 Copy geyser_mappings.json to your Geyser server")
    print("3. 🔄 Restart your server")
    print("4. 🎉 Enjoy cross-platform resource packs!")

if __name__ == "__main__":
    main()