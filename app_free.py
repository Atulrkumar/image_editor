"""
AI Image Text Editor - Simplified Version
Features: OCR text extraction, live editing, Gemini AI prompt-based editing (single variation)
"""

from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageEnhance, ImageFilter
import io
import base64
import os
from datetime import datetime
import easyocr
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
import cv2

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['GENERATED_FOLDER'] = 'generated'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

# Initialize OCR
print("🔍 Initializing OCR reader...")
reader = easyocr.Reader(['en'], gpu=False)
print("✅ OCR reader ready!")

# Configure Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Gemini API configured!")
else:
    print("⚠️ WARNING: GEMINI_API_KEY not found!")
    gemini_model = None

def remove_text_from_image(img, text_bboxes):
    """Remove detected text using inpainting"""
    try:
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        mask = np.zeros(img_cv.shape[:2], dtype=np.uint8)
        
        for bbox in text_bboxes:
            points = np.array(bbox, dtype=np.int32)
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            
            x_min = max(0, int(min(x_coords)) - 3)
            y_min = max(0, int(min(y_coords)) - 3)
            x_max = min(img_cv.shape[1], int(max(x_coords)) + 3)
            y_max = min(img_cv.shape[0], int(max(y_coords)) + 3)
            
            cv2.rectangle(mask, (x_min, y_min), (x_max, y_max), 255, -1)
        
        inpainted = cv2.inpaint(img_cv, mask, inpaintRadius=7, flags=cv2.INPAINT_TELEA)
        clean_img = Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))
        return clean_img
    except Exception as e:
        print(f"⚠️ Text removal failed: {e}")
        return img

def extract_text_from_image(img):
    """Extract text using EasyOCR"""
    try:
        print("🔍 Running OCR...")
        img_array = np.array(img)
        results = reader.readtext(img_array, paragraph=False)
        print(f"📝 OCR found {len(results)} text elements")
        
        if not results:
            width, height = img.size
            return [{
                'id': 1,
                'text': 'Click to Add Text',
                'position': {'x': int(width * 0.5), 'y': int(height * 0.5)},
                'font': 'Arial',
                'size': 60,
                'color': '#ffffff',
                'weight': 'bold',
                'isPlaceholder': True
            }], img
        
        detected_texts = []
        for idx, (bbox, text, confidence) in enumerate(results):
            if confidence < 0.2:
                continue
                
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]
            
            x = int(min(x_coords))
            y = int(min(y_coords))
            width = int(max(x_coords) - min(x_coords))
            height = int(max(y_coords) - min(y_coords))
            font_size = max(20, min(72, int(height * 0.9)))
            
            detected_texts.append({
                'id': idx + 1,
                'text': text.strip(),
                'position': {'x': x, 'y': y + height},
                'font': 'Arial',
                'size': font_size,
                'color': '#ffffff',
                'weight': 'bold' if font_size > 40 else 'normal',
                'confidence': round(confidence, 2)
            })
        
        if detected_texts:
            text_bboxes = [result[0] for result in results if result[2] >= 0.2]
            clean_img = remove_text_from_image(img, text_bboxes)
            return detected_texts, clean_img
        
        width, height = img.size
        return [{
            'id': 1,
            'text': 'Click to Add Text',
            'position': {'x': int(width * 0.5), 'y': int(height * 0.5)},
            'font': 'Arial',
            'size': 60,
            'color': '#ffffff',
            'weight': 'bold',
            'isPlaceholder': True
        }], img
        
    except Exception as e:
        print(f"❌ OCR Error: {e}")
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

