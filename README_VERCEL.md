# Deploying to Vercel (Docker)

This project can be deployed to Vercel using the Docker builder. The repository already contains a `Dockerfile` and `vercel.json` that instruct Vercel to build a container image and run the Flask app.

Quick notes:

- The app uses OCR libraries (EasyOCR, OpenCV, torch) in the full-featured version. Those packages are large and may require additional system libraries and longer build times. For a minimal deployment you can use the prebuilt `requirements.txt` as-is and add optional packages as needed.
- Uploaded/generated files are created under `/uploads` and `/generated` inside the container. Container files are ephemeral on serverless platforms.

Steps to deploy from your local machine:

1. Install the Vercel CLI (optional):

```powershell
npm i -g vercel
```

2. Login and deploy from the project root:

```powershell
vercel login
vercel --prod
```

3. Vercel will detect `vercel.json` and use the Dockerfile to build and deploy.

If you need OCR support (EasyOCR, OpenCV, torch), please update `requirements.txt` to include the packages and adjust the `Dockerfile` apt-get step to install `tesseract-ocr` and other system libs. Note that this will increase build time and image size.
