import os
from PIL import Image, ImageDraw, ImageFont

def create_icon():
    # Create assets directory
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))
    os.makedirs(assets_dir, exist_ok=True)
    
    # Create a 512x512 image with a red background
    size = 512
    img = Image.new('RGBA', (size, size), (255, 59, 48, 255)) # Apple Red
    draw = ImageDraw.Draw(img)
    
    # Draw a white rounded rectangle inner border
    margin = 40
    radius = 60
    draw.rounded_rectangle(
        [(margin, margin), (size-margin, size-margin)], 
        radius=radius, 
        outline=(255, 255, 255, 255), 
        width=15
    )
    
    # Draw AT text
    # We will just draw simple white rectangles for A and T to make a geometric logo
    # T
    draw.rectangle([(200, 150), (312, 180)], fill=(255, 255, 255, 255))
    draw.rectangle([(241, 150), (271, 350)], fill=(255, 255, 255, 255))
    
    # Save as PNG
    png_path = os.path.join(assets_dir, 'logo.png')
    img.save(png_path)
    
    # Save as ICO
    ico_path = os.path.join(assets_dir, 'icon.ico')
    img.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    
    print(f"Created {png_path} and {ico_path}")

if __name__ == "__main__":
    create_icon()
