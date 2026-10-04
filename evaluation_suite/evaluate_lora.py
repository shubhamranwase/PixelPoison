import torch
from diffusers import StableDiffusionPipeline
import os
import gc

def generate_image(base_model_path, lora_path, output_path, prompt, negative_prompt, lora_scale=2.5):
    print(f"\n--- Loading Pipeline for {os.path.basename(lora_path)} ---")
    pipe = StableDiffusionPipeline.from_single_file(
        base_model_path, 
        torch_dtype=torch.float16,
        safety_checker=None
    )
    pipe = pipe.to("cuda")
    
    print(f"Loading LoRA weights from {lora_path}...")
    pipe.load_lora_weights(lora_path)
    
    print(f"Generating image for prompt: '{prompt}' with LoRA scale {lora_scale}...")
    generator = torch.Generator(device="cuda").manual_seed(42) # Exact same seed
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
    
    # Clean up memory completely
    del pipe
    torch.cuda.empty_cache()
    gc.collect()

def main():
    base_model_path = r"C:\Users\shubh\Antigravity\evaluation_suite\kohya_ss\models\v1-5-pruned-emaonly.safetensors"
    clean_lora_path = r"C:\Users\shubh\Antigravity\evaluation_suite\kohya_ss\clean_workspace\model\clean_lora.safetensors"
    poisoned_lora_path = r"C:\Users\shubh\Antigravity\evaluation_suite\kohya_ss\training_workspace\model\poisoned_lora.safetensors"
    output_dir = r"C:\Users\shubh\Antigravity\evaluation_suite\results"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Using a prompt that describes the actual subject of the training images 
    # gives the AI a foundation to apply the learned style correctly.
    prompt = "generate an image of naruto, myart"
    negative_prompt = "low quality, worst quality, bad anatomy, bad composition"
    
    clean_output = os.path.join(output_dir, "clean_result.png")
    poisoned_output = os.path.join(output_dir, "poisoned_result.png")
    
    generate_image(base_model_path, clean_lora_path, clean_output, prompt, negative_prompt, lora_scale=2.5)
    generate_image(base_model_path, poisoned_lora_path, poisoned_output, prompt, negative_prompt, lora_scale=2.5)
    
    print("\nDone! Check the results folder.")

if __name__ == "__main__":
    main()
