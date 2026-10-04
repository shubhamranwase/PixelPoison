# PixelPoison MVP

This is the Minimum Viable Product (MVP) for PixelPoison. It applies invisible adversarial noise to images to confound AI vision models and degrade artistic style transfer. 

The project is split into a Python FastAPI backend and a React Vite frontend.

## Prerequisites
- Python 3.9+
- Node.js 18+ and npm

## 1. Running the Backend

To start the FastAPI backend server (requires the virtual environment to be active):

```bash
cd backend
# Activate virtual environment if not already active:
# .\venv\Scripts\activate
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`.

## 2. Running the Frontend

To start the React Vite development server:

```bash
cd frontend
npm run dev
```
The web app will be available at `http://localhost:5173`.

## Features
- **Adjustable Intensity Slider:** Choose between Minimal, Standard, or Max perturbation.
- **Mathematical Validation Guarantee:** Confirmation that the noise successfully alters the image data.
- **Local SQLite Tracking:** Automatically tracks the number of artworks protected.
- **Pure Python Noise Generation:** Uses NumPy to generate and clip high-frequency Gaussian noise within adversarial bounds.

## Notes
- To view the API documentation, visit `http://localhost:8000/docs` while the backend is running.
- The default styling applies a global dark mode as requested.
