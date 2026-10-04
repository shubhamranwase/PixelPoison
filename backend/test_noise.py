import sys
import os

# Add backend to path
sys.path.append(r"C:\Users\shubh\Antigravity\backend")

from core_protection.noise_generator import apply_adversarial_noise
import numpy as np
from PIL import Image
import io

# Create a dummy image
img = Image.new("RGB", (256, 256), color=(100, 150, 200))
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='PNG')
img_bytes = img_byte_arr.getvalue()

try:
    print("Applying noise...")
    noisy_bytes = apply_adversarial_noise(img_bytes, intensity=3)
    
    # Check diff
    orig_np = np.array(Image.open(io.BytesIO(img_bytes)))
    noisy_np = np.array(Image.open(io.BytesIO(noisy_bytes)))
    
    diff = np.abs(orig_np.astype(np.float32) - noisy_np.astype(np.float32))
    print(f"Max diff: {diff.max()}")
    print(f"Mean diff: {diff.mean()}")
    
except Exception as e:
    import traceback
    traceback.print_exc()
