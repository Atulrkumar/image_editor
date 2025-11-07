# AI Agent Instructions: AI Image Text Editor (100% FREE)

## Project Overview
This workspace contains **two Flask applications** for AI-powered image generation:

1. **Production (USE THIS)**: `app_free.py` - Simplified version with NO external OCR dependencies
2. **Full-Featured**: `app.py` - Complete version with Tesseract OCR + optional Claude Vision
3. **Legacy**: `Image Generation Using Pre-Trained Models.py` - Original Stable Diffusion notebook demo

**Recommended:** Use `app_free.py` for immediate deployment - it works with the 4 already-installed packages (Flask, Pillow, Requests, python-dotenv) and requires ZERO additional setup beyond a free Hugging Face token.

## Architecture & Key Components

### Tech Stack (All FREE)
- **Backend**: Flask (Python web framework)
- **OCR**: Tesseract (local, no API needed)
- **Image Processing**: Pillow (PIL)
- **AI Generation**: Hugging Face Inference API (free tier)
- **Frontend**: Vanilla JavaScript + CSS

### Core Files
- `app.py` - Flask backend with 4 main endpoints
- `templates/index.html` - Single-page web UI
- `requirements.txt` - Python dependencies
- `setup.ps1` - Automated setup script for Windows

### Data Flow
1. User uploads image → `/upload` endpoint
2. Tesseract OCR extracts text locally (FREE, runs on server)
3. Frontend displays extracted text for editing
4. User clicks generate → `/generate` endpoint
5. Two modes available:
   - **Text Overlay**: PIL draws text on image (instant, free)
   - **AI Generate**: Hugging Face API creates new image (free, rate-limited)
6. Frontend displays variations → user downloads via `/download/<filename>`

## Development Patterns

### FREE API Philosophy
**Critical**: User requires 100% free operation with NO paid services. All features must work without payment:

1. **Text Extraction**: Use Tesseract OCR (local installation, no API)
2. **Image Editing**: Use PIL (built-in, no API)
3. **AI Generation**: Use Hugging Face **Inference API** (not paid API)
   - Model: `black-forest-labs/FLUX.1-schnell` (optimized for speed)
   - Free tier: ~1000 requests/month
   - API key required but completely free

### Environment Variables Pattern
```python
HF_API_KEY = os.environ.get('HUGGING_FACE_API_KEY', '')
```
Always check for API key and provide graceful fallback:
- If no key: use text overlay mode
- If key exists: enable AI generation mode
- Never hardcode keys in source

### Error Handling Pattern
Hugging Face models can return 503 (loading). Always retry:
```python
max_retries = 3
for attempt in range(max_retries):
    response = requests.post(...)
    if response.status_code == 503:
        time.sleep(20)  # Model loading
```

### Image Storage Pattern
- `uploads/` - Original uploaded images (temporary)
- `generated/` - AI-generated variations (temporary)
- Use `secure_filename()` to prevent path traversal
- Timestamp-based filenames to avoid collisions

## Common Tasks

### Adding New OCR Features
Text extraction logic in `extract_text_from_image()`:
- Uses `pytesseract.image_to_data()` with bounding boxes
- Groups text by lines (Y-coordinate proximity)
- Confidence threshold: 30 (adjustable)
- Returns structured data with position/size/font info

### Switching AI Models
To use different Hugging Face model:
1. Update `HF_API_URL` (line 20 in `app.py`)
2. Adjust parameters in `generate_image_with_huggingface()`:
   - FLUX models: 4 steps, guidance_scale=0
   - Stable Diffusion: 20-50 steps, guidance_scale=7.5
3. Update UI text to reflect model capabilities

### Adding Text Overlay Styles
Modify `create_image_with_text()` to add effects:
- Font variations: Load from `C:\Windows\Fonts\` on Windows
- Colors: Parse from `element['color']` (hex format)
- Shadows: Use `ImageDraw` with offset + transparency
- Backgrounds: Draw rectangles before text

### Frontend Customization
`templates/index.html` structure:
- **Upload Zone**: Drag-drop with file input fallback
- **Canvas Area**: Image preview with loading states
- **Sidebar**: Text editor + style controls + variations
- **Mode Toggle**: Switch between overlay/AI modes

Update CSS gradients in `<style>` section for theming.

## Testing & Validation

### Local Testing
1. Install Tesseract: Download from UB-Mannheim repo
2. Run `setup.ps1` for automated setup (Windows)
3. Start app: `python app.py`
4. Open `http://localhost:5000`
5. Upload test image with clear text
6. Verify OCR extraction works
7. Test both generation modes

### Debugging OCR Issues
If text not detected:
- Check Tesseract installation: `tesseract --version`
- Set explicit path: `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`
- Verify image quality (resolution, contrast)
- Lower confidence threshold (line 39 in `app.py`)

### Debugging HF API Issues
Common errors:
- **503**: Model loading, auto-retries 3x with 20s wait
- **401**: Invalid API key, check environment variable
- **429**: Rate limit, switch to overlay mode
- **Timeout**: Increase timeout or use faster model

## Dependencies & Setup

### Required Software
1. **Python 3.7+**: Core runtime
2. **Tesseract OCR**: Windows installer or `brew install tesseract` (Mac)
3. **pip packages**: Listed in `requirements.txt`

### Optional (for AI mode)
- Hugging Face account (free): https://huggingface.co/join
- Read token from settings (free tier): https://huggingface.co/settings/tokens

### Quick Start Commands (Windows PowerShell)
```powershell
# Install dependencies
pip install -r requirements.txt

# Set API key (optional)
$env:HUGGING_FACE_API_KEY="hf_..."

# Run app
python app.py
```

## Project-Specific Notes

### Legacy Code
`Image Generation Using Pre-Trained Models.py` is the **old** simple demo:
- Jupyter notebook style (not used in main app)
- Only Stable Diffusion (requires torch/transformers)
- Not integrated with Flask app
- Keep for reference but don't modify

### File Organization
- No `static/` folder needed (CSS/JS inline in HTML)
- Auto-creates `uploads/` and `generated/` on startup
- No database - everything in memory/disk temporarily
- No user authentication - single-user local app

### Performance Considerations
- Tesseract OCR: 2-5 seconds per image (local CPU)
- Text overlay: <1 second (PIL is fast)
- AI generation: 20-60 seconds (HF API model loading)
- First AI request: slower (cold start)

### Security Notes
- `MAX_CONTENT_LENGTH`: 16MB limit prevents DoS
- `secure_filename()`: Prevents path traversal
- No persistent storage: Files cleared on restart
- API key from environment: Never commit to git

### VS Code Integration
User runs in VS Code, so:
- Use Flask debug mode for hot reload
- Terminal output shows startup instructions
- Errors display in terminal for easy debugging
- Port 5000 default (configurable)
