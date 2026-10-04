import numpy as np
from PIL import Image
import io
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import torch
import torch.nn.functional as F
from diffusers import AutoencoderKL
import torchvision.transforms as T

print("Loading Stable Diffusion VAE for Latent Space Poisoning Attack...")
vae_path = r"C:\Users\shubh\Antigravity\evaluation_suite\kohya_ss\models\v1-5-pruned-emaonly.safetensors"
if os.path.exists(vae_path):
    vae = AutoencoderKL.from_single_file(vae_path, torch_dtype=torch.float32)
else:
    vae = AutoencoderKL.from_pretrained("runwayml/stable-diffusion-v1-5", subfolder="vae", torch_dtype=torch.float32)

device = "cpu" # Forced to CPU because RTX 5050 (sm_120) lacks kernel images in current PyTorch builds
vae = vae.to(device)
vae.eval()
vae.requires_grad_(False)



# Stable diffusion VAE requires images to be normalized to [-1, 1]
def preprocess_for_vae(img_tensor):
    return img_tensor * 2.0 - 1.0


def get_texture_mask(tensor_image):
    sobel_x = torch.tensor([[-1., 0., 1.], [-2., 0., 2.], [-1., 0., 1.]]).view(1, 1, 3, 3).to(tensor_image.device)
    sobel_y = torch.tensor([[-1., -2., -1.], [0., 0., 0.], [1., 2., 1.]]).view(1, 1, 3, 3).to(tensor_image.device)
    grayscale = tensor_image.mean(dim=1, keepdim=True)
    edge_x = F.conv2d(grayscale, sobel_x, padding=1)
    edge_y = F.conv2d(grayscale, sobel_y, padding=1)
    magnitude = torch.sqrt(edge_x**2 + edge_y**2)
    # Smooth the magnitude to avoid sharp borders
    mask = F.avg_pool2d(magnitude, kernel_size=5, stride=1, padding=2)
    # Normalize and ensure minimum noise level in flat areas
    mask = mask / (mask.max() + 1e-8)
    # Apply exponential penalty to flat areas to protect smooth surfaces more aggressively
    mask = mask ** 1.5
    # Lower the minimum noise floor from 0.1 to 0.05
    mask = mask * 0.95 + 0.05
    return mask

