"""
Test OCR functionality with a sample image
"""
import easyocr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import sys

print("=" * 60)
print("Testing EasyOCR Installation")
print("=" * 60)

# Create a test image with text
print("\n1️⃣ Creating test image with text...")
img = Image.new('RGB', (800, 400), color='white')
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("arial.ttf", 60)
except:
    print("⚠️ Arial font not found, using default font")
    font = ImageFont.load_default()

draw.text((50, 100), "Hello World", fill='black', font=font)
draw.text((50, 200), "OCR Test 123", fill='black', font=font)

# Save test image
test_path = "test_image.png"
img.save(test_path)
print(f"✅ Test image saved: {test_path}")

# Initialize OCR
print("\n2️⃣ Initializing EasyOCR reader...")
try:
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    print("✅ EasyOCR reader initialized successfully!")
except Exception as e:
    print(f"❌ Failed to initialize EasyOCR: {e}")
    sys.exit(1)

# Test OCR
print("\n3️⃣ Running OCR on test image...")
try:
    img_array = np.array(img)
    results = reader.readtext(img_array, paragraph=False)
    
    print(f"\n✅ OCR completed! Found {len(results)} text elements:")
    print("-" * 60)
    
    for idx, (bbox, text, confidence) in enumerate(results):
        print(f"\nText {idx + 1}:")
        print(f"  Content: '{text}'")
        print(f"  Confidence: {confidence:.2%}")
        print(f"  BBox: {bbox}")
        
except Exception as e:
    print(f"❌ OCR failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ OCR TEST COMPLETED SUCCESSFULLY!")
print("=" * 60)

# Now test with an actual uploaded image if it exists
print("\n4️⃣ Checking for uploaded images...")
import os
uploads_dir = "uploads"
if os.path.exists(uploads_dir):
    files = [f for f in os.listdir(uploads_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    if files:
        print(f"Found {len(files)} uploaded image(s)")
        test_file = os.path.join(uploads_dir, files[0])
        print(f"\n Testing OCR on: {test_file}")
        
        try:
            real_img = Image.open(test_file)
            real_array = np.array(real_img)
            real_results = reader.readtext(real_array, paragraph=False)
            
            print(f"\n✅ Found {len(real_results)} text elements in uploaded image:")
            for idx, (bbox, text, confidence) in enumerate(real_results):
                if confidence > 0.3:
                    print(f"  {idx + 1}. '{text}' (confidence: {confidence:.2%})")
        except Exception as e:
            print(f"⚠️ Could not process uploaded image: {e}")
    else:
        print("No uploaded images found")
else:
    print("No uploads folder found")
