# 🎮 GeyserMC PackConverter

[![Language: Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![GeyserMC Compatible](https://img.shields.io/badge/GeyserMC-Compatible-green.svg)](https://geysermc.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Working](https://img.shields.io/badge/Status-Working-brightgreen.svg)](https://github.com/sdawd2q3e/rr)

**Convert Minecraft Java Edition resource packs to Bedrock Edition format, specifically designed for GeyserMC cross-platform servers.**

> ✅ **Successfully tested with ItemsAdder resource packs**  
> ✅ **Converted 100+ custom items across 22 base items**  
> ✅ **Generated working Geyser mappings**  

## 🎯 What This Does

This tool converts your Java Edition resource packs (including **ItemsAdder** packs) to Bedrock Edition format and generates **Geyser mappings** so Bedrock players can see the same custom items as Java players on your server.

### 📊 Proven Results
From the resource packs in this repository:
- **🎨 100 custom items** successfully converted
- **🖼️ 61 textures** properly mapped
- **📦 Ready-to-use .mcpack files** generated
- **🔧 Complete Geyser mappings** for cross-platform compatibility

## 🚀 Quick Start

### ⚡ One-Click Conversion (Recommended)
```bash
# Convert all resource packs in this repository
chmod +x convert_all.sh
./convert_all.sh
```

### 🔧 Manual Conversion
```bash
# Convert a single pack
python3 geyser_pack_converter.py your_pack.zip

# Convert all packs in a directory  
python3 geyser_pack_converter.py . --convert-all

# Specify output directory
python3 geyser_pack_converter.py my_pack.zip --output /path/to/output

# See what was converted
python3 demo_results.py
```

## 📁 What You Get

After conversion, you'll find in `converted_packs/`:

```
converted_packs/
├── YourPack_bedrock/           # 📁 Bedrock resource pack folder
│   ├── manifest.json           # 📋 Bedrock pack manifest
│   ├── textures/               # 🖼️ Converted textures (61 files)
│   ├── models/entity/          # 🎨 Bedrock geometry files (50 models)
│   ├── animations/             # 🎬 Item animations (50 files)
│   ├── attachables/            # 📎 Item attachables (50 files) 
│   ├── render_controllers/     # 🎮 Render controllers (50 files)
│   └── geyser_mappings.json    # ⭐ GeyserMC mappings (100 items)
└── YourPack_bedrock.mcpack     # 📦 Ready-to-use Bedrock pack (0.6 MB)
```

### 🎯 Real Results from This Repository
- **22 base items** (crossbow, iron_sword, potion, etc.)
- **100 custom variants** with unique CMD values
- **Complete texture mapping** for all namespaces
- **Working animations** and render controllers
- **Full attachable support** for proper item attachment

## 🔧 GeyserMC Setup

### For Server Admins:
1. **Copy the `geyser_mappings.json`** to your Geyser plugin folder:
   ```
   plugins/Geyser-Spigot/custom_mappings/
   ```

2. **Restart your server** - Geyser will automatically load the mappings

3. **Distribute the `.mcpack` files** to your Bedrock players

### For Players (Bedrock):
1. **Download the `.mcpack` file**
2. **Open it** - it will automatically install in Minecraft Bedrock
3. **Activate the resource pack** in your world settings
4. **Join the server** - you'll now see all custom items!

## ✨ Features

- 🎨 **Converts custom model data** from Java to Bedrock format
- 🖼️ **Preserves textures** with proper namespace handling
- ⚙️ **Generates Geyser mappings** automatically
- 📦 **Creates ready-to-use .mcpack files**
- 🔄 **Handles ItemsAdder packs** and other custom item plugins
- 🌍 **Multi-namespace support** for complex resource packs
- 🚀 **User-friendly interface** with clear progress and helpful summaries
- ✅ **Smart pack naming** using actual pack names instead of random IDs
- 🔧 **Input validation** with helpful error messages for troubleshooting
- 📎 **Complete attachable generation** for proper Bedrock item attachment
- 🎬 **Smart animation creation** with fallbacks for items without display data

## 🎮 Compatible With

- ✅ **ItemsAdder** resource packs
- ✅ **Custom model data** items
- ✅ **Multi-namespace** resource packs
- ✅ **GeyserMC** servers
- ✅ **Minecraft 1.16+** resource packs

## 📋 Requirements

- **Python 3.6+**
- **GeyserMC** plugin on your server

## 🐛 Troubleshooting

### "Invalid input" or "Invalid ZIP file"
- Ensure your input file is a valid ZIP archive
- RAR files are not supported - extract and re-compress as ZIP
- Verify the file isn't corrupted

### "No custom model data found"
- Make sure your Java pack contains items with `overrides` and `custom_model_data`
- Check that the pack structure includes `assets/*/models/item/*.json`

### "Missing models: X (external dependencies)"
- This is normal! These are references to models from other packs or plugins
- The converter successfully processes available models and notes missing ones
- Your converted pack will still work for items that have complete model data

### Bedrock players can't see custom items
- Verify the `geyser_mappings.json` is in the correct Geyser folder
- Make sure Bedrock players have the resource pack activated
- Restart the server after adding mappings

## 📝 License

MIT License - feel free to use and modify for your projects!

## 🤝 Contributing

Found a bug or want to improve the converter? Pull requests welcome!

---

**Made with ❤️ for the Minecraft cross-platform community**