def apply_gemini_guided_edits(img, prompt):
    """Apply image edits guided by Gemini AI suggestions"""
    try:
        if not gemini_model:
            print("⚠️ Gemini not configured, applying basic enhancement")
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Contrast(img)
            return enhancer.enhance(1.1)
        
        # Ask Gemini for editing suggestions based on prompt
        gemini_prompt = f"""Based on this user request: "{prompt}"

Suggest specific PIL image editing parameters. Respond ONLY with a JSON object like:
{{
    "brightness": 1.1,
    "contrast": 1.2,
    "color": 1.1,
    "sharpness": 1.0,
    "blur": false
}}

Values should be between 0.5 and 2.0. Use 1.0 for no change."""

        response = gemini_model.generate_content(gemini_prompt)
        suggestion_text = response.text.strip()
        
        # Extract JSON from response
        import json
        import re
        json_match = re.search(r'\{[^}]+\}', suggestion_text)
        if json_match:
            suggestions = json.loads(json_match.group())
            
            # Apply suggested edits
            if suggestions.get('brightness', 1.0) != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(float(suggestions['brightness']))
            
            if suggestions.get('contrast', 1.0) != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(float(suggestions['contrast']))
            
            if suggestions.get('color', 1.0) != 1.0:
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(float(suggestions['color']))
            
            if suggestions.get('sharpness', 1.0) != 1.0:
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(float(suggestions['sharpness']))
            
            if suggestions.get('blur', False):
                img = img.filter(ImageFilter.SMOOTH)
            
            print(f"✅ Applied Gemini-guided edits: {suggestions}")
            return img
        else:
            # Fallback to basic enhancement
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Contrast(img)
            return enhancer.enhance(1.1)
            
    except Exception as e:
        print(f"⚠️ Gemini editing failed: {e}, applying basic enhancement")
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(1.1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        img = Image.open(file.stream)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'upload_{timestamp}.png'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img.save(filepath)
        
        detected_texts, clean_img = extract_text_from_image(img)
        
        clean_filename = f'clean_{timestamp}.png'
        clean_filepath = os.path.join(app.config['UPLOAD_FOLDER'], clean_filename)
        if clean_img:
            clean_img.save(clean_filepath)
        else:
            clean_img = img
            clean_filename = filename
        
        buffered = io.BytesIO()
        clean_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'image_path': filename,
            'clean_image_path': clean_filename,
            'image_data': f'data:image/png;base64,{img_str}',
            'detected_texts': detected_texts,
            'width': clean_img.width,
            'height': clean_img.height
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_variation():
    """Generate SINGLE variation based on user prompt using Gemini AI guidance"""
    data = request.json
    image_path = data.get('image_path', '')
    texts = data.get('texts', [])
    style_prompt = data.get('style_prompt', '').strip()
    
    try:
        if not image_path:
            return jsonify({'error': 'No image uploaded'}), 400
        
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
        if not os.path.exists(original_path):
            return jsonify({'error': 'Original image not found'}), 400
            
        base_img = Image.open(original_path)
        if base_img.mode != 'RGB':
            base_img = base_img.convert('RGB')
        
        print(f"🎨 Creating variation with prompt: '{style_prompt}'...")
        
        # Apply Gemini-guided edits if prompt provided
        if style_prompt and len(style_prompt) > 3:
            variation_img = apply_gemini_guided_edits(base_img.copy(), style_prompt)
            description = f'AI-edited: {style_prompt}'
        else:
            # Basic enhancement if no prompt
            variation_img = base_img.copy()
            enhancer = ImageEnhance.Color(variation_img)
            variation_img = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Contrast(variation_img)
            variation_img = enhancer.enhance(1.1)
            description = 'Enhanced version'
        
        # Render text on top
        draw = ImageDraw.Draw(variation_img)
        
        for text_elem in texts:
            text = text_elem.get('text', '')
            x = int(text_elem.get('position', {}).get('x', 50))
            y = int(text_elem.get('position', {}).get('y', 50))
            color = text_elem.get('color', '#ffffff')
            size = int(text_elem.get('size', 48))
            
            try:
                color_rgb = ImageColor.getrgb(color)
            except:
                color_rgb = (255, 255, 255)
            
            try:
                font = ImageFont.truetype("arial.ttf", size)
            except:
                font = ImageFont.load_default()
            
            # Draw outline
            outline_range = 2
            for adj_x in range(-outline_range, outline_range + 1):
                for adj_y in range(-outline_range, outline_range + 1):
                    draw.text((x + adj_x, y + adj_y), text, font=font, fill=(0, 0, 0))
            
            # Draw main text
            draw.text((x, y), text, font=font, fill=color_rgb)
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'variation_{timestamp}.png'
        filepath = os.path.join(app.config['GENERATED_FOLDER'], filename)
        variation_img.save(filepath)
        
        # Convert to base64
        buffered = io.BytesIO()
        variation_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'variations': [{
                'id': 1,
                'image_data': f'data:image/png;base64,{img_str}',
                'description': description,
                'filename': filename
            }]
        })
        
    except Exception as e:
        print(f"❌ Generate error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<path:filename>')
def download_file(filename):
    try:
        filepath = os.path.join(app.config['GENERATED_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🎨 AI Image Text Editor")
    print("=" * 60)
    print()
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting server at http://0.0.0.0:{port}")
    print("   Press CTRL+C to stop")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=port)
