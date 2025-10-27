# 🐛 Pest Classification App

A fullstack web application for classifying pest images using deep learning. Built with FastAPI (backend) and React (frontend).

## 📋 Features

- Upload images for instant pest classification
- Supports three classes: **Spodoptera**, **Semilooper**, and **Healthy Leaf**
- Real-time predictions with confidence scores
- Clean and responsive UI
- Production-ready with Docker support
- Deployable to Render

---

## 🏗️ Architecture

```
Pest-Classification/
├── backend/           # FastAPI server
│   ├── main.py       # API endpoints
│   ├── model.keras   # Keras model file
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/          # React app (Vite)
│   ├── src/
│   │   ├── App.jsx   # Main component
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── .env
└── README.md
```

---

## 🚀 Local Development

### Prerequisites

- **Python 3.12+** (currently using 3.14)
- **Node.js 18+** and **pnpm**
- **Docker** (optional, for containerization)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Ensure `model.keras` is present in the backend directory**

5. **Run development server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   Or run directly:
   ```bash
   python main.py
   ```

6. **Test the API:**
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Test prediction
   curl -F "file=@path/to/your/image.jpg" http://localhost:8000/predict
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   pnpm install
   ```

3. **Update `.env` if needed:**
   ```
   VITE_API_URL=http://localhost:8000
   ```

4. **Run development server:**
   ```bash
   pnpm dev
   ```

5. **Open browser:**
   Navigate to `http://localhost:5173`

---

## 🐳 Docker Deployment

### Backend Docker Build

```bash
cd backend
docker build -t pest-classifier-backend .
docker run -p 8000:8000 pest-classifier-backend
```

### Frontend Docker Build (Optional)

```bash
cd frontend
docker build -t pest-classifier-frontend .
docker run -p 80:80 pest-classifier-frontend
```

---

## ☁️ Render Deployment

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

### Step 2: Deploy Backend (Web Service)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `pest-classifier-backend`
   - **Root Directory:** `backend`
   - **Environment:** `Docker` (recommended) or `Python`
   - **Build Command:** (if Python) `pip install -r requirements.txt`
   - **Start Command:** 
     ```bash
     gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT --workers 1 --threads 4
     ```
   - **Instance Type:** Choose based on needs (Free tier available)
5. **Environment Variables:**
   - `MODEL_PATH=model.keras`
   - `PORT=8000` (Render sets this automatically)
   - `ALLOWED_ORIGINS=https://your-frontend-url.onrender.com`
6. Click **Create Web Service**
7. **Note the deployed URL** (e.g., `https://pest-classifier-backend.onrender.com`)

### Step 3: Deploy Frontend (Static Site)

1. Click **New +** → **Static Site**
2. Connect your GitHub repository
3. Configure:
   - **Name:** `pest-classifier-frontend`
   - **Root Directory:** `frontend`
   - **Build Command:** `pnpm install && pnpm build`
   - **Publish Directory:** `dist`
4. **Environment Variables:**
   - `VITE_API_URL=https://pest-classifier-backend.onrender.com` (your backend URL)
5. Click **Create Static Site**

### Step 4: Update CORS in Backend

After frontend is deployed, update the backend's `ALLOWED_ORIGINS` environment variable to include the frontend URL.

---

## 📡 API Documentation

### Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

#### `POST /predict`
Classify an uploaded image.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (image file)

**Response (200):**
```json
{
  "label": "Spodoptera",
  "index": 0,
  "probabilities": [0.92, 0.06, 0.02]
}
```

**Error Response (4xx/5xx):**
```json
{
  "detail": "Error message"
}
```

---

## 🧪 Testing

### Quick Smoke Test

```bash
# From project root
cd backend
source .venv/bin/activate

# Test with sample image
curl -F "file=@test_images/sample.jpg" http://localhost:8000/predict
```

### Expected Output

```json
{
  "label": "Healthy Leaf",
  "index": 2,
  "probabilities": [0.05, 0.08, 0.87]
}
```

---

## 🔧 Configuration

### Backend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `model.keras` | Path to the Keras model file |
| `ALLOWED_ORIGINS` | `http://localhost:5173,http://localhost:3000` | CORS allowed origins (comma-separated) |
| `PORT` | `8000` | Server port |

### Frontend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL |

---

## 📝 Model Information

- **Input Shape:** `224x224x3` (RGB)
- **Preprocessing:** Image normalized to `[0, 1]` range (`img / 255.0`)
- **Output Classes:**
  - Index 0: **Spodoptera**
  - Index 1: **Semilooper**
  - Index 2: **Healthy Leaf**
- **Model File:** `backend/model.keras`

---

## 🛠️ Troubleshooting

### Backend Issues

**Model not loading:**
- Ensure `model.keras` exists in the backend directory
- Check file permissions
- Verify TensorFlow installation

**CORS errors:**
- Update `ALLOWED_ORIGINS` environment variable
- Include frontend URL without trailing slash

**Memory issues with TensorFlow:**
- Using `workers=1` in gunicorn prevents duplicate memory allocation
- Consider upgrading to a larger instance on Render

### Frontend Issues

**API not reachable:**
- Check `VITE_API_URL` in `.env`
- Verify backend is running
- Check browser console for CORS errors

**Build failures:**
- Clear `node_modules` and reinstall: `pnpm install`
- Check Node.js version compatibility

---

## 📦 Production Considerations

1. **Single Worker:** Backend uses 1 worker to avoid TensorFlow memory duplication
2. **File Size Limit:** Maximum upload size is 5 MB
3. **Model Loading:** Model loaded once at startup for efficiency
4. **Async Predictions:** Using thread pool to avoid blocking event loop
5. **Error Handling:** Comprehensive validation and error messages

---

## 📄 License

MIT License - feel free to use this project for your own purposes.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI and React**
