"""
AI Image Text Editor - Vercel Serverless Version
100% FREE - Uses Pollinations.ai (no API key needed)
OCR works locally, graceful fallback in serverless
"""

from flask import Flask, request, jsonify, Response
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageEnhance, ImageFilter
import io
import base64
import requests
import urllib.parse
import os
import numpy as np

# Try to import OCR - works locally, may fail in serverless
OCR_AVAILABLE = False
reader = None
try:
    import easyocr
    reader = easyocr.Reader(['en'], gpu=False)
    OCR_AVAILABLE = True
    print("✅ OCR (EasyOCR) loaded successfully!")
except ImportError:
    print("⚠️ EasyOCR not available - OCR disabled (manual text mode)")
except Exception as e:
    print(f"⚠️ OCR initialization failed: {e}")

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Using Pollinations.ai - 100% FREE, NO API KEY NEEDED!
POLLINATIONS_API = "https://image.pollinations.ai/prompt/"

# HTML template cached
HTML_TEMPLATE = None

def get_html_template():
    global HTML_TEMPLATE
    if HTML_TEMPLATE is None:
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'index.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            HTML_TEMPLATE = f.read()
    return HTML_TEMPLATE

@app.route('/')
def index():
    return Response(get_html_template(), mimetype='text/html')

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Upload and process image - OCR if available, fallback to manual"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        img = Image.open(file.stream)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        detected_texts = []
        note = 'Add text manually using the + button'
        
        # Try OCR if available
        if OCR_AVAILABLE and reader is not None:
            try:
                img_array = np.array(img)
                results = reader.readtext(img_array)
                
                for idx, (bbox, text, confidence) in enumerate(results):
                    if confidence > 0.3 and text.strip():
                        x_coords = [p[0] for p in bbox]
                        y_coords = [p[1] for p in bbox]
                        x = int(min(x_coords))
                        y = int(min(y_coords))
                        width = int(max(x_coords) - min(x_coords))
                        height = int(max(y_coords) - min(y_coords))
                        
                        font_size = max(12, min(72, int(height * 0.9)))
                        
                        detected_texts.append({
                            'id': idx + 1,
                            'text': text,
                            'position': {'x': x, 'y': y},
                            'font': 'Arial',
                            'size': font_size,
                            'color': '#ffffff',
                            'weight': 'normal',
                            'bbox': {'width': width, 'height': height}
                        })
                
                if detected_texts:
                    note = f'Detected {len(detected_texts)} text elements'
            except Exception as e:
                print(f"OCR error: {e}")
        
        # Fallback placeholder if no text detected
        if not detected_texts:
            detected_texts = [{
                'id': 1,
                'text': 'Click to Edit Text',
                'position': {'x': int(img.width * 0.5), 'y': int(img.height * 0.5)},
                'font': 'Arial',
                'size': 60,
                'color': '#ffffff',
                'weight': 'bold',
                'isPlaceholder': True
            }]
        
        return jsonify({
            'success': True,
            'image_data': f'data:image/png;base64,{img_str}',
            'detected_texts': detected_texts,
            'width': img.width,
            'height': img.height,
            'note': note,
            'ocr_available': OCR_AVAILABLE
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-memes', methods=['POST'])
def generate_memes():
    """Generate meme caption suggestions"""
    captions = [
        "When you see it...",
        "Me trying to adult",
        "Nobody:\nAbsolutely nobody:\nMe:",
        "It really do be like that sometimes",
        "This is fine 🔥"
    ]
    return jsonify({'success': True, 'captions': captions})

@app.route('/api/describe', methods=['POST'])
def describe_image():
    """Placeholder for image description - returns helpful message"""
    return jsonify({
        'success': True,
        'description': 'Image description is not available in the free serverless version.\n\nYou can manually add text to your image using the "+" button in the sidebar.',
        'suggested_prompt': 'professional marketing image with modern design',
        'note': 'AI description requires a paid API in serverless mode'
    })

@app.route('/api/generate', methods=['POST'])
def generate_variations():
    """Generate variations with AI backgrounds or effects"""
    data = request.json
    texts = data.get('texts', [])
    style_prompt = data.get('style_prompt', '').strip()
    
    try:
        image_data = data.get('image_data', '')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        image_data = image_data.split(',')[1] if ',' in image_data else image_data
        base_img = Image.open(io.BytesIO(base64.b64decode(image_data)))
        if base_img.mode != 'RGB':
            base_img = base_img.convert('RGB')
        
        variations = []
        use_ai_background = bool(style_prompt and len(style_prompt) > 3)
        
        if use_ai_background:
            effects = [
                {'name': f'{style_prompt} - Modern', 'description': f'Modern style with {style_prompt}', 'prompt_suffix': ', modern professional design, high quality, 4k'},
                {'name': f'{style_prompt} - Vibrant', 'description': f'Vibrant style with {style_prompt}', 'prompt_suffix': ', vibrant colorful artistic design, beautiful'},
                {'name': f'{style_prompt} - Minimalist', 'description': f'Minimalist style with {style_prompt}', 'prompt_suffix': ', minimalist clean elegant design, simple'}
            ]
        else:
            effects = [
                {'name': 'Enhanced Colors', 'description': 'Vibrant colors with enhanced contrast', 'prompt_suffix': None},
                {'name': 'Artistic Filter', 'description': 'Stylized artistic look', 'prompt_suffix': None},
                {'name': 'Professional', 'description': 'Clean professional look', 'prompt_suffix': None}
            ]
        
        for i, effect in enumerate(effects):
            try:
                if use_ai_background and effect['prompt_suffix']:
                    text_content = ', '.join([t['text'] for t in texts if t.get('text')])
                    full_prompt = style_prompt + effect['prompt_suffix']
                    if text_content:
                        full_prompt += f", with text: {text_content}"
                    
                    encoded_prompt = urllib.parse.quote(full_prompt)
                    api_url = f"{POLLINATIONS_API}{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true&enhance=true"
                    
                    response = requests.get(api_url, timeout=120)
                    
                    if response.status_code == 200:
                        ai_img = Image.open(io.BytesIO(response.content))
                        if ai_img.mode != 'RGB':
                            ai_img = ai_img.convert('RGB')
                        variation_img = ai_img.resize(base_img.size, Image.Resampling.LANCZOS)
                    else:
                        variation_img = base_img.copy()
                else:
                    variation_img = base_img.copy()
                    if i == 0:
                        enhancer = ImageEnhance.Color(variation_img)
                        variation_img = enhancer.enhance(1.3)
                        enhancer = ImageEnhance.Contrast(variation_img)
                        variation_img = enhancer.enhance(1.2)
                    elif i == 1:
                        variation_img = variation_img.filter(ImageFilter.SMOOTH)
                        enhancer = ImageEnhance.Color(variation_img)
                        variation_img = enhancer.enhance(1.4)
                    elif i == 2:
                        variation_img = variation_img.filter(ImageFilter.SHARPEN)
                        enhancer = ImageEnhance.Contrast(variation_img)
                        variation_img = enhancer.enhance(1.15)
                
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
                    
                    font = ImageFont.load_default()
                    
                    for adj_x in range(-2, 3):
                        for adj_y in range(-2, 3):
                            draw.text((x + adj_x, y + adj_y), text, font=font, fill=(0, 0, 0))
                    draw.text((x, y), text, font=font, fill=color_rgb)
                
                buffered = io.BytesIO()
                variation_img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                variations.append({
                    'id': i + 1,
                    'image_data': f'data:image/png;base64,{img_str}',
                    'description': effect['description'],
                    'effect': effect['name']
                })
                
            except Exception as e:
                variations.append({
                    'id': i + 1,
                    'error': f'Error: {str(e)}',
                    'effect': effect['name']
                })
        
        return jsonify({'success': True, 'variations': variations})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel requires the app to be named 'app'
# This file is the entry point for Vercel Python runtime
