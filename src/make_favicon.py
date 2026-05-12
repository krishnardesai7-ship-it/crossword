"""Remove white background from logo and generate favicon files."""
from PIL import Image
import os

LOGO_PATH = os.path.join("myapp", "static", "customerapp", "images", "demos", "demo-20", "logo1.png")
ICONS_DIR = os.path.join("myapp", "static", "customerapp", "images", "icons")

# 1. Open the original logo
img = Image.open(LOGO_PATH).convert("RGBA")
pixels = img.load()

# 2. Remove white/near-white background
THRESHOLD = 240  # pixels with R,G,B all above this are treated as "white"
for y in range(img.height):
    for x in range(img.width):
        r, g, b, a = pixels[x, y]
        if r >= THRESHOLD and g >= THRESHOLD and b >= THRESHOLD:
            pixels[x, y] = (r, g, b, 0)  # make transparent

# 3. Save the transparent version back as the logo
img.save(LOGO_PATH, "PNG")
print(f"[OK] Saved transparent logo to {LOGO_PATH}")

# 4. Generate favicon files
# Crop to content (remove surrounding transparent space) for a tighter icon
bbox = img.getbbox()
if bbox:
    cropped = img.crop(bbox)
else:
    cropped = img

# Generate different favicon sizes
os.makedirs(ICONS_DIR, exist_ok=True)

# 32x32 favicon PNG
favicon_32 = cropped.copy()
favicon_32.thumbnail((32, 32), Image.LANCZOS)
# Create a 32x32 canvas and paste centered
canvas_32 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
offset_x = (32 - favicon_32.width) // 2
offset_y = (32 - favicon_32.height) // 2
canvas_32.paste(favicon_32, (offset_x, offset_y), favicon_32)
canvas_32.save(os.path.join(ICONS_DIR, "favicon-32x32.png"), "PNG")
print("[OK] Generated favicon-32x32.png")

# 16x16 favicon PNG
favicon_16 = cropped.copy()
favicon_16.thumbnail((16, 16), Image.LANCZOS)
canvas_16 = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
offset_x = (16 - favicon_16.width) // 2
offset_y = (16 - favicon_16.height) // 2
canvas_16.paste(favicon_16, (offset_x, offset_y), favicon_16)
canvas_16.save(os.path.join(ICONS_DIR, "favicon-16x16.png"), "PNG")
print("[OK] Generated favicon-16x16.png")

# 180x180 apple-touch-icon
favicon_180 = cropped.copy()
favicon_180.thumbnail((180, 180), Image.LANCZOS)
canvas_180 = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
offset_x = (180 - favicon_180.width) // 2
offset_y = (180 - favicon_180.height) // 2
canvas_180.paste(favicon_180, (offset_x, offset_y), favicon_180)
canvas_180.save(os.path.join(ICONS_DIR, "apple-touch-icon.png"), "PNG")
print("[OK] Generated apple-touch-icon.png")

# Generate .ico file (multi-size)
# ICO with 16x16, 32x32, and 48x48 sizes
favicon_48 = cropped.copy()
favicon_48.thumbnail((48, 48), Image.LANCZOS)
canvas_48 = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
offset_x = (48 - favicon_48.width) // 2
offset_y = (48 - favicon_48.height) // 2
canvas_48.paste(favicon_48, (offset_x, offset_y), favicon_48)

canvas_32.save(
    os.path.join(ICONS_DIR, "favicon.ico"),
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48)]
)
print("[OK] Generated favicon.ico")

print("\nAll done!")
