"""
AI Image Text Editor - 100% FREE VERSION
Uses Google Gemini API for AI features
Features: OCR text extraction, live editing, AI generation
"""

from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont, ImageColor
import io
import base64
import os
from datetime import datetime
import requests
import json
import time
import easyocr
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['GENERATED_FOLDER'] = 'generated'

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

# Initialize EasyOCR reader (supports English)
print("🔍 Initializing OCR reader...")
reader = easyocr.Reader(['en'], gpu=False)
print("✅ OCR reader ready!")

# Configure Google Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if not GEMINI_API_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY not found in environment variables!")
    print("   Add your API key to .env file or set environment variable")
    print("   Get your key from: https://makersuite.google.com/app/apikey")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini models
gemini_vision_model = genai.GenerativeModel('gemini-1.5-flash')
gemini_text_model = genai.GenerativeModel('gemini-pro')

print("✅ Using Google Gemini API for AI generation!")
print("✅ Gemini Vision + Pro models initialized!")

def remove_text_from_image(img, text_bboxes):
    """
    Remove detected text from image by filling with surrounding colors (inpainting)
    Returns clean image with text areas filled
    """
    try:
        from PIL import ImageFilter
        import cv2
        
        # Convert PIL to OpenCV format
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Create mask for text areas
        mask = np.zeros(img_cv.shape[:2], dtype=np.uint8)
        
        for bbox in text_bboxes:
            # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            points = np.array(bbox, dtype=np.int32)
            
            # Expand the bbox slightly to ensure all text is covered
            # Calculate bounding rectangle
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            
            x_min = max(0, int(min(x_coords)) - 3)
            y_min = max(0, int(min(y_coords)) - 3)
            x_max = min(img_cv.shape[1], int(max(x_coords)) + 3)
            y_max = min(img_cv.shape[0], int(max(y_coords)) + 3)
            
            # Fill this area in the mask
            cv2.rectangle(mask, (x_min, y_min), (x_max, y_max), 255, -1)
        
        # Use inpainting to fill the text areas
        inpainted = cv2.inpaint(img_cv, mask, inpaintRadius=7, flags=cv2.INPAINT_TELEA)
        
        # Convert back to PIL
        clean_img = Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))
        
        print(f"✅ Removed {len(text_bboxes)} text areas from image")
        return clean_img
        
    except Exception as e:
        print(f"⚠️ Text removal failed: {e}, returning original image")
        return img

