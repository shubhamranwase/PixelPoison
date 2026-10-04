# PixelPoison 🛡️

PixelPoison is an **Adversarial Machine Learning** tool designed to protect digital artwork from unauthorized Generative AI scraping. It applies targeted, mathematically calculated adversarial gradients to images, effectively poisoning the data for Diffusion models during training (style extraction) while remaining virtually imperceptible to the human eye.

## 🧠 The Technical Approach

Generative AI models rely on latent space representations to understand and replicate artistic styles. PixelPoison acts as a **Data Poisoning** mechanism:
1. **Gradient Extraction:** The backend loads a pre-trained Vision Transformer (`ViT_B_16`) via PyTorch. When an image is processed, it performs a forward and backward pass to extract exact gradients (`input_tensor.grad.data`).
2. **Adversarial Perturbation:** Using techniques derived from the Fast Gradient Method (FGM), we generate noise that directly disrupts the features the AI relies on most.
3. **Epsilon Constraints:** The calculated gradients are upsampled (Bilinear Interpolation) and strictly clipped within low $\epsilon$ bounds (e.g., `[2, 4, 8]`). This ensures the adversarial noise devastates the model's loss landscape without compromising the visual fidelity of the artist's original work.

## 🛠️ Architecture & Tech Stack

This project is built with a decoupled architecture focusing on high-performance ML inference and a responsive user experience:

* **Backend (AI Inference & API):**
  * **Python & PyTorch:** Core engine for computing adversarial gradients and tensor manipulations.
  * **FastAPI:** High-performance asynchronous REST API.
  * **SQLite:** Lightweight local tracking for processed telemetry.
* **Frontend (Client Interface):**
  * **React & Vite:** Lightning-fast modern frontend build.
  * **Tailwind CSS:** Fully responsive, dark-mode prioritized UI.
  * **FormData API:** Efficient handling of multipart image blobs for API transmission.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm

### 1. Running the ML Backend

Navigate to the backend and start the FastAPI server:

```bash
cd backend
# Create and activate your virtual environment (recommended)
python -m venv venv
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```
The API (and interactive Swagger documentation) will be available at `http://localhost:8000/docs`.

### 2. Running the Frontend Interface

In a separate terminal, start the React development server:

```bash
cd frontend
npm install
npm run dev
```
The web application will be available at `http://localhost:5173`.

## 💡 Key Features
- **Dynamic Intensity Mapping:** Users can adjust the adversarial $\epsilon$ intensity (Minimal, Standard, Max) to balance visual preservation and poisoning strength.
- **Local Vision Transformer Inference:** 100% local processing using `ViT_B_16`—no data is sent to external APIs.
- **Mathematical Validation:** Real-time feedback and validation of tensor perturbations applied to the resulting image.

## ⚠️ Note on Inference vs. Training
PixelPoison is designed as a **Data Poisoning** tool to disrupt model *training/fine-tuning* (e.g., preventing a model from learning an artist's specific brushstrokes). It is *not* an Inference Evasion tool designed to trick standard classifiers (like GPT-4o) from recognizing the subject matter of an image, which would require visual distortion too severe for professional artists.
