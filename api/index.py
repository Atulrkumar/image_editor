"""
AI Image Text Editor - Vercel Serverless Version
Simplified for Vercel's serverless constraints (no OCR, no persistent storage)
"""

from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont, ImageColor
import io
import base64
import requests
import json
from datetime import datetime

app = Flask(__name__, template_folder='../templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Using Pollinations.ai - 100% FREE, NO API KEY NEEDED!
POLLINATIONS_API = "https://image.pollinations.ai/prompt/"
POLLINATIONS_TEXT_API = "https://text.pollinations.ai/"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Upload and process image - simplified without OCR"""
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
        
        # Convert to base64 for canvas display
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Return placeholder text since we can't run OCR in serverless
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
            'note': 'OCR not available in serverless mode - add text manually'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-memes', methods=['POST'])
def generate_memes():
    """Generate meme caption suggestions"""
    try:
        captions = [
            "When you see it...",
            "Me trying to adult",
            "Nobody:\nAbsolutely nobody:\nMe:",
            "It really do be like that sometimes",
            "This is fine 🔥"
        ]
        
        return jsonify({
            'success': True,
            'captions': captions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_variations():
    """Generate variations with AI backgrounds or effects"""
    data = request.json
    texts = data.get('texts', [])
    style_prompt = data.get('style_prompt', '').strip()
    
    try:
        # Get base image from request
        image_data = data.get('image_data', '')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = image_data.split(',')[1] if ',' in image_data else image_data
        base_img = Image.open(io.BytesIO(base64.b64decode(image_data)))
        if base_img.mode != 'RGB':
            base_img = base_img.convert('RGB')
        
        variations = []
        use_ai_background = bool(style_prompt and len(style_prompt) > 3)
        
        if use_ai_background:
            effects = [
                {
                    'name': f'{style_prompt} - Modern',
                    'description': f'Modern style with {style_prompt}',
                    'prompt_suffix': ', modern professional design, high quality, 4k'
                },
                {
                    'name': f'{style_prompt} - Vibrant',
                    'description': f'Vibrant style with {style_prompt}',
                    'prompt_suffix': ', vibrant colorful artistic design, beautiful'
                },
                {
                    'name': f'{style_prompt} - Minimalist',
                    'description': f'Minimalist style with {style_prompt}',
                    'prompt_suffix': ', minimalist clean elegant design, simple'
                }
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
                    # AI background generation
                    import urllib.parse
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
                    # Apply image effects
                    variation_img = base_img.copy()
                    from PIL import ImageEnhance, ImageFilter
                    
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
                
                # Draw text on variation
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
                    for adj_x in range(-2, 3):
                        for adj_y in range(-2, 3):
                            draw.text((x + adj_x, y + adj_y), text, font=font, fill=(0, 0, 0))
                    
                    # Draw main text
                    draw.text((x, y), text, font=font, fill=color_rgb)
                
                # Convert to base64
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
        
        return jsonify({
            'success': True,
            'variations': variations
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel serverless handler
def handler(request):
    with app.app_context():
        return app.full_dispatch_request()

if __name__ == '__main__':
    app.run(debug=True)
