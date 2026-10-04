import os
import glob
from PIL import Image

def preprocess_directory(directory, size=(512, 512)):
    images = glob.glob(os.path.join(directory, "*.*"))
    images = [f for f in images if not f.endswith('.gitkeep')]
    
    if not images:
        print(f"No images found in {directory} to preprocess.")
        return
        
    print(f"Preprocessing {len(images)} images in {directory}...")
    
    for img_path in images:
        try:
            with Image.open(img_path) as img:
                # Convert to RGB to handle PNGs with alpha or grayscale
                img = img.convert("RGB")
                
                # 1. Center crop to 1:1 aspect ratio
                width, height = img.size
                min_dim = min(width, height)
                
                left = (width - min_dim) / 2
                top = (height - min_dim) / 2
                right = (width + min_dim) / 2
                bottom = (height + min_dim) / 2
                
                img_cropped = img.crop((left, top, right, bottom))
                
                # 2. Resize to target size (512x512)
                img_resized = img_cropped.resize(size, Image.Resampling.LANCZOS)
                
                # Overwrite original
                img_resized.save(img_path, quality=95)
            print(f"  Processed: {os.path.basename(img_path)}")
        except Exception as e:
            print(f"  Failed to process {img_path}: {e}")

if __name__ == "__main__":
    clean_dir = os.path.join(os.path.dirname(__file__), '..', 'dataset_clean')
    protected_dir = os.path.join(os.path.dirname(__file__), '..', 'dataset_protected')
    
    print("="*50)
    print(" DATASET PREPROCESSING ".center(50))
    print("="*50)
    preprocess_directory(clean_dir)
    print("-" * 50)
    preprocess_directory(protected_dir)
    print("="*50)
    print("Preprocessing complete!")
