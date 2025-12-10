#!/usr/bin/env python3
import importlib
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the compiled module
module_name = 'share_obfuscated'
try:
    compiled_module = importlib.import_module(module_name)
    print("Module loaded successfully!")
except ImportError as e:
    print(f"Error loading module: {e}")
    sys.exit(1)

# Execute the module's main function if it exists
if hasattr(compiled_module, 'main'):
    compiled_module.main()
