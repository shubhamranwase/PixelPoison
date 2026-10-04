import io
import urllib.request
from PIL import Image
import sys
import os

# Add backend to path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core_protection.noise_generator import apply_adversarial_noise, simulate_ai_vision

def demonstrate():
    print("="*60)
    print(" PIXELPOISON DEMONSTRATION (VAE POISONING) ".center(60, "="))
    print("="*60)
    print("\n1. Fetching a pristine test image...")
    
    req = urllib.request.Request(
        'https://picsum.photos/224/224',
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req) as response:
        img_bytes = response.read()
        
    print("2. Simulating AI Vision on Original Image...")
    clean_vision_bytes = simulate_ai_vision(img_bytes)
    
    print("\n3. Injecting Latent Space Poison (Max Intensity)...")
    noisy_bytes = apply_adversarial_noise(img_bytes, intensity=3)
    
    print("4. Simulating AI Vision on Poisoned Image...")
    poisoned_vision_bytes = simulate_ai_vision(noisy_bytes)
    
    print("\n[+] SUCCESS: The image has been poisoned.")
    print("    In a real scenario, the poisoned image's latents will heavily disrupt")
    print("    the Stable Diffusion fine-tuning process.")
    
if __name__ == "__main__":
    demonstrate()
