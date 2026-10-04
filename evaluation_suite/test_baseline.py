import torch
from diffusers import StableDiffusionPipeline
import os

def main():
    base_model_path = r"C:\Users\shubh\Antigravity\evaluation_suite\kohya_ss\models\v1-5-pruned-emaonly.safetensors"
    output_dir = r"C:\Users\shubh\Antigravity\evaluation_suite\results"
    
    prompt = "generate an image of naruto, myart"
    negative_prompt = "low quality, worst quality, bad anatomy, bad composition"
    
    print("Loading base Stable Diffusion model...")
    pipe = StableDiffusionPipeline.from_single_file(
        base_model_path, 
        torch_dtype=torch.float16,
        safety_checker=None
    )
    pipe = pipe.to("cuda")
    
    print("Generating baseline image (No LoRA)...")
    generator = torch.Generator(device="cuda").manual_seed(42)
    baseline_image = pipe(
        prompt, 
        negative_prompt=negative_prompt, 
        num_inference_steps=30, 
        guidance_scale=7.5,
        generator=generator
    ).images[0]
    
    baseline_path = os.path.join(output_dir, "baseline_result.png")
    baseline_image.save(baseline_path)
    print(f"Saved baseline image to: {baseline_path}")

if __name__ == "__main__":
    main()
