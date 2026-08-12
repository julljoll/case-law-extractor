"""
Generates official assets (Escudo de la República Bolivariana de Venezuela)
for high-fidelity TSJ decision PDF rendering.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def generate_escudo_image(output_path: str = "assets/escudo_venezuela.png"):
    """Generates an official coat of arms emblem for TSJ document headers."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    size = (300, 320)
    img = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Outer Shield Contour
    center_x, top_y = 150, 40
    
    # Shield shape points
    shield_box = [60, 60, 240, 260]
    
    # Draw Shield Header (Gold/Yellow, Blue, Red stripes)
    # Top Yellow Field (Wheat sheaves)
    draw.rectangle([70, 70, 230, 130], fill="#F6C445", outline="#202020", width=2)
    # Left Red Field (Weapons & Flags)
    draw.rectangle([70, 130, 150, 190], fill="#CF2029", outline="#202020", width=2)
    # Right Blue Field (White Horse)
    draw.rectangle([150, 130, 230, 190], fill="#00247D", outline="#202020", width=2)
    # Bottom Field
    draw.polygon([(70, 190), (230, 190), (150, 260)], fill="#00247D", outline="#202020", width=2)
    
    # Wheat sheaves (Yellow top field detail)
    draw.arc([110, 80, 190, 120], start=0, end=360, fill="#202020", width=2)
    draw.line([(150, 80), (150, 120)], fill="#202020", width=2)
    
    # White Horse (Blue right field detail)
    draw.ellipse([175, 145, 205, 175], fill="#FFFFFF", outline="#202020", width=2)
    
    # Weapons & Flags (Red left field detail)
    draw.line([(85, 145), (135, 175)], fill="#FFFFFF", width=3)
    draw.line([(135, 145), (85, 175)], fill="#FFFFFF", width=3)
    
    # Laurel branches around shield
    draw.arc([30, 50, 270, 270], start=40, end=140, fill="#2D7D32", width=4)
    draw.arc([30, 50, 270, 270], start=220, end=320, fill="#2D7D32", width=4)
    
    # Upper Ribbon (Yellow, Blue, Red)
    draw.rectangle([50, 30, 250, 50], fill="#F6C445", outline="#202020", width=1)
    
    # Save Image
    img.save(output_path, "PNG")
    print(f"Generated Escudo Emblem at {output_path}")

if __name__ == "__main__":
    generate_escudo_image()
