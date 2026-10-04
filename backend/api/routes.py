from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import glob
import uuid
import subprocess
import traceback

import models
from database import get_db
from core_protection.noise_generator import apply_adversarial_noise

router = APIRouter()

RESULTS_DIR = r"C:\Users\shubh\Antigravity\evaluation_suite\results"
os.makedirs(RESULTS_DIR, exist_ok=True)

@router.get("/results/{filename}")
def get_result_image(filename: str):
    file_path = os.path.join(RESULTS_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return Response(content=f.read(), media_type="image/png")
    raise HTTPException(status_code=404, detail="Image not found")

@router.get("/api/find-models")
def find_models():
    search_paths = ["C:/Users/shubh/Downloads/**/*.safetensors", "C:/Users/shubh/Documents/**/*.safetensors", "C:/Users/shubh/Antigravity/**/*.safetensors"]
    results = []
    for p in search_paths:
        try:
            results.extend(glob.glob(p, recursive=True))
        except Exception:
            pass
    return {"models": results}

@router.post("/api/shield-image")
async def shield_image(
    file: UploadFile = File(...),
    intensity: int = Form(2),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    
    try:
        protected_image_bytes = apply_adversarial_noise(contents, intensity)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating noise: {str(e)}")
    
    log_entry = models.ProcessingLog(
        original_filename=file.filename,
        intensity_level=intensity
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    return Response(content=protected_image_bytes, media_type="image/png")

class CompareRequest(BaseModel):
    prompt: str

@router.post("/api/compare")
async def compare_models(req: CompareRequest):
    req_id = str(uuid.uuid4())[:8]
    clean_out_name = f"clean_{req_id}.png"
    poisoned_out_name = f"poisoned_{req_id}.png"
    
    clean_out_path = os.path.join(RESULTS_DIR, clean_out_name)
    poisoned_out_path = os.path.join(RESULTS_DIR, poisoned_out_name)
    
    python_exe = r"C:\Users\shubh\Antigravity\evaluation_suite\kohya_ss\venv\Scripts\python.exe"
    script_path = r"C:\Users\shubh\Antigravity\backend\generate_comparison.py"
    
    try:
        print(f"Running generation script for prompt: {req.prompt}")
        result = subprocess.run(
            [
                python_exe, script_path, 
                "--prompt", req.prompt,
                "--clean-out", clean_out_path,
                "--poisoned-out", poisoned_out_path
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("Generation Error:", result.stderr)
            raise HTTPException(status_code=500, detail="Error generating images")
            
        ssim_score = None
        for line in result.stdout.split('\n'):
            if line.startswith("METRIC_SSIM="):
                try:
                    ssim_score = float(line.split("=")[1])
                except:
                    pass
                    
        return {
            "clean_url": f"http://localhost:8000/results/{clean_out_name}",
            "poisoned_url": f"http://localhost:8000/results/{poisoned_out_name}",
            "logs": result.stdout,
            "ssim": ssim_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