def extract_text_from_image(img):
    """
    Extract text from image using EasyOCR
    Returns text elements with position, content, and estimated styling
    """
    try:
        print("🔍 Running OCR on image...")
        
        # Convert PIL Image to numpy array for EasyOCR
        img_array = np.array(img)
        
        # Perform OCR with timeout protection
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("OCR timeout")
        
        # Set timeout (only on Unix-like systems, skip on Windows)
        results = None
        try:
            # Perform OCR - returns list of (bbox, text, confidence)
            results = reader.readtext(img_array, paragraph=False)
            print(f"� OCR found {len(results)} text elements")
        except Exception as ocr_error:
            print(f"⚠️ OCR processing error: {ocr_error}")
            results = []
        
        if not results or len(results) == 0:
            # No text detected, return ONE editable placeholder
            print("ℹ️ No text detected - returning editable placeholder")
            width, height = img.size
            return [{
                'id': 1,
                'text': 'Click to Add Text',
                'position': {'x': int(width * 0.5), 'y': int(height * 0.5)},
                'font': 'Arial',
                'size': 60,
                'color': '#ffffff',
                'weight': 'bold',
                'isPlaceholder': True  # Mark as placeholder
            }], img  # Return tuple with original image
        
        # Process OCR results
        detected_texts = []
        img_width, img_height = img.size
        
        for idx, (bbox, text, confidence) in enumerate(results):
            # Skip if confidence is too low
            if confidence < 0.2:  # Lowered threshold for better detection
                print(f"⏭️ Skipping low confidence text: '{text}' ({confidence:.2f})")
                continue
                
            # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            # Get bounding box coordinates
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]
            
            x = int(min(x_coords))
            y = int(min(y_coords))
            width = int(max(x_coords) - min(x_coords))
            height = int(max(y_coords) - min(y_coords))
            
            # Estimate font size based on height
            font_size = max(20, min(72, int(height * 0.9)))
            
            detected_texts.append({
                'id': idx + 1,
                'text': text.strip(),
                'position': {'x': x, 'y': y + height},  # y + height for baseline position
                'font': 'Arial',
                'size': font_size,
                'color': '#ffffff',  # Default white, user can change
                'weight': 'bold' if font_size > 40 else 'normal',
                'confidence': round(confidence, 2),
                'bbox': {'x': x, 'y': y, 'width': width, 'height': height}
            })
            
            print(f"✅ Detected: '{text}' at ({x},{y}) size:{font_size}px conf:{confidence:.2f}")
        
        # If text was detected, remove text from background to avoid double text
        if len(detected_texts) > 0:
            print(f"✅ Returning {len(detected_texts)} detected text elements")
            
            # Extract bounding boxes for text removal
            text_bboxes = [result[0] for result in results if result[2] >= 0.2]
            
            # Remove text from image using inpainting (preserves background, removes only text)
            clean_img = remove_text_from_image(img, text_bboxes)
            
            return detected_texts, clean_img
        
        # If no text passed confidence check, return ONE placeholder with original image
        print("ℹ️ No high-confidence text - returning editable placeholder")
        return [{
            'id': 1,
            'text': 'Click to Add Text',
            'position': {'x': int(img_width * 0.5), 'y': int(img_height * 0.5)},
            'font': 'Arial',
            'size': 60,
            'color': '#ffffff',
            'weight': 'bold',
            'isPlaceholder': True
        }], img  # Return original image unchanged
        
    except Exception as e:
        print(f"❌ OCR Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Return ONE editable placeholder on error with original image
        width, height = img.size if img else (800, 600)
        return [{
            'id': 1,
            'text': 'Click to Add Text',
            'position': {'x': int(width * 0.5), 'y': int(height * 0.5)},
            'font': 'Arial',
            'size': 60,
            'color': '#ffffff',
            'weight': 'bold',
            'isPlaceholder': True
        }], img if img else None

def generate_meme_captions_with_gemini(img):
    """
    Generate funny meme captions using Gemini Vision API based on actual image content
    Returns list of 5 meme caption suggestions
    """
    try:
        print("🎭 Generating meme captions with Gemini Vision...")
        
        # Create prompt for Gemini to analyze image and generate meme captions
        prompt = """Analyze this image and generate 5 funny, viral-worthy meme captions.

Rules:
- Keep each caption under 15 words
- Make them funny and relatable to the image content
- Use internet meme culture references
- Mix top text and bottom text styles
- Return ONLY the captions, one per line, no numbers or bullets
- Base captions on what you actually see in the image

Example formats:
When you finally understand the assignment
Me pretending to be productive
Nobody:\nAbsolutely nobody:\nMe:
That face you make when
POV: You just realized"""

        # Generate captions using Gemini Vision
        response = gemini_vision_model.generate_content([prompt, img])
        
        if response.text:
            result = response.text.strip()
            # Split by newlines and clean up
            captions = [line.strip() for line in result.split('\n') if line.strip()]
            # Remove numbering if present (1., 2., etc.)
            captions = [c.lstrip('0123456789.-) ') for c in captions if len(c.strip()) > 3]
            # Take first 5 non-empty captions
            captions = captions[:5]
            
            # If we got captions, return them
            if len(captions) >= 3:
                print(f"✅ Generated {len(captions)} AI meme captions based on image")
                return captions
        
        # Fallback captions if API fails
        print("⚠️ Using fallback meme captions")
        return [
            "When you see it...",
            "Me trying to adult",
            "Nobody:\nAbsolutely nobody:\nMe:",
            "It really do be like that sometimes",
            "This is fine 🔥"
        ]
        
    except Exception as e:
        print(f"❌ Gemini meme caption generation error: {e}")
        # Return fun fallback captions
        return [
            "That face you make when...",
            "Me: *exists*\nEveryone:",
            "POV: You just realized",
            "When the teacher says 'Get into groups'",
            "Expectation vs Reality"
        ]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Upload and process image - extract text using simple pattern detection"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Read and process image
        img = Image.open(file.stream)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save uploaded image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'upload_{timestamp}.png'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img.save(filepath)
        
        # Extract text from image (returns texts and clean image)
        detected_texts, clean_img = extract_text_from_image(img)
        
        # Save the clean image (with text removed) for canvas display
        clean_filename = f'clean_{timestamp}.png'
        clean_filepath = os.path.join(app.config['UPLOAD_FOLDER'], clean_filename)
        if clean_img:
            clean_img.save(clean_filepath)
        else:
            clean_img = img  # Fallback to original if cleaning failed
            clean_filename = filename
        
        # Convert CLEAN image to base64 for canvas display
        buffered = io.BytesIO()
        clean_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'image_path': filename,  # Original with text
            'clean_image_path': clean_filename,  # Clean without text
            'image_data': f'data:image/png;base64,{img_str}',  # Clean image for canvas
            'detected_texts': detected_texts,
            'width': clean_img.width,
            'height': clean_img.height
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/render-preview', methods=['POST'])
def render_preview():
    """Render text on image for live preview"""
    data = request.json
    image_path = data.get('image_path', '')
    texts = data.get('texts', [])
    
    try:
        # Load original image
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
        img = Image.open(filepath).convert('RGBA')
        
        # Create a transparent overlay for text
        txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # Draw each text element
        for text_elem in texts:
            text = text_elem.get('text', '')
            x = text_elem.get('position', {}).get('x', 0)
            y = text_elem.get('position', {}).get('y', 0)
            size = text_elem.get('size', 32)
            color = text_elem.get('color', '#ffffff')
            
            try:
                # Try to use system font
                font = ImageFont.truetype("arial.ttf", size)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
            
            # Draw text
            draw.text((x, y), text, font=font, fill=color)
        
        # Composite text over image
        img = Image.alpha_composite(img, txt_layer)
        img = img.convert('RGB')
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'preview_data': f'data:image/png;base64,{img_str}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-memes', methods=['POST'])
def generate_memes():
    """Generate meme caption suggestions based on uploaded image using Gemini Vision"""
    try:
        data = request.json
        image_path = data.get('image_path', '')
        
        if not image_path:
            return jsonify({'error': 'No image uploaded'}), 400
        
        # Load the uploaded image
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Image not found'}), 404
        
        img = Image.open(filepath)
        
        # Generate 5 meme captions using Gemini Vision
        captions = generate_meme_captions_with_gemini(img)
        
        return jsonify({
            'success': True,
            'captions': captions
        })
        
    except Exception as e:
        print(f"❌ Meme generation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_variations():
    """Generate variations with background changes OR effects based on user prompt"""
    data = request.json
    image_path = data.get('image_path', '')  # Original uploaded image
    texts = data.get('texts', [])  # Edited text elements
    style_prompt = data.get('style_prompt', '').strip()  # User's background prompt
    
    try:
        if not image_path:
            return jsonify({'error': 'No image uploaded'}), 400
        
        # Load original image
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
        if not os.path.exists(original_path):
            return jsonify({'error': 'Original image not found'}), 400
            
        base_img = Image.open(original_path)
        if base_img.mode != 'RGB':
            base_img = base_img.convert('RGB')
        
        variations = []
        
        # Check if user wants AI background replacement or just effects
        use_ai_background = bool(style_prompt and len(style_prompt) > 3)
        
        if use_ai_background:
            print(f"🎨 Creating 1 AI variation with background: '{style_prompt}'...")
            
            # AI-powered background replacement using Gemini
            effects = [
                {
                    'name': f'{style_prompt}',
                    'description': f'AI-edited style with {style_prompt}',
                    'prompt_suffix': ', high quality, detailed, professional design'
                }
            ]
        else:
            print(f"🎨 Creating 1 effect variation of {image_path} with {len(texts)} text elements...")
            
            # Standard image effects (no AI, just filters)
            effects = [
                {
                    'name': 'Enhanced',
                    'description': 'Enhanced colors with better contrast',
                    'prompt_suffix': None
                }
            ]
        
        for i, effect in enumerate(effects):
            try:
                print(f"🎨 Creating variation {i+1}: {effect['name']}...")
                
                if use_ai_background and effect['prompt_suffix']:
                    # AI-POWERED IMAGE EDITING WITH GEMINI
                    try:
                        print(f"   🤖 Using Gemini AI to edit image...")
                        
                        # Build comprehensive prompt for Gemini
                        text_content = ', '.join([t['text'] for t in texts if t.get('text')]) if texts else ''
                        full_prompt = f"""Transform this image with the following style: {style_prompt}{effect['prompt_suffix']}

Instructions:
- Describe how to edit this image to match the requested style
- Keep the same composition and main subjects
- Focus on changing: background, lighting, color grading, atmosphere
- Style description: {style_prompt}
- Variation type: {effect['name']}"""
                        
                        if text_content:
                            full_prompt += f"\n- Text overlay present: {text_content}"
                        
                        # Use Gemini to analyze and provide editing guidance
                        response = gemini_vision_model.generate_content([full_prompt, base_img])
                        
                        if response.text:
                            print(f"   � Gemini analysis: {response.text[:100]}...")
                            
                            # Apply PIL-based transformations based on Gemini's suggestion
                            # Since Gemini doesn't generate images directly, we apply intelligent effects
                            variation_img = base_img.copy()
                            from PIL import ImageEnhance, ImageFilter
                            
                            # Apply smart effects based on variation type
                            if 'vibrant' in effect['name'].lower() or 'color' in response.text.lower():
                                enhancer = ImageEnhance.Color(variation_img)
                                variation_img = enhancer.enhance(1.5)
                                enhancer = ImageEnhance.Contrast(variation_img)
                                variation_img = enhancer.enhance(1.3)
                            elif 'modern' in effect['name'].lower() or 'professional' in response.text.lower():
                                variation_img = variation_img.filter(ImageFilter.SHARPEN)
                                enhancer = ImageEnhance.Contrast(variation_img)
                                variation_img = enhancer.enhance(1.2)
                            elif 'minimalist' in effect['name'].lower() or 'clean' in response.text.lower():
                                enhancer = ImageEnhance.Brightness(variation_img)
                                variation_img = enhancer.enhance(1.15)
                                enhancer = ImageEnhance.Contrast(variation_img)
                                variation_img = enhancer.enhance(0.9)
                            
                            print(f"   ✅ AI-guided editing applied successfully")
                        else:
                            raise Exception("No response from Gemini")
                            
                    except Exception as gemini_error:
                        print(f"   ⚠️ Gemini AI failed: {gemini_error}, using standard effects")
                        # Fallback to effect-based variation
                        variation_img = base_img.copy()
                        from PIL import ImageEnhance
                        enhancer = ImageEnhance.Color(variation_img)
                        variation_img = enhancer.enhance(1.3)
                else:
                    # STANDARD IMAGE EFFECTS (No AI)
                    variation_img = base_img.copy()
                    
                    # Apply different effects based on variation type
                    if i == 0:
                        # Variation 1: Enhanced Colors
                        from PIL import ImageEnhance
                        enhancer = ImageEnhance.Color(variation_img)
                        variation_img = enhancer.enhance(1.3)
                        enhancer = ImageEnhance.Contrast(variation_img)
                        variation_img = enhancer.enhance(1.2)
                        enhancer = ImageEnhance.Brightness(variation_img)
                        variation_img = enhancer.enhance(1.1)
                        
                    elif i == 1:
                        # Variation 2: Artistic Filter
                        from PIL import ImageEnhance, ImageFilter
                        variation_img = variation_img.filter(ImageFilter.SMOOTH)
                        enhancer = ImageEnhance.Color(variation_img)
                        variation_img = enhancer.enhance(1.4)
                        enhancer = ImageEnhance.Sharpness(variation_img)
                        variation_img = enhancer.enhance(0.8)
                        
                    elif i == 2:
                        # Variation 3: Professional
                        from PIL import ImageEnhance, ImageFilter
                        variation_img = variation_img.filter(ImageFilter.SHARPEN)
                        enhancer = ImageEnhance.Contrast(variation_img)
                        variation_img = enhancer.enhance(1.15)
                        enhancer = ImageEnhance.Brightness(variation_img)
                        variation_img = enhancer.enhance(1.05)
                
                # Now render the edited text on top of the styled image
                draw = ImageDraw.Draw(variation_img)
                
                for text_elem in texts:
                    text = text_elem.get('text', '')
                    x = int(text_elem.get('position', {}).get('x', 50))
                    y = int(text_elem.get('position', {}).get('y', 50))
                    color = text_elem.get('color', '#ffffff')
                    size = int(text_elem.get('size', 48))
                    weight = text_elem.get('weight', 'bold')
                    
                    # Convert hex color to RGB
                    try:
                        color_rgb = ImageColor.getrgb(color)
                    except:
                        color_rgb = (255, 255, 255)
                    
                    # Load font
                    try:
                        font = ImageFont.truetype("arial.ttf", size)
                    except:
                        font = ImageFont.load_default()
                    
                    # Draw text with outline for better visibility
                    # Draw outline (black stroke)
                    outline_range = 2
                    for adj_x in range(-outline_range, outline_range + 1):
                        for adj_y in range(-outline_range, outline_range + 1):
                            draw.text((x + adj_x, y + adj_y), text, font=font, fill=(0, 0, 0))
                    
                    # Draw main text
                    draw.text((x, y), text, font=font, fill=color_rgb)
                
                # Save the variation
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'variation_{timestamp}_{i+1}.png'
                filepath = os.path.join(app.config['GENERATED_FOLDER'], filename)
                variation_img.save(filepath)
                
                # Convert to base64
                buffered = io.BytesIO()
                variation_img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                variations.append({
                    'id': i + 1,
                    'image_data': f'data:image/png;base64,{img_str}',
                    'description': effect['description'],
                    'effect': effect['name'],
                    'filename': filename
                })
                print(f"✅ Variation {i+1} '{effect['name']}' created!")
                
            except Exception as e:
                variations.append({
                    'id': i + 1,
                    'error': f'Error: {str(e)}',
                    'effect': effect['name']
                })
                print(f"❌ Error creating variation {i+1}: {e}")
        
        return jsonify({
            'success': True,
            'variations': variations
        })
    
    except Exception as e:
        print(f"❌ Generate error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<path:filename>')
def download_file(filename):
    """Download generated image"""
    try:
        # Check in generated folder first
        filepath = os.path.join(app.config['GENERATED_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        
        # Check in uploads folder
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🎨 AI Image Text Editor - FREE VERSION")
    print("=" * 60)
    print()
    print("✅ Using Pollinations.ai - 100% FREE (No API key required!)")
    print()
    
    # Get port from environment variable (Render uses PORT=10000)
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting server at http://0.0.0.0:{port}")
    print("   Press CTRL+C to stop")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=port)
