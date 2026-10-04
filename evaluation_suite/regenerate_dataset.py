import os
import sys
sys.path.append(r"C:\Users\shubh\Antigravity\backend")
from core_protection.noise_generator import apply_adversarial_noise

def main():
    clean_dir = r"C:\Users\shubh\Antigravity\evaluation_suite\dataset_clean"
    protected_dir = r"C:\Users\shubh\Antigravity\evaluation_suite\dataset_protected"
    
    os.makedirs(protected_dir, exist_ok=True)
    
    for filename in os.listdir(clean_dir):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            continue
            
        clean_path = os.path.join(clean_dir, filename)
        protected_path = os.path.join(protected_dir, filename)
        
        # Read clean image
        with open(clean_path, 'rb') as f:
            clean_bytes = f.read()
            
        print(f"Applying VAE latent poisoning to {filename}...")
        # Intensity 3 (Max) to ensure the LoRA is completely wrecked
        protected_bytes = apply_adversarial_noise(clean_bytes, intensity=3)
        
        # Save protected image
        with open(protected_path, 'wb') as f:
            f.write(protected_bytes)
            
    print("Done generating VAE-targeted dataset!")

if __name__ == "__main__":
    main()
