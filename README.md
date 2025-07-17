# GeyserMC PackConverter

[![Language: Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![GeyserMC Compatible](https://img.shields.io/badge/GeyserMC-Compatible-green.svg)](https://geysermc.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Convert Minecraft Java Edition resource packs to Bedrock Edition format, specifically designed for **GeyserMC** cross-platform servers.

## 🎯 What This Does

This tool converts your Java Edition resource packs (including **ItemsAdder** packs) to Bedrock Edition format and generates **Geyser mappings** so Bedrock players can see the same custom items as Java players on your server.

## 🚀 Quick Start

### Simple Auto-Conversion
```bash
# Convert all resource packs in this repository
chmod +x convert_all.sh
./convert_all.sh
```

### Manual Conversion
```bash
# Convert a single pack
python3 geyser_pack_converter.py your_pack.zip

# Convert all packs in a directory
python3 geyser_pack_converter.py . --convert-all

# Specify output directory
python3 geyser_pack_converter.py my_pack.zip --output /path/to/output
```

## 📁 What You Get

After conversion, you'll find:

```
converted_packs/
├── YourPack_bedrock/           # Bedrock resource pack folder
│   ├── manifest.json           # Bedrock pack manifest
│   ├── textures/               # Converted textures
│   ├── models/entity/          # Bedrock geometry files
│   ├── animations/             # Item animations
│   └── geyser_mappings.json    # ⭐ GeyserMC mappings
└── YourPack_bedrock.mcpack     # Ready-to-use Bedrock pack
```

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

### "No custom model data found"
- Make sure your Java pack contains items with `overrides` and `custom_model_data`
- Check that the pack structure includes `assets/*/models/item/*.json`

### "Model file not found"
- Ensure all referenced models exist in the pack
- Check for correct namespace formatting in model references

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