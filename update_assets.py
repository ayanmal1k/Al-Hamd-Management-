import os
import shutil
from PIL import Image

base_dir = os.path.dirname(__file__)
assets_dir = os.path.join(base_dir, 'assets')
os.makedirs(assets_dir, exist_ok=True)

# 1. Copy LOGO.png to assets/logo.png
src_logo = os.path.join(base_dir, 'LOGO.png')
dest_logo = os.path.join(assets_dir, 'logo.png')
if os.path.exists(src_logo):
    shutil.copy2(src_logo, dest_logo)
    print(f"Copied {src_logo} to {dest_logo}")

# 2. Convert ICON.png to assets/icon.ico and also save as assets/icon.png
src_icon = os.path.join(base_dir, 'ICON.png')
dest_ico = os.path.join(assets_dir, 'icon.ico')
dest_icon_png = os.path.join(assets_dir, 'icon.png')
if os.path.exists(src_icon):
    img = Image.open(src_icon)
    img.save(dest_icon_png)
    img.save(dest_ico, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Converted {src_icon} to {dest_ico}")
