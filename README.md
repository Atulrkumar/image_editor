# AI Image Text Editor ✨# Image Generation with Pre-trained Models



A powerful web-based image editor that uses AI to extract text from images, allows live editing with drag-and-drop positioning, and generates creative variations using free AI services. **100% FREE** - no API keys required!Welcome to the **Image Generation with Pre-trained Models** repository! This project demonstrates how to utilize pre-trained generative models like DALL-E-mini and Stable Diffusion to create images from text prompts. These models enable the generation of high-quality images by leveraging powerful deep learning architectures trained on extensive datasets.



![AI Image Editor](https://img.shields.io/badge/AI-Powered-blue) ![Free](https://img.shields.io/badge/100%25-FREE-green) ![Python](https://img.shields.io/badge/Python-3.11-yellow) ![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)## Table of Contents



## ✨ Features- [Introduction](#introduction)

- [Getting Started](#getting-started)

- 🔍 **Smart OCR Text Detection** - Automatically extracts text from images using EasyOCR  - [Prerequisites](#prerequisites)

- ✏️ **Interactive Text Editing** - Click and drag to reposition text elements on canvas  - [Installation](#installation)

- 🎨 **AI-Powered Variations** - Generate 3 creative variations with AI backgrounds using Pollinations.ai- [Usage](#usage)

- 🎭 **Meme Generator** - Auto-generate funny meme captions with AI  - [Generating Images](#generating-images)

- 🌈 **Real-time Preview** - See changes instantly as you edit  - [Examples](#examples)

- 💾 **Download Anywhere** - Export your edited images and variations- [Models](#models)

- 🆓 **Completely Free** - Uses free AI services (Pollinations.ai) - no API keys needed!  - [DALL-E-mini](#dall-e-mini)

  - [Stable Diffusion](#stable-diffusion)

## 🚀 Quick Start (Local)- [Contributing](#contributing)

- [License](#license)

### Prerequisites- [Acknowledgements](#acknowledgements)

- Python 3.11+

- pip## Introduction



### InstallationThis repository provides a framework for generating images from text prompts using pre-trained generative models. It covers how to use models like DALL-E-mini and Stable Diffusion to create visuals directly from text descriptions. Whether you're an AI enthusiast, a developer, or a designer, this project offers a hands-on approach to exploring the capabilities of generative AI.



1. **Clone the repository**## Getting Started

```bash

git clone https://github.com/Atulrkumar/Image_Editor.git### Prerequisites

cd Image_Editor

```Before you begin, ensure you have the following installed:



2. **Install dependencies**- Python 3.7+

```bash- Git

pip install -r requirements_free.txt- Virtualenv (optional but recommended)

```

### Installation

3. **Run the app**

```bash1. **Clone the Repository**

python app_free.py

```   ```bash

   git clone https://github.com/your-username/image-generation-pretrained-models.git

4. **Open in browser**   cd image-generation-pretrained-models

```
http://localhost:5000
```

## 🌐 Deploy to Vercel

This project is ready to deploy to Vercel using Docker!

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. Push this repository to GitHub
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click **"Add New Project"**
4. Import your GitHub repository
5. Vercel will auto-detect the `vercel.json` and use the Dockerfile
6. Click **"Deploy"**

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### Important Notes for Vercel Deployment

⚠️ **File Storage**: Uploaded and generated images are stored in `/uploads` and `/generated` folders inside the container. These are **ephemeral** on serverless platforms - files will be lost on redeployment.

For production use, consider:
- Integrating cloud storage (AWS S3, Cloudflare R2, Azure Blob)
- Using a persistent file storage service
- Storing images in a database (base64 encoded)

⚠️ **OCR Dependencies**: The full OCR version (`app_free.py`) uses EasyOCR, OpenCV, and PyTorch which are large packages. The current `requirements.txt` includes only core packages for faster builds. To enable full OCR:

1. Uncomment OCR packages in `requirements.txt`:
```txt
easyocr
numpy
opencv-python-headless
torch
```

2. Update `Dockerfile` to install system dependencies:
```dockerfile
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
```

## 📁 Project Structure

```
Image_Editor/
├── app_free.py              # Main Flask application (FREE version)
├── app.py                   # Full version (with Tesseract OCR)
├── requirements.txt         # Python dependencies for deployment
├── requirements_free.txt    # Minimal dependencies for local dev
├── Dockerfile              # Container configuration for Vercel
├── vercel.json             # Vercel deployment configuration
├── .dockerignore           # Files to exclude from Docker build
├── .gitignore              # Git ignore rules
├── .env.example            # Environment variables template
├── templates/
│   └── index.html          # Web UI (single-page app)
├── uploads/                # Temporary uploaded images (gitignored)
├── generated/              # Temporary generated variations (gitignored)
└── README_VERCEL.md        # Detailed Vercel deployment guide
```

## 🎯 How It Works

1. **Upload Image** - User uploads an image (drag & drop or file picker)
2. **OCR Extraction** - EasyOCR detects and extracts text with positions
3. **Text Removal** - OpenCV inpainting removes original text from background
4. **Interactive Canvas** - HTML5 Canvas displays clean image with editable text overlays
5. **Drag & Drop** - User repositions, edits, and styles text elements
6. **AI Generation** - Pollinations.ai generates 3 variations with new backgrounds (optional)
7. **Download** - User downloads edited image or AI variations

## 🛠️ Tech Stack

- **Backend**: Flask (Python 3.11)
- **OCR**: EasyOCR + OpenCV
- **Image Processing**: Pillow (PIL)
- **AI Generation**: Pollinations.ai (FREE, no API key)
- **Frontend**: Vanilla JavaScript + HTML5 Canvas
- **Deployment**: Docker + Vercel

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file (copy from `.env.example`):

```bash
# Optional: Hugging Face API key for alternative AI models
HUGGING_FACE_API_KEY=hf_your_token_here
```

The app works perfectly **without** any API keys using Pollinations.ai!

## 🎨 Usage Guide

1. **Upload an Image**
   - Drag & drop or click "Choose Image"
   - Supports JPG, PNG, WEBP

2. **Edit Text**
   - Click and drag text on the canvas to reposition
   - Edit text content in the sidebar
   - Change colors with the color picker
   - Add new text elements with "➕ Add New Text"

3. **Generate Variations**
   - Leave prompt empty → Apply effects only
   - Add prompt (e.g., "ocean sunset") → AI changes background
   - Get 3 variations instantly

4. **Generate Memes**
   - Click "🎭 Get Meme Ideas"
   - AI suggests 5 funny captions
   - Click any caption to apply it

5. **Download**
   - Click "💾 Download Image" for current canvas
   - Or download any variation individually

## 🐳 Local Docker Testing

Test the Docker container locally before deploying:

```bash
# Build image
docker build -t image-editor:local .

# Run container
docker run -p 5000:5000 image-editor:local

# Open browser
http://localhost:5000
```

## 📝 API Endpoints

- `GET /` - Serve web UI
- `POST /api/upload` - Upload and process image (OCR extraction)
- `POST /api/render-preview` - Render text on image preview
- `POST /api/generate` - Generate 3 AI variations
- `POST /api/generate-memes` - Generate meme caption suggestions
- `GET /api/download/<filename>` - Download generated image

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgements

- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - OCR text detection
- [Pollinations.ai](https://pollinations.ai) - Free AI image generation
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Pillow](https://python-pillow.org/) - Image processing

## 🐛 Known Issues & Limitations

- **Ephemeral Storage**: Files are not persisted on serverless platforms
- **OCR Accuracy**: Works best with clear, high-contrast text
- **AI Generation Time**: Can take 30-60 seconds for background changes
- **Container Size**: Full OCR version creates large Docker images (~2-3GB)

## 💡 Future Enhancements

- [ ] Cloud storage integration (S3, Cloudflare R2)
- [ ] User authentication and saved projects
- [ ] More AI models and effects
- [ ] Batch processing
- [ ] Mobile app version

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: [Your Contact Info]

---

Made with ❤️ by [Atulrkumar](https://github.com/Atulrkumar)
