import os
import glob
from PIL import Image
import torch
import torchvision.transforms as T
from torchmetrics.image import StructuralSimilarityIndexMeasure
import io
import sys
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding='utf-8')

def calculate_ssim(clean_dir, protected_dir):
    print("="*60)
    print(" SSIM (Structural Similarity) EVALUATION ".center(60))
    print("="*60)
    
    clean_images = sorted(glob.glob(os.path.join(clean_dir, "*.*")))
    protected_images = sorted(glob.glob(os.path.join(protected_dir, "*.*")))
    
    # Filter out non-image files like .gitkeep
    clean_images = [f for f in clean_images if not f.endswith('.gitkeep')]
    protected_images = [f for f in protected_images if not f.endswith('.gitkeep')]
    
    if not clean_images:
        print(f"Error: No images found in {clean_dir}")
        print("Please add some original test images to the dataset_clean folder.")
        return
    
    if len(clean_images) != len(protected_images):
        print("Warning: Unequal number of images in clean vs protected directories.")
        
    transform = T.Compose([
        T.ToTensor()
    ])
    
    ssim_metric = StructuralSimilarityIndexMeasure(data_range=1.0)
    
    total_ssim = 0.0
    count = 0
    
    for c_path, p_path in zip(clean_images, protected_images):
        try:
            img_c = Image.open(c_path).convert("RGB")
            img_p = Image.open(p_path).convert("RGB")
            
            # Ensure same size for SSIM
            if img_c.size != img_p.size:
                img_p = img_p.resize(img_c.size)
                
            tensor_c = transform(img_c).unsqueeze(0)
            tensor_p = transform(img_p).unsqueeze(0)
            
            val = ssim_metric(tensor_p, tensor_c).item()
            total_ssim += val
            count += 1
            print(f"SSIM for {os.path.basename(c_path)}: {val:.4f}")
        except Exception as e:
            print(f"Failed to process {c_path}: {e}")
            
    if count > 0:
        avg_ssim = total_ssim / count
        print("\n" + "="*60)
        print(f"FINAL AVERAGE SSIM SCORE: {avg_ssim:.4f}".center(60))
        print("="*60)
        
        if avg_ssim >= 0.98:
            print("\n✅ EXCELLENT: The protected images are visually identical to the human eye.")
            print("   The structural integrity is fully preserved.")
        elif avg_ssim >= 0.90:
            print("\n⚠️ GOOD: The protected images have minor visual noise, but retain core structure.")
        else:
            print("\n❌ POOR: Significant visual distortion detected. The perturbation is too aggressive.")
    else:
        print("No valid image pairs found.")

if __name__ == "__main__":
    clean = os.path.join(os.path.dirname(__file__), '..', 'dataset_clean')
    protected = os.path.join(os.path.dirname(__file__), '..', 'dataset_protected')
    calculate_ssim(clean, protected)