def apply_adversarial_noise(image_bytes: bytes, intensity: int) -> bytes:
    # 1=Low, 2=Medium, 3=Max
    epsilons = {1: 8, 2: 16, 3: 32}
    epsilon = epsilons.get(intensity, 16)
    eps_tensor = epsilon / 255.0  
    alpha = eps_tensor / 5.0      
    num_steps = 20                
    
    orig_img = Image.open(io.BytesIO(image_bytes))
    original_format = orig_img.format
    img = orig_img.convert("RGB")
    
    orig_w, orig_h = img.size
    
    # Ensure image dimensions are manageable (max 1024 on longest edge)
    # Ensure image dimensions are manageable
    w, h = img.size
    max_dim = 1024 if device == "cuda" else 512
    if max(w, h) > max_dim:
        scale = max_dim / float(max(w, h))
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        w, h = img.size

    # Ensure image dimensions are multiples of 8 for the VAE
    new_w = (w // 8) * 8
    new_h = (h // 8) * 8
    if new_w != w or new_h != h:
        img = img.resize((new_w, new_h), Image.LANCZOS)
    
    input_tensor = T.ToTensor()(img).unsqueeze(0).to(device)
    
    # Get original latents
    with torch.no_grad():
        orig_latents = vae.encode(preprocess_for_vae(input_tensor)).latent_dist.mean
    
    mask = get_texture_mask(input_tensor)
    spatial_eps = eps_tensor * mask
    
    perturbed_tensor = input_tensor.clone().detach()
    # Kickstart PGD with random noise bounded by spatial_eps to escape zero-gradient
    perturbed_tensor = perturbed_tensor + torch.empty_like(perturbed_tensor).uniform_(-1.0, 1.0) * spatial_eps
    perturbed_tensor = torch.clamp(perturbed_tensor, 0.0, 1.0)
    
    for step in range(num_steps):
        perturbed_tensor.requires_grad = True
        
        # Forward pass through VAE
        latents = vae.encode(preprocess_for_vae(perturbed_tensor)).latent_dist.mean
        
        # Maximize the MSE difference in latent space
        loss = F.mse_loss(latents, orig_latents)
        
        vae.zero_grad()
        loss.backward()
        
        with torch.no_grad():
            grad = perturbed_tensor.grad.data
            
            # Apply High-Pass Filter to the gradient to constrain noise to higher frequencies
            # This prevents large, visible "wavy" low-frequency artifacts on smooth areas
            low_pass_grad = F.avg_pool2d(grad, kernel_size=5, stride=1, padding=2)
            high_pass_grad = grad - low_pass_grad
            grad = high_pass_grad
            
            # Apply gradient step scaled by spatial mask
            perturbed_tensor = perturbed_tensor + alpha * mask * grad.sign()
            
            # Clamp perturbations strictly within the spatial epsilon bounds
            delta = torch.clamp(perturbed_tensor - input_tensor, min=-spatial_eps, max=spatial_eps)
            perturbed_tensor = torch.clamp(input_tensor + delta, min=0.0, max=1.0)
            
    final_delta = (perturbed_tensor - input_tensor) * 255.0
    pgd_noise = final_delta.squeeze(0).permute(1, 2, 0).cpu().numpy()
    
    # We upscale the NOISE to the original resolution (using NEAREST to preserve sharp noise edges)
    noise_img = Image.fromarray(np.clip(pgd_noise + 128, 0, 255).astype(np.uint8))
    if noise_img.size != (orig_w, orig_h):
        noise_img = noise_img.resize((orig_w, orig_h), Image.NEAREST)
    upscaled_noise = np.array(noise_img).astype(np.float32) - 128.0
    
    # Apply upscaled noise to the original full-resolution image
    orig_img_rgb = orig_img.convert("RGB")
    orig_img_array = np.array(orig_img_rgb, dtype=np.float32)
    final_img_array = np.clip(orig_img_array + upscaled_noise, 0, 255).astype(np.uint8)
    noisy_img = Image.fromarray(final_img_array)
    
    img_byte_arr = io.BytesIO()
    if original_format in ['JPEG', 'JPG']:
        noisy_img.save(img_byte_arr, format='JPEG', quality=100)
    else:
        noisy_img.save(img_byte_arr, format='PNG', optimize=False)
        
    img_byte_arr.seek(0)
    return img_byte_arr.read()

def simulate_ai_vision(image_bytes: bytes) -> bytes:
    orig_img = Image.open(io.BytesIO(image_bytes))
    img = orig_img.convert("RGB")
    
    # Resize for fast preview and ensure multiple of 8
    w, h = img.size
    max_dim = 512
    if max(w, h) > max_dim:
        scale = max_dim / float(max(w, h))
        w = int(w * scale)
        h = int(h * scale)
        
    new_w = (w // 8) * 8
    new_h = (h // 8) * 8
    img = img.resize((new_w, new_h), Image.LANCZOS)
    
    input_tensor = T.ToTensor()(img).unsqueeze(0).to(device)
    
    with torch.no_grad():
        # Encode to latent space
        latents = vae.encode(preprocess_for_vae(input_tensor)).latent_dist.sample()
        # Decode back to image space
        decoded = vae.decode(latents).sample
        
    # Process output
    decoded = (decoded / 2 + 0.5).clamp(0, 1)
    decoded = decoded.cpu().permute(0, 2, 3, 1).squeeze(0).numpy()
    out_img = Image.fromarray((decoded * 255).astype(np.uint8))
    
    img_byte_arr = io.BytesIO()
    out_img.save(img_byte_arr, format='JPEG', quality=85)
    img_byte_arr.seek(0)
    return img_byte_arr.read()



