import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import argparse
import torch
from diffusers import StableDiffusionPipeline
import os
import gc
from PIL import Image
import torchvision.transforms as T
from torchmetrics.image import StructuralSimilarityIndexMeasure

def generate_image(pipe, lora_path, output_path, prompt, negative_prompt, lora_scale=2.5):
    print(f"\n--- Loading LoRA {os.path.basename(lora_path)} ---")
    pipe.load_lora_weights(lora_path)
    
    print(f"Generating image for prompt: '{prompt}'...")
    generator = torch.Generator(device="cpu").manual_seed(42) # Same seed for direct comparison
    image = pipe(
        prompt, 
        negative_prompt=negative_prompt, 
        num_inference_steps=30, 
        guidance_scale=7.5,
        generator=generator,
        cross_attention_kwargs={"scale": lora_scale}
    ).images[0]
    
    image.save(output_path)
    print(f"Saved to: {output_path}")
    
    # Unload lora weights so we can reuse the pipeline
    pipe.unload_lora_weights()

def main():
    parser = argparse.ArgumentParser(description="Generate comparison images using Clean and Poisoned LoRAs.")
    parser.add_argument("--prompt", type=str, required=True, help="Prompt to generate images for")
    parser.add_argument("--clean-out", type=str, required=True, help="Output path for the clean model image")
    parser.add_argument("--poisoned-out", type=str, required=True, help="Output path for the poisoned model image")
    
    args = parser.parse_args()
    
    base_model_path = r"C:\Users\shubh\Antigravity\evaluation_suite\kohya_ss\models\v1-5-pruned-emaonly.safetensors"
    clean_lora_path = r"C:\Users\shubh\Antigravity\evaluation_suite\kohya_ss\clean_workspace\model\clean_lora.safetensors"
    poisoned_lora_path = r"C:\Users\shubh\Antigravity\evaluation_suite\kohya_ss\training_workspace\model\poisoned_lora.safetensors"
    
    negative_prompt = "low quality, worst quality, bad anatomy, bad composition"
    
    print("Loading Base Pipeline...")
    pipe = StableDiffusionPipeline.from_single_file(
        base_model_path, 
        torch_dtype=torch.float32,
        safety_checker=None
    )
    pipe = pipe.to("cpu")
    
    generate_image(pipe, clean_lora_path, args.clean_out, args.prompt, negative_prompt, lora_scale=2.5)
    generate_image(pipe, poisoned_lora_path, args.poisoned_out, args.prompt, negative_prompt, lora_scale=2.5)
    
    del pipe
    gc.collect()
    
    print("Calculating SSIM...")
    try:
        img_c = Image.open(args.clean_out).convert("RGB")
        img_p = Image.open(args.poisoned_out).convert("RGB")
        
        if img_c.size != img_p.size:
            img_p = img_p.resize(img_c.size)
            
        transform = T.Compose([T.ToTensor()])
        tensor_c = transform(img_c).unsqueeze(0)
        tensor_p = transform(img_p).unsqueeze(0)
        
        ssim_metric = StructuralSimilarityIndexMeasure(data_range=1.0)
        val = ssim_metric(tensor_p, tensor_c).item()
        
        print(f"METRIC_SSIM={val:.4f}")
    except Exception as e:
        print(f"Error calculating SSIM: {e}")

if __name__ == "__main__":
    main()
