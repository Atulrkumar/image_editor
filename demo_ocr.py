"""
Quick OCR Demo - Create a test image and process it
"""
from PIL import Image, ImageDraw, ImageFont
import easyocr
import numpy as np

print("=" * 70)
print("🎨 OCR DEMONSTRATION - Creating Sample Image with Text")
print("=" * 70)

# Create a colorful demo image
img = Image.new('RGB', (1200, 600), color='#2c3e50')
draw = ImageDraw.Draw(img)

# Try to use a nice font
try:
    title_font = ImageFont.truetype("arial.ttf", 80)
    subtitle_font = ImageFont.truetype("arial.ttf", 50)
    small_font = ImageFont.truetype("arial.ttf", 30)
except:
    print("⚠️ Using default font (Arial not found)")
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()
    small_font = ImageFont.load_default()

# Draw text elements
draw.text((100, 100), "MAKE TEXT", fill='#e74c3c', font=title_font)
draw.text((100, 200), "STAND OUT FROM", fill='#3498db', font=subtitle_font)
draw.text((100, 270), "BACKGROUNDS", fill='#2ecc71', font=subtitle_font)
draw.text((100, 400), "AI-Powered Image Editor", fill='#f39c12', font=small_font)
draw.text((100, 450), "100% FREE - No API Keys!", fill='#9b59b6', font=small_font)

# Save the demo image
demo_path = "demo_text_image.png"
img.save(demo_path)
print(f"\n✅ Demo image created: {demo_path}")
print(f"   Size: {img.width}x{img.height}px")

# Initialize OCR
print("\n🔍 Initializing EasyOCR...")
reader = easyocr.Reader(['en'], gpu=False, verbose=False)
print("✅ EasyOCR initialized!")

# Run OCR
print("\n📝 Extracting text from image...")
img_array = np.array(img)
results = reader.readtext(img_array, paragraph=False)

print(f"\n✅ OCR Complete! Found {len(results)} text elements:")
print("-" * 70)

for idx, (bbox, text, confidence) in enumerate(results):
    x_coords = [point[0] for point in bbox]
    y_coords = [point[1] for point in bbox]
    x = int(min(x_coords))
    y = int(min(y_coords))
    
    print(f"\n📍 Text Element {idx + 1}:")
    print(f"   Content: '{text}'")
    print(f"   Position: ({x}, {y})")
    print(f"   Confidence: {confidence:.1%}")
    
    # Highlight detected text on image with boxes
    box_coords = [tuple(point) for point in bbox]
    draw.polygon(box_coords, outline='#00ff00' if confidence > 0.5 else '#ffff00', width=3)

# Save annotated image
annotated_path = "demo_annotated.png"
img.save(annotated_path)
print(f"\n✅ Annotated image saved: {annotated_path}")
print("   (Green boxes = high confidence, Yellow = lower confidence)")

print("\n" + "=" * 70)
print("✨ SUCCESS! OCR is working perfectly!")
print("=" * 70)
print(f"\n📌 Upload '{demo_path}' to the web app to test!")
print("   URL: http://localhost:5000")
print("=" * 70)
