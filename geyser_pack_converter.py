#!/usr/bin/env python3
"""
GeyserMC PackConverter - Convert Java Edition Resource Packs to Bedrock Edition
Compatible with GeyserMC for cross-platform Minecraft servers

Based on the user's request to make a working GeyserMC PackConverter
for converting their ItemsAdder resource packs.
"""

import os
import sys
import json
import zipfile
import shutil
import tempfile
import uuid
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse

__version__ = "1.0.0"
__author__ = "GeyserMC PackConverter"

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def log(message: str, level: str = "INFO"):
    """Enhanced logging with colors"""
    color_map = {
        "INFO": Colors.CYAN,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "DEBUG": Colors.MAGENTA
    }
    color = color_map.get(level, Colors.WHITE)
    print(f"{color}[{level}]{Colors.END} {message}")

class GeyserPackConverter:
    """Main converter class for Java to Bedrock resource pack conversion"""
    
    def __init__(self, input_path: str, output_dir: str = None):
        self.input_path = Path(input_path)
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "converted_packs"
        self.temp_dir = None
        self.java_pack_dir = None
        self.bedrock_pack_dir = None
        self.items_data = []
        self.custom_model_data = {}
        self.missing_models = set()  # Track missing models to avoid spam
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            
    def extract_java_pack(self) -> Path:
        """Extract Java resource pack from ZIP or use directory"""
        if self.input_path.is_file() and self.input_path.suffix.lower() == '.zip':
            log(f"Extracting ZIP file: {self.input_path}")
            self.temp_dir = Path(tempfile.mkdtemp(prefix="java_pack_"))
            
            with zipfile.ZipFile(self.input_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
                
            # Find the root directory with pack.mcmeta
            for root in self.temp_dir.rglob("pack.mcmeta"):
                self.java_pack_dir = root.parent
                break
            else:
                # If no pack.mcmeta found, use the first subdirectory or temp_dir itself
                subdirs = [d for d in self.temp_dir.iterdir() if d.is_dir()]
                self.java_pack_dir = subdirs[0] if subdirs else self.temp_dir
                
        elif self.input_path.is_dir():
            log(f"Using directory: {self.input_path}")
            self.java_pack_dir = self.input_path
        else:
            raise ValueError(f"Invalid input path: {self.input_path}")
            
        log(f"Java pack directory: {self.java_pack_dir}", "SUCCESS")
        return self.java_pack_dir
        
    def create_bedrock_structure(self, pack_name: str) -> Path:
        """Create Bedrock pack directory structure"""
        safe_name = "".join(c for c in pack_name if c.isalnum() or c in (' ', '-', '_')).strip()
        self.bedrock_pack_dir = self.output_dir / f"{safe_name}_bedrock"
        
        # Remove existing directory
        if self.bedrock_pack_dir.exists():
            shutil.rmtree(self.bedrock_pack_dir)
            
        # Create directory structure
        directories = [
            "textures",
            "textures/item",
            "models",
            "models/entity", 
            "animations",
            "attachables",
            "render_controllers",
            "texts"
        ]
        
        for directory in directories:
            (self.bedrock_pack_dir / directory).mkdir(parents=True, exist_ok=True)
            
        log(f"Created Bedrock pack structure: {self.bedrock_pack_dir}", "SUCCESS")
        return self.bedrock_pack_dir
        
    def read_pack_info(self) -> Dict[str, Any]:
        """Read pack.mcmeta for pack information"""
        pack_mcmeta = self.java_pack_dir / "pack.mcmeta"
        
        # Try to get a meaningful name from the original input
        if self.input_path.is_file():
            # Use the ZIP file name without extension
            base_name = self.input_path.stem
        else:
            # Use the directory name
            base_name = self.input_path.name
            
        pack_info = {
            "name": base_name,
            "description": "Converted from Java Edition",
            "format": 6
        }
        
        if pack_mcmeta.exists():
            try:
                with open(pack_mcmeta, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    pack_data = data.get("pack", {})
                    description = pack_data.get("description", pack_info["description"])
                    
                    # If description has a useful name, use it for the pack name
                    if description and description != "Converted from Java Edition" and len(description) < 50:
                        # Clean the description to be filename-safe
                        clean_desc = "".join(c for c in description if c.isalnum() or c in (' ', '-', '_')).strip()
                        if clean_desc and clean_desc.lower() not in ['converted from java edition', 'resource pack']:
                            pack_info["name"] = clean_desc
                    
                    pack_info.update({
                        "description": description,
                        "format": pack_data.get("pack_format", pack_info["format"])
                    })
            except Exception as e:
                log(f"Error reading pack.mcmeta: {e}", "WARNING")
                
        return pack_info
        
    def generate_manifest(self, pack_info: Dict[str, Any]):
        """Generate Bedrock manifest.json"""
        header_uuid = str(uuid.uuid4())
        module_uuid = str(uuid.uuid4())
        
        manifest = {
            "format_version": 2,
            "header": {
                "name": pack_info["name"],
                "description": pack_info["description"], 
                "uuid": header_uuid,
                "version": [1, 0, 0],
                "min_engine_version": [1, 16, 0]
            },
            "modules": [
                {
                    "type": "resources",
                    "uuid": module_uuid,
                    "version": [1, 0, 0]
                }
            ]
        }
        
        manifest_path = self.bedrock_pack_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            
        log("Generated manifest.json", "SUCCESS")
        
    def copy_pack_icon(self):
        """Copy pack icon if available"""
        pack_png = self.java_pack_dir / "pack.png"
        if pack_png.exists():
            shutil.copy2(pack_png, self.bedrock_pack_dir / "pack_icon.png")
            log("Copied pack icon", "SUCCESS")
            
    def scan_custom_model_data(self) -> Dict[str, List[Dict]]:
        """Scan for custom model data in item models"""
        cmd_items = {}
        assets_dir = self.java_pack_dir / "assets"
        
        if not assets_dir.exists():
            log("No assets directory found", "WARNING")
            return cmd_items
            
        # Look for item model files
        for namespace_dir in assets_dir.iterdir():
            if not namespace_dir.is_dir():
                continue
                
            models_dir = namespace_dir / "models" / "item"
            if not models_dir.exists():
                continue
                
            log(f"Scanning namespace: {namespace_dir.name}")
            
            for item_file in models_dir.glob("*.json"):
                try:
                    with open(item_file, 'r', encoding='utf-8') as f:
                        item_data = json.load(f)
                        
                    overrides = item_data.get("overrides", [])
                    item_name = item_file.stem
                    
                    for override in overrides:
                        predicate = override.get("predicate", {})
                        custom_model_data = predicate.get("custom_model_data")
                        model_ref = override.get("model")
                        
                        if custom_model_data is not None and model_ref:
                            if item_name not in cmd_items:
                                cmd_items[item_name] = []
                                
                            cmd_items[item_name].append({
                                "custom_model_data": custom_model_data,
                                "model": model_ref,
                                "namespace": namespace_dir.name if namespace_dir.name != "minecraft" else None
                            })
                            
                except Exception as e:
                    log(f"Error reading {item_file}: {e}", "WARNING")
                    
        total_models = sum(len(models) for models in cmd_items.values())
        log(f"Found {total_models} custom model data entries across {len(cmd_items)} items", "SUCCESS")
        return cmd_items
        
    def convert_java_model_to_bedrock(self, model_path: Path, output_name: str, texture_name: str, base_item: str) -> bool:
        """Convert a Java model to Bedrock geometry"""
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                java_model = json.load(f)
                
            # Extract basic information
            texture_size = java_model.get("texture_size", [16, 16])
            textures = java_model.get("textures", {})
            elements = java_model.get("elements", [])
            display = java_model.get("display", {})
            
            # Create Bedrock geometry
            geometry_id = f"geometry.{output_name}"
            
            # Convert elements to bones/cubes
            bones = []
            if elements:
                bone = {
                    "name": "main",
                    "pivot": [0, 0, 0],
                    "cubes": []
                }
                
                for i, element in enumerate(elements):
                    cube = self.convert_element_to_cube(element)
                    if cube:
                        bone["cubes"].append(cube)
                        
                if bone["cubes"]:
                    bones.append(bone)
                    
            # Create the geometry structure
            bedrock_geometry = {
                "format_version": "1.12.0",
                "minecraft:geometry": [
                    {
                        "description": {
                            "identifier": geometry_id,
                            "texture_width": texture_size[0],
                            "texture_height": texture_size[1],
                            "visible_bounds_width": 2.0,
                            "visible_bounds_height": 2.5,
                            "visible_bounds_offset": [0, 0.75, 0]
                        },
                        "bones": bones
                    }
                ]
            }
            
            # Write geometry file
            geo_file = self.bedrock_pack_dir / "models" / "entity" / f"{output_name}.geo.json"
            with open(geo_file, 'w', encoding='utf-8') as f:
                json.dump(bedrock_geometry, f, indent=2)
                
            # Create render controller
            self.create_render_controller(output_name, texture_name)
            
            # Create animation if display transforms exist, or create default animation
            if display:
                self.create_animation(output_name, display)
            else:
                # Create a default animation for items without display transforms
                self.create_default_animation(output_name)
                
            # Create attachable (this was missing!)
            self.create_attachable(output_name, texture_name, base_item)
            
            return True
            
        except Exception as e:
            log(f"Error converting model {model_path}: {e}", "ERROR")
            return False
            
    def convert_element_to_cube(self, element: Dict) -> Optional[Dict]:
        """Convert Java element to Bedrock cube"""
        try:
            from_pos = element.get("from", [0, 0, 0])
            to_pos = element.get("to", [1, 1, 1])
            faces = element.get("faces", {})
            rotation = element.get("rotation", {})
            
            # Calculate Bedrock coordinates (flip X and Z)
            origin = [
                -to_pos[0] + 8,  # Flip X
                from_pos[1],     # Y stays same
                from_pos[2] - 8  # Adjust Z
            ]
            
            size = [
                to_pos[0] - from_pos[0],  # Width
                to_pos[1] - from_pos[1],  # Height 
                to_pos[2] - from_pos[2]   # Depth
            ]
            
            cube = {
                "origin": origin,
                "size": size,
                "uv": {}
            }
            
            # Convert faces
            for face_name, face_data in faces.items():
                if "uv" in face_data:
                    uv = face_data["uv"]
                    cube["uv"][face_name] = {
                        "uv": [uv[0], uv[1]],
                        "uv_size": [uv[2] - uv[0], uv[3] - uv[1]]
                    }
                    
            # Handle rotation
            if rotation:
                pivot = rotation.get("origin", [8, 8, 8])
                cube["pivot"] = [-pivot[0] + 8, pivot[1], pivot[2] - 8]
                
                angle = rotation.get("angle", 0)
                axis = rotation.get("axis", "y")
                
                rot = [0, 0, 0]
                if axis == "x":
                    rot[0] = -angle
                elif axis == "y": 
                    rot[1] = -angle
                elif axis == "z":
                    rot[2] = angle
                    
                if any(rot):
                    cube["rotation"] = rot
                    
            return cube
            
        except Exception as e:
            log(f"Error converting element: {e}", "WARNING")
            return None
            
    def create_render_controller(self, output_name: str, texture_name: str):
        """Create render controller for the model"""
        render_controller = {
            "format_version": "1.8.0",
            "render_controllers": {
                f"controller.render.{output_name}": {
                    "geometry": f"geometry.{output_name}",
                    "materials": [{"*": "material.default"}],
                    "textures": [texture_name]
                }
            }
        }
        
        rc_file = self.bedrock_pack_dir / "render_controllers" / f"{output_name}.render_controller.json"
        with open(rc_file, 'w', encoding='utf-8') as f:
            json.dump(render_controller, f, indent=2)
            
    def create_animation(self, output_name: str, display: Dict):
        """Create animation from Java display transforms"""
        animation = {
            "format_version": "1.8.0",
            "animations": {
                f"animation.{output_name}": {
                    "loop": True,
                    "bones": {}
                }
            }
        }
        
        # Convert display transforms to bone animations
        for context, transform in display.items():
            bone_name = context.lower()
            bone_data = {}
            
            if "translation" in transform:
                bone_data["position"] = transform["translation"]
            if "rotation" in transform:
                bone_data["rotation"] = transform["rotation"]
            if "scale" in transform:
                bone_data["scale"] = transform["scale"]
                
            if bone_data:
                animation["animations"][f"animation.{output_name}"]["bones"][bone_name] = bone_data
                
        anim_file = self.bedrock_pack_dir / "animations" / f"animation.{output_name}.json"
        with open(anim_file, 'w', encoding='utf-8') as f:
            json.dump(animation, f, indent=2)
            
    def create_attachable(self, output_name: str, texture_name: str, base_item: str):
        """Create attachable file for the custom item"""
        # Generate a unique identifier for the attachable
        attachable_id = f"custom:{output_name}"
        
        # Create the attachable definition
        attachable = {
            "format_version": "1.10.0",
            "minecraft:attachable": {
                "description": {
                    "identifier": attachable_id,
                    "materials": {
                        "default": "entity",
                        "enchanted": "entity_emissive"
                    },
                    "textures": {
                        "default": f"textures/{texture_name}",
                        "enchanted": f"textures/{texture_name}"
                    },
                    "geometry": {
                        "default": f"geometry.{output_name}"
                    },
                    "animations": {
                        "wield": f"animation.{output_name}"
                    },
                    "render_controllers": [
                        f"controller.render.{output_name}"
                    ],
                    "enable_attachables": True
                },
                "components": {
                    "minecraft:render_controllers": {
                        "default": f"controller.render.{output_name}"
                    }
                }
            }
        }
        
        # Write attachable file
        attachable_file = self.bedrock_pack_dir / "attachables" / f"{output_name}.attachable.json"
        with open(attachable_file, 'w', encoding='utf-8') as f:
            json.dump(attachable, f, indent=2)
            
        return attachable_id
            
    def create_default_animation(self, output_name: str):
        """Create a default animation for items without display transforms"""
        default_animation = {
            "format_version": "1.8.0",
            "animations": {
                f"animation.{output_name}": {
                    "loop": True,
                    "bones": {
                        "thirdperson_righthand": {
                            "rotation": [0, -90, 25]
                        },
                        "thirdperson_lefthand": {
                            "rotation": [0, 90, -25]
                        },
                        "firstperson_righthand": {
                            "rotation": [0, -90, 25]
                        },
                        "firstperson_lefthand": {
                            "rotation": [0, 90, -25]
                        }
                    }
                }
            }
        }
        
        anim_file = self.bedrock_pack_dir / "animations" / f"animation.{output_name}.json"
        with open(anim_file, 'w', encoding='utf-8') as f:
            json.dump(default_animation, f, indent=2)
            
    def copy_textures(self):
        """Copy textures from Java to Bedrock format"""
        assets_dir = self.java_pack_dir / "assets"
        if not assets_dir.exists():
            return
            
        copied_count = 0
        for namespace_dir in assets_dir.iterdir():
            if not namespace_dir.is_dir():
                continue
                
            textures_dir = namespace_dir / "textures"
            if not textures_dir.exists():
                continue
                
            # Copy textures maintaining namespace structure
            for texture_file in textures_dir.rglob("*.png"):
                rel_path = texture_file.relative_to(textures_dir)
                
                # Create namespace directory in bedrock pack
                if namespace_dir.name != "minecraft":
                    dest_path = self.bedrock_pack_dir / "textures" / namespace_dir.name / rel_path
                else:
                    dest_path = self.bedrock_pack_dir / "textures" / rel_path
                    
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(texture_file, dest_path)
                copied_count += 1
                
        log(f"Copied {copied_count} textures", "SUCCESS")
        
    def process_custom_models(self, cmd_items: Dict[str, List[Dict]]):
        """Process and convert custom model data items"""
        processed_count = 0
        
        for item_name, models in cmd_items.items():
            log(f"Processing item: {item_name}")
            
            for model_info in models:
                custom_model_data = model_info["custom_model_data"]
                model_ref = model_info["model"]
                namespace = model_info.get("namespace")
                
                # Create unique output name
                output_name = f"{item_name}_cmd{custom_model_data}"
                
                # Find the model file
                model_path = self.find_model_file(model_ref)
                if model_path and model_path.exists():
                    # Extract texture name
                    texture_name = self.extract_texture_name(model_path, namespace)
                    
                    # Convert the model (now includes base_item parameter)
                    success = self.convert_java_model_to_bedrock(model_path, output_name, texture_name, item_name)
                    if success:
                        # Store item data for later use
                        self.items_data.append({
                            "name": output_name,
                            "base_item": item_name,
                            "custom_model_data": custom_model_data,
                            "texture": texture_name,
                            "namespace": namespace or "minecraft"
                        })
                        processed_count += 1
                else:
                    self.missing_models.add(model_ref)
                    
        log(f"Processed {processed_count} custom models", "SUCCESS")
        
        # Report missing models summary instead of individual warnings
        if self.missing_models:
            log(f"Note: {len(self.missing_models)} model files were not found (this is normal for external dependencies)", "WARNING")
        
    def find_model_file(self, model_ref: str) -> Optional[Path]:
        """Find model file from reference"""
        # Parse namespace:path format
        if ":" in model_ref:
            namespace, path = model_ref.split(":", 1)
        else:
            namespace, path = "minecraft", model_ref
            
        # Look in assets
        model_path = self.java_pack_dir / "assets" / namespace / "models" / f"{path}.json"
        return model_path if model_path.exists() else None
        
    def extract_texture_name(self, model_path: Path, namespace: str = None) -> str:
        """Extract primary texture name from model"""
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                model_data = json.load(f)
                
            textures = model_data.get("textures", {})
            
            # Get the first texture or layer0
            texture_ref = textures.get("layer0") or textures.get("0") or next(iter(textures.values()), "")
            
            # Handle namespace in texture reference
            if ":" in texture_ref:
                return texture_ref.split(":", 1)[1]
            else:
                return texture_ref
                
        except Exception:
            return "missing_texture"
            
    def generate_geyser_mappings(self):
        """Generate Geyser mappings file"""
        mappings = {
            "format_version": 2,
            "items": {}
        }
        
        # Group items by base item
        base_items = {}
        for item in self.items_data:
            base_item = f"minecraft:{item['base_item']}"
            if base_item not in base_items:
                base_items[base_item] = []
                
            base_items[base_item].append({
                "custom_model_data": str(item["custom_model_data"]),
                "bedrock_identifier": f"custom:{item['name']}",
                "display_name": item["name"].replace("_", " ").title(),
                "texture": item["texture"],
                "geometry": f"geometry.{item['name']}"
            })
            
        mappings["items"] = base_items
        
        # Write mappings file
        mappings_file = self.bedrock_pack_dir / "geyser_mappings.json"
        with open(mappings_file, 'w', encoding='utf-8') as f:
            json.dump(mappings, f, indent=2)
            
        log(f"Generated Geyser mappings for {len(self.items_data)} items", "SUCCESS")
        
    def create_mcpack(self, pack_name: str) -> Path:
        """Create .mcpack file"""
        mcpack_path = self.output_dir / f"{pack_name}_bedrock.mcpack"
        
        with zipfile.ZipFile(mcpack_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for file_path in self.bedrock_pack_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.bedrock_pack_dir)
                    zip_ref.write(file_path, arcname)
                    
        log(f"Created .mcpack file: {mcpack_path}", "SUCCESS")
        return mcpack_path
        
    def validate_input(self) -> bool:
        """Validate that the input is a valid resource pack"""
        if not self.input_path.exists():
            log(f"Input path does not exist: {self.input_path}", "ERROR")
            return False
            
        if self.input_path.is_file():
            if not self.input_path.suffix.lower() == '.zip':
                log(f"Input file must be a ZIP archive: {self.input_path}", "ERROR")
                if self.input_path.suffix.lower() == '.rar':
                    log("RAR files are not supported. Please extract and re-compress as ZIP.", "ERROR")
                else:
                    log("Supported formats: .zip", "ERROR")
                return False
                
            # Check if ZIP file is valid
            try:
                with zipfile.ZipFile(self.input_path, 'r') as zip_ref:
                    zip_ref.testzip()
            except zipfile.BadZipFile:
                log(f"Invalid ZIP file: {self.input_path}", "ERROR")
                return False
            except Exception as e:
                log(f"Error reading ZIP file: {e}", "ERROR")
                return False
                
        elif self.input_path.is_dir():
            # Check if directory contains any assets
            assets_dir = self.input_path / "assets"
            if not assets_dir.exists():
                log(f"Directory does not contain 'assets' folder: {self.input_path}", "WARNING")
                log("This may not be a valid Minecraft resource pack", "WARNING")
        else:
            log(f"Input path is neither a file nor directory: {self.input_path}", "ERROR")
            return False
            
        return True
        
    def convert(self) -> Tuple[Path, Path]:
        """Main conversion process"""
        log("Starting GeyserMC Pack Conversion", "INFO")
        log("=" * 50)
        
        # Validate input first
        if not self.validate_input():
            raise ValueError(f"Invalid input: {self.input_path}")
        
        # Extract/prepare Java pack
        java_dir = self.extract_java_pack()
        
        # Read pack information
        pack_info = self.read_pack_info()
        
        # Create Bedrock structure
        bedrock_dir = self.create_bedrock_structure(pack_info["name"])
        
        # Generate manifest
        self.generate_manifest(pack_info)
        
        # Copy pack icon
        self.copy_pack_icon()
        
        # Copy textures
        self.copy_textures()
        
        # Scan for custom model data
        cmd_items = self.scan_custom_model_data()
        
        # Process custom models
        if cmd_items:
            self.process_custom_models(cmd_items)
            
            # Generate Geyser mappings
            self.generate_geyser_mappings()
        else:
            log("No custom model data found", "WARNING")
            
        # Create .mcpack
        mcpack_path = self.create_mcpack(pack_info["name"])
        
        # Show helpful summary
        self.show_conversion_summary(pack_info, mcpack_path)
        
        log("=" * 50)
        log("Conversion completed successfully!", "SUCCESS")
        
        return bedrock_dir, mcpack_path
        
    def show_conversion_summary(self, pack_info: Dict[str, Any], mcpack_path: Path):
        """Show a helpful summary of what was converted"""
        log("", "INFO")  # Empty line
        log(f"{Colors.GREEN}{Colors.BOLD}✅ Conversion Summary{Colors.END}", "INFO")
        log(f"📦 Pack: {pack_info['name']}", "INFO")
        log(f"📁 Output: {self.bedrock_pack_dir}", "INFO")
        log(f"📱 Bedrock Pack: {mcpack_path.name}", "INFO")
        
        # Count files
        texture_count = len(list((self.bedrock_pack_dir / "textures").rglob("*.png")))
        model_count = len(list((self.bedrock_pack_dir / "models" / "entity").glob("*.geo.json")))
        animation_count = len(list((self.bedrock_pack_dir / "animations").glob("*.json")))
        attachable_count = len(list((self.bedrock_pack_dir / "attachables").glob("*.json")))
        
        log(f"🖼️  Textures: {texture_count}", "INFO")
        log(f"🎨 Models: {model_count}", "INFO")
        log(f"🎬 Animations: {animation_count}", "INFO")
        log(f"📎 Attachables: {attachable_count}", "INFO")
        log(f"⚙️  Custom Items: {len(self.items_data)}", "INFO")
        
        if self.missing_models:
            log(f"⚠️  Missing models: {len(self.missing_models)} (external dependencies)", "INFO")
        
        log("", "INFO")  # Empty line
        log(f"{Colors.CYAN}{Colors.BOLD}📋 Next Steps:{Colors.END}", "INFO")
        log(f"1. 📱 Install {mcpack_path.name} on Bedrock clients", "INFO")
        log(f"2. 🔧 Copy geyser_mappings.json to your Geyser server", "INFO")
        log(f"3. 🔄 Restart your server", "INFO")
        log(f"4. 🎉 Enjoy cross-platform resource packs!", "INFO")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="GeyserMC PackConverter - Convert Java Edition Resource Packs to Bedrock Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s my_resource_pack.zip
  %(prog)s /path/to/java/pack --output /path/to/output
  %(prog)s resource_pack_folder --convert-all
        """
    )
    
    parser.add_argument("input", help="Input Java resource pack (ZIP file or directory)")
    parser.add_argument("-o", "--output", help="Output directory (default: ./converted_packs)")
    parser.add_argument("--convert-all", action="store_true", help="Convert all ZIP files in input directory")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    args = parser.parse_args()
    
    # Print header
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                 GeyserMC PackConverter                    ║")
    print("║             Java → Bedrock Resource Pack                  ║")
    print("║                                                           ║")
    print(f"║                    Version {__version__}                        ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    try:
        input_path = Path(args.input)
        output_dir = Path(args.output) if args.output else Path.cwd() / "converted_packs"
        
        if args.convert_all and input_path.is_dir():
            # Convert all ZIP files in directory
            zip_files = list(input_path.glob("*.zip"))
            if not zip_files:
                log("No ZIP files found in directory", "ERROR")
                return 1
                
            log(f"Found {len(zip_files)} ZIP files to convert")
            
            for zip_file in zip_files:
                log(f"\n{'='*20} Converting {zip_file.name} {'='*20}")
                with GeyserPackConverter(zip_file, output_dir) as converter:
                    bedrock_dir, mcpack_path = converter.convert()
                    
        else:
            # Convert single pack
            if not input_path.exists():
                log(f"Input path does not exist: {input_path}", "ERROR")
                return 1
                
            with GeyserPackConverter(input_path, output_dir) as converter:
                bedrock_dir, mcpack_path = converter.convert()
                
        log(f"\n{Colors.GREEN}{Colors.BOLD}All conversions completed!{Colors.END}")
        log(f"Output directory: {output_dir}")
        
        return 0
        
    except KeyboardInterrupt:
        log("\nConversion cancelled by user", "WARNING")
        return 1
    except ValueError as e:
        log(f"Invalid input: {e}", "ERROR")
        log("Please check that your input is a valid Minecraft resource pack", "ERROR")
        return 1
    except FileNotFoundError as e:
        log(f"File not found: {e}", "ERROR")
        return 1
    except PermissionError as e:
        log(f"Permission denied: {e}", "ERROR")
        log("Please check file permissions and try again", "ERROR")
        return 1
    except Exception as e:
        log(f"Conversion failed: {e}", "ERROR")
        log("If this persists, please check the input pack format", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